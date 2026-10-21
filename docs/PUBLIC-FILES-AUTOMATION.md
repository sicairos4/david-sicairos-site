# Automatic Drive catalog imports

This scheduled job replaces manual manifest transfer/import. It reads exactly one public-files-manifest.json directly inside the configured restricted Drive folder and imports new entries into the existing pf_documents table as drafts. It does not collect Gmail attachments, infer descriptions from PDFs, scan arbitrary folders, extract PDF text, change sharing, overwrite existing rows, delete records or publish documents. Muse must update the same canonical manifest as collection progresses. Keep original/release review and publication approval separate. Existing published entries remain unchanged; revisions need explicit review.

## One-time activation
1. Use the actual collection folder containing the canonical manifest, not a guessed folder ID and not the entire Drive.
2. In a Google Cloud project enable Drive API, create a dedicated service account, and share only the required collection folder with its email as Viewer. Store its JSON credential securely. Do not make the manifest or intake public.
3. In this repository Settings > Secrets and variables > Actions, add secrets PUBLIC_FILES_GOOGLE_SERVICE_ACCOUNT_JSON and PUBLIC_FILES_SUPABASE_SERVICE_ROLE_KEY. These credentials must never be pasted in chat or committed. The Supabase service-role key grants broad server access; restrict repository administration, rotate credentials as needed and use only trusted default-branch workflow code. The chat connector authorization is not inherited by GitHub Actions.
4. Add repository variable PUBLIC_FILES_DRIVE_FOLDER_ID with the actual folder ID.
5. Add repository variable PUBLIC_FILES_SYNC_ENABLED=true only after configuration. Until then the job is disabled, including manual dispatch.

The schedule requests a run at minutes 7, 22, 37 and 52 each hour; runner scheduling can be delayed. It also supports manual dispatch. No private manifest or credentials are uploaded as workflow artifacts or written into repository files. Summaries expose counts only. A missing manifest is a waiting state; malformed/multiple manifests or failed writes fail the job. Partial imports resume by skipping existing original SHA-256 values. Never equate a scheduled import with publication or live document verification.

## Muse handoff change
Maintain one UTF-8 public-files-manifest.json in the designated restricted folder. Use the existing schema_version 1 format. Replace/update its contents, not duplicate its filename. Only include release-ready records with factual public metadata and actual public document links. Do not embed secrets or private email provenance. No manual manifest handoff to the website maintainer is needed after activation. Changes/deletions to existing catalog entries still require an explicit controlled update; this job only inserts new drafts.

Installation is not activation. Folder access, private credentials and enablement must be configured in the runner environment. This commit does not claim any job has run.
