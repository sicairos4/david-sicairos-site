# 209 remaining implementation — 2026-10-22

This is a source-status checklist, not a claim that everything is built, deployed or accepted. Last confirmed direct-entry source before this batch: d6431c98cdde252192fa10afb88f5157310a1cb7. Refresh current source before each write. No tests, browser/device checks, branch comparisons, deployment checks or workflow dispatch are included. Existing push-triggered automation can run normally; its result is not established here.

## Source already committed in this conversation

- Saved-range report: f7f1e76. Date range, section choice, private-writing opt-in, read-only saved records and print preview. Not full-account backup.
- Smaller-day visual filter: 1ac9c53. Temporary hiding, not rescheduling.
- Same-day set aside: 83e093c. Changes task area with local undo, not a cross-day move.
- Cross-day file-copy handoff: b71bf42; repair and guarded undo: 1a2dcf8. Copies selected text/area tasks using new IDs and carryOrigin; does not transfer all metadata or remove source tasks.
- Original Audit homepage introduction protected against live overrides: 59d7c83. Preserve the original copy, not another rewrite.
- Reflection prompts-first explanations, navigation help and welcome text: 091b9e6.
- Local Creator topic/hook/body/CTA builder and shared theme controls: ebc9e4d. Arranges supplied wording; not an AI rewrite or fact checker. Shared CSS coverage is not a page-by-page visual audit.
- Android direct workspace entry: d6431c9. Version 0.3.5 (8), no duplicate native welcome, existing login/OAuth routes and signing preserved. No matching installed artifact established.
- Account export/self-deletion UI was independently found in current source, loaded through account-profile.js. Preserve it. Its backend installation/coverage document is not independently verified runtime evidence.

## This batch — implementation, not acceptance

- Native document chooser for existing file inputs on the embedded account/guest planner, up to five content URIs only; checks top-level origin and page/account/day context before delivery. Cancels on navigation/destroy. No broad storage permission, background import, automatic restore or automatic upload added.
- Native saved-report print route: reads a report preview snapshot, requires confirmation, rechecks context, uses a separate JavaScript-disabled/network-blocked WebView and opens Android Print. Does not confirm PDF saving or print delivery. Existing output bridges remain.
- Current package IDs, signing configuration, direct entry and version are preserved. No production key or credential configuration is changed.

## Remaining source work

- [ ] Genuine cross-day defer/move/reschedule: define atomicity, task metadata, milestone/schedule handling and reversal; file copy does not fulfill this.
- [ ] Persistent set-aside original-area recovery if required; current local undo expires and Edit task can set a chosen area later.
- [ ] Account export/deletion coverage reconciliation against actual backend registry and relationships; extend existing system only if a concrete gap is found. Never delete an account as a build check.
- [ ] Optional Drive backup only after destination/scope authorization; retain local PDF independence.
- [ ] Recover/review the three original course kits and landing drafts, or obtain explicit replacement approval. Related Drive candidates found were not established as the originals.
- [ ] Accessible course HTML equivalents and lesson/worksheet/practice-tool return flows; reconcile the separate six-workbook commitment with six existing worksheets.
- [ ] Distinct remaining lesson/video deliverables and truthful author/credential copy. No invented accreditation or health/income/legal promises.
- [ ] Specific website destination, media-source, accessibility, responsive and theme exceptions; no assertion that all pages have been inspected.
- [ ] Public Files durable private ingestion, reviewed-original/public-copy storage, safety scanning strategy, redaction receipts, amendments and accurate Atwater/Merced County filer-position-period coverage.
- [ ] Private Audit request/receipt/event/source relationships and source-cited CEDS observation/interpretation/alternatives/progress work. Preserve existing schemas and privacy separation.
- [ ] Existing Muse runtime/schema inspection and completion of human-approved publishing UI, actual connections, scheduling, dedupe/idempotency, pause/retry, provider receipts/read-back and rollback.
- [ ] Consented campaign analytics, explicit attribution windows, no-data handling and experiment stop conditions; no private writing ingestion.
- [ ] Native binary attachment sharing/FileProvider where still required. A file chooser or text share is not binary outbound sharing or a publication receipt.
- [ ] Artifact/download/source/checksum alignment, release-receipt UX and authorized distribution. Correct stale build instructions that still call the app a browser-backed launcher when changing that specific delivery workflow.
- [ ] Operational backup/restore, incident/retry controls, status-monitor authorization/configuration and specifically authorized legacy Aura hosting retirement without account/record deletion.

## Owner-controlled activation — not invented defaults

- [ ] Original course assets or explicit replacement deliverables.
- [ ] Free/paid boundaries, product prices, provider, access fulfillment, receipts, refunds and support policy. Preserve Ecwid.
- [ ] Protected existing production keystore and authorized release environment; no substitute signing identity.
- [ ] OAuth callback allowlisting and exact provider credentials/scopes, entered only in proper secret settings.
- [ ] Public Files authorized private folder/service account and reviewed public release decisions. Do not publish or fabricate records.
- [ ] Social destinations, editorial approval, cadence and enabled-dispatch policy. Browser sharing is not a server publisher.
- [ ] Newsletter provider changes and email delivery configuration with appropriate permissions.

## Deferred acceptance and build status

- [ ] Source compiles / APK produced / artifact receipt matches source / signature compatible / installed / accepted: separate outcomes, none inferred from a push.
- [ ] Native chooser, JSON validators, restore/handoff ownership, cancellation and real saved records.
- [ ] Native and browser PDF output, keyboard/focus/assistive technology, account switching and data isolation.
- [ ] Google return, email/password/recovery, callback configuration and live session saving.
- [ ] Site deployment, theme coverage, checkout/fulfillment, sender delivery, actual publishing and operational restoration.

Do not replace this list with a blanket done claim. Group compatible writes under exact approval, implement concrete batches and preserve receipts. Unskipped source work remains work; skipped checks remain deferred, not passed.
