# Explicit Creator sharing

This batch adds sharing for the master Creator draft and the selected social variant. It does not finish the entire remaining-build specification or every part of Batch 3. It builds on the already committed Batch 2 social desk and preserves normal planner PDF-only output.

The Creator loader includes creator-share.js. The panel provides an exact plain-text preview and an explicit outbound-sharing checkbox. It never reads journal/reflection fields, uploads to Workstation, fetches attachment URLs, connects an account, schedules or publishes. Social attachment-reference URLs are shared as text, not silently downloaded into files.

Where browser Web Share and file sharing are available, users can select up to five local files totaling 20 MiB. The script supplies those files directly to the user-chosen browser share target without reading their bytes or storing them in account records. Unsupported file sharing produces an explicit error; it does not silently drop files. Copy text only is a separate deliberate fallback and never copies files. Clipboard writes and outbound shares already initiated by the user cannot be recalled.

Android builds containing the new shareText bridge use a second native exact-text preview and ACTION_SEND chooser for text/links. The native bridge restricts the top-level route to the active HTTPS member app and compares WorkstationApp.context before preview and again before launch. URLs and payload are not logged. Existing email/password, Google return, guest access, print and text-save functions remain in source. Existing installed APKs need the new native code before that bridge is available; no installation or build is claimed here.

Sharing previews bind account context, selected day, record and exact source text/title. They clear on account/day/source invalidation and pagehide. Choosing a target, browser promise resolution or requesting a native chooser is never labelled successful publication. Target apps control their own posting steps. Local files are removed from the sharing UI when it closes.

Remaining Batch 3 scope includes native Android binary-file sharing/FileProvider and broader explicitly selected public-resource/output entry points. Browser file selection is not promised inside an older embedded WebView without file-picker support. Native text sharing does not require binary-file permissions. This batch does not replace provider publishing adapters or finish storage, account deletion, courses, Public Files, commercial delivery or external activation.

No tests, browser/device checks, workflow dispatch, APK assembly, credential changes, payments or publication are performed while preparing this source batch. Existing automatic workflows are unchanged. It is source implementation, not a runtime acceptance or publication receipt.
