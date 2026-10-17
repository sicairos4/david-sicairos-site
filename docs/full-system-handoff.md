# 209 full-system completion handoff

## Read this first
Purpose: complete deployment and operation of the entire 209 ecosystem, not merely its latest planner patch. This document is a work order and acceptance framework, not proof that Muse received it, jobs were dispatched, publishing is running or the system is finalized.
Primary source repository: sicairos4/david-sicairos-site. Baseline commit: c462587db9500fee89038172d5422d0b6fb1c5e3. Original application source to inspect before rebuilding equivalent modules: sicairos4/aura-launchpad.
Start with docs/muse-release-audit.md, docs/system-blueprint.md, docs/automation-implementation-status.md and docs/muse-audit-reconciliation.md. The blueprint describes the target; status and reconciliation documents contain open acceptance gates. Older statements of completion must not override current evidence.
The companion ops/full-system-backlog.json is a dependency-checked backlog, not an executable queue. execution_enabled and auto_publish are false. Any live execution requires a connected executor, resolved targets, applicable approvals and an execution receipt.

## Product contract
- 209 Audit is the public evidence engine. Follow the Receipt explains the relationships without inventing cases or live traffic.
- 209 Media connects Audit, Signal, Intelligence, the media library and multimedia.
- 209 Connect connects Studio, resume/business/brand tools and Sovereign University learning pathways.
- 209 Workstation is the native, signed-in planning product. Aura is source inspiration and a legacy technical name, not the product identity.
- Intentional Morning precedes Intentional Day: choose direction, arrange a realistic routine, plan the day, focus, reflect and review.
- dBeastco Wellness, Lifestyle ID and the Realignment Room remain coherent personal-system routes. Do not create a duplicate store or force every wellness action into commerce.
- Keep the website theme, toolbar, accessible controls and public/private boundaries. Do not redirect members to Lovable or create another disconnected dashboard.
- Private journals, personal check-ins and raw habit records are not publishing, analytics or AI inputs by default.

## Evidence baseline
Source changes committed: c462587 auth repair and initial Muse audit; b44c9ca Follow the Receipt; a885156 free-time finder; 207cf50 quick capture/small start; 6e03322 task-goal-schedule-focus links; 46a3c47 planner persistence/tests; 2ad1cc4 account entry/recovery. Commit existence is not proof of deployment.
Local test results previously observed: 12 mocked-auth tests; 10 receipt data/markup tests; 20 free-time algorithm/mocked tests with 100 randomized schedules; 15 quick-capture tests; 9 planner-model tests; 15 persistence tests. Re-run the repository suites; do not sum these into a claim of end-to-end coverage.
Backend uwidjnnhdgtrpsymuhwp most recently reported ACTIVE_HEALTHY. intentional_days, intentional_preferences and intentional_digests exist with ownership policies. A permission migration restricted direct member day/digest writes; day saving uses intentional_save_day. The digest cron was active and its 30 recent inspected runs succeeded. Member receipt, two-account isolation and full save/read behavior remain acceptance gates.
Existing account day saving includes journal text in Supabase. Member-owned Drive storage and encrypted backups are not implemented.
Existing workflow files include adaptation, backup, Beehiiv, YouTube, site QA and member tests. Each needs actual run evidence. Do not infer publishing from a workflow file or a database row.
ops/delegated-review-policy.json reports proposal_only_not_an_executor and transport not_connected. This establishes an unresolved repository handoff transport, not the absence of every external Muse runtime. Locate the real runtime before replacing it.

## Completion jobs
### R00 — Inventory and authority
Resolve production origins/base paths, repositories, deployed revisions, responsible operators, secret locations, actual publishers, queues, channels and approval boundaries. Inventory every original module and existing commitment. Deliver a redacted system registry with source/config/runtime distinctions. Never put secrets or member content in this repository.
### R01 — Deployment and access points
Verify the production build, direct URLs, nested assets, error pages and routing with real HTTP/browser checks. Check logged-out and logged-in Workspace behavior. Supply deployed revision and URL evidence. No stale source/live equivalence claims.
### R02 — Auth configuration
Verify exact Supabase Site URL/redirect entries, Google provider configuration, email confirmation/recovery delivery and session behavior for supported origins. Avoid broad production wildcards and never copy callback tokens into receipts. Frontend auth repair does not change these settings.
### R03 — Authenticated planner acceptance
Test two authorized accounts: signup, confirmation, email/Google login, recovery, local-device sign out, day save/reload, competing revisions, preferences, digest reads and account switches. Use synthetic test content. Pass only with correct ownership and no stale private UI reappearance.
### R04 — Data protection and migration ledger
Reconcile deployed migrations with source-controlled SQL; verify grants, policies, constraints, preference validation and privileged functions. Review current advisors, leaked-password protection, retention and plain-language privacy/export/deletion notices; obtain appropriate legal review rather than claiming automatic compliance. Define deletion/export consent and attachment limits. No permission relaxation to make tests pass.
### R05 — Public navigation and Follow the Receipt
Browser-test all three routes, map nodes, collection reset/copy fallback, fallback directory, themes, keyboard use and mobile layouts. Preserve the Audit center and private/public separation. Keep examples labelled as examples; no fake counts, cases, traffic or verification.
### R06 — dBeastco routing defect
Capture the exact failing clicked URL and origin. Trace source, hash, redirect, deployment and cache behavior. Current toolbar Wellness points to dbeastco.html; source did not show a homepage redirect. Fix the reproduced cause and test desktop/mobile, nested routes and legitimate fragments. No guessed global hash interception.
### R07 — Embedded Intentional Morning
Build the native timed routine builder before Intentional Day, not a separate replacement app. Add habit blocks, start time, editable durations, enable/skip, drag reordering with keyboard/touch alternatives, calculated timeline and explicit completion. Preview handoff conflicts, preserve existing day work and prevent duplicate transferred blocks. Timers do not certify completion; browser timers are not background alarms.
### R08 — Guided notebook and habit tracker
Add a habit choice library, small-action/cue guidance, custom habits, optional check-ins, brain dump, guided reflection and open notebook. Distinguish done/partial/skipped/unrecorded; explain the denominator in summaries. Keep reviewed lessons and creator drafts separate. No diagnosis, shame-based scores or automatic publishing.
### R09 — Daily scheduler completion
Integrate direct block editing/rescheduling, undo, task/goal links, capacity, focus, free-time finder and weekly review. Check overlap validation and stale suggestions against the canonical record; replace display-text parsing with a tested read-only model interface when extending the controller. Document day-scoped goals and explicitly decide whether to add cross-day goals/templates/rollover. No silent carryover.
### R10 — Local data and backup/restore
Implement account-scoped local storage if selected, clear storage indicators, versioned exports, validation and non-destructive restore preview with duplicate/conflict handling. Warn that local storage can be cleared. The earlier standalone legacy-recovery proposal was not committed; do not treat it as deployed or silently import old device records.
### R11 — User-owned cloud storage
Build separate Drive authorization with narrow file access, clear ownership/quota messaging, upload failure handling, disconnect and restore. Start with backup/restore, then conflict-aware multi-device sync. Design encryption/key recovery before promising end-to-end encryption. Decide what small opt-in planning data, if any, is available for server digests. No AI/provider access to raw journals by default.
### R12 — Public evidence tools
Finish Public Files search, real entity/record extraction, tracker display and any graphic map from validated records. Verify counts and provenance; do not fabricate entities, coordinates or article thumbnails. Connect CPRA workflows to actual request/response receipts and preserve legal uncertainty.
### R13 — Original modules, learning and product catalog
Inventory original profile/avatar/community, routine, focus, evening, review, learning and business/brand modules. For each, record keep/adapt/rebuild/retire proposal, data disposition and acceptance tests; retirement requires explicit approval. Verify Sovereign University, resume/business builders, guides and PDFs, download destinations and existing purchase/access boundaries. Morning/day tools should work without AI keys.
### R14 — Newsletter lifecycle
Verify existing Beehiiv integration, on-site subscription UX, consent, confirmation/welcome path, segmentation and ingestion freshness. Do not send a test or campaign to real recipients without the required exact-target approval. Preserve unsubscribe and suppression behavior.
### R15 — Revenue and checkout
Verify actual store, donation/support and any payment destinations, pricing, receipts, refunds/contact and conversion attribution. Do not invent a Stripe deployment, live product, free-shipping promise or checkout pass. Use authorized test mode first; no real charge or paid provisioning without approval.
### R16 — Muse runtime and orchestration
Locate the actual existing publisher and its authority/transport. Reconcile blueprints with real queues and worker deployments. Implement or verify durable jobs, isolated lanes, transactional leases, idempotency, timeouts, retries/backoff, expiry/deduplication, heartbeats, repair queues and a kill switch. Do not create a second publisher because runtime location is unresolved. A desired lane count or staging buffer is not an observed healthy queue.
### R17 — Channel adapters and publication receipts
Inventory authorized destinations on Beehiiv, YouTube, Bluesky, Facebook, Discord and any other configured channels. Verify scopes, target identities, rate limits and media/link rules. Use a reviewed synthetic/canary plan with required approval before external writes. Distinguish draft/approved/scheduled/dispatched/provider-accepted/verified/failed. Store real platform IDs/URLs and read-back evidence; never silently retry a potentially completed write.
### R18 — Analytics and attribution
Verify GA4/property identity, Search Console, tag/consent configuration, newsletter/social ingestion and campaign/content IDs. Keep missing/stale data distinct from real zero. Use provider-calendar windows, source timestamps and documented event definitions. Do not publish PII, raw journal text or service-account keys in telemetry. Validate crawler-visible canonical, OG/Twitter, favicon, sitemap and public/member indexing boundaries.
### R19 — Closed-loop intelligence and growth
Connect verified signals to recommendations, approvals, actions and outcome receipts. Implement directive consumption, experiment assignment, durable results and rollback in the actual runtime. Source docs describe minimum-volume/lift heuristics; these are not significance, causality or guaranteed growth. Use restrained tests and stop rules. Do not rewrite sensitive public claims based on engagement alone.
### R20 — Reliability and operational controls
Verify recurring jobs, alerting, secret rotation, backup destination and an off-host restore drill. Document incidents, rollback, failed migrations, rate limits, dead-letter queues and recovery ownership. Keep public status feeds free of secrets/member data. Do not call backups operational until restoration is tested.
### R21 — Whole-experience quality
Audit all relevant pages and tools for coherent typography, spacing, responsive navigation, focus order, contrast, reduced motion, descriptive errors, password-manager compatibility, content accuracy and accessible alternatives to dragging. Test real devices/browsers. Treat emotional-response/brand claims as hypotheses, not claims of clinical efficacy or universal persuasion.
### R22 — Release and operations acceptance
Re-run source suites and real deployed acceptance tests. Verify source-to-deployment revision, no critical open security/access defects, documented storage/retention, recoverability, authorized lane health and live receipts for enabled integrations. Publish a truthful pass/fail/blocked matrix, ownership and support runbook. Do not label the entire machine finalized while required jobs are blocked or unverified.

### R23 — Research, doctoral work and content integrity
Maintain separate research questions and source libraries for accountability, organizational leadership/cybernetics, education, business and wellness. Record provenance, dates, methods, uncertainty and conflicting evidence. Distinguish primary records, research findings, interpretation, creative proposals and advertising claims. Treat brand emotion/conversion hypotheses as testable ideas, not universal truths; do not infer member health or use private notebooks as research data without separate appropriate consent. Publish only reviewed claims and keep internal research notes separate from public receipts.

## Work lanes and dispatch rules
Access/security, product UX, public evidence/navigation, publishing runtime, measurement/growth and release operations can research independently. Assign one writer per shared file and coordinate migrations; no overlapping main-branch mutations. Prioritize R00-R04 before declaring member access ready. A four-hour work window is an allocation, not a promise to finish this whole scope.
This document does not authorize new platform writes, newsletters, charges, permission changes, private exports or destructive operations. Obtain fully resolved action-specific approval where required. Preserve already-authorized healthy jobs unless an incident requires an approved response; do not claim their cadence is maintained without receipts.

## Required receipt for every completed job
Record job ID, actor, source/deployed commit, UTC observation time, environment, redacted input scope, test method, expected/actual result, artifact or provider receipt, approval reference when applicable, rollback and remaining limitations. Do not store passwords, tokens, raw auth logs, recovery links or private journals. A screenshot alone is not proof of backend ownership; an API acknowledgement alone is not proof of a live post.

## Machine definition of done
Public evidence can be inspected; member access and save/read isolation work; Morning and Day form one tested experience; storage is explicit and recoverable; enabled integrations have read-back evidence; approvals/privacy boundaries hold; measurement can explain an action without inventing causality; failures are visible and recoverable. A pipeline diagram or this handoff is not that operating system.

## Delivery and acknowledgement
Repository handoff entry: docs/full-system-handoff.md. Backlog: ops/full-system-backlog.json. Muse or an authorized operator must acknowledge the exact handoff commit and report the actual executor/runtime before any assignment is described as received or running. Until then, delivery/execution is unconfirmed.
