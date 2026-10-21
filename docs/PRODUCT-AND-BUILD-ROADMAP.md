# 209 - Product and running build roadmap

Updated 2026-10-21, Batch 1 source reconciliation. Source committed, deployed, installed, draft built and runtime accepted are distinct. User-deferred checks stay unverified, not passed. This supplements BUILD-BACKLOG.md and does not delete its requirements. REMAINING-BUILD.md is the earlier broad specification, not an up-to-date list of wholly missing features; use this roadmap and the running backlog for current source status.

## Immediate experience decision

Normal personal-planner output is Save PDF. Keep selected content, preview, filled/blank pages and optional writing space. Do not present JSON/CSV/text export or file import as normal planning steps. Preserve existing data and recovery implementation; hiding technical controls is not a data migration. Saving a PDF uses the device print/PDF destination. A direct PDF generator is not claimed. Public Files editorial document intake is a separate system, not a personal-planner upload.

The shared selected-day panel already includes routines, Morning sessions, priorities, tasks, schedules, habits, journal, guided reflections, notes, milestones, Creator draft, closeout and weekly-review text. It also supports task filters and explicit private-writing confirmation. A selected-day review text export is not a multi-day aggregate. Extend this implementation rather than build a second output panel.

## Three entrances into Sovereign University

1. dBeastco Wellness -> Build Your Intentional Day -> routine/day/reflection workbook -> Workstation practice. Educational structure, not medical treatment.
2. 209 Connect -> From Personal Brand to First Offer -> brand statement, focused offer, sample deliverable and publishing plan. No income guarantee.
3. 209 Audit / 209 Media -> Public Records to Clear Evidence -> neutral question, request draft, provenance log and source-supported brief. Educational material, not legal advice or allegations.

These use one University, not three new platforms. Preserve the existing six business launch guides (Brand, AI, Content, Newsletter, Product, Website) as supporting business modules. Practical AI assistance, information organization and systems thinking are shared skills, not extra public brands. Muse remains a private implementation tool.

## Actual product drafts already built in the conversation

- DRAFT BUILT: three six-page PDF starter workbooks, each with four written lessons, worked examples, exercises and final deliverable.
- DRAFT BUILT: three dedicated landing-page drafts inside the attached starter course kit.
- NOT PUBLISHED: these files are not yet repository assets, live courses, priced products or checkout deliveries. No completed videos, credentials or accreditation are claimed.

## Next product publishing work

- [ ] Publish the three reviewed course landing pages and PDFs at explicit site paths when the draft assets are available.
- [ ] Connect Wellness, Connect, Audit and University hubs to the real course destinations, not another general explainer.
- [ ] Include who it helps, concrete output, lesson outline, workbook/PDF, practice tool and next step on every landing page.
- [ ] Add accessible HTML equivalents and worked answer examples.
- [ ] Reconcile older courses and the promised six-workbook batch without assuming the starter guides fulfill them.
- [ ] Decide free/paid boundaries and authorized checkout/delivery destinations before enabling purchases.
- [ ] Build later lessons/videos only when the starter deliverable is useful.

## Consolidate reusable features

- [ ] One task identity across capture, scheduling, Focus, course practice and review.
- [ ] Extend the existing configurable PDF system to course worksheets and genuine multi-day summaries where required; do not rebuild selected-day output.
- [ ] Reuse sequence execution for future study/evening routines without relabeling every new use as a new app.
- [ ] Keep journals private; use deliberate opt-in when including writing in PDFs. Never auto-convert private writing into marketing.
- [ ] Reuse milestones for personal goals, business deliverables and course outputs.
- [ ] Reuse review prompts for wellness, learning and project retrospectives.
- [ ] Keep public research documents and private personal writing under distinct access/release rules.
- [ ] Add Agenda/Timeline switch, compact task cards and secondary navigation under More.
- [ ] Consolidate competing DOM-layout modules into one ownership path.
- [x] Batch 1 source fix: initialize each Settings backup disclosure collapsed once per DOM element rather than closing it on every rearrangement. Runtime acceptance is not claimed; normal technical controls remain hidden by the PDF-only interface.
- [ ] Add Make today lighter without silent deletion or schedule shifts.

## Completed source batches carried forward

- e7dee0c: account save read-back and mock regression coverage.
- 4231a84: embedded Android workspace, native output helpers, compact sub-tabs and guide page.
- 3688b0f: Schedule Cancel focus and tab-aware browser walkthrough.
- ae176a7: Morning execution/session controls and optional cues.
- 4abea4e: sign-in-first welcome/login/guest redesign and optional continuation controls.
- 69862b3: Settings and selected-day output system.
- 67f427d: PDF-only normal personal output and product roadmap; supersedes earlier technical-format choices.
- 8f9e995: native Google browser/code return, PKCE exchange, isolated session handoff and build wiring. Operator configuration and outcomes remain separate.
- 3aac88d: Public Files and Tracker presentation/source links, not records collection.
- Existing reusable lists, repeat rules, explicit carry-forward and planner/toolkit restore are documented in WORKSPACE-TOOLKIT-COMPLETION.md.
- Existing compact shelves, Ecwid catalog/cart destinations and public Morning/day/week/month worksheets are documented in public-resource-batch.md. Preserve these instead of starting another storefront or basic planner.

## Existing release/backend work remains

- [ ] Activate intended package-specific native Google callback routes and the deployed handoff page. Native implementation is already in source; do not rebuild it because configuration/acceptance is outstanding.
- [ ] Protected production signing, stable upgrades, current version/receipt/source alignment.
- [ ] Resolve demonstrated signup/email/recovery/loading defects; real-account and phone checks requested deferred are still unverified.
- [ ] Define optional account-backed storage versus local-only behavior explicitly. Existing saved-day storage is not no-storage.
- [ ] Large-account backup scope/pagination, broader account controls and operational restore.
- [ ] Retire remaining legacy Aura hosted entry points without deleting users or data.

## Public service and wider ecosystem

- [ ] Real Atwater/Merced government records, provenance, redaction review and approved release; source/receipt/request/Tracker relationships and persistent intake beyond the existing local draft tool.
- [ ] CEDS sources, interpretation, alternative and progress presentation.
- [ ] New digital-product checkout/access delivery and exact authorized payment/product destinations; preserve existing Ecwid routes.
- [ ] Media playback, newsletter journey, remaining dBeastco routes, resume/business tools and older learning catalog.
- [ ] Creator social draft variants and explicit sharing, followed separately by authorized server-side platform connections and integration with the actual publisher runtime. No platform is labelled connected or published merely because a destination was selected.
- [ ] Real private Muse runtime, consented analytics, approved publishing receipts/rollback; do not create a competing publisher.
- [ ] Status-monitor authorization, off-host backups and reconciled older R00-R23 backlog.

## Batch 1 limits

Only Settings disclosure initialization/copy, login help and the two planning documents change. No social composer, share action, account connection, database migration, payment setup or publication is implemented by this batch. No tests or device checks are run here; existing GitHub workflows are unchanged. Older deferred acceptance remains open, not passed.

## Folder guide

My Workstation / Schedules / Routines & Habits / Journals & Reflections / Weekly Reviews / Business & Creative Work / Course Workbooks / Civic Research. Create only useful folders. Suggested filenames start YYYY-MM-DD; users choose their destination. Keep personal journals and sensitive research private. No broad device or Google Drive permission is needed just to save a PDF.

## Research informing the design

- Day One: journal/date-range export and web PDF via Print -> Save as PDF. https://dayoneapp.com/guides/tips-and-tutorials/exporting-entries/
- Structured: explicit rescheduling/return of unfinished tasks to an inbox. https://structured.app/blog/replan
- Finch: approachable self-care instead of another chore. https://help.finchcare.com/hc/en-us/articles/37935669335309-Our-Approach-to-Self-Care
- Notion Academy: learning connected to practical project/task systems. https://academy.notion.com/
- California DOJ: official public-records guidance. https://oag.ca.gov/consumers/general/pra
