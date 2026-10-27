# Audit update repair — October 27, 2026

The corrected audit_archive_save_drive_intake_v1 migration was applied successfully to uwidjnnhdgtrpsymuhwp through the connected Supabase tool before this frontend patch was prepared. The first attempt failed with SQL syntax error 42601; the separately approved corrected retry succeeded. No private record was imported and no function call with user data was performed.

## Request updates

audit-workspace.js no longer submits version. Its update still filters owner, ID and expected version, then checks the returned identity, next revision and changed values. The existing database trigger owns version and updated_at. Existing column-level UPDATE grants remain unchanged.

## Drive intake

audit-drive-intake.js calls public.audit_archive_save_drive_intake_v1(p_document_id uuid,p_expected_version integer,p_details jsonb,p_review jsonb default null). p_details contains original, candidate (object or JSON null), public_metadata, batch_reference, source_message_reference and verification_reference. p_review is SQL null for a draft, otherwise an object with id, snapshot_sha256, safety_receipt_reference and redaction_receipt_reference. The function returns a SETOF audit_archive_documents; the client selects its existing columns and requires one row. No direct update fallback is used.

The installed SECURITY DEFINER function is owned by postgres with search_path pg_catalog. EXECUTE is revoked from PUBLIC and anon and granted to authenticated. It derives auth.uid(), locks that owner's private row, checks revision, validates allowed payload keys/types and lengths, rejects replacement of established original Drive ID/hash, preserves unrelated metadata and review history, and appends review receipts with server reviewer/time. The existing update trigger increments the revision. Direct restricted-column UPDATE grants were not broadened. The migration source remains in the Supabase migration record; this commit does not claim to add its SQL to the repository.

Public metadata source URLs reject credentials, query strings, fragments and known private mail/Drive hosts. This guard does not prove a URL or document is safe to publish.

## Receipt boundaries

The client checks returned ownership/revision, submitted binding and provenance, unrelated metadata preservation, prior receipt history and current review. A draft preserves current review only when the stored snapshot matches the new binding; otherwise it clears the pointer without deleting history.

snapshot_sha256 remains the browser-supplied operator digest. server_snapshot_sha256 is SHA-256 of Postgres JSONB text encoded as UTF-8, labelled postgres-jsonb-text-utf8-v1. They use different serialization contracts and must not be compared as though identical. Neither verifies Drive bytes, permissions, effective redaction or safety; basis remains operator-attestation-not-server-verified. Existing history is preserved, not retroactively certified. Other privileged and direct-insert paths are outside this update-only repair.

## Deferred work

No tests, browser checks, deployment verification, live user saves, imports, file transfers, publication or Muse runtime execution were performed. A successful migration and source commit do not establish runtime acceptance. Personal CHP publication hold and all private/public boundaries remain unchanged. Full-text storage, OCR/generator, relationships and the broader archive backlog remain separate.
