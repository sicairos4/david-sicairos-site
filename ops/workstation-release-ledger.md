# Workstation release and blocker ledger

Source-level checkpoint, not a deployed release certificate. Update completion only with observed results. Never store member records, tokens, passwords, recovery URLs or raw auth logs here.

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
