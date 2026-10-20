# Form 700 library

2026-10-20. Public Files is now a purpose-built Form 700 browser over the existing pf_* tables and public read policies. No schema or database write is part of this commit. The former public-files-live.js remains in source but is not loaded by the rewritten page.

Browse by agency, filer, reporting-period end year and statement type; search visible positions, indexed interests and filing IDs; sort by date/name; display 20 results per page; export all filtered published metadata as CSV or JSON. This is a metadata index, not a ZIP of PDFs. Agency cards retain official sources and request routes even when no filings are published.

Documents and filings must both be published, documents redaction-reviewed, people/agencies visible and agencies in the configured scope. Positions must match both the filing agency and filer. Interests must be published. Original and amendment records remain separate. Anonymous requests use the existing publishable key and no service credential. Reads page through tables with a 20,000-row per-table ceiling; reaching the ceiling without completion produces an error, not a partial total. A consistent multi-table snapshot or large-scale server search remains future work.

Reviewed PDF links open directly; download attempts retrieve only the approved public URL, omit credentials, cap streaming at 25 MB and check PDF magic bytes. Cross-origin restrictions or larger documents fall back to the Open reviewed PDF link. Source-file hashes are not misrepresented as hashes of redacted public copies.

The intake form is LOCAL ONLY: choose a PDF, enter agency/filer/position/type/source/dates, calculate its SHA-256, and download a draft JSON receipt compatible in shape with the existing preparation tool. No document bytes or metadata are sent to a server by intake. It is not a persistent upload/review queue. It checks file signature, not whether the PDF is an authentic completed filing or safe/redacted. Public publication still requires controlled operator ingestion, identity/source/redaction review and actual reviewed file storage. Actual Form 700 PDFs have not been located or uploaded in this batch.

Core logic tests and browser-script parsing were exercised locally before the proposal; no deployed API/browser/download or publication acceptance pass is asserted. No filings are fabricated, no private Drive document is made public, and no anonymous write policy or bucket is introduced.
