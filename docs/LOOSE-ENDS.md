# Promise reconciliation, 2026-10-19

Reviewed scope: current conversation and source inspected within it. This is not a claim to have retrieved every older conversation. Parent list: BUILD-BACKLOG.md.

## Confirmed integration fix in this batch

The routine template refresh bridge was committed but not loaded. morning.js now loads it before planner-next.js using ordered dynamic scripts, avoids duplicate URLs, and the bridge produces a distinct status event for repeated template applications. Existing morning-ui status observation resets the editor from the current record. Browser acceptance remains open.

## Implemented versus accepted

- f7faa5c: morning completion/evening closeout source; save/reload and account isolation acceptance open.
- 76cf93f: monthly navigation and routine template source; this batch fixes missing refresh wiring. Month navigation is not a saved-record monthly overview.
- a6ecc4c: duplicate morning transfer guards; runtime acceptance open.
- b78b20d: Public Files schema/intake source; eight database tables subsequently applied and verified with RLS.
- db468cb: database-backed public browser source; public deployment, API/browser acceptance, pagination beyond 500 rows and actual filings collection remain open.
- 1781e07: APK image source 0.3.3/code 6; successful build, install, both displayed images and stable signing remain open.

## Promises not to lose

- Real downloadable, installable mobile app with shared account/backend and dependable updates, not merely a browser launcher or workflow.
- Google login/recovery/password setup and account isolation actually work; user reports production URL settings applied, not end-to-end acceptance.
- Retire hosted Aura/Lovable UI; source startup retirement is not proof of hosted deployment. Preserve accounts/data.
- Explicit optional unfinished-task carry-forward; full backup/restore; broader reusable templates; saved monthly overview if required.
- Consolidated save/error/session behavior and private-data clearing, including focused text fields on account changes.
- Atwater and Merced County real Form 700 collection, provenance, redaction review, controlled document storage/intake, roster coverage, CPRA receipts and search.
- Public Files amendment navigation, agency/person/interest search, timelines, Master Tracker integration, Audit journey and integrated CEDS.
- Website square logo, dBeastco wrong route, store/cart/payment/access delivery and working printable downloads.
- Locate the previously claimed six-pathway workbook batch before calling it prepared or complete; finish learning/video/kit delivery.
- Homepage/landing explanations, resume/business tools, Lifestyle ID, Realignment Room, media and newsletter flows.
- Muse real sanitized runtime export and acknowledgement, consented outcome inputs, reviewed publisher integration/receipts/rollback.
- Monitoring authorization, backups with restoration demonstration, mobile/accessibility and release provenance.

## Google consent-screen branding

Select the Google Cloud project owning the OAuth client configured in Supabase Google provider. Google Auth Platform > Branding: app name 209 Workstation, square approved logo, support email, actual homepage/privacy links. Save, Verify Branding if required, then Publish branding after approval. A saved draft is not public branding. This is distinct from the APK icon, website logo and Supabase redirect settings.

Official guidance: https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification and https://support.google.com/cloud/answer/15549049
