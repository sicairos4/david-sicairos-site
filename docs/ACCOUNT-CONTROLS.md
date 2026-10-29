# Account controls

Backend migration: workstation_account_controls_v1, installed in the existing uwidjnnhdgtrpsymuhwp project. RPC contracts: workstation_account_manifest(), workstation_account_export_page(p_table,p_after,p_limit), workstation_delete_self(p_confirm_user,p_confirmation,p_export_acknowledged).

## Archive-text coverage update — 2026-10-28

The approved migration workstation_account_archive_text_coverage_v1 returned success. Its source is recorded in supabase/workstation_account_archive_text_coverage_v1.sql. Recording this source does not execute it again; do not rerun it against the already-migrated project. The source file assumes the existing account-controls and private archive page-search schema; it is not a complete fresh-database bootstrap.

The shared registry now declares 29 account-owned tables, up from 27. Added audit_archive_pages (owner_id, export_id cursor, cleanup order 1) and audit_archive_extractions (owner_id, document_id cursor, cleanup order 2). Existing entries/order are retained. Pages receive a technical UUID export_id with a unique owner/export index. This is a pagination key, not a document identity, source hash or verification receipt. Children precede parent archive documents during explicit self-deletion.

The existing manifest/export-page/deletion RPCs consume this shared registry; they were not replaced. Authentication, recent-sign-in/MFA checks, confirmation text, operator blockers, grants and row-level access policies were not relaxed. No user export, deletion, archive import, live acceptance check or tests were performed. Migration success is not proof of end-to-end export/deletion behavior.

## Export scope

Settings > Your profile > Account controls loads a verified target identity. Export covers the registered account-owned tables plus selected Auth identity/profile metadata, now including saved private archive extraction metadata and page text. It uses bounded RPC pages and streamed JSONL where supported, otherwise downloadable parts. It is not an automatic restore file or a promise of a database-wide atomic snapshot. Credentials, Storage binaries, external Drive originals, shared/protected records, external providers, retained backups and device-only drafts are excluded. Existing planner backup/restore controls remain separate. Save unencrypted exports privately. The current UI loads its table list from the backend manifest, not a hardcoded table count.

## Deletion safeguards

Self-deletion requires an active session, a recent new sign-in/token, configured MFA assurance where applicable, the matching account ID, DELETE MY ACCOUNT and an explicit export-choice acknowledgement. The server blocks owned Storage files, shared-resource relationships, protected records and unregistered account foreign keys. Registered owned-row cleanup and Auth user deletion occur in the same database transaction. Related-data failure rolls back the transaction. Do not auto-retry an uncertain deletion request.

The UI pins each operation to the verified user token and current account/day context, clears staged metadata and downloads on context changes, and signs out locally after a confirmed deletion. Existing JWTs can remain cryptographically valid until expiry; account-control RPCs also require a live user/session, and registered ownership foreign keys prevent writes referencing a deleted user. Do not describe external provider accounts, original Drive files or retained backups as erased.

## Remaining limits

This closes the specifically identified archive-text registry omission, not a complete new audit of every ownership relationship. Shared-state/stale-operation integration remains separate coordinated work. Paginated exports are not cross-table atomic snapshots, and no account-restore capability is implied. Actual archive source ingestion remains separate. Older private-import/browser notes describing text export coverage as pending are superseded only for this registry addition, not for live acceptance.
