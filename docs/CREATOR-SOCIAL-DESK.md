# Batch 2: Creator social drafting desk

Prepared against main f9c7692701288177fb55fceb1f81c14b758fd1e7, which already contains Batch 1. This is source implementation, not a deployment, account connection, publication or acceptance receipt. No tests or device checks are run as part of this batch; existing workflows are unchanged.

## Implemented scope

The existing Creator output module loads social-desk.js and its scoped stylesheet. The master remains plan.draft. Six independent editable versions (Facebook, Bluesky, Threads, Instagram, LinkedIn and Newsletter) live in plan.creatorSocial under version 1. Each holds text, optional HTTPS post link, call to action and up to five typed image/video/file URL references with descriptions. Unknown future model versions fail closed rather than being overwritten. A 200,000-byte client-side cap bounds the social model; this is an app bound, not a statement of provider posting limits or server quota.

Every social edit uses WorkstationApp.change, marks the existing selected day dirty and participates in its explicit Save selected day flow. ConnectCore.normalize preserves additional plan properties, and the existing adapter supplies the plan to intentional_save_day. No table, policy, RPC or credential is changed. Demo saves remain memory-only. Live server acceptance/persistence and backup/restore coverage for the new fields are not asserted here.

Use master text is deliberate and confirms replacement of existing platform text. Links, calls to action and references remain independent. No journal, lesson, reflection or notebook content is read automatically. The existing reviewed-lesson import remains a separate explicit action.

Preview is plain text and validates HTTPS URLs without embedded credentials before Copy or download. Attachment references are not fetched, embedded, uploaded or included as binary files. Text download uses the existing Android saveText helper when available or a browser text download; requested output is not labelled saved or published. These Creator draft text actions do not replace or expand normal personal-planner Save PDF controls.

## Privacy and limits

The panel gates edits/output on loaded member state, current context, day, record and master-field availability. It clears its fields/previews when unavailable, on account/day changes and on pagehide, then reloads from the current record. Async clipboard results are context-bound, but an explicitly initiated clipboard write cannot be recalled; users should clear sensitive copied text themselves.

This batch does not connect accounts, upload media, enforce provider-specific posting limits, call an AI service, publish, schedule, ingest engagement or create another publisher queue. Selecting a destination never means connected. Browser/native share sheets and real server-side publishing adapters are later batches. Draft/model exports and user privacy remain distinct from public distribution.
