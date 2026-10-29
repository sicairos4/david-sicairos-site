# Private intake and analytics controls

Source batch only. No migration, deployment, original-file collection, provider dispatch, production analytics run, test or browser/device verification is included. Existing push-triggered automation may run; its outcome is not established.

## Draft catalog intake

The importer accepts an absent/null public_document_url, so restricted metadata can enter draft review without creating a public copy. A supplied HTTPS URL remains only a reference: the importer neither changes its permissions nor proves its safety. Never supply a signed/token-bearing private URL. The schema still requires source provenance and an original SHA-256. The importer does not download or hash bytes and cannot certify those claims.

The importer rejects attempts to set a reviewed/published state, binds writes to the existing 209 project, and requires an inserted-row receipt with the expected SHA-256 and private draft state. Existing hashes are skipped without comparing or updating metadata. On a transport failure, stop and inspect that hash before retrying; earlier rows may already have committed. Dry-run remains default. No batch-wide transaction is claimed.

Still required: durable protected original storage; authorized collection; malware/safety scan workflow; reviewed copy checksums; immutable redaction receipts; amendments and filer/position/period coverage; exact release approval and revocation. This patch does not authorize release or alter RLS.

## Analytics worker

worker/adaptation-cycle.js now requires ANALYTICS_EXPERIMENT_POLICY before any GA4 query. ANALYTICS_EXPERIMENT_PAUSED=true stops execution. Missing/expired consent evidence or owner approval, invalid windows/duration, no usable data, incomplete/thresholded reports and timezone mismatch stop the run without a new snapshot. A failed run does not erase an older snapshot; consumer freshness enforcement and withdrawal/purge orchestration remain separate work.

Policy fields: enabled=true; collection_consent_attested=true; consent_evidence_ref and approval_ref (non-secret references); experiment_id; approved_at, starts_at, ends_at (timezone-qualified timestamps); max_duration_hours (explicit 1–744 cap); property_timezone; action=review_only; attribution_model=aggregate_page_engagement; private_writing_allowed=false; stop_on_no_data=true; stop_on_incomplete=true; stop_on_consent_withdrawal=true. Do not invent authorization or evidence values to activate a run.

Consent is an operator attestation, not a browser consent-management implementation. Withdraw consent by pausing/disabling the experiment; this is not automatic detection of individual withdrawal. Window reporting remains previous seven complete GA4 property-calendar days against the preceding seven, not person-level attribution, conversion attribution, or causal lift. Report windows can predate the experiment; a separate approved measurement design is required for campaign claims.

Candidates are review-only and featured is always empty. There is no automatic website or social promotion. Snapshot expiry is capped at experiment end. Stopping the producer does not retract an already stored or externally consumed snapshot. Freshness, read-back, deletion/withdrawal and consumer integration require subsequent implementation.

## Other requested work remains open

Preserve the private Audit request/event/source schema and extend it only after inspecting live definitions. Source-cited CEDS work requires real evidence with page/section locators; do not fabricate observations. Existing creator_engine_bus.py prepares handoffs and explicitly does not publish. Complete the actual Muse consumer/provider integration instead of treating this script as a dispatcher or building a competing publisher. Authorized destinations, payload-bound approvals, scheduling, deduplication, uncertain-outcome reconciliation, retries, provider receipts/read-back and rollback remain open.

Website/newsletter/media/accessibility/responsive/theme exceptions need concrete source findings and bounded fixes. This batch does not mark any of those areas finished. Tests and live acceptance remain deferred by user instruction.
