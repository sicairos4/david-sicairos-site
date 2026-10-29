"""Build a PRIVATE review queue from Gmail archive manifests. No network or publication."""
import argparse
import datetime
import json
import pathlib
import re

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output exists; choose a new private output directory.')
    documents, messages, errors, skipped = {}, {}, [], []
    for path in sorted(args.archive.rglob('*.json')):
        try:
            item = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(item, dict) or item.get('schemaVersion') != 1 or not isinstance(item.get('attachments'), list) or not item.get('gmailMessageId'):
                skipped.append(str(path))
                continue
            mailbox = item.get('mailbox', '')
            mid = str(item['gmailMessageId'])
            source_key = mailbox + ':' + mid
            messages[source_key] = {k: item.get(k) for k in ('mailbox', 'gmailMessageId', 'gmailThreadId', 'dateUtc', 'from', 'to', 'cc', 'subject', 'sourceEmlFileId', 'retrievedAtUtc')}
            for attachment in item['attachments']:
                digest = attachment.get('sha256', '')
                file_id = attachment.get('driveFileId', '')
                if not re.fullmatch(r'[0-9a-f]{64}', digest) or not re.fullmatch(r'[A-Za-z0-9_-]+', file_id):
                    raise ValueError('Attachment lacks valid hash or Drive ID')
                row = documents.setdefault(digest, {
                    'sha256': digest, 'title': attachment.get('originalFilename', ''),
                    'mime_type': attachment.get('mimeType'), 'bytes': attachment.get('bytes'),
                    'agency': None, 'matter_ids': [], 'document_type': None,
                    'review_status': 'private_intake', 'publication_status': 'private',
                    'redaction_reviewed': False, 'public_document_url': None,
                    'extraction_status': 'pending', 'sources': []
                })
                source = {'message_key': source_key, 'drive_file_id': file_id,
                          'ordinal': attachment.get('ordinal'),
                          'original_filename': attachment.get('originalFilename'),
                          'retrieved_at': item.get('retrievedAtUtc')}
                if source not in row['sources']:
                    row['sources'].append(source)
        except (ValueError, TypeError, AttributeError, OSError) as error:
            errors.append({'path': str(path), 'error': str(error)})
    args.output.mkdir(parents=True)
    payload = {'schema_version': 1, 'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'visibility': 'private', 'messages': list(messages.values()),
               'documents': list(documents.values()), 'errors': errors, 'skipped_files': skipped}
    (args.output / 'private-attachment-intake.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps({'messages': len(messages), 'unique_documents': len(documents),
                      'errors': len(errors), 'skipped_files': len(skipped), 'published': 0}))

if __name__ == '__main__':
    main()
