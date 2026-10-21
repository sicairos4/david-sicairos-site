# Native Google return implementation batch

Source proposal, 2026-10-21. This batch implements native browser launch, package-specific code callbacks, PKCE exchange and an isolated same-origin WebView session handoff. It does not finish the wider remaining-build specification.

The native welcome button and existing embedded Google authorization navigation start a newly confirmed native attempt. A random nonce binds the callback; a private app preference stores the verifier and creation time for at most ten minutes of validity. Valid callbacks are consumed before exchange. Tokens never enter callback URLs, intents or logs. A bounded HTTPS exchange returns tokens in memory, and only the exact HTTPS /members/native-google.html page can receive them. The account SDK imports the session, verifies its user and then opens the workspace. Email/password, guest, print and text export remain available.

Android uses ${applicationId} as its callback scheme, including debug and isolated test variants. Operator configuration must allow the appropriate package's oauth/callback route and its attempt query. Do not add broad unrelated redirect destinations. This commit does not change Supabase settings.

The handoff page must actually be deployed at https://209connect.com/members/native-google.html before device testing. It uses the same major-version account SDK source as the existing login page; this is not exact dependency pinning. Website content remains live, not APK-pinned.

The candidate workflow already covers android/** and members/** and gates the reusable APK workflow. The reusable APK workflow additionally compiles/runs the 22 pure-Java callback checks before assembling the app. Test source is not a test-pass receipt. No Java/Android compilation, workflow result, configured callback, device installation or live sign-in acceptance is asserted by this document.

Open acceptance: allowed callback configuration for each intended package; browser cancellation and retry; repeated, expired and mismatched callbacks; activity recreation/process loss; network errors; fresh and existing account sessions; isolation and saved-record reload; actual production signing and update behavior. An exchange interrupted after its one-time attempt was consumed requires a fresh sign-in. No background publishing, payment, private-data migration or full-backlog completion is authorized or claimed.
