# Public Files implementation and deployment

This batch implements SQL source and a local intake validator. It does not apply SQL to production, upload documents, populate real filings, connect the public page to Supabase, or close the backlog's database/collection tasks.

## Database

Review and apply supabase/public_files_schema.sql to the intended Supabase project through an approved migration. It creates only pf_-prefixed tables and does not alter member tables. It is a one-time migration, not an idempotent bootstrap. A duplicate-table error rolls back the transaction.

Entities: organizations, people, dated positions, source documents, filings/amendments, filing-position links, disclosed interests/page references, and request receipts. UUID identity does not merge people with similar names. No people or completed filings are seeded.

RLS is enabled on every table. Public/authenticated users have SELECT only. Published filings require a readable reviewed document and visible organization/person. Interest and position-link visibility follows parent records. Drafts are not public. Privileged server-only intake/publishing is required; never expose the service role key. Public flags are explicit editorial decisions. Review raw source PDFs for private information before publishing URLs.

Document storage/bucket policy, staff authorization UI, write audit history, live page integration, person deduplication and cross-organization relationship validation remain open. SQL constraints are not a full editorial review system.

## Private intake

Run: python3 scripts/prepare-form700-intake.py --metadata private-metadata.json --pdf original.pdf --output private-receipt.json

Required metadata: organization_slug (city-atwater-ca or county-merced-ca), official_name, position_title, statement_type, source_url and timezone-aware retrieved_at. Optional: reporting_period_start, reporting_period_end, filed_date and amends_external_id. Dates use ISO YYYY-MM-DD. Statement types: annual, assuming_office, leaving_office, candidate, amendment, other.

The validator checks scope, metadata allowlist, HTTPS URL shape, period ordering, amendment linkage input and PDF header. It calculates SHA-256 and creates a draft-only receipt; refuses to overwrite an existing output. It does not authenticate source ownership, parse schedules, detect PDF malware or prove a PDF is a completed filing. Human review remains mandatory.

Keep PDFs and draft receipts outside the public Git repository. Match document hashes before import. Create organizations and resolve reviewed person/position identities before inserting filings. Resolve amendment external IDs to actual database IDs. Never use a blank template as a filing.

## Acceptance still required

- Apply/rollback in an authorized environment and inspect generated tables.
- Test anonymous and authenticated access to drafts, published parents and withdrawn parents.
- Verify no client writes; test service-only intake.
- Test validator with valid PDFs, invalid URLs/dates, reversed periods, non-PDFs, unexpected fields and duplicate outputs.
- Collect/review actual Atwater and Merced County government records and publish a truthful coverage report.

No SQL execution, browser integration or runtime test pass is claimed by this source batch. Parent running list: docs/BUILD-BACKLOG.md.
