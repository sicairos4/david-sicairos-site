# Mobile/release workstream — coordination handoff

## Base and ownership
Branch: workstation/mobile-release-20261020.
Created from main at 5ef21de710763750dcd1c82668fc2e2e13498e17.
Canonical custom domain in CNAME: 209connect.com.
This chat cannot read the other chat's unsaved conversation. Shared commits, branches, PRs and these notes are the coordination surface. No acknowledgement from the other builder is claimed.

## Existing parallel work observed
Main includes signup simplification (3b11d36), task scheduling/browser acceptance work (c3ac804, 6c77af0), Today/guest cleanup (7540517), responsive toolbar alignment (12c9e95) and guest continuation/member merge (5ef21de). These are committed changes, not proof of live acceptance. Do not restore yesterday's login/menu/guest code over them.

## This slice: isolated new files only
- .github/workflows/android-preview-release.yml
- scripts/prepare_android_preview.py
- tests/test_android_preview_delivery.py
- tests/test_android_download.cjs
- android-download.html
- assets/android-download.js
- docs/mobile-release-coordination.md

No edits to login.html, assets/topbar.js, members/app.html, guest continuation/auth modules, current Android activity or backend settings in this slice.

## What this code does
After an approved merge to main and a successful trusted main-branch Android APK build, a separate workflow validates the source SHA, triggering run, receipt, checksum and basic APK entries, then publishes an immutable per-build GitHub prerelease. Fork/PR builds cannot publish. Existing APK assets/tags are not overwritten or deleted. The public download page discovers only a complete matching asset set. No existing release or live APK is claimed merely because this code is committed.

## Request for the web builder
Please acknowledge the file split in a PR comment or a new coordination message. Own the active login/menu/guest/UI work. After this branch is reviewed and merged, replace the old Actions-artifact APK href with relative android-download.html in the welcome screen, website menu and appropriate homepage app section. Keep Sign in, Continue as guest and Explore website visible. Do not claim a native/full-screen APK until an actual Android implementation and device test exist.

## Test boundary
Local tests validate fixtures and the delivery/discovery logic, not Android compilation, APK signatures, installation or OAuth. The existing Android build workflow is reused rather than replaced. A native/hybrid app change remains a separate reviewed patch; its callback and new-domain behavior must be coordinated with the auth workstream.

## Merge and release checklist
- [ ] Re-read current main and compare this branch before merge.
- [ ] Other builder acknowledges ownership; resolve any new overlap.
- [ ] Delivery validator and discovery tests pass in CI.
- [ ] Merge is explicitly approved; no production deployment is implied by a branch commit.
- [ ] Confirm new release workflow is on default branch, then a main APK build succeeds.
- [ ] Confirm publisher succeeds and all four assets are available anonymously.
- [ ] Open android-download.html on the actual canonical domain.
- [ ] Web builder updates old download links after validation.
- [ ] Device install/auth/save/sign-out test is recorded separately.

## Remaining release blockers
Stable production signing; installed-app architecture/no Chrome bar; verified Google return; complete iOS source import/build/signing; notification and Google Calendar/Tasks integration; newsletter embed. Guest continuation must be reconciled against the new main implementation rather than reimplemented here.
