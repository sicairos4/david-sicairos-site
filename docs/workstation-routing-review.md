# Workstation routing review

Reviewed November 8, 2026. Static source inspection only; browser, native callbacks, database policies, and production deployment have not been acceptance-tested.

## Canonical routes

- `login.html`: email/password, signup, Google entry.
- `recover.html`: recovery entry referenced by the auth script.
- `members/app.html`: canonical tool-first application; temporary tab workspace plus optional account-backed records.
- `members/index.html` and `members/workstation.html`: compatibility entry routes to login, preserving search and hash.
- `members/workspace.html`: compatibility entry route now goes directly to login, removing the workstation.html intermediate hop.
- `members/dashboard.html` and root `dashboard.html`: aliases to members/app.html.

Do not delete compatibility files without searching references, native entry points, service workers, tests, and external bookmarks.

## Authentication trace

`assets/workstation-auth.js` checks `auth.getUser()` and returns authenticated login visitors to members/app.html. Password login routes there after a session is returned. Signup and Google also use this destination. OAuth authorization destinations are validated; preserve that validation.

`members/app.html` loads connect-core.js and connect-app.js. connect-app.js starts with an in-memory adapter, attempts verified account loading, and keeps tools usable when signed out. It uses account identity checks and explicit save controls. Frontend visibility is not authorization; database policies require a separate audit.

`assets/workstation/account-entry.js` preserves unsigned work before sign-in and offers explicit restore/export/discard choices. Do not silently overwrite account data.

## User flow

1. Open entry route.
2. Check account session on login.
3. Sign in, create an account, recover access, or choose guest entry.
4. Return to canonical app after successful authentication.
5. Verify account and load the selected day; distinguish loading, account mode, and guest mode.
6. Choose Today, tasks, schedule, focus, reflection, review, creator desk, learning, or settings.
7. Save explicitly; warn before discarding unsaved work.
8. On sign-out clear private account state; describe remaining guest mode clearly.

## Open findings — not fixed by this commit

- Recognized section hashes are preserved into login aliases but the login success destination is built without that section. Design section restoration without forwarding authentication fragments or changing OAuth/native redirect contracts blindly.
- member-session.js combines module loading, theme, navigation, and legal mounting; it is not a simple authentication gate.
- member-session.js inserts a section dropdown in addition to existing navigation; inspect responsive CSS before removing either.
- Root/app ready-state markup should not be treated as proof of authentication or a private-data leak.
- Inspect Android entry configuration, native-google.html, guest routes, recovery, staging references, worker/ versus workers/, and Supabase policies before larger cleanup.
- Workflow inventory has many tests/builds; review actual triggers and dependencies before consolidating.

## Repository responsibilities

Public HTML: website pages. members/: app and aliases. assets/: UI and shared code. assets/workstation/: planning modules. android/: packaging. supabase/: backend-related files. worker/ and workers/: inspect responsibilities. scripts/: support tasks. data/: registries/content. tests/: checks. docs/: documentation. .github/workflows/: deployment, testing, and automation.

## Deployment and rollback

Pushes to main trigger deploy-pages-main.yml, which requests a Pages build if existing configuration matches main/root legacy hosting. Workflow configuration does not prove successful deployment. Verify the actual build and browser behavior. To roll back this batch, revert its commit; no database migration or auth configuration is included.

## Acceptance checklist

- Run `node tests/member-entry-alias.test.cjs`.
- Open members/workspace.html with no query/hash, then with query and a recognized section hash.
- Confirm direct navigation to login and functioning fallback link.
- Verify password, Google, confirmation, recovery, guest preservation, account load/save, and sign-out in a safe test environment.
- Verify Android separately.
