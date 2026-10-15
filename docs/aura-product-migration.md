# Full Aura product-suite migration

## Scope and status
This workflow migrates a BUILD COPY of the original React application, preserving its existing modules instead of replacing them with links or simplified rewrites. It is build-only and does not deploy, modify the source repository, change database grants, copy private member records, or activate automations.

Source: sicairos4/aura-launchpad (private).
Destination: sicairos4/david-sicairos-site, proposed mount /members/aura/.
Existing Intentional Day: /members/products.html.
Backend retained: uwidjnnhdgtrpsymuhwp.

## Products carried by the original application
Morning/Evening routines; Time Architect; Goal Architect; Scribe; Focus; Weekly Review; Content Studio; Creator Toolkit; Resume tools; Personal Brand; Learn; Homework Helper; Community/Guilds; wellness tools; profile/settings. Presence in source is not proof of functioning integrations. Parent/student/admin and biometric features require distinct privacy/accessibility/security review before launch.

## Build preparation
1. Review a full immutable source commit.
2. Add AURA_SOURCE_READ_TOKEN as an Actions secret in the destination repository: read-only Contents access limited to aura-launchpad. Do not paste it into chat or commit it. Cross-repository checkout cannot read this private source with the destination's default token.
3. Run the workflow manually with that reviewed 40-character SHA.
4. TypeScript or build errors stop the workflow. Fix inherited errors deliberately rather than suppressing checks.
5. Inspect the review artifact and migration-routes.json. Artifacts expire after three days. Check repository artifact access before running with private source; compiled frontend code must be treated as disclosed to artifact readers. A private staging repository is preferable for sensitive reviews.

## Adaptations
HashRouter supports static hosting under the website's project path without server route rewrites. Vite's base points bundled assets to /david-sicairos-site/members/aura/. The global service-worker optimizer is disabled in this build copy; independently registered workers/hardcoded root URLs still need inspection. Shared member links are added. AuthContext delegates sign-in to the existing member page and removes that context's personal-data console logs. This is not a repository-wide log scrub or complete rebrand.

## Authentication and integrations
The website and migrated app retain the same Supabase project and default local session storage, but cross-tab/session behavior needs browser testing. Member login currently returns to products.html; members must navigate to the suite after signing in. Do not claim deep-link return behavior is implemented. Other direct OAuth calls in components need review. The existing Time Architect uses a Google provider token: ordinary Google identity sign-in does not establish that Calendar permissions, refresh/reconnect or background execution are working. Test calendar scope, consent, token expiry, all-day event handling, and CRUD separately before exposing calendar controls. No calendar events are modified by the build workflow.

## Data boundaries
Keep private routine/journal tables separate from public publishing analytics. Newly installed intentional_* tables and legacy routines/dynamic_schedules/journal_entries are separate authorities until an explicit reconciliation is reviewed. No automatic data copying or merge is part of this build. Backend admin/worker function warnings reported in the earlier review remain unresolved and should block unrestricted member launch.

## Release gates
- Successful locked-dependency install, TypeScript check, production build.
- Audit dependencies and inspect compiled assets for secrets/private configuration; publishable Supabase keys are browser keys, service keys/provider secrets are prohibited.
- Check root-relative assets/anchors, other OAuth entrypoints, service-worker registrations, and API endpoints.
- Two-account RLS and privileged-function authorization tests; signed-out access tests.
- Browser checks for each product: saving, refresh, back navigation, mobile layout, errors.
- Verify backend integrations and AI providers; label unavailable capabilities honestly.
- Test source-to-member session handoff and sign-out cache clearing.
- Confirm existing Pages build configuration before changing deployment.
- After separate approval, copy only reviewed built files into members/aura/ and add suite links to the member workspace. Do not alter the root 404 or existing site deployment blindly.
- Keep the old Aura deployment available until the new deployment passes acceptance; document rollback to the previous website commit.

## Not completed by this commit
The workflow has not been run. No compiled suite has been published. No security grants, OAuth allowlists, API secrets, backups or cron schedules were changed. Actual migration completion requires the source read credential, successful build and acceptance review, followed by a separately approved deployment.
