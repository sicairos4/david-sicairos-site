# Credential-free QA

This QA workflow uses GitHub Actions, a local HTTP server and Chromium. It does not need a Cloudflare/Airtop account, OAuth token, database service key or browser-service key. Standard GitHub Actions usage still applies.

## Checks

- Static references across repository HTML: local pages, scripts, stylesheets and media sources. Missing files fail; missing static anchors and metadata produce warnings because some anchors are generated at runtime. This is not an external-link or full accessibility audit.
- Local previews of homepage, Warchest, support, store, Launch Pathways and multimedia.
- Widths 360, 390, 768 and 1440 pixels; light and midnight themes.
- Full-page screenshots, plus homepage menu screenshots on narrow screens.
- Automated checks for page-level horizontal overflow, overlapping visible content buttons, the Warchest two-button hero, desktop payment-action alignment, menu Escape closing and uncaught JavaScript errors. These checks are not a substitute for human visual review.

## Safety and limits

Remote browser requests are blocked. Screenshots therefore show static content and local fallbacks, not live Ecwid catalogs, remote logos/thumbnails, Supabase records, authenticated member content or YouTube playback. No analytics requests, social publication, payments or private scheduler writes are made. The browser audit is not evidence of successful live deployment.

The workflow does not deploy the site or change branch-protection settings. Existing broken links may cause its first run to fail; inspect the JSON reports instead of treating a failed audit as a deployment change.

## Artifacts

Each run stores static-site-audit and responsive-local-preview artifacts for seven days. Inspect report.json and the PNG screenshots. A workflow must actually execute before any results can be claimed.

## Build status

The static checker passed five local synthetic fixture checks during preparation. The repository-wide audit and Chromium matrix have not been executed by the assistant. Credential-dependent production verification remains pending; do not mark integrations connected or complete from this workflow.
