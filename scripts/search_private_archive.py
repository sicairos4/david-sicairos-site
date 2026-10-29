"""Local, read-only consumer for Muse's existing page-text snapshot. No network."""
import argparse
import collections
import getpass
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def load_private(path):
    resolved = Path(path).expanduser().resolve(strict=True)
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError('Private inputs must be outside the repository')
    with resolved.open('rb') as stream:
        raw = stream.read(128 * 1024 * 1024 + 1)
    if len(raw) > 128 * 1024 * 1024:
        raise ValueError('Input exceeds 128 MiB')
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def validate(index, catalog):
    if not isinstance(index, list) or not isinstance(catalog, dict):
        raise ValueError('Expected index array and catalog object')
    if not isinstance(catalog.get('files'), list) or not isinstance(catalog.get('missing'), list):
        raise ValueError('Catalog requires files and missing arrays')
    if any(not isinstance(r, dict) for r in catalog['files'] + catalog['missing']):
        raise ValueError('Invalid catalog rows')
    ids = set()
    for row in index:
        if not isinstance(row, dict):
            raise ValueError('Invalid index row')
        for key in ('file', 'entity', 'drive_file_id', 'text_status'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('Missing index identity or status')
        if row['drive_file_id'] in ids:
            raise ValueError('Repeated Drive ID; reconcile before search')
        ids.add(row['drive_file_id'])
        if not isinstance(row.get('pages'), list):
            raise ValueError('Expected page array')
        page_ids = set()
        for page in row['pages']:
            if not isinstance(page, dict) or type(page.get('page')) is not int or page['page'] < 1 or page['page'] in page_ids or not isinstance(page.get('text'), str):
                raise ValueError('Invalid or duplicate page locator')
            page_ids.add(page['page'])
    def key(row, entity_field):
        if not isinstance(row.get('file'), str) or not isinstance(row.get(entity_field), str):
            raise ValueError('Invalid catalog identity')
        return row[entity_field], row['file']
    expected = [key(r, 'folder') for r in catalog['files']]
    actual = [key(r, 'entity') for r in index]
    if collections.Counter(expected) != collections.Counter(actual):
        raise ValueError('Index/catalog file sets differ; no partial search displayed')
    for row in catalog['missing']:
        key(row, 'folder')

def search(index, catalog, terms, agency, limit, index_hash, catalog_hash):
    selected = [r for r in index if not agency or r['entity'].casefold() == agency.casefold()]
    missing = [r for r in catalog['missing'] if not agency or r['folder'].casefold() == agency.casefold()]
    searchable = [r for r in selected if r['text_status'] == 'ok' and any(p['text'].strip() for p in r['pages'])]
    hits = []
    matched_ids = set()
    matched_agencies = set()
    matching_pages = 0
    for row in searchable:
        for page in row['pages']:
            folded = page['text'].casefold()
            if not all(term.casefold() in folded for term in terms):
                continue
            matching_pages += 1
            matched_ids.add(row['drive_file_id'])
            matched_agencies.add(row['entity'])
            if len(hits) < limit:
                original = page['text']
                positions = [i for term in terms if (i := original.lower().find(term.lower())) >= 0]
                start = max(0, min(positions, default=0) - 100)
                snippet = original[start:start + 500]
                hits.append({'file': row['file'], 'agency_label': row['entity'], 'drive_file_id': row['drive_file_id'], 'page': page['page'], 'excerpt': snippet, 'excerpt_is_partial': start > 0 or start + 500 < len(original), 'match_basis': 'All literal terms on this page; no entity identity or role inferred'})
    excluded = [r for r in selected if r not in searchable]
    return {'format': '209-private-page-search-v1', 'visibility': 'private', 'snapshot_sha256': {'index': index_hash, 'catalog': catalog_hash}, 'coverage': {'scope': 'Supplied snapshot and optional agency-label filter, not all audit matters', 'retrieved_file_copies': len(selected), 'copies_with_searchable_text': len(searchable), 'excluded_copy_count': len(excluded), 'excluded': [{'file': r['file'], 'agency_label': r['entity'], 'text_status': r['text_status']} for r in excluded], 'missing_attachment_count': len(missing), 'missing': [{'file': r['file'], 'agency_label': r['folder']} for r in missing], 'missing_and_excluded_are_not_query_matches': True}, 'matches': {'page_count': matching_pages, 'drive_copy_count': len(matched_ids), 'agency_labels': sorted(matched_agencies), 'returned_pages': len(hits), 'truncated': matching_pages > len(hits)}, 'results': hits, 'limitations': ['Not OCR, not an index generator, not a backend or website endpoint', 'No hash deduplication: counts refer to Drive copies, not unique documents', 'Literal mentions do not establish vendor identity, role, relationships or wrongdoing', 'No result does not establish absence; missing/unsearchable files were not searched', 'Input checksums identify snapshots, not original-file integrity; no Drive/Gmail lookup performed', 'JSON output contains private text; do not publish or redirect into the website/repository']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--agency', help='Exact case-insensitive existing agency label')
    parser.add_argument('--limit', type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.limit <= 500:
        parser.error('Limit must be 1–500')
    try:
        index, index_hash = load_private(args.index)
        catalog, catalog_hash = load_private(args.catalog)
        validate(index, catalog)
        print('PRIVATE OUTPUT: use an authorized local terminal, not CI or shared logs. Enter literal terms separated by |; all must occur on the same page.', file=sys.stderr)
        raw = getpass.getpass('Private search terms (not echoed): ')
        terms = list(dict.fromkeys(t.strip() for t in raw.split('|') if t.strip()))
        if not terms or len(terms) > 20 or any(len(t) > 200 for t in terms):
            raise ValueError('Use 1–20 nonempty terms, each at most 200 characters')
        print(json.dumps(search(index, catalog, terms, args.agency, args.limit, index_hash, catalog_hash), ensure_ascii=True, indent=2))
    except (ValueError, OSError, TypeError, KeyError, EOFError):
        parser.exit(1, 'Private search stopped: unreadable/invalid input, mismatched snapshot, or invalid query. No source changed.\n')

if __name__ == '__main__':
    main()
