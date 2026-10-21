# 209 running build backlog

Updated 2026-10-21 after reviewing main through ff583ffc8a50969437124c8adf3d036d82249bd9 and the newer source records present in the repository tree (including commits 38c5212 and 8e5e086). This is a targeted documentation reconciliation, not a fresh audit of every route, workflow, database policy or deployment. Treat checkboxes below as implementation/configuration work, not runtime acceptance. Preserve working modules and do not rebuild them because an older note is stale.

## Status vocabulary and boundaries

Source committed, compiled, deployed, installed and accepted are different states. No tests, browser/device checks or deployment checks are being requested as part of the current build-planning preference; their state remains unverified, never silently passed. Existing Github automation may run normally on pushes; this documentation does not disable it.

Public planner output currently offers an explicit configurable selected-day snapshot, print/PDF, text copy/download and a separate restorable-day JSON export. Selected-day weekly-review text is not a multi-day weekly report. Recovery is not a personal PDF. Keep private writing opt-in for copies and preserve explicit save semantics.

Posting, subscribing, purchasing, changing account credentials, publishing public records, migrating data, changing access rules or adding release credentials require their applicable authorization. Connected assistant/API tools are not automatically credentials or a background worker for the website.

## Already in source — extend, do not rebuild

- Embedded Android WebView app, welcome/guest/login paths, native print/text output: 4231a84 and follow-ons. It is online and displays live website content; it is not a standalone/offline client.
- Native Google browser/code return, package callback intent, PKCE attempt/exchange, WebView handoff and callback build-gate source: 8f9e995. Operator callback allowlisting, signing setup, deployed page and device/live account behavior are distinct.
- Guided Morning runner/session controls and Schedule task-focus correction: ae176a7 and 3688b0f.
- Save read-back, account/day safeguards and revision-aware save path: e7dee0c and current source.
- Optional selected-day PDF/text output with section selection, preview and private-writing confirmation: assets/workstation/unified-output.js. Restorable JSON export and resumable saved-day-only archive/skip-existing restore: assets/workstation/saved-day-recovery.js. Archive omits preferences, digest history, reusable definitions, profile/identity, credentials and browser-only drafts; do not describe it as full-account backup.
- Daily closeout to Review and seven-saved-day closeout copy are explicit actions in saved-day recovery. This is not proof of runtime persistence or a 7-day PDF report.
- Planner view/task editing source: Agenda/Timeline toggle, compact task cards, selected-day task edit with optional exact-linked block-title rename, and context-bound local undo are committed in ff583ff plus assets/workstation/planner-finishing.js. Existing schedule overlap/protected-sleep, time-block editor and schedule undo are reused. “Make today lighter” and true multi-day reporting are still open.
- Existing list/repeat-rule/manual add/unfinished-task copy toolkit and owner-matched missing-day restore: docs/WORKSPACE-TOOLKIT-COMPLETION.md.
- Existing University six business launch guides at sovereign-university/pathways.html, six separate interactive local-only worksheets at sovereign-university/workbooks.html, seven short Realignment/Systems HTML practice lessons and five source-linked Wellness HTML lessons. Worksheet text is not the three separately promised PDF course kits. Wellness lessons are general education, not individualized care or credentials.
- Public planning worksheets at planning.html; existing Ecwid catalog/cart and product URLs at store.html.
- Searchable static-snapshot Media Library with on-demand browser player at library.html. Snapshot is not a live upload feed. Support/help routing at support.html and hosted-provider newsletter signup/unsubscribe guidance at signal-subscribe.html; neither proves provider email delivery.
- Public Files/Form 700 browser and local draft intake (not persistent upload), existing pf_* schema/validator, scheduled restricted-Drive draft-manifest importer, request context, Master Tracker/source links, and private owner-scoped Audit metadata/request/event desk. These are distinct: schema/workflow source does not prove it is configured, real PDFs collected, redactions reviewed, files stored or public release approved. Never seed fake filings or expose private archive records.
- Creator social draft variants for Facebook, Bluesky, Threads, Instagram, LinkedIn and Newsletter; explicit browser sharing and Android text share preview. Attachments are references in the draft; browser file share is supported only where the API supports it. There is no website publisher/scheduler connected merely by choosing a platform.
- Public author bio and refined course-kit descriptions at working-record.html, data/course-author.json and docs/COURSE-KIT-COPY.md. Degree wording sourced from the owner’s resumes plus official program title; it is not external diploma/licensing verification. Three original course PDFs have not been located/reviewed/published as repository assets; use the copy document as editorial draft, not as a claim those kits shipped.
- Homepage’s duplicate “New to Workstation?” panel was removed from assets/site.js in 778e3ea; keep the existing shared toolbar entry and do not re-add that card.
- Recent content changes retained: site-flow fixes 32fd50f and 2923d87; wellness lesson batch e1ee61e; author/copy e8e5e086.
- Public Record search/Tracker connections: 3aac88d and newer source. Public Audit and Research pages plus new private operator desk exist; substantive case/agency CEDS evidence-to-analysis-to-alternatives-to-progress work remains.

## P0: Release and account implementation/configuration

- [ ] Activate the intended Android package-specific Supabase callback destinations and deploy members/native-google.html. Keep Google PKCE source; do not rewrite it to compensate for missing operator configuration.
- [ ] Configure GitHub `android-production` environment restrictions/reviewers and the intended existing keystore secrets. Manual fail-closed APK/AAB workflow source is in .github/workflows/android-production-artifact.yml; no key is generated. Set a deliberate upgrade-compatible version code/name before distribution. Workflow produces artifacts only; it does not publish to Play or make a GitHub Release.
- [ ] Finish any demonstrated account signup, password setup, confirmation-email, recovery, session/day ownership, save-conflict, account deletion/export or identity-data gaps. Do not claim live account flows fixed based only on markup/source.
- [ ] Complete the user-approved remaining legacy Aura hosting retirement without deleting accounts or records.

## P1: Workstation finishing

- [ ] Finish “Make today lighter” with explicit reversible choices; never silently delete or reschedule work.
- [ ] Implement a genuine multi-day PDF/report, if still desired, with date-range choice, selected sections, optional private-writing inclusion, readable page breaks, truthful “no entries” states and context-bound preview. Extend existing output; do not replace it.
- [ ] Finish account-wide export/deletion coverage, separate from current day-archive recovery. Include clear scope, confirmation, failure handling and privacy instructions.
- [ ] If user-owned Drive backup is pursued, add narrowly scoped authorization, account ownership checks, quota/large-file handling, upload/download/restore cancellation and disconnect. Ordinary local PDF saving must not require Drive scopes.
- [ ] Reuse existing workout handoff/routine pages, rather than add another workout planner. Preserve user-provided program details; do not invent individualized exercise prescription.
- [ ] Remaining accessiblity/responsive/destination fixes only when source is identified; do not re-open closed design tasks broadly.

## P1: PDF course-kit publication and learning content

- [ ] Locate/recover and review the three promised original six-page, four-lesson PDFs plus their three landing-page drafts. Drive exact-title search during 2026-10-21 14:22 did not locate the kits; this does not prove they do not exist elsewhere. If unavailable, ask/obtain explicit replacement-content approval before creating replacements; never call new HTML pages the original PDFs.
- [ ] For each kit, align claims with pages, examples, exercises and a concrete final deliverable: Build Your Intentional Day; From Personal Brand to First Offer; Public Records to Clear Evidence.
- [ ] Publish reviewed assets to explicit public paths only after content review and selected destinations/permissions. Add accessible HTML equivalents and close the lesson→tool→return route.
- [ ] Reconcile the separately promised six-workbook commitment against the existing six interactive HTML worksheets. They may overlap, but that equivalence has not been authorized or established. Existing worksheets are local-page drafts, not account-backed course progress.
- [ ] Keep completed degrees distinct from professional licenses, accredited programs, badges, draft educational materials and doctoral study status. Course maker's actual expertise may be stated confidently; do not invent program accreditation or guaranteed health/income/legal outcomes.
- [ ] Finish specific older topic entries (hydration, mobility, sleep, protein and foundations now have general educational lessons; avoid duplicates and individual treatment plans), videos and learning outcomes only as distinct deliverables.

## P2: Website flow, media and commercial delivery

- [ ] Continue the whole-site flow map through Home, Audit, Signal, Intelligence, Connect, Learning, Wellness, Store, Tools, Media and Workstation. Repair only identified mismatches; preserve toolbar; no duplicate Workstation homepage banner.
- [ ] Finish remaining specific nested destinations, per-item source/media crosslinks and return routes where the destination exists. Distinguish overview, course, worksheet, tool, archive and hosted service accurately.
- [ ] Review Media Library snapshot dates/source links and support/reporting route. Continuous ingestion is not implemented merely by a static snapshot.
- [ ] Preserve the hosted Ecwid cart. Digital-course payments, access fulfillment, refunds and receipts require an authorized provider/product model and delivery design; do not invent prices or payment destinations.
- [ ] Finish newsletter provider flows/configuration only with provider permissions. Current site directs signup to hosted Beehiiv and documents follow-up/unsubscribe; this is not delivery proof.
- [ ] Complete website accessibility, responsive, metadata/canonical/open-graph and indexing refinements from actual specific findings.

## P1: Public Files / 209 Audit

- [ ] Treat current source accurately: pf_* schema, browser, local intake and scheduled Drive manifest import exist; private owner archive tool exists. Inspect configuration before changing it; preserve existing RLS and private/public separation.
- [ ] Configure and execute authorized durable Drive→private-draft ingestion with the intended service account, folder, secret and workflow variable. Current workflow is gated by PUBLIC_FILES_SYNC_ENABLED and draft import never publishes. No real filings/records are evidenced by the schema alone.
- [ ] Add reviewed original-to-public-copy storage workflow/metadata, malware/safety scanning strategy, redaction review receipt, amendment mapping and an owner/admin-only controlled release step. No public storage bucket/permission change or release is authorized here.
- [ ] Collect real City of Atwater and Merced County government records and create an accurate filer/position/period coverage inventory, recording unknowns without inferring nonfiling.
- [ ] Finish category-aware CPRA response/receipt timelines and explicit supported links between private events, request records and source docs; distinguish inferred references from verified relationships. Build against already existing private Audit desk/schema, not a competing schema.
- [ ] Complete CEDS research steps: cite sources, label observation versus interpretation, compare alternatives and track progress. Public-facing claims need source review; do not publish allegations or private archive content by implication.

## P2: Social publishing, analytics and Muse

- [ ] Add native Android binary attachment sharing/FileProvider to complement committed browser file share and Android text/share chooser. Do not label share chooser completion as a post receipt.
- [ ] Reuse existing Supabase `content_items`, `content_variants`, `platform_connections`, `approval_tasks`, `risk_flags`, `analytics_snapshots`, `cta_events`, `intelligence_events` and `muse-bridge-209` family. The databases/functions and assistant connectors are present; do not create a parallel queue/publisher or assume tokens/scopes/configured runtime are ready.
- [ ] Implement/finish a human-configured publisher UI that reflects actual authorized connection state, safe adapters, draft review, approved scheduled jobs, idempotency/dedupe, paused/retry state, provider IDs/read-back receipts and rollback. Keep dispatch disabled until the exact credential authority and destination policy are configured.
- [ ] Link available GA4/Search Console/social metrics to content and campaign identifiers; distinguish no-data from zero, keep attribution/windows explicit and avoid private journal/check-in ingestion. Existing assistant analytics connectors are not automatically wired into site backend.
- [ ] Ensure consented experiments require an outcome metric, stop condition and retained action/rollback receipts; no autonomous high-frequency publishing is implied.

## P1/P2: Android production artifact and operations

- [ ] Finish operator configuration for the production signing environment with the existing authorized signing/upload key, protected recovery copy and correct environment reviewers.
- [ ] Before distribution, choose upgrade-compatible app identity/version and explicit Play/hosted destination. The current manual workflow only builds an artifact; it does not publish.
- [ ] Integrate downloadable receipt/artifact UX after approval; match APK/AAB/source/content revision and checksums. WebView content is live and unpinned.
- [ ] Add operational backup/restore and incident/retry controls distinct from user day exports.
- [ ] Resolve the existing status monitor’s authorization/config issue and provide safe redacted operational state.
- [ ] Reconcile older R00–R23/ops records from current evidence, not stale checkboxes.

## Deferred acceptance, intentionally not treated as build work here

Live website deployment, OAuth callbacks, saved-account operation, sender email delivery, real account isolation, Android installation/signature compatibility, native chooser behavior, current APK/download receipt alignment, Print-to-PDF target behavior, store checkout, real public filings, review/publication policy enforcement, Drive import configuration, actual post publication and operational restoration remain unverified unless a later authorized outcome provides evidence. The user said skip verification; these are not being represented as passed or used as reason to stop source-only implementation.

## Human/owner-controlled activation queue (not automatic code tasks)

1. Recover/confirm original course PDFs/drafts, or explicitly approve replacement course deliverables.
2. Confirm exact award/certificate wording for any additional education credentials; do not include private transcript/resume data wholesale.
3. Provide/configure the intended protected Android signing identity and GitHub environment protections.
4. Configure authorized OAuth/provider scopes and Public Files service credentials in their proper settings; never send secrets in chat or commit them.
5. Select paid/free product policy, prices, checkout/access and support/refund destinations.
6. Approve specific Public Files release copies only after document/source/privacy review.
7. Authorize particular social accounts, posting policy/cadence and publisher destinations; assistant connector availability is not blanket posting consent.

This backlog edit is not an executable queue. No database migrations, credential or payment changes, publication, tests, browser/device checks, workflow dispatch or site deploy occur merely by updating it.
