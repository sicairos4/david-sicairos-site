# Offline browser review

Download browser-review.html as a standalone file and open it locally. It includes all of its own styling and JavaScript; no package install, hosted server, external assets or provider credentials are required. Browser/platform support for opening local HTML files must still be checked on the chosen device. A GitHub HTML preview is not the tool: hosted mode deliberately disables snapshot loading.

Choose your own sanitized JSON export matching the committed v1 steering contract. The viewer keeps it in tab memory, displays up to 500 observations with platform/text filters, source declarations, reported evidence and metric definitions, and presents only advisories passing its current expiry/source-collection checks. Expired observations remain labelled historical. Missing values are Not reported, not zero. There are no clickable provider links, network calls, upload controls, publishing controls, local-storage writes or receipt downloads. Clear and page-leave handlers remove the preview.

The browser parser rejects duplicate keys, excess nesting and non-finite numbers. Browser numeric checks reject integers outside safe JavaScript precision. This is a preview with conservative checks, not a replacement for the Python schema/intake path or proof of exporter authenticity, consent, metrics, sample size, live publication or authorization. It creates no accepted bundle and cannot actuate recommendations. All supplied text is rendered as text, never as HTML or commands.

Keep real exports outside the website checkout. The empty viewer is source code, not a hosted private dashboard. A compromised local device or altered viewer can still expose selected files; CSP and in-memory handling are not encryption or a substitute for trusted software. Individual Life ID records, private journals, raw habit entries and authentication data must never be used as steering snapshots.

No real snapshot, browser acceptance, tests, runtime connection or live provider integration was performed while authoring this source.
