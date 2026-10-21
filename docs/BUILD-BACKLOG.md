# 209 running build backlog

Updated 2026-10-21 for Batch 1 small corrections. Source baseline: 8f9e995cc9cbb4d8a7e8a89fb173a92add31420c. This is a targeted reconciliation of recent source and status records, not a whole-system audit. Preserve requirements and working modules; do not rebuild a feature because an older checkbox calls it missing.

## Status and scope

Source committed, compiled, deployed, installed and acceptance passed are separate states. User-deferred tests and phone/account checks remain unverified, not passed, and are not the current implementation queue. Historical acceptance requirements are retained below. No background implementation, publishing or execution authority is implied. Never replace real records with fabricated filings.

Normal personal-planner output is Save PDF. Preserve section selection, preview, filled/blank pages, task filters and optional writing space. JSON/CSV/text export and file import are not normal planning steps. Technical recovery implementation remains separate; hiding its controls is not data deletion. Public Files editorial intake is not a personal-planner upload.

## Already implemented in source: extend, do not rebuild

- Native Google browser launch, package-specific callback, PKCE exchange and isolated WebView session handoff: 8f9e995 and NATIVE-GOOGLE-RETURN.md. Callback configuration, deployed handoff and runtime outcomes are separate.
- Full-screen embedded Android workspace and native print/text helpers: 4231a84. The preview remains online, debug-signed and backed by live website content, not a standalone/offline client.
- Account save read-back: e7dee0c; Schedule Cancel focus correction: 3688b0f.
- Guided Morning execution/session controls and optional cues: ae176a7.
- Sign-in-first entry, guest access and optional continuation controls: 4abea4e.
- Settings panes and selected-day output: 69862b3; normal personal output simplified to PDF-only: 67f427d. The shared panel already covers routines, Morning sessions, priorities, tasks, schedules, habits, journal, prompts, notes, milestones, Creator draft, closeout and selected-day weekly-review text.
- Reusable lists, repeat-rule management, matching-day manual addition and explicit unfinished-task copying; planner/toolkit export and owner-matched missing-day restore; optional preference and revision-checked toolkit restore: WORKSPACE-TOOLKIT-STATUS.md and WORKSPACE-TOOLKIT-COMPLETION.md. No automatic background recurrence is implied.
- Compact store shelves, optional existing Ecwid catalog, hosted-store/cart destinations and product fallbacks; public Morning/day/week/month worksheets: store.html, planning.html and public-resource-batch.md. Do not replace the existing cart merely because new digital-course delivery remains unfinished.
- Six learning pathways and optional task handoff exist. The three newer starter workbook/landing drafts recorded in PRODUCT-AND-BUILD-ROADMAP.md are not yet repository course assets. Neither set proves delivery of the separately promised six-workbook batch.
- Public Files browser/filtering/search, metadata exports, reviewed-PDF links and local draft intake: FORM700-LIBRARY.md; Audit/Tracker presentation and source links: 3aac88d. This is not persistent intake or evidence of real filings collection.
- Beehiiv/YouTube worker source and web adaptation source exist. They do not establish a live social publisher; see automation-implementation-status.md.
- Batch 1 source change: initialize each backup disclosure collapsed once per DOM element instead of closing it on every rearrangement; retain PDF-only copy and update login help. No runtime acceptance is claimed.

## P0: Android and account implementation/configuration

- [ ] Activate the intended package-specific Supabase callback routes and deployed native handoff page. Do not reimplement native Google merely because activation or acceptance remains open.
- [ ] Establish protected production signing, stable update keys and dependable release/download automation. Debug CI keys are not a dependable upgrade path.
- [ ] Finish demonstrated password setup, signup, confirmation, recovery, sign-out and email-delivery configuration gaps without weakening access policies.
- [ ] Finish demonstrated account/day state, saved-record loading and revision-conflict gaps. Preserve users and saved data.
- [ ] Retire remaining legacy Aura hosted entry points through authorized configuration; repository retirement source alone does not establish hosted retirement.

## P1: Workstation implementation

- [ ] Finish demonstrated gaps in Morning completion/transfer, saved monthly navigation, reusable routines/lists and carry-forward. Reuse existing modules and explicit save behavior.
- [ ] Finish selected-task identity and continuity across capture, Tasks, Schedule, Focus, course practice and Review; preserve records and undo/reschedule semantics.
- [ ] Consolidate competing session/state and DOM-layout ownership, save/error/conflict handling and account/day clearing.
- [ ] Add the roadmap's Agenda/Timeline switch, compact task cards and Make today lighter without silent deletion or schedule shifts.
- [ ] Extend existing selected-day PDFs to course worksheets or genuine multi-day reports where required; selected-day weekly-review text is not a seven-day aggregate.
- [ ] Finish large-account backup pagination, broader account export coverage, privacy/storage controls and account deletion. Current restore skips existing days by default and excludes identity/password/browser-draft coverage; do not call it full-account restore.
- [ ] Keep optional user-owned Drive backup separate from ordinary PDF saving; do not request broad storage permissions merely to save a PDF.
- [ ] Preserve shared accounts/backend, green/dark/gold theme, toolbar, mobile-first layout and distinction between online WebView, browser launcher and offline software.

## P1: Public Files

- [ ] Collect and review real City of Atwater and Merced County government Form 700s. Schools, independent special districts and other cities remain deferred.
- [ ] Establish people/position roster and reporting-period coverage; record gaps without alleging nonfiling.
- [ ] Extend existing schema/intake/browser into durable document storage and controlled persistent ingestion/review/publication. Preserve access policies; do not recreate tables blindly.
- [ ] Preserve official sources, retrieval dates, original/public-copy hash distinctions, page citations, review decisions and amendment chains.
- [ ] Review extraction and official redactions; exclude unnecessary private contact details.
- [ ] Extend existing search and source links with CPRA request/response receipts, timelines and Master Tracker relationships; finish large-scale search/consistent reads where needed.
- [ ] Finish Audit/CEDS sources, interpretation, alternatives and progress presentation.

## P2: Website, store and learning

- [ ] Finish specific navigation/logo/destination inconsistencies, including the reported dBeastco route, from actual source rather than replacing working pages.
- [ ] Publish the three reviewed starter course landing pages, PDFs, accessible HTML lessons and worked examples when their draft assets are available; connect the existing hubs to explicit destinations.
- [ ] Reconcile the separate six-workbook commitment and remaining courses, paired videos, kits and learning outcomes.
- [ ] Finish new digital-product checkout/access delivery and authorized product/payment/QR destinations; preserve existing Ecwid catalog/cart routes and public printables.
- [ ] Finish remaining homepage explanations, landing next steps, resume/business tools, Lifestyle ID and Realignment Room gaps without rebuilding existing modules.
- [ ] Finish media playback and newsletter subscription, consent, welcome, unsubscribe and customer journeys.

## P2: Social, Muse and analytics

- [ ] Extend Creator with saved platform-specific draft variants, destination previews and explicit Copy/Share actions. No private journal content is selected automatically.
- [ ] Add user-initiated browser/Android sharing with fallbacks; opening a share sheet is not publication.
- [ ] Locate and acknowledge the actual Muse/publisher runtime and obtain a genuine sanitized export; preserve healthy integrations and avoid a competing publisher.
- [ ] Connect authorized server-side account adapters, persistent scheduling, duplicate prevention, pause/retry controls and publication receipts/rollback to that runtime.
- [ ] Connect consented social/website/learning analytics and outcome IDs through authenticated privacy-controlled ingestion. Existing assistant connectors do not automatically belong to the app or unattended worker.
- [ ] Keep editorial approval/authority, provider-accepted state and actual published outcome distinct. No automatic publishing is authorized by this backlog.

## P1/P2: Operations

- [ ] Resolve status-monitor authorization failures and finish redacted operational reporting, secret rotation, recovery ownership and off-host backups.
- [ ] Establish operational restore separately from existing user-facing planner recovery.
- [ ] Consolidate demonstrated duplicate auth/theme/navigation handlers without replacing working modules blindly.
- [ ] Finish actual accessibility, responsive layout, downloads, metadata and indexing gaps.
- [ ] Reconcile remaining older documents and R00-R23 states against source and evidence. The historical ops/full-system-backlog.json is not made an executable queue or automatically updated by this file.

## Deferred acceptance record: not the current build batch

- Installed APK/source/checksum/receipt/download and live-web revision correspondence; launcher/opening artwork, full-screen display, keyboard, Back, restart, print/file destinations and upgrades remain unverified here. The older full-screen APK compile/install was user-reported complete; do not ask for repeated installation without a concrete reason.
- Existing-account signup, confirmation, recovery, sign-out, Google access, email delivery, account isolation, saved-day reloads and revision conflicts remain unverified here.
- Morning completion/transfer, carry-forward, scheduling, protected sleep, day switching, unsaved edits, learning handoff and recovery behavior remain unverified here.
- Public deployment, actual database/storage policies, customer checkout, real-record publication, hosted Aura retirement and operational restoration remain unverified here.
- No test or device-check commands are part of Batch 1. Existing GitHub workflows are unchanged; source changes can still trigger their normal automation. Source wiring assertions and a successful commit are not runtime acceptance.

## Human-dependent configuration

- [ ] Authorized production Auth updater access and callback configuration; never place secrets in chat or public files.
- [ ] Worker Supabase access, analytics identities/scopes, newsletter scopes, private-source access if needed and member Google consent. Discover connected capabilities before assuming credentials are absent; connection alone does not establish every scope.
- [ ] Publisher destination/authority, protected signing and exact authorized checkout/payment/QR destinations. No private-data migration, payment activation or publication is authorized by this file.

## Historical references

- The prior full 2026-10-20 checkpoint is preserved in repository history at 8f9e995: docs/BUILD-BACKLOG.md.
- 215ffbd: authentication test repair; a75cb48: isolated full-screen recipe; 01525d1: candidate pipeline. These are historical source references, not current build targets or pass receipts.
- 53ff6e1: offline steering viewer; 5ed5b24: visible Android logo/version; 29fdb3f: packaging/checksum/receipt source.
- fe1da49: initial static Public Files framework; its original zero-filings statement is not a current database inventory.
- aura-launchpad 4d98d40 and disabled migration source: historical retirement progress, not hosted-retirement evidence.
- Old version 0.3.3/code 6 and the 2026-10-19 brand/migration checkpoint are not instructions to rebuild an old APK.

Batch 1 changes Settings behavior, login help and these planning records only. It does not change database schemas, records, credentials, payment destinations, signing, workflows, releases or machine-readable execution/publication flags.
