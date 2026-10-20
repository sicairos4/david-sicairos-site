# Recent feature release checks

This batch adds Node tests for daily-flow data mutations, file-based carry-forward validation/deduplication, module wiring, and Public Files RLS source invariants. It updates the older review-share integration expectation from a two-script list to the actual four-script loader and runs these tests in the Workstation release gate.

Source inspection only at preparation time; tests have not been executed by this connector. CI completion and results must be checked separately. No APK is produced by this release gate; the Android debug workflow is separate. These tests do not establish deployment, device installation, authenticated save/reload, live anonymous RLS access, or real Form 700 collection.

Next acceptance: verify both release-gate jobs, examine QA reports, inspect Android build artifact/receipt, install the identified APK, confirm icon and launch image, and check Google sign-in and private-account isolation. Do not mark checklist items done based only on a committed test.
