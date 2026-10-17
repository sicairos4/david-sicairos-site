# 209 release audit and Muse handoff

## Execution boundary
This is an audit snapshot and a work plan, not an active agent or an overnight scheduler. No nine-browser fleet or four-hour background process has been launched. The repository policy ops/delegated-review-policy.json reports proposal_only_not_an_executor and transport not_connected. Do not represent that policy as an operating publishing pipeline.

## Observed in this pass
- Backend project uwidjnnhdgtrpsymuhwp reported ACTIVE_HEALTHY.
- Log window: 2026-10-17 04:00:00Z through 06:29:00Z. Auth logs included one /authorize 302 and one /callback 302; most entries lacked usable status fields. This does not prove successful member access.
- The current login form preserves password-manager autocomplete and does not prohibit pasting.
- The shared controller previously did not react to successful sign-in events on login. This change adds deferred event-driven verification, session-missing handling, bounded waits, retry UI, safe error messages and explicit password visibility.
- Existing workflow files include site QA, member tests, adaptation cycle, backups, Beehiiv and YouTube sync. Their existence is configuration evidence, not proof of a successful run or publication.
- Follow the Receipt commit b44c9ca and planner commits a885156, 207cf50 and 6e03322 are source changes, not proof of deployment or browser acceptance.

## P0: release gate for scheduler access
1. Resolve the exact production origin and project base path. No redirect URL is changed by this source commit.
2. Verify Supabase's production Site URL and exact redirect allowlist entries for members/workstation.html and recover.html on each intentionally supported origin. Do not use a broad production wildcard to bypass diagnosis.
3. Test email signup/confirmation, email sign in, Google callback, recovery and local-device sign out in a real browser. Never copy access tokens, callback fragments, passwords or recovery URLs into a public receipt.
4. Enter Workstation, open Today and Schedule, save a synthetic day, reload and confirm the same record. Repeat with a second authorized test account to test isolation. Test competing revisions and session changes.
5. Record commit, deployed URL, test method, result and redacted evidence. Mark passed only after the actual test.

## P1: remaining product work
- Embed Intentional Morning before Intentional Day: editable timed routines, drag reorder with keyboard alternatives, explicit handoff and duplicate/conflict protection. Not implemented by this access repair.
- Add the habit choice library, explained tracker and guided notebook. Do not treat missing habit entries as automatic failure.
- Build storage choice, local backup/restore and user-owned Drive authorization separately. Existing account day saving still includes journal text in Supabase. Do not migrate private data silently.
- Reproduce the reported dBeastco-homepage navigation issue using the exact clicked URL. Current toolbar Wellness points to dbeastco.html; source inspection did not find a homepage redirect. Do not guess a global hash redirect.
- Verify mobile navigation, focus order, theme contrast, reduced motion, forms, route drawer, clipboard fallback and no-JavaScript navigation.

## Optional four-hour plan for an authorized operator or connected executor
This schedule is a suggested allocation, not a running job.
- 00:00-01:00: access/configuration diagnosis and synthetic save/read checks.
- 01:00-02:00: link, keyboard, mobile and privacy-boundary checks; focused repairs.
- 02:00-03:00: Morning/habit/notebook implementation slice with regression tests.
- 03:00-04:00: deployment verification, open-blocker report and reviewed content drafts.
Independent research lanes may cover source verification, accessibility/usability and brand/content hypotheses. They must not make overlapping writes to the same files or turn private journals into research inputs.

## Publishing and growth
Do not change permissions, provision paid services, send newsletters, delete records or publish new material under this document alone. Inspect existing authorized jobs and report their real status. A draft, scheduled job, API acknowledgement and verified live post are distinct states. Keep sensitive or unverified claims held for review. No journal text in public handoffs.

## Evidence-led design
Use clear choices, descriptive errors, password-manager support, reversible actions and reduced-motion alternatives. Treat emotional-response and conversion claims as hypotheses until measured. Do not claim scientific proof or invent metrics.
References:
- https://supabase.com/docs/guides/auth/redirect-urls
- https://supabase.com/docs/reference/javascript/auth-onauthstatechange
- https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html

## Completion rule
This repair's local mocked tests do not certify production auth, account privacy, live posting, backups/restoration or the full site. The website is not finalized while P0 gates and material product blockers remain open.
