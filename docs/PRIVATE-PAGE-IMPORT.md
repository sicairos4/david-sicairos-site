# Private archive page-text import

## Build status

Private page storage/search migration applied; account browser integration committed. This batch adds an offline SQL-plan builder. It is not a completed archive import, live acceptance or a claim that all 88 records are present. No tests or deployment checks were run.

The connected Drive search returned related attachment-index documents, not the required archive-search-index.json and attachment-index-dataset JSON source pair. Do not reconstruct missing page text from inventories or index PDFs.

## Prepare the exact private transaction

Run scripts/prepare_private_page_import.py with --index PATH --catalog PATH --mapping PATH --owner OWNER_UUID --output NEW_PRIVATE_DIRECTORY. It uses the Python standard library, makes no network requests and does not execute SQL. Keep all inputs/outputs outside the public repository. The mapping is a JSON object whose keys are source drive_file_id values and whose values are existing private audit_archive_documents.id UUIDs for the explicit owner. It must cover exactly the source index. Obtain those references from an authorized account export/intake, not title inference. Metadata ingestion must happen separately before page ingestion; this tool never invents metadata or creates owner accounts.

The builder preserves page numbers, splits long pages into 50000-character chunks, indexes only source text_status=ok, records source snapshot identity and marks all nonempty extractions partial because page completeness is unknown. Empty ok text becomes no_text; other statuses become failed with the source status preserved in processing_note. Original hashes are copied from the existing document record during execution and are not byte verification. Catalog missing entries are counted in the private receipt but are not inserted as fake documents or account coverage totals.

Generated SQL is a single transaction. It locks the owner import stream and existing parent rows, requires exact owner/document/Drive binding, refuses conflicting existing extractions and skips a matching snapshot binding on repeat. It does not replace or repair already-imported snapshots. Replacements and repairs need a separate explicit plan. The skip condition does not certify historical page completeness or absence of corruption.

Review and approve the exact private SQL through the external-action confirmation gate before executing with privileged database access. Never put a service key in the browser or commit private SQL, snapshot contents, mappings or receipts to the site. POSIX output files use mode 0600 in a mode 0700 directory; Windows permissions depend on the local filesystem policy. A preparation error can leave an incomplete private output directory; do not execute any partial artifact.

## Remaining dependencies

Actual source JSON pair, correct owner identity and exact existing-reference mapping are needed for a real import. Full-account export inclusion for the new text tables remains a separate integration task. Existing source Drive permissions, CHP publication hold and public catalog stay unchanged. Data import execution and live deployment acceptance are not implied by this code commit.
