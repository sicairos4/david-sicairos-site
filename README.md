# David Sicairos — 209 Control Panel

A personal operating hub and multi-page website for David Sicairos, 209 Media Connect, 209 Audit, dBeastco Wellness, and 209 Systems Studio.

## Domain and deployment

`CNAME` configures `209connect.com`. The repository also has the default GitHub Pages address `https://sicairos4.github.io/david-sicairos-site/`; custom-domain redirects and availability depend on Pages and DNS configuration. Neither address is a verified deployment receipt.

Keep `index.html`, `CNAME`, `404.html`, verification files, `robots.txt`, and `sitemap.xml` at the published root. For branch-based Pages publishing, use `main` and `/ (root)` in Settings > Pages. Do not change publishing mode or DNS as part of routine file organization.

## Repository map

| Location | Responsibility |
| --- | --- |
| Root HTML files | Stable public page entry points, including `index.html` and `social.html` |
| `assets/` | Shared browser assets |
| `data/` | Site data and public feed inputs; not a place for credentials or private records |
| `scripts/` | Collection, import/export, operational helpers, and Creator Engine modules; see its README |
| `.github/workflows/` | Existing automation definitions and triggers |
| `docs/` | Architecture, operating guides, integration boundaries, and deferred work |
| `tests/` | Existing automated checks; some additional check scripts remain in `scripts/` |
| `prompts/` | Creator Engine draft instructions |
| `supabase/` | Database-related source/configuration |
| `worker/`, `workers/` | Separate existing worker areas; not assumed interchangeable |
| `android/` | Android-related source/assets |
| Other feature directories | Existing page groups and feature implementations; retain their paths until references are mapped |

## Editing safely

The site is not a single-file application. Edit the relevant page and its referenced assets or data. Preserve public filenames and relative paths unless all consumers and redirects are handled together. Keep the existing Google Form integration; this cleanup does not create a replacement contact form or change its destination.

Social showcase guidance is in `docs/social-showcase.md`. The source collectors retain their existing paths and workflow references. Selected LinkedIn cards are curated previews, not an automatically collected LinkedIn timeline.

## Creator Engine

The implementation is grouped with its related modules in `scripts/creator_engine.py`. The existing root command `python creator_engine_bus.py ...` remains as a compatibility entry point, including for the existing workflow. Importing `creator_engine_bus` resolves to the implementation module.

See `docs/creator-engine-operation.md` for provider configuration and operating boundaries. This runner prepares review bundles; it does not publish, insert database rows, send email, or dispatch social posts. Moving the implementation changes source fingerprints for opt-in checkpoints; do not assume an older checkpoint can be resumed with the reorganized source.

## Main links

- 209 Media: https://209connect.beehiiv.com/
- 209 Audit Tracker Index: https://sicairos4.github.io/209audit-index-tracker/
- 209 Audit CPRA Playbook: https://sicairos4.github.io/209audit-cpra-playbook/

## Scope and verification

This organizational change updates documentation and groups the Creator Engine implementation without moving page routes, assets, data, forms, worker areas, tests, or workflow files. Tests, provider calls, builds, and live deployment checks were not run as part of this change. Existing workflows may still run according to their own triggers. Committed source does not establish live operational success.
