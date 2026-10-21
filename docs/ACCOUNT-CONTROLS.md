# Account controls

Backend migration: workstation_account_controls_v1, installed in the existing uwidjnnhdgtrpsymuhwp project. RPC contracts: workstation_account_manifest(), workstation_account_export_page(p_table,p_after,p_limit), workstation_delete_self(p_confirm_user,p_confirmation,p_export_acknowledged). No backend migration is rerun by this UI commit.

Settings > Your profile > Account controls loads a verified target identity. Export covers the 27 registered account-owned tables plus selected Auth identity/profile metadata. It uses bounded RPC pages and streamed JSONL where supported, otherwise downloadable parts. It is not an automatic restore file or a promise of a database-wide atomic snapshot. Credentials, Storage binaries, Drive files, shared/protected records, external providers, retained backups and device-only drafts are excluded. Existing planner backup/restore controls remain separate.

Self-deletion requires an active session, a recent new sign-in/token, configured MFA assurance where applicable, the matching account ID, DELETE MY ACCOUNT and an explicit export-choice acknowledgement. The server blocks owned Storage files, shared-resource relationships, protected records and unregistered account foreign keys. Registered owned-row cleanup and Auth user deletion occur in the same database transaction. Related-data failure rolls back the transaction. Do not auto-retry an uncertain deletion request.

The UI pins each operation to the verified user token and current account/day context, clears staged metadata and downloads on context changes, and signs out locally after a confirmed deletion. Existing JWTs can remain cryptographically valid until expiry; new account-control RPCs also require a live user/session, and registered ownership foreign keys prevent writes referencing a deleted user. Do not describe external provider accounts or retained backups as erased.

This source commit does not run an export, delete an account, or establish production deployment or acceptance. No tests are claimed.
