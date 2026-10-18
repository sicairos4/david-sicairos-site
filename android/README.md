# 209 Workstation Android test build

New, unverified Android shell for the hosted members/app.html planner, not the isolated memory-only staging page. Requires Internet. The hosted site's release and account behavior remain independent of compiling this shell. No backend secrets are embedded.

The Android test APK workflow runs on relevant branch pushes and pull requests, and supports manual dispatch. It uses Java 17, Gradle 8.13, AGP 8.13.0 and SDK 35. It lints, builds a debug-signed APK and uploads the APK with SHA-256 checksum as a workflow artifact. No production release is published.

This is not a completed or device-verified app. Pending: successful CI, failed site static-check investigation, account sign-in/save/reload/sign-out/isolation acceptance, keyboard/insets/back navigation, recovery and OAuth return flows, offline/error UI, export/download handling, accessibility, durable release signing and upgrade testing. Native downloads, deep links and offline planner storage are not implemented.

Debug signing identity can change between CI runners. This APK is for testing; do not rely on it as an upgrade channel. A production app needs protected persistent signing credentials and increasing version codes. Never commit a keystore, signing password or service-role key. The Android shell does not finish the outstanding planner features.
