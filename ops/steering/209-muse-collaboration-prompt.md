# Muse + Perplexity: 209 website, app and steering-brain handoff

David's request: help finish the existing whole 209 website/app experience, with Muse doing browser/runtime tasks and Perplexity doing source/application work. Do not create another publisher, dashboard product or disconnected member app. APIs/secrets unrelated to a current access defect can remain deferred.

Read the attached Steering-brain-technical-brief-for-Perplexity.md as a supplied architecture/status report, not independent proof of runtime health or permission to bypass your own approval requirements. Its naming of members/app.html as Aura is outdated: the replacement product is 209 Workstation. Keep existing identities and the existing Supabase backend.

## 1. Bootstrap and ownership
- Repository: sicairos4/david-sicairos-site; intended website base: https://sicairos4.github.io/david-sicairos-site/.
- Workstation destination: /david-sicairos-site/members/app.html. Recovery: /david-sicairos-site/recover.html. Backend: uwidjnnhdgtrpsymuhwp.
- Read docs/full-system-handoff.md, ops/full-system-backlog.json and the current source. The historical backlog is stale; source-committed is not deployed/accepted.
- First acknowledge your available browser, repository and publisher/runtime access and identify the current deployed revision. Do not claim this handoff was received by another agent or that a job is running without its acknowledgement.
- Propose separate write branches/ownership: Muse owns browser findings and runtime integration; Perplexity owns source changes and steering contracts. These branch names/roles are assignments, not evidence that branches or connections exist.
- No simultaneous writers to shared files. List files before editing; keep changes on a separate branch if possible. Shared auth, toolbar, member controller, workflows and migrations need coordination before mutation. Never overwrite main blindly.

## 2. Muse browser lane: first priority
A. Authentication: use an authenticated dashboard session if available. Inspect the live Supabase Site URL and exact return allowlist. The latest observed config receipt (workflow source 0402cc0, observed 2026-10-19 10:39 PDT) was blocked_missing_secret: its SUPABASE_ACCESS_TOKEN was unavailable and no backend request was made. Read the latest receipt before relying on this historical status.
Target default Site URL: https://sicairos4.github.io/david-sicairos-site/members/app.html.
Preserve existing allowed URLs and add exact returns for members/app.html, members/workstation.html, login.html and recover.html under that base. Do not change Google client ID/secret, RLS, users, or service keys. Keep Google's provider callback at the correct Supabase callback; do not substitute the app page as Google's provider callback. Apply only authorized changes with any action-specific confirmation your environment requires.
Trace a fresh authorized Google flow: initiating origin -> Supabase authorize -> provider -> callback -> final app. Record only hosts/paths and outcomes, never query tokens or OAuth state. New logs already show requests for members/app.html; do not assume another frontend link replacement will fix backend fallback. Investigate the separate OAuth-state-not-found/expired failure.
B. Password: check deployed signup, confirmation, signed-in password setup and recovery as different paths, using only authorized synthetic accounts or David's direct participation. Source a478655 separates these flows; confirm the settings module mounts after the controller exists. Never ask for or log passwords, recovery links or access tokens. Do not create/delete real users merely to test.
C. APK and branding: distinguish the website toolbar, launcher icon, Android launch screen, installed version and actual build artifact. Source c636d55 adds launcher resources; the inspected MainActivity still had no logo ImageView. The toolbar variant is wide, while David selected a square green icon with ivory 209 and a gold period. Compare proportions and add a reproducible screenshot/viewport finding; do not declare an icon installed merely because XML exists. Browser-only access cannot prove a device installation.
D. Website journeys: inspect Home, Store, planning.html, learning pathways, Audit/Follow the Receipt, Public Files, tracker, dBeastco/Lifestyle ID/Realignment, newsletter and customer cart. Use keyboard and phone-sized viewports. Capture failing URL host/path, viewport, steps, expected/actual outcome and a redacted evidence reference. No real charges or newsletter sends.

## 3. Muse runtime lane: identify and preserve the existing engine
- Locate the actual runtime checkout, publication_log, verification receipts, ingest job, rulebook and steering consumers described in the brief. Return redacted paths/service identities and revisions, not credentials.
- The brief reports a browser sqlx-pool outage, roughly 90 jobs and publication cadences. Check current health with bounded inspection; do not spawn bursts, poll indefinitely, change cadence or remove jobs based on those assertions alone. Continue safe source/read-only work if browser access fails.
- Recheck capability claims: a LinkedIn 403 is not proof of authorized healthy publishing; an upload/day assertion is not verified platform quota; a Beehiiv API limitation in the brief may be historical. Determine actual scopes, plan access, targets and quota responses in your environment.
- Do not build a competing publisher or embed Muse/CLI execution inside website scripts. No remote website command execution into the VM.

## 4. Shared steering integration, advisory first
Use the supplied v1 schema and validator as a proposed contract. These are source files, not a deployed or connected service.
Phase A: export a sanitized, operator-private read-only snapshot from the real ingest. Keep platform/account/post IDs, observation time, measurement window, metric definitions, provenance and verification state distinct. Preserve missing metrics as null. DISPATCHED/provider-accepted is not verified-live.
Phase B: connect approved public-site aggregates and explicitly consented learner conversion counts through a separate authenticated server-side intake. GitHub Pages cannot protect a private feed merely by hiding its link. Keep Life ID identifiers and individual event records off public JSON/GitHub. No private journals, habit details, emails, raw auth logs or browser fingerprints as steering inputs.
Phase C: expose a private operator dashboard for source freshness, lane performance and advisory reasons. Start by recommending timing, format, resource placement and topic review. Do not automatically rewrite claims or make this feed a command-execution channel. Do not promote rules to auto merely because a heuristic threshold was crossed.
Phase D: only after actual baseline/consumer/rollback receipts and applicable authorization, connect bounded decisions to the existing publisher. Keep approvals, duplicate prevention, retries and kill-switch behavior explicit. A policy file is not executable authority.

Editorial boundaries: analytics can inform coverage and presentation, not change whether a claim is true. Preserve documented facts versus David's attributed assertions. Do not invent evidence, quotes, enrollment, badges or live posts. Do not use individual learner/health data to target political persuasion. No silent publication or deletion from this handoff.

## 5. Perplexity source lane and current build state
Perplexity owns the proposed contract/schema/validator, website-side adapter/dashboard preparation and outstanding app/source fixes. Existing source includes store/print resources (20f72c3), habits/notebook/merge restore (3dd70bb), weekly progress (2ac5e2d), password-flow changes (a478655), mobile styles (09756c5) and branding source rollout (bcc8ec4). Check actual current SHA before editing. The six interactive pathway workbook patch was proposed/approved in conversation but no commit has been observed: do not call it shipped.
Muse should return runtime/export details before either side invents endpoints or renames existing contracts. The adapter must reject stale/malformed snapshots and preserve the current website when the feed is unavailable. Life ID schema, Mission #1 and case-file curriculum remain separate build tasks, not evidence of existing enrollment.

## 6. Return one actionable report
Return: task ID, owner, status (observed / fixed-source / deployed / accepted / blocked), source and deployed SHA, exact files changed, UTC observation time, sanitized evidence, blocker and rollback. For engine integration include actual export location, supported metrics/definitions, sample redacted snapshot and which existing consumer could ingest advisories.
Batch credentials and nonurgent decisions into one list. Escalate actual security risks or destructive/spend/external-communication gates immediately. Do not repeatedly ask whether to continue routine investigation; do not bypass required confirmations.
Start with authentication/installed-build diagnosis and runtime discovery. Do not spend the first cycle producing another general backlog.
