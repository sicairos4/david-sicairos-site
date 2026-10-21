# Public Files operations

Owner: repository administrator for sicairos4/david-sicairos-site. A GitHub issue titled Public Files import failed receives a run URL on failed scheduled runs only when PUBLIC_FILES_SYNC_ENABLED=true; repository issue notifications must be enabled by the operator. It contains no document data or credentials. This workflow does not authorize or perform publication.

If a run fails: pause PUBLIC_FILES_SYNC_ENABLED by setting it to false if the cause could leak content or create bad drafts. Inspect Actions logs privately. Confirm the canonical restricted manifest and the actual folder ID, service-account scope, Supabase server secret and source permissions. Repair the cause. The importer skips an existing original SHA-256; a failed write may have succeeded, so never blind-retry a different payload. Re-enable only after the inputs are corrected. A run that is skipped while disabled is not a success signal.

The existing .github/workflows/backup.yml archives the website repository weekly for 90 days as an Actions artifact. This is neither an off-host copy nor a Supabase database backup; retain a separate protected off-host repository copy and database backup before claiming disaster recovery. Rotation order for the Drive service account and Supabase server credential: create replacement privately, change repository Actions secrets, verify authorized read/import from a non-public manifest, revoke the old credential; never paste secrets in an issue or commit.

Account-control failures: stop an uncertain deletion; do not automatically retry it. A user may need operator assistance when Storage ownership, shared resources or protected records block deletion. External files, provider accounts and retained database backups have separate handling and are never described as erased by the website RPC.

This file and failure workflow do not activate Drive sync, establish email paging, prove an off-host backup, or fix production hosting.
