# 209 Connect Workstation — release and blocker ledger

Source-level checkpoint, not a deployed release certificate. Update completion only with observed results. Never store member records, tokens, passwords, recovery URLs or raw auth logs here.

## Current reconciliation: 2026-10-29

The requested product/project name is 209 Connect Workstation. The existing backend reference remains uwidjnnhdgtrpsymuhwp. This documentation update does not rename the Supabase dashboard project, database, URLs, OAuth configuration or Android identity. Dashboard rename remains pending an authorized management action.

This is the existing release ledger, not a second tracker or executable queue. Read alongside docs/BUILD-BACKLOG.md, docs/CONSOLIDATED-SOURCE-STATUS.md and current implementation. Historical unchecked boxes and ops/full-system-backlog.json are not proof that newer source is missing. Source present, configured, deployed, runtime accepted and blocked remain distinct. Do not rebuild working modules or mark all jobs complete from a documentation change.

### Drive and Public Files completion queue

| Item | Current evidence/status | Completion requirement |
| --- | --- | --- |
| 1. Reconcile cleanup | Partial observations; no complete cleanup receipt reconciled | Obtain Muse's retained/trashed ID and move receipts; verify exceptions without repeating completed actions. |
| 2. Preserve source artifacts | Protected package and separate document dataset must remain distinct; independent package identification/hash check outstanding | Locate original bytes and provenance in the authorized private workspace. Do not overwrite, regenerate, merge, publish or discard either artifact during cleanup. Keep identifying fingerprints and private paths out of this public ledger. |
| 3. Document-to-Drive mapping | Last approved database audit found audit_archive_documents empty; this does not mean Drive is empty | Reconcile actual source dataset and upload receipts to retained file IDs and original-byte hashes. Prepare an owner-bound import for separate exact approval; do not fabricate mappings or infer matter completion. |
| 4. Missing attachments | Historical retrieval-gap list exists; current recovery has not been reconciled | Resolve each historical gap against actual bytes and provenance. A found email, attachment name, duplicate removal or substituted document is not recovery. |
| 5. Matter/source reconciliation | Some correspondence and generic-file contents reviewed; whole inventory not verified | Preserve request identifiers and categories; reconcile current correspondence before changing statuses or deadlines. Keep personal CHP publication hold intact. |
| 6. Release access | Last approved catalog audit found existing published/reviewed rows; flags alone do not prove current Drive access or effective redaction | Verify exact release versions, approval basis and signed-out access. No blanket parent-folder sharing, private-source publication or new release approval is implied. |
| 7. Catalog reconciliation | Existing pf_documents links reference specific newer Merced instances | Protect catalog-linked IDs during deduplication; do not default to oldest upload. Update links only through an exact approved change with rollback information. |
| 8. Complete Drive coverage | Partial paginated inventory only | Finish pagination, record coverage and exclusions, compare full-file hashes, preserve unique versions, and produce an action receipt. No full-audit or storage-reclamation claim from partial results. |

### Execution and privacy boundaries

- Use one canonical file per distinct document; move rather than create additional unchanged copies. Private originals and substantively different/redacted releases are distinct artifacts.
- Before trashing, identify exact retained/redundant IDs, verify equivalence and existing references, and obtain required action confirmation. Trashing is not permanent deletion or reclaimed storage.
- Do not delete entire repeated directory trees until unique contents, links and access boundaries are reconciled. Signed records and OCR differences require appropriate comparison, not filename inference.
- Drive move/trash/sharing and Supabase project rename are not exposed by the assistant's currently inspected connectors. Muse actions require actual capability and receipts; this file does not dispatch Muse.
- No database import, schema or RLS change, public release, workflow dispatch, credentials change, payment action or permanent deletion is performed or authorized merely by this ledger update. Existing push-triggered automation may run normally.
- Public Files collection/release work remains separate from personal-planner UI, social publishing and unrelated court screenshots. Do not put private correspondence or protected source datasets in GitHub.
- Fix independent demonstrated source defects in bounded, coordinated batches; use actual runtime evidence for acceptance. Preserve existing authorization gates and historical records.

## Source checkpoint: 2026-10-19

- 7588ed4: Google authorization URL validation and initialization handling committed. Backend settings and live login remain unconfirmed.
- aaa74a7: record scheduler, morning handoff, protected sleep and undo committed. Browser behavior and live save/reload remain unconfirmed.
- 6e344fd: account-first member interface and browser-backed Android source committed. Installation and live login remain unconfirmed.
- This patch uses WorkstationApp.record and WorkstationApp.busy, which the controller actually exposes, plus the account-mode indicator and a server-verified session. It does not claim to expose the adapter user ID. Backend ownership remains enforced by the existing Cloud adapter's identity checks, save RPC and RLS.
- The earlier proposed use of WorkstationApp.mode/userId/loaded was not committed: those getters are absent from the controller.

## Running credential register

| Secret | Consumer | Status |
| --- | --- | --- |
| SUPABASE_ACCESS_TOKEN | Production auth configuration; project uwidjnnhdgtrpsymuhwp | User will add later; successful run unconfirmed |
| SUPABASE_URL, SUPABASE_SERVICE_KEY | YouTube, Beehiiv and adaptation workers | Availability and successful worker runs unconfirmed |
| GA4_PROPERTY_ID, GA4_CREDENTIALS | Adaptation worker | Property identity and report access unconfirmed |
| BEEHIIV_API_KEY | Newsletter sync | Scope/publication and sync receipts unconfirmed |
| AURA_SOURCE_READ_TOKEN | Optional reviewed private-source migration build | Required only for that build |

Use GitHub Actions secrets, never client code or chat. GitHub supplies its workflow token. Do not copy external publisher credentials here until its real runtime and secret store are resolved.

## Ordered next work

1. Record source/deployed revisions and actual APK build outcome.
2. After the user's credential setup, run the existing auth-config workflow and resolve Google/email/recovery return behavior.
3. Use two authorized accounts with synthetic records for save/reload, day switches, revision conflict, preferences, digest reads, sign-out and account-switch isolation.
4. Finish Morning-to-Day acceptance, duplicate-transfer prevention, accessible editing, guided habits/notebook and non-destructive export/restore.
5. Reconcile all R00-R23 jobs against current source and evidence. Preserve the distinction between committed, deployed, accepted and blocked.

## Batched human decisions

- Exact payment/QR recipients and checkout destinations.
- Explicit private-data migration and user-owned cloud scopes.
- Actual Muse publisher, authority, transport and credential store.
- Protected Android signing identity and production distribution.

Continue independent code work while blocked items wait. This ledger does not dispatch an executor, enable unattended coding, authorize publishing, or change execution_enabled/auto_publish in the historical backlog.
