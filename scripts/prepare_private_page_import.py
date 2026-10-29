"""Prepare private page-text SQL for explicit approval. No network or database writes."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import uuid


def read(path):
    if path.stat().st_size > 67108864:
        raise ValueError('Each source must be under 64 MiB')
    raw = path.read_bytes()
    return json.loads(raw.decode('utf-8-sig')), hashlib.sha256(raw).hexdigest()


def literal(value):
    text = str(value)
    if '\x00' in text:
        raise ValueError('NUL characters cannot be imported')
    return "'" + text.replace("'", "''") + "'"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True, type=pathlib.Path)
    parser.add_argument('--catalog', required=True, type=pathlib.Path)
    parser.add_argument('--mapping', required=True, type=pathlib.Path)
    parser.add_argument('--owner', required=True, type=uuid.UUID)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new private output directory')
    index, index_hash = read(args.index)
    catalog, catalog_hash = read(args.catalog)
    mapping, mapping_hash = read(args.mapping)
    if not isinstance(index, list) or not isinstance(catalog, dict) or not isinstance(catalog.get('files'), list) or not isinstance(catalog.get('missing'), list) or not isinstance(mapping, dict):
        raise ValueError('Unsupported source structures')
    if any(len(v) > 20000 for v in [index, catalog['files'], catalog['missing']]):
        raise ValueError('Source list exceeds 20000 entries')
    def key(row, agency_key):
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k] for k in [agency_key, 'file']):
            raise ValueError('Invalid source identity')
        return row[agency_key], row['file']
    expected = [key(row, 'folder') for row in catalog['files']]
    actual = [key(row, 'entity') for row in index]
    if len(set(expected)) != len(expected) or len(set(actual)) != len(actual) or set(expected) != set(actual):
        raise ValueError('Catalog/index mismatch or duplicate labels')
    for row in catalog['missing']:
        key(row, 'folder')
    ids, targets, prepared = set(), set(), []
    for row in index:
        drive = row.get('drive_file_id')
        if not isinstance(drive, str) or not re.fullmatch(r'[A-Za-z0-9_-]{10,200}', drive) or drive in ids:
            raise ValueError('Invalid or repeated Drive identity')
        ids.add(drive)
        if drive not in mapping:
            raise ValueError('Explicit existing-document mapping required for every Drive identity')
        document = str(uuid.UUID(mapping[drive]))
        if document in targets:
            raise ValueError('Repeated target document')
        targets.add(document)
        status = row.get('text_status')
        if not isinstance(status, str) or not status or len(status) > 100 or not isinstance(row.get('pages'), list):
            raise ValueError('Invalid extraction status/pages')
        seen, chunks = set(), []
        for page in row['pages']:
            if not isinstance(page, dict):
                raise ValueError('Invalid page object')
            number, text = page.get('page'), page.get('text')
            if type(number) is not int or not 1 <= number <= 100000 or number in seen or not isinstance(text, str):
                raise ValueError('Invalid or repeated page locator')
            if '\x00' in text:
                raise ValueError('NUL characters cannot be imported')
            seen.add(number)
            if status != 'ok':
                continue
            for start in range(0, len(text), 50000):
                body = text[start:start + 50000]
                chunk = start // 50000 + 1
                if chunk > 10000:
                    raise ValueError('Page exceeds chunk limit')
                if body.strip():
                    chunks.append({'page_number': number, 'chunk_number': chunk, 'body': body})
        normalized = 'partial' if chunks else ('no_text' if status == 'ok' else 'failed')
        prepared.append({'document': document, 'drive': drive, 'generation': str(uuid.uuid4()), 'status': normalized, 'source_status': status, 'pages': chunks})
    if set(mapping) != ids:
        raise ValueError('Mapping contains unused or missing identities')
    owner = literal(args.owner)
    statements = ['begin;', "set local standard_conforming_strings = on;", "set local lock_timeout = '5s';", "select pg_advisory_xact_lock(hashtextextended(" + owner + " || ':archive-page-import',0));"]
    for item in prepared:
        doc, drive, generation = map(literal, [item['document'], item['drive'], item['generation']])
        payload = literal(json.dumps(item['pages'], ensure_ascii=False, separators=(',', ':')))
        note = literal('Source text_status=' + item['source_status'] + '; page completeness and original bytes are not certified. Only source status ok is indexed.')
        block = f"""declare original_hash text;
begin
 select d.sha256 into original_hash from public.audit_archive_documents d
 where d.owner_id={owner}::uuid and d.id={doc}::uuid and d.drive_file_id={drive} for update;
 if not found then raise exception 'Owner/document/Drive binding missing or changed'; end if;
 if exists(select 1 from public.audit_archive_extractions e where e.owner_id={owner}::uuid and e.document_id={doc}::uuid) then
  if exists(select 1 from public.audit_archive_extractions e where e.owner_id={owner}::uuid and e.document_id={doc}::uuid and e.source_snapshot_sha256={literal(index_hash)} and e.drive_file_id={drive} and e.original_sha256 is not distinct from original_hash) then return; end if;
  raise exception 'Extraction already exists; replacement requires separate approval';
 end if;
 insert into public.audit_archive_extractions(owner_id,document_id,generation,drive_file_id,original_sha256,source_snapshot_sha256,source_label,text_status,processing_note)
 values({owner}::uuid,{doc}::uuid,{generation}::uuid,{drive},original_hash,{literal(index_hash)},'archive-search-index.json',{literal(item['status'])},{note});
 insert into public.audit_archive_pages(owner_id,document_id,generation,page_number,chunk_number,body)
 select {owner}::uuid,{doc}::uuid,{generation}::uuid,x.page_number,x.chunk_number,x.body
 from jsonb_to_recordset({payload}::jsonb) as x(page_number integer,chunk_number integer,body text);
end;"""
        delimiter = '$import_' + uuid.uuid4().hex + '$'
        while delimiter in block:
            delimiter = '$import_' + uuid.uuid4().hex + '$'
        statements.append('do ' + delimiter + '\n' + block + '\n' + delimiter + ';')
    statements.append('commit;')
    receipt = {'format': '209-private-page-import-plan-v1', 'owner_id': str(args.owner), 'index_sha256': index_hash, 'catalog_sha256': catalog_hash, 'mapping_sha256': mapping_hash, 'document_references': len(prepared), 'page_chunks': sum(len(i['pages']) for i in prepared), 'catalog_missing_entries': len(catalog['missing']), 'missing_entries_imported': 0, 'metadata_created': 0, 'executed': False, 'tested': False, 'notice': 'Private plan only. Approve the exact SQL before database execution. Existing document mappings are required. No publication or completeness assertion.'}
    args.output.mkdir(parents=True, mode=0o700)
    for name, content in [('private-page-import.sql', '\n'.join(statements) + '\n'), ('private-page-import-receipt.json', json.dumps(receipt, indent=2) + '\n')]:
        path = args.output / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            output.write(content)


if __name__ == '__main__':
    main()
