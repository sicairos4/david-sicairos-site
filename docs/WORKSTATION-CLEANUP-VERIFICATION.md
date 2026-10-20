# Workstation cleanup verification gate

2026-10-20. This adds verification, not a claim that the full project backlog is implemented or accepted.

The new workflow runs existing creator/page-cleanup Node tests and Chromium checks against a local repository server at desktop and phone widths. External browser requests, including the auth SDK and database, are blocked. The member gate is explicitly bypassed inside the isolated test, the adapter must show synthetic-demo mode, and clipboard writing is mocked. No live account acceptance can be inferred from this test.

Checks: all eight member views and horizontal overflow, Settings/Review grouping, reviewed-lesson append and replacement confirmation/cancellation, oversize refusal, exact displayed-text copy/download, empty-output disabling, demo save/reload, day-switch clearing and JavaScript page errors. Screenshots and a source-SHA JSON report are retained as workflow artifacts.

The test stops on its first failure. A failed or skipped run closes no gate. Passing confirms only its executed assertions: native clipboard permissions, real Google sign-in, two-account isolation, cloud revision conflicts, production deployment, keyboard/screen-reader acceptance, APK installation/signing, actual records collection, commerce and external integrations remain separate.

Python parsing was checked locally. Chromium execution and hosted CI results were not verified before this commit proposal. Public deployment/CI fetches failed in this session. Cloudflare Browser Rendering was discovered but disconnected; a connection through Settings > Connectors is needed to use that service for live-browser work.
