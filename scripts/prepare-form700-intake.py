import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ORGS = {'city-atwater-ca', 'county-merced-ca'}
TYPES = {'annual', 'assuming_office', 'leaving_office', 'candidate', 'amendment', 'other'}
FIELDS = {'organization_slug', 'official_name', 'position_title', 'statement_type', 'reporting_period_start', 'reporting_period_end', 'filed_date', 'source_url', 'retrieved_at', 'amends_external_id'}

def prepare(metadata, document):
    if not isinstance(metadata, dict) or set(metadata) - FIELDS:
        raise ValueError('Metadata must use only documented fields; personal contact fields are not accepted.')
    for key in ('organization_slug', 'official_name', 'position_title', 'statement_type', 'source_url', 'retrieved_at'):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError('Missing required text: ' + key)
    if metadata['organization_slug'] not in ORGS:
        raise ValueError('Organization is outside the initial collection scope.')
    if metadata['statement_type'] not in TYPES:
        raise ValueError('Unsupported statement type.')
    url = urlsplit(metadata['source_url'])
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.fragment:
        raise ValueError('Use an official HTTPS source URL without credentials or fragments.')
    for key in ('reporting_period_start', 'reporting_period_end', 'filed_date'):
        if metadata.get(key):
            dt.date.fromisoformat(metadata[key])
    start, end = metadata.get('reporting_period_start'), metadata.get('reporting_period_end')
    if start and end and dt.date.fromisoformat(start) > dt.date.fromisoformat(end):
        raise ValueError('Reporting period is reversed.')
    retrieved = dt.datetime.fromisoformat(metadata['retrieved_at'].replace('Z', '+00:00'))
    if retrieved.tzinfo is None:
        raise ValueError('Retrieval timestamp requires a timezone.')
    if metadata['statement_type'] == 'amendment' and not metadata.get('amends_external_id'):
        raise ValueError('Amendment requires the original external ID.')
    if not document.startswith(b'%PDF-'):
        raise ValueError('Input is not a PDF; templates and guidance must not be imported as completed filings.')
    digest = hashlib.sha256(document).hexdigest()
    return {'schema_version': 1, 'external_id': 'sha256:' + digest, 'metadata': metadata, 'document_sha256': digest, 'document_bytes': len(document), 'review_status': 'draft', 'redaction_reviewed': False, 'published': False, 'warning': 'Human source, filer identity, completed-filing and redaction review required. No automatic upload or publication.'}

def main():
    parser = argparse.ArgumentParser(description='Prepare a private Form 700 intake receipt without uploading or publishing.')
    parser.add_argument('--metadata', required=True, type=Path)
    parser.add_argument('--pdf', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    receipt = prepare(json.loads(args.metadata.read_text(encoding='utf-8')), args.pdf.read_bytes())
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(receipt, handle, indent=2)
        handle.write('\n')

if __name__ == '__main__':
    main()
