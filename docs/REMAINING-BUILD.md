# Complete remaining-build specification

Recorded 2026-10-21. Baseline observed: main at 69862b30de927ab6d60babee29f2eb318c4b0af3 (simplified settings and unified selected-day output). This document records remaining work; it does not implement features, verify live deployments, start background work, authorize publication or mark acceptance passed.

Preserve existing implementation: full-screen WebView, welcome/entry redesign, navigation/install changes, save guard, guest-import validation, Creator tools, Form 700 library, toolkit and restore functionality. Do not rebuild a feature solely because an older checklist says it is missing.

Status vocabulary:
- Build: code or functionality still needs implementation.
- Finish: source exists, but gaps or integration work remain.
- Activate: authorized configuration, credentials or real content are required.
- Accept: establish that the delivered implementation actually works. Acceptance is a release gate, not a requirement to stop after every small edit.

Source committed, compiled, deployed, installed and acceptance passed are separate states. All requirements below remain open until supported by appropriate evidence. Preserve real records; never substitute fabricated filings or outcomes.

## 1. Native Google sign-in and return-to-app

Status: not implemented at the documented checkpoint. Website redirect settings alone do not implement it.

- [ ] Build a coordinated flow for the current Android WebView architecture, not the retired browser launcher.
- [ ] Open Google authentication in the system browser.
- [ ] Create a fresh PKCE attempt and bind the return to that attempt.
- [ ] Register supported callbacks for each Android package variant.
- [ ] Reject unsolicited, expired, mismatched, malformed and repeated callbacks.
- [ ] Carry a one-time authorization code, not access or refresh tokens, in the callback.
- [ ] Exchange the code where the matching verifier is held; establish the session, verify the account and enter the workspace.
- [ ] Handle cancellation, retry, app recreation, process loss and network failure without accepting another attempt.
- [ ] Preserve email/password and guest access.
- [ ] Update affected source, manifest, build recipes and receipt descriptions together.
- [ ] Activate required Supabase callbacks through authorized configuration. The previously reported missing management secret is a separate configuration issue, not proof that app code exists.

## 2. Account access and private-data safety

Status: implementation exists; live failures and acceptance remain unresolved.

- [ ] Finish signup, confirmation email, resend, existing-account password setup, recovery, Google sign-in and local-device sign-out.
- [ ] Make errors actionable without exposing passwords, tokens, recovery links or raw server responses.
- [ ] Keep one session/account owner across the app.
- [ ] Prevent late load/save responses from repainting a different account or day.
- [ ] Clear private fields, previews and staged imports on account changes and sign-out.
- [ ] Verify saved-day reload, preferences, digest reads and competing revisions with authorized synthetic accounts.
- [ ] Preserve ownership policies and privileged save functions; do not relax permissions to make a flow work.
- [ ] Confirm the old hosted Aura entry no longer sends members into a competing app while preserving their records.

## 3. Android app and installation delivery

Status: full-screen WebView and welcome experience are committed; production delivery remains unfinished.

- [ ] Finish welcome, account/guest and workspace continuity; retain normal capitalization of 209 Connect.
- [ ] Preserve the clean public version display and full build identity in App information and receipts.
- [ ] Finish keyboard, safe-area, Back, resume/restart and connection-error behavior.
- [ ] Finish print/PDF and text-export destinations without leaking private content or implying failed exports succeeded.
- [ ] Review the native JavaScript interface; restrict privileged actions to intended trusted contexts.
- [ ] Keep external websites separate from internal workspace navigation.
- [ ] Distinguish Home Screen web-app installation from APK installation.
- [ ] Match each APK to source revision, package, checksum and receipt.
- [ ] Establish protected production signing and a reliable update path; rotating debug keys are not that path.
- [ ] Preserve installed data during upgrades and document rollback. Do not require uninstallation to conceal update problems.
- [ ] Treat iPhone Home Screen installation as a web-app route, not an App Store release.

## 4. One coherent Workstation journey

Status: redesigned views and journey code exist; finish demonstrated gaps instead of replacing the app again.

- [ ] Complete welcome, sign-in/guest, Morning, Today, schedule/tasks, Focus, Reflection and Review progression.
- [ ] Keep essential actions visible and optional help secondary.
- [ ] Remove demonstrated redundant account chrome, explanations and competing navigation controls.
- [ ] Maintain the theme, toolbar, accounts and backend across entry points.
- [ ] Consolidate loading/state ownership so dynamically loaded modules do not compete or initialize twice.
- [ ] Preserve existing field/action contracts during layout and loading changes.
- [ ] Keep unsaved edits distinct from saved account records.
- [ ] Use calm copy without converting personal planning into a score or clinical claim.

## 5. Morning routines, habits and notebook

Status: substantial source exists.

- [ ] Reconcile start time, duration editing, enable/skip, accessible reordering, timeline preview and explicit step completion.
- [ ] Finish conflict-aware Morning-to-Schedule transfer and duplicate-transfer prevention.
- [ ] Preserve day work when routines are applied or repeated.
- [ ] Finish demonstrated gaps in habit choices, custom habits, cues and small-action guidance.
- [ ] Distinguish done, partial, skipped and unrecorded.
- [ ] Finish brain-dump, guided-reflection and open-notebook continuity.
- [ ] Keep reviewed lessons and Creator drafts separate from private journals.
- [ ] Do not treat a running timer as proof of routine completion.

## 6. Tasks, milestones, scheduling and Focus

Status: connected planner, free-time finder, carry-forward and toolkit implementations exist.

- [ ] Finish direct editing/rescheduling, undo and canonical-record consistency.
- [ ] Preserve task-to-milestone, task-to-time-block and task-to-Focus links.
- [ ] Finish selected-task continuity across views.
- [ ] Reconcile monthly navigation, day switching, reusable routines/lists and manually reviewed repeat rules.
- [ ] Make carry-forward explicit and non-destructive; do not silently move unfinished work.
- [ ] Finish capacity, overlap, protected-sleep and stale free-time-suggestion behavior.
- [ ] Decide explicitly whether cross-day goals or automatic rollover are required; do not introduce them accidentally.
- [ ] Keep focus timing honest about foreground/background limitations.

## 7. Reflection, Review, Creator and output

Status: journal-first layout, guarded lesson import, private draft output and unified-output source are committed.

- [ ] Finish day-closeout and weekly-review continuity.
- [ ] Preserve journal, lesson and Creator-draft separation.
- [ ] Prevent lesson import/output from silently replacing or saving private writing.
- [ ] Unify selected-day printing/exporting without duplicate handlers or conflicting output panels.
- [ ] Keep print, download, copy and account-record save distinct.
- [ ] Preserve explicit publishing approval; copying a draft is not publishing.
- [ ] Close demonstrated native/browser clipboard, print/PDF and destination gaps.

## 8. Backup, restore, privacy and account controls

Status: planner/toolkit export and owner-matched missing-day restore exist.

- [ ] Finish large-account backup pagination, including accounts exceeding the documented 25 MB interface limit.
- [ ] Define full-account export coverage; do not imply current planner backup includes identity/profile data or browser-only drafts.
- [ ] Finish versioned validation, restore preview, duplicate/conflict handling and failure recovery.
- [ ] Preserve skip-existing-days as the safe default.
- [ ] Make preference/toolkit-definition restoration separate explicit choices; do not silently enable private digests or reminders.
- [ ] Define and implement account export/deletion controls with clear scope and consequences.
- [ ] Explain local storage, retention, unencrypted exports and removal risks.
- [ ] If user-owned Drive storage is selected, build narrow-scope authorization, backup/restore, disconnect, quota and upload-failure handling before promising synchronization or encryption.
- [ ] Keep operational database backup/restore distinct from user-facing planner export.

## 9. Public Files and Form 700 collection

Status: browser, filters, metadata exports, reviewed-PDF links and local draft intake exist.

- [ ] Establish actual deployed database/browser/storage inventory against existing source.
- [ ] Build controlled persistent intake and review/publication queue; current intake is local-only.
- [ ] Collect genuine City of Atwater and Merced County government filings.
- [ ] Establish people/position roster, reporting periods and truthful coverage/gaps report.
- [ ] Preserve sources, retrieval dates, hashes, page citations, amendments and review decisions.
- [ ] Preserve official redactions and exclude unnecessary private contact details.
- [ ] Distinguish original-source hashes from redacted-public-copy hashes.
- [ ] Finish larger-scale search or consistent multi-table reads beyond the documented client ceiling.
- [ ] Complete CPRA request/response receipts, timelines and Master Tracker connections.
- [ ] Finish Audit/CEDS evidence, analysis, alternatives and progress without fabricated records, counts or conclusions.

## 10. Website structure, navigation and landing pages

Status: shared navigation and install-menu changes are committed; whole-site consistency is incomplete.

- [ ] Finish circular navigation among Home, Media, Audit, Signal, Intelligence, Connect, Tools, learning, Wellness and Workstation.
- [ ] Preserve public identity; do not recreate the removed duplicate Wellness Store.
- [ ] Reproduce/fix the reported dBeastco routing defect at its source.
- [ ] Reconcile legacy headers, theme controls, footers and disconnected entry points.
- [ ] Keep one appropriate shared theme control, three existing themes and readable selected states.
- [ ] Fit Subscribe, theme and menu controls without hiding useful content.
- [ ] Keep installation options truthful: Home Screen web app versus Android preview.
- [ ] Finish homepage explanations and landing-page next steps without turning every page into another dashboard.
- [ ] Maintain public/member privacy and indexing boundaries.

## 11. Store, learning, resources and media

Status: source and pathways exist; delivery is not comprehensively established.

- [ ] Finish catalog/cart, product destinations, pricing, checkout, receipts, contact/refund information and access fulfilment.
- [ ] Resolve authorized payment, donation and QR destinations; do not invent products or payment infrastructure.
- [ ] Locate the separately promised workbook batch and reconcile it against the six learning pathways.
- [ ] Finish courses, paired videos, kits, learning outcomes and download destinations.
- [ ] Finish Morning and daily/weekly/monthly printables.
- [ ] Reconcile Resume Builder, Business Builder, Personal Branding, Lifestyle ID and Realignment Room against existing modules and commitments.
- [ ] Finish real media playback and usable library navigation.
- [ ] Finish newsletter subscription, consent, confirmation/welcome, segmentation, freshness, unsubscribe and suppression.
- [ ] Do not send campaigns, charge customers or publish solely because this backlog exists.

## 12. Muse runtime and publishing

Status: repository handoffs/integration source do not prove a running system.

- [ ] Locate actual runtime, publisher, transport, credential store, queues and responsible operator.
- [ ] Obtain acknowledgement of the actual handoff and a genuine sanitized runtime export.
- [ ] Preserve healthy integrations; do not create a second publisher.
- [ ] Finish durable jobs, leases, idempotency, retries/backoff, timeouts, expiry, deduplication, heartbeats, repair queues and kill switch in the actual runtime.
- [ ] Connect only authorized destinations and scopes.
- [ ] Distinguish draft, approved, scheduled, dispatched, provider-accepted, verified and failed.
- [ ] Retain provider IDs, URLs, read-back evidence and rollback.
- [ ] Do not automatically repeat a potentially completed external write.

## 13. Analytics, research and adaptive decisions

Status: reconcile framework/integration work with actual access and data.

- [ ] Confirm property identities, consent, event definitions, campaign/content IDs and freshness.
- [ ] Distinguish missing/stale measurements from zero.
- [ ] Exclude raw journals, sensitive check-ins and credentials from telemetry.
- [ ] Connect verified signals to reviewed recommendations, approved actions and measurable outcomes.
- [ ] Implement restrained experiments, stop rules, durable results and rollback in the real runtime.
- [ ] Separate public-record evidence, research findings, interpretation, creative proposals and advertising claims.
- [ ] Preserve provenance, dates, methods, uncertainty and conflicting evidence.
- [ ] Do not use private member writing as research or AI input without separate appropriate consent.

## 14. Operations and production release

Status: open.

- [ ] Resolve monitoring authorization failures and establish redacted operational status.
- [ ] Finish alerting, secret rotation, failed-job recovery, rate limits and incident ownership.
- [ ] Establish off-host backups and demonstrate restoration.
- [ ] Reconcile deployed migrations and document rollback.
- [ ] Finish responsive behavior, accessibility, focus order, contrast, reduced motion and password-manager compatibility.
- [ ] Finish canonical URLs, social previews, favicon, sitemap, downloads and public/member indexing rules.
- [ ] Match source, deployed website and installed APK revisions.
- [ ] Produce a truthful ready/blocked/failed release matrix and support runbook.
- [ ] Reconcile the running backlog and older R00-R23 records against implementation/results, not assumed completion.

## Execution order and activation boundaries

1. Account/session foundation and native Google return.
2. Morning, Day, Focus, Reflection, output and recovery.
3. Independent website, learning/store and Public Files work in parallel.
4. Authorized integrations and operational recovery.
5. Production-signed release and final acceptance record.

Batch code work systematically. Credentials, signing identity, payment destinations, publication authority and real-record review are explicit activation boundaries, not reasons to claim code is complete or stop independent work. No migration, payment, publishing, private-data transfer or automatic execution is authorized by this document.

## Evidence basis and limitations

- docs/BUILD-BACKLOG.md
- docs/WORKSPACE-TOOLKIT-COMPLETION.md
- docs/FORM700-LIBRARY.md
- Observed main commit 69862b30de927ab6d60babee29f2eb318c4b0af3.
- The complete remaining-build specification stated in the conversation on 2026-10-21, including carried-forward requirements. This is not a fresh source audit of every module or proof that every historical claim was independently verified.

Do not use this documentation commit as evidence that any listed feature was implemented, any workflow passed, any service was configured, any record was collected or any APK was installed.
