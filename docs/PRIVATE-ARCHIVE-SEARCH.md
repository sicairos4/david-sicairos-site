# Private archive page search: first consumer

Source implementation only. No private datasets are committed. No import, migration, Drive/Gmail transfer, public release, CI job, test or live acceptance is included.

## Boundary and correction

Muse reported an existing archive-search-index.json with page text but no producer or consumer found by workspace inspection. scripts/search_private_archive.py adds a local read-only consumer. It does not recreate the producer, perform OCR, claim a connected backend/UI, or change the historical workspace finding. Do not report it operational on Muse until this source is actually available there and used.

The live Audit schema already has metadata search_vector plus a GIN index. That vector covers title, filename, labels, request references, tags and notes, not the standalone extracted page text. This consumer does not alter that schema.

## Use in Muse's authorized private terminal

Run the code from the repository checkout, with the real private input paths outside that checkout:

```sh
python scripts/search_private_archive.py --index /private/archive-ingest/archive-search-index.json --catalog /private/archive-ingest/attachment-index-dataset-20261024.json --limit 30
```

The paths above are placeholders, not newly discovered destinations. Use Muse's existing resolved paths. Optionally add --agency with the exact entity label stored in the index. The catalog uses folder labels; label differences are not guessed or normalized.

The interactive prompt reads non-echoed literal terms separated by |. For example, enter a vendor name or vendor name|contract. All terms must occur on the same page, case-insensitively. This is mention discovery, not canonical-vendor matching or proof of a relationship. Terms are not passed as command-line arguments. Do not run in CI/shared logs. JSON output contains private excerpts and must stay in the authorized private terminal; never redirect it into the repository, public site, or shared log.

## Results and coverage

Output includes existing Drive IDs, document names, page locators, partial excerpts, total matching-page and Drive-copy counts, result truncation, agency labels, and SHA-256 identifiers of the exact input snapshots. It does not fetch Drive, validate original bytes, or emit original source URLs.

The companion catalog is required so missing attachments remain visible. Coverage includes all agency-scoped missing/excluded entries regardless of query; they are not asserted query matches. Rows with text_status other than ok, or with no nonempty page text, are withheld from text search. Per-page extraction completeness is not inferred from the presence of some text. No-result never establishes absence.

The consumer rejects mismatched catalog/index file sets, repeated Drive IDs, malformed page locators, and private inputs inside the repository. It reads at most 128 MiB per input. It writes no files and performs no network requests. It is not an access-control service: anyone able to read the local files can read their content.

Counts refer to copies, not unique document hashes. Raw agency labels are not independently verified provenance. There is no matter filter because no matter assignments have been established. No canonical entity IDs, alias resolution, role classification, payment aggregation, or confirmed cross-matter relationships are added.

## Next work

Inspect the actual private data with this consumer only after the source is available to Muse. Separately prepare a reproducible generator, OCR/status handling, private page-text persistence and authenticated queries, matter/entity relationships, and exact CHP import payload. Resolve column-level grants before proposing permissions changes. All external writes need exact approval. Optional tests remain deferred, not passed.
