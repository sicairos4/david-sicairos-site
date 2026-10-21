# Public Files catalog

Existing public-files.html uses assets/audit-records.js to search published metadata in pf_documents. Titles, descriptions, agencies, document types, dates and keywords are searchable. Form 700 browsing stays separate. No full-PDF/OCR search or automatic Drive watcher is installed.

Documents live in Drive. Restricted originals and provenance must remain separate from approved public release copies. The manifest must have schema_version 1 and documents containing title, description, agency, document_type, document_date (YYYY-MM-DD or null), keywords (string array), source_url (public HTTPS source), public_document_url (verified release link), sha256 (original-byte lowercase hash), retrieved_at (timestamp with timezone). Do not import private email URLs or confidential metadata. The public copy may differ after redaction.

Dry run: python scripts/import_public_files.py manifest.json
Apply, only after approval: set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in a trusted local/server environment, then run python scripts/import_public_files.py manifest.json --apply. Never commit a service key or put it in browser code. Imports create drafts only, skip existing hashes without updating them and whitelist catalog fields. Network failure can leave a partial set of drafts; rerun to skip those. Concurrent duplicate inserts may fail rather than overwrite.

Review draft metadata, source bytes, redaction, release authorization and signed-out Drive access. Obtain owner approval before setting redaction_reviewed=true and review_status=published. Verify the real item appears in website search and opens signed out; verify Form 700 browsing and CSV export. Withdrawal removes the catalog item but does not revoke a Drive sharing link.

Run tests: python -m unittest discover -s tests -p test_public_files_import.py

Deploy the catalog SQL extension before this JavaScript. Existing RLS/read policies remain unchanged. No collection, publication or live end-to-end test is implied by this code commit.
