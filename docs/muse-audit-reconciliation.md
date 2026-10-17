# Muse first-audit reconciliation

Baseline: Site-inspection-report.md, 2026-10-16 approximately 18:15–19:00 PT. That report is historical evidence, not a current live-site certificate.

| Finding | Current treatment | Evidence still required |
|---|---|---|
| G1, G10 deploy/UA 404s | Open; no causal conclusion | Post-deployment HTTP checks with multiple user agents |
| G2 social previews | Runtime title/description fallback preserves page copy; favicon is no longer invented as a preview image | Static HTML OG/Twitter tags and a suitable raster brand card, then crawler verification |
| G3 nested favicons | Runtime fallback resolves against project root | Raw HTML favicon coverage and browser verification |
| G4 canonical/theme/schema | Runtime canonical strips query/fragment/index alias; theme-color follows --bg; WebSite JSON-LD added | Static metadata generation and indexing checks; no claim of crawler coverage |
| G5 visitor analytics | Open | Verified measurement ID, consent policy, install and receipt; never expose a service-account credential in HTML |
| G6 zero analytics | Missing/stale data withheld; real measured zero retained; source and baseline regression tests committed | Fresh provider measurements and recurring ingestion receipts |
| G7 sitemap | Public missing routes added; member workspace removed; login/dashboard/ops not added | Published sitemap fetch and Search Console submission |
| G8 tracker | Open | Extract and validate real entity records; do not fabricate coordinates |
| G9 promos | Added data/experience.json matching experience.js schema, pointing only to existing public site routes | Confirm deployed JSON and rendered cards |
| G11 social identity | Audit and public 209 Connect source agree on TikTok @sicairosdavid; source-wide repair remains open | Inventory and correct every occurrence without altering unrelated content |
| G12 member navigation | Open | Review intended app chrome and authenticated flows |
| G13 unused media.json | No file invented for an unreferenced endpoint | None unless a real consumer is introduced |

## Other work not closed by this batch

- Public Files searchable records UI, real tracker feed, receipt-backed calendar upkeep, verified article thumbnails and safe public social navigation.
- Static social-share metadata and a raster preview asset. JavaScript metadata is not a substitute for raw HTML metadata used by non-JavaScript crawlers.
- Newsletter confirmation/welcome flow, payment destination verification, authenticated two-account isolation, broad table-policy review and remaining platform security settings.
- Provider access must be checked through connected tools before calling it blocked. Connector availability alone does not prove a worker is running.
- Browser/contrast/keyboard/checkout verification remains deferred. No live pass, publishing receipt, metric, credential or runtime handoff is invented.

Metadata tests use a minimal DOM harness. They do not establish rendered appearance or crawler behavior. Sitemap exclusions and robots metadata are discovery controls, not authorization controls.
