# 209 running build backlog

Updated 2026-10-20. Documentation reconciliation of the existing backlog, current conversation, and source-status documents. This is not a whole-system source audit or a claim that every older conversation was reviewed. Preserve requirements; do not rebuild an existing feature solely because an older checkbox says it is missing.

## Status rules

Source committed, compiled, deployed, installed, and acceptance passed are separate states. User-reported results are evidence with that attribution, not independently observed results. An open checkbox below represents remaining work, not necessarily missing code. No background implementation is implied. Never replace real records with fabricated seed filings.

## Reconciled checkpoint: 2026-10-20

| Item | Reconciled status | Remaining evidence or work |
| --- | --- | --- |
| Old APK 0.3.3/code 6 build-and-install target | Historical target; not the current rebuild instruction. User reports the full-screen test APK compiled and was already installed. | Exact installed APK checksum/build receipt was not supplied; launcher/opening images, device navigation and account acceptance remain unverified. Do not ask the user to repeat installation without a concrete reason. |
| Authentication test repair | Source committed at 215ffbd1d316726b7c1f905d1cbb07eab5cf8f61. | Full CI results were not independently retrieved. This is not proof of live account access. |
| Isolated full-screen APK recipe | Source committed at a75cb48be2e8909e42ef4d235cbbfb7d3eb3e149. Test package com.sicairos.workstation.fullscreentest is separate from existing apps. | User-reported compile/install above is not a receipt-to-device match. Google return-to-app is not implemented in this preview; it uses live website content and debug signing. |
| Consolidated candidate pipeline | Source committed at 01525d182b18b1fa1b060fcd267884d49a4fa084. JavaScript, Python and browser checks gate the full-screen APK. | Completion/results unverified. A test/build pipeline does not implement the remaining feature backlog. |
| Repeat rules, reusable lists and task carry-forward | Existing implementation documented in [WORKSPACE-TOOLKIT-STATUS.md](WORKSPACE-TOOLKIT-STATUS.md); verify before duplicating. | Real-account writes, conflict handling, carry-forward and mobile acceptance remain open. Nothing repeats or schedules automatically in the background. |
| Planner/toolkit backup and restore | Export and owner-matched missing-day restore documented in [WORKSPACE-TOOLKIT-STATUS.md](WORKSPACE-TOOLKIT-STATUS.md). | Real-account recovery tests and accounts over 25 MB remain open. This is not full-account restore; profile/identity metadata, passwords and browser-only drafts are excluded. |
| Six learning pathways | Pathways and optional Today task preview documented in [WORKSPACE-TOOLKIT-STATUS.md](WORKSPACE-TOOLKIT-STATUS.md). | Verify links, preview/add/save and mobile behavior. This does not establish that every previously promised workbook, course or video batch exists. |
| Public Files static-only description | Historical fe1da49 description is not a complete current inventory. SQL and intake-validator source are described in [PUBLIC-FILES-DEPLOYMENT.md](PUBLIC-FILES-DEPLOYMENT.md); later status notes also need reconciliation. | Verify actual database/browser deployment and storage/ingestion. Conflicting or older documents are not proof of deployed tables, collected filings or acceptance. |

No feature or integration acceptance gate is closed by this documentation update. The historical ops/full-system-backlog.json is not reconciled by this patch and is not an executable queue; its execution and publication flags are unchanged.

## P0: Android and account access

- [ ] Finish device acceptance of the installed test build: match its receipt/checksum to source; verify launcher and opening-screen images, full-screen display, keyboard, Back navigation and app restart. Compilation and installation are user-reported done, not new implementation tasks.
- [ ] Establish production signing and stable update keys; debug CI keys are not a dependable upgrade path.
- [ ] Match the installed APK, build receipt, source revision, live website revision and actual download location. The current full-screen preview does not pin website content.
- [ ] Implement and verify secure Google return-to-app for the full-screen client. Separately verify website Google login reaches the intended account-backed Workstation. User-reported backend settings changes are not live sign-in acceptance.
- [ ] Verify existing-account password setup, signup, confirmation, recovery and sign-out, including actual email delivery.
- [ ] Verify two-account isolation, saved-day reloads and revision conflicts.
- [ ] Verify deployed Aura app is retired. Legacy repository startup patch 4d98d40 and disabled import-workflow source are historical progress, not hosted-retirement evidence. Preserve users and saved data.

## P1: Workstation functionality

- [ ] Reconcile and test existing morning-step completion and repeated Morning-to-Schedule transfers before adding duplicate implementations. See DAILY-FLOW-ACCEPTANCE.md and MORNING-TRANSFER-ACCEPTANCE.md; source documentation is not runtime acceptance.
- [ ] Verify saved monthly navigation and existing routine/template, reusable-list and unfinished-task carry-forward behavior; implement only demonstrated gaps. See WORKSPACE-TOOLKIT-STATUS.md and CARRY-FORWARD-ACCEPTANCE.md.
- [ ] Verify documented evening closeout and finish selected-task continuity across Tasks, Schedule and Focus. Preserve existing records and explicit save behavior.
- [ ] Consolidate remaining session/state ownership and save/error/conflict inconsistencies against actual source; test focused-field clearing, sign-out and account/day switches.
- [ ] Verify existing planner/toolkit export and missing-day restore; finish large-account pagination and storage/privacy controls. Define remaining full-account coverage rather than describing the existing feature as absent or complete.
- [ ] Acceptance: scheduler, day switching, protected sleep and unsaved edits on mobile.
- [ ] Preserve shared accounts/backend, aligned green/dark/gold theme, toolbar and mobile-first experience. The browser-backed launcher and the isolated online WebView test are distinct; neither establishes a standalone/offline client.

## P1: Public Files

- [ ] Collect and review real Form 700s for City of Atwater government and Merced County government. Schools, independent special districts and other cities are deferred. This reconciliation provides no collection evidence.
- [ ] Establish people/position roster and reporting-period coverage; record gaps without alleging nonfiling.
- [ ] Reconcile existing SQL schema, intake validator and browser source with the actual deployed database. Verify durable document storage, controlled ingestion and access policies; do not recreate tables blindly from old setup instructions.
- [ ] Preserve sources, retrieval dates, hashes, page citations, review status and amendment chains.
- [ ] Review extraction, preserve official redactions and exclude unnecessary private contact details.
- [ ] Complete and verify agency/person/interest search, CPRA request/response receipts, timelines and Master Tracker links.
- [ ] Complete Audit visitor journey and integrated CEDS source/analysis/alternative/progress presentation.

## P2: Website, store and learning

- [ ] Verify toolbar-logo sizing after existing styling work; reproduce the reported dBeastco wrong route before changing it.
- [ ] Finish compact store/catalog/cart and payment/product/access delivery; verify existing source before rebuilding it.
- [ ] Verify Morning/daily/weekly/monthly printable resources.
- [ ] Verify the documented six learning pathways and Today task preview. Separately locate/reconcile the exact promised six-pathway workbook batch; pathways alone do not prove workbook delivery.
- [ ] Finish courses, paired videos, kits and learning outcomes.
- [ ] Finish homepage explanations, landing-page next steps, resume/business tools, Lifestyle ID and Realignment Room.
- [ ] Complete media playback and newsletter subscription/customer journeys.

## P2: Steering and integrations

- [ ] Obtain Muse runtime acknowledgement and genuine sanitized export; committed handoff/schema/validator/intake/viewer are not a live integration.
- [ ] Connect consented analytics and learning outcomes with authenticated privacy-controlled ingestion.
- [ ] Connect operator interface, reviewed publisher consumers, outcome receipts and rollback. No automatic publishing assumed.

## P1/P2: Operations and release

- [ ] Resolve status-monitor authorization failures; verify reports against current source/runtime.
- [ ] Establish operational backups and demonstrate restoration. Keep this distinct from the existing user-facing planner export/restore feature.
- [ ] Consolidate demonstrated duplicate auth/theme/navigation handlers without replacing working modules blindly.
- [ ] Mobile/accessibility/download/metadata/indexing acceptance.
- [ ] Reconcile remaining older documents and R00-R23 backlog states against source and observed evidence. This file cleanup does not mark that system-wide audit complete.

## Human-dependent configuration

- [ ] Confirm production Auth configuration and authorized updater access without putting secrets in chat or public files.
- [ ] Verify worker Supabase access, analytics setup, newsletter API scopes, private-source access if still needed, and member Google authorizations. Check connected-service capabilities before assuming credentials are absent; connection alone does not prove every required scope.
- [ ] Resolve publisher destinations/authority, protected Android production signing and exact checkout/payment/QR destinations. No private-data migration, payment setup or publishing is authorized merely by this backlog.

## Historical source references

- 53ff6e1: offline steering viewer source.
- 5ed5b24: Android visible logo/version source.
- 29fdb3f: APK packaging/checksum/receipt workflow source.
- fe1da49: initial Atwater/Merced Public Files static framework; zero collected filings at its creation, not a current database inventory.
- aura-launchpad 4d98d40: legacy startup-retirement source.
- The 2026-10-19 brand surfaces, canonical members/app.html destination, package display, version 0.3.3 and disabled Aura migration are historical changes, not an instruction to rebuild that old APK.

Cleanup scope: this file only. No app code, database, workflow, credential, payment destination, release or machine-readable execution flag changes.
