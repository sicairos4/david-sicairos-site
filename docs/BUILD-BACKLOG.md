# 209 running build backlog

Updated 2026-10-19. Scope: requests visible in the current conversation and retrieved product preferences. This is not an assertion that inaccessible older chats were fully reviewed. Earlier assistant claims of missing work require source reconciliation before rebuilding existing features.

## Status rules

Source committed, compiled, deployed, installed, and acceptance passed are separate states. Never close a task based solely on a commit. No background implementation is implied. Never replace real records with fabricated seed filings.

## P0: Android and account access

- [ ] Compile and deliver APK 0.3.3 (code 6), install it, and confirm both launcher and opening-screen images. This batch adds an explicit green-backed brand drawable used by both surfaces; actual device failure cause remains unconfirmed.
- [ ] Establish production signing and stable update keys; debug CI keys are not a dependable upgrade path.
- [ ] Link APK receipt, exact source revision, website revision and download location.
- [ ] Verify Google login reaches the account-backed Workstation. User reports Supabase URL settings updated; successful sign-in is not established.
- [ ] Verify existing-account password setup, signup, confirmation, recovery and sign-out.
- [ ] Verify two-account isolation, saved-day reloads and revision conflicts.
- [ ] Verify deployed Aura app is retired. Legacy repository startup patch 4d98d40 is committed; hosted deployment remains unconfirmed. This batch disables the old site's Aura import workflow. Preserve users and saved data.

## P1: Workstation functionality

- [ ] Reconcile morning-step completion and repeated Morning-to-Schedule transfers.
- [ ] Finish saved monthly navigation, reusable routines/templates and optional unfinished-task carry-forward.
- [ ] Finish evening closeout and selected-task continuity across Tasks, Schedule and Focus.
- [ ] Consolidate session/state ownership and save/error/conflict indicators.
- [ ] Complete full backup/restore and storage/privacy controls.
- [ ] Acceptance: scheduler, day switching, protected sleep and unsaved edits on mobile.
- [ ] Preserve shared accounts/backend, aligned green/dark/gold theme, toolbar and mobile-first experience. Browser-backed launcher is not equivalent to a complete standalone/offline client.

## P1: Public Files

- [ ] Collect real Form 700s for City of Atwater government and Merced County government. Schools, independent special districts and other cities are deferred.
- [ ] Establish people/position roster and reporting-period coverage; record gaps without alleging nonfiling.
- [ ] Build durable database, document storage and controlled ingestion. Current fe1da49 implementation is a static JSON framework and browser, not an uploaded records database.
- [ ] Preserve sources, retrieval dates, hashes, page citations, review status and amendment chains.
- [ ] Review extraction, preserve official redactions and exclude unnecessary private contact details.
- [ ] Complete agency/person/interest search, CPRA request/response receipts, timelines and Master Tracker links.
- [ ] Complete Audit visitor journey and integrated CEDS source/analysis/alternative/progress presentation.

## P2: Website, store and learning

- [ ] Correct stretched website toolbar logo and reported dBeastco wrong route.
- [ ] Finish compact store/catalog/cart and payment/product/access delivery.
- [ ] Verify Morning/daily/weekly/monthly printable resources.
- [ ] Locate and reconcile the previously described six-pathway workbook batch; do not claim it exists without locating the files.
- [ ] Finish courses, paired videos, kits and learning outcomes.
- [ ] Finish homepage explanations, landing-page next steps, resume/business tools, Lifestyle ID and Realignment Room.
- [ ] Complete media playback and newsletter subscription/customer journeys.

## P2: Steering and integrations

- [ ] Obtain Muse runtime acknowledgement and genuine sanitized export; committed handoff/schema/validator/intake/viewer are not a live integration.
- [ ] Connect consented analytics and learning outcomes with authenticated privacy-controlled ingestion.
- [ ] Connect operator interface, reviewed publisher consumers, outcome receipts and rollback. No automatic publishing assumed.

## P1/P2: Operations and release

- [ ] Resolve status-monitor authorization failures; verify reports against current source/runtime.
- [ ] Establish backups and demonstrate restoration.
- [ ] Consolidate duplicate auth/theme/navigation handlers.
- [ ] Mobile/accessibility/download/metadata/indexing acceptance.
- [ ] Reconcile older docs and backlog with current source before closing or duplicating work.

## Human-dependent configuration

- [ ] Confirm production Auth configuration and authorized updater access without putting secrets in chat or public files.
- [ ] Worker Supabase credentials, analytics setup, newsletter API access, private-source access if still needed, and member Google authorizations. Reuse connected-service capabilities where appropriate rather than assume absent credentials.
- [ ] Publisher destinations/credentials, Android production signing and exact checkout/payment/QR destinations.

## Changes known from this conversation

- 53ff6e1: offline steering viewer source.
- 5ed5b24: Android visible logo/version source.
- 29fdb3f: APK packaging/checksum/receipt workflow source.
- fe1da49: Atwater/Merced Public Files static framework; zero collected filings at creation.
- aura-launchpad 4d98d40: legacy startup retirement source.
- Current batch: explicit native brand surfaces, canonical members/app.html destination, visible package ID, version 0.3.3, disabled Aura migration and this backlog. Await compilation/deployment/installation evidence.
