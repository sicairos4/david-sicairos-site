# Private attachment intake: execution handoff

Owner confirms Muse uses sicairos4@gmail.com. Do not request a separate Muse sharing grant or enable public-link access. This document is a handoff, not a dispatch mechanism or evidence that Muse ran it.

## Existing archive

Use the established private Drive archive and existing agency folders; do not create a parallel archive. Retrieve original attachments through owner-authorized Gmail access. Preserve EML source, original filenames, attachment bytes, timestamps, Drive IDs, SHA-256, and the version-1 per-message JSON manifests produced by the supplied Gmail Apps Script. Do not commit source manifests or private records to this repository.

## Execution order

1. Download the actual CHP production attachments, not another inventory: messages 1a092cb1980a7a48 (nine PDFs) and 1a13757339ab7449 (four PDFs), request R009119-062926. Preserve Gmail originals.
2. Continue Tuolumne and Boyenga/education correspondence, then the complete audit matter list. Distinguish campaign comments, public records, court access, discovery, and patient access.
3. Archive each matter's records privately. Keep unidentified provenance in a private unattributed queue rather than guessing the agency.
4. Export the per-message JSON manifests to a private working directory and run the adapter below. It merges identical attachment hashes while preserving distinct delivery references. It does not fetch Drive files, extract PDF text, verify file bytes against hashes, or assign an agency from a filename.
5. Use the queue for private narrative updates, production comparisons, reply drafts, and extraction. Do not send drafts automatically.
6. Prepare separate reviewed public versions. Only approved versions and approved-copy extracted text may enter public pages/search.

## Adapter command

```sh
python scripts/prepare_attachment_intake.py /private/path/manifests --output /private/path/new-intake-batch
```

This is an execution command, not a test run. Use a new output directory. Inspect the reported error count; errors do not establish completion. The output contains private email metadata and must stay outside the public repository, website directory, public storage, and public search index.

## Existing integration boundary

The current scripts/import_public_files.py requires source_url and public_document_url and always inserts drafts. Do not manufacture a public URL for a restricted original. The new private queue deliberately does not feed that importer until a separately reviewed public copy and correct metadata exist.

The existing scripts/sync_public_files_drive.py uses GOOGLE_SERVICE_ACCOUNT_JSON and SUPABASE_SERVICE_ROLE_KEY. Owner-authorized Muse access does not automatically authorize that service account. Leave credentials and permissions unchanged; this handoff uses the private export path instead. Never put secrets into browser code or this repository.

## Speed and completion

Optional automated tests, browser checks, and presentation polish are deferred at the owner's request. Retain source references, private/public separation, required action approvals, and truthful file-transfer receipts. A saved checklist is not a completed ingestion run. Public publication and outgoing communications remain separate approved actions. No background runtime, deployment, OCR, database write, or attachment transfer is installed merely by this commit.
