# Final-batch release-signing foundation

Prepared against a2b418b61866064adbf47a2f2d13aac50ec4598f. This implements only the Android signing/artifact portion of Batch 7. Batches 3-6, account storage/deletion work in Batch 7 and wider Batch 8 work are not completed by this patch. Skipping their order does not mark them done.

## Source changes

Release tasks require an existing external keystore and four environment values: ANDROID_KEYSTORE_PATH, ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_ALIAS and ANDROID_KEY_PASSWORD. Missing configuration fails before release tasks execute. Debug and isolated full-screen suffix/version declarations remain unchanged. There is no debug-signing fallback for release and no key generation. No version number or application identity is changed.

The new workflow is manual-only, main-only and builds APK/AAB artifacts for its exact workflow commit. It does not run a test suite, create a GitHub Release, upload to Play, change the download page, publish records or migrate private data. Existing workflows remain in place and may run their normal automation when source changes are pushed.

## Required operator setup before manual execution

1. Use the intended existing production signing or upload identity, with its protected recovery copy. Do not replace a key associated with an installed or distributed app merely to get a build through. Debug/full-screen packages are separate identities and are not automatically upgraded by this production package.
2. Configure the GitHub environment named android-production with the intended reviewers and deployment-branch restrictions before storing credentials or running the workflow. Naming an environment in YAML does not create its reviewer protection rules.
3. Store the existing keystore as single-line ANDROID_KEYSTORE_BASE64 and its matching ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_ALIAS and ANDROID_KEY_PASSWORD as protected environment secrets. Their availability has not been checked or changed here. Never put keystores or passwords in repository files or chat.
4. Set the intended versionCode/versionName in source before a new distribution; reuse of the current code is not an established upgrade path. The workflow records actual APK output metadata rather than guessing a version from source text.
5. Dispatch Android production-signed artifacts from main only when authorized. The keystore is decoded with restrictive permissions in runner temporary storage and removed by an always step. Only artifacts, a receipt, notes and checksums are uploaded, never signing material.

## Limits

No build, test, device check, signing-identity check or release was run while preparing this source patch. Artifact hashes identify output bytes; they do not prove key identity or installed-app compatibility. The supplied identity must be the authorized intended key. Receipt fields deliberately leave identity/device acceptance false rather than infer success from compilation. The online WebView still uses live website content, and native Google callbacks still require their authorized server configuration.

The current repository also contains public-files-drive-sync.yml for draft import. That source is not evidence of collected, reviewed or published records; final-batch Public Files work must extend it rather than replace it blindly.
