# Private document browser — account page-search integration

The private page-text migration audit_archive_private_page_search_v1 was applied successfully to project uwidjnnhdgtrpsymuhwp before this source patch. It adds audit_archive_extractions and audit_archive_pages, owner SELECT RLS and a read-only SECURITY INVOKER audit_archive_search_documents_v1 RPC. No archive records or text were imported. No tests or runtime/deployment verification were performed.

## Account mode

The browser defaults to My account documents and page text. It calls audit_archive_search_documents_v1 with p_query, p_agency, p_record_type, p_request_ref, p_limit=20 and page offset. All simple-token words must occur in a metadata vector or one page chunk. This is not literal phrase, partial-word, alias or relationship matching. Pipes are converted to spaces for account queries. The first matching page/chunk is shown per document, with an unhighlighted partial excerpt and private Drive link. Rows, counts, format, pagination, coverage counters and page locators are validated before display. Identity is checked before and after the request; changed query context rejects stale results. No automatic metadata fallback follows an RPC failure.

The two explicit alternatives remain: Loaded account metadata only uses substring matching; Opened private snapshot uses the existing JSON pair in page memory, with all required literal terms together in metadata or one page. Neither uploads files. Local snapshot source ownership is user-attested, not verified against account identity.

## Coverage and privacy

Account coverage reports imported document references, searchable pages/documents, partial/no-text/failed/pending states, absent extraction records, stale Drive/hash bindings and known missing originals. Archive-wide missing total remains unknown until actual missing-file records are integrated. Coverage counters are not query matches, unique hash totals or completeness evidence. If a referenced Drive ID or recorded original hash no longer matches the extraction binding, that extraction is excluded. Unknown original hashes do not certify bytes.

Account metadata options are loaded owner-filtered in 200-row batches, withholding an incomplete metadata list at 20,000 rows; the paginated RPC does not rely on that list for all document matches. Snapshot inputs are capped at 64 MiB each and lists at 20,000. Private data renders through textContent. Drive links are constructed from validated IDs with noreferrer. Search/snapshots clear on identity changes, desk hiding, page exit and reload. No query or excerpts are stored in browser storage by this code. The public catalog is untouched and the CHP publication hold remains intact.

## Import contract and remaining work

Private metadata records must first exist under the correct owner in audit_archive_documents. Each extraction row references owner_id + document_id, records its Drive ID, optional original SHA-256, source snapshot SHA-256/label, generation UUID and processing status. Each nonempty page body is at most 50,000 characters; longer pages must be split with preserved page_number and increasing chunk_number. Chunk boundaries limit multiword matching: a query spanning chunks may not match. Pages reference the same owner/document/generation. Changing an extraction generation requires an explicitly approved transactional replacement strategy; do not orphan or silently mix snapshots.

Client roles have SELECT only on the new tables. A privileged import is a separately approved data write, not a browser upload or a reason to expose a service key. No import, OCR, generator, matter assignment, canonical entity/alias mapping, provider activation or permission repair is included. Account deletion cascades through parent documents, but full-account export coverage for the new page-text tables still needs reconciliation. The actual Muse package is required before preparing exact owner-scoped metadata/text imports. A successful migration or commit is not proof of live successful search.
