# Data-to-content implementation status

## This patch

- Uses the existing Aura Morning System project uwidjnnhdgtrpsymuhwp.
- site_content/adaptive_web is the authoritative WEB snapshot; existing JSON social contracts are not silently redefined.
- GA4 compares previous seven complete property-calendar days with the preceding seven complete days. These are not rolling 48-hour windows.
- sessions and engagedSessions define engagement rate. Relative lift is separately named. At least 100 sessions per window and 20% relative lift are required. This is a heuristic, not a statistical significance or causal claim.
- Limits recommendations to four existing public resources: resume-builder, studio, tools, library. No article text, legal claims, medical claims, social captions, or social schedules are rewritten.
- Existing live-content consumers gain an optional homepage resource section; static content survives failed or stale data. Eligibility is not labeled as published or applied.
- Snapshot writes use an existing primary key, so repeated runs replace the snapshot rather than grow duplicate rows. The write response is checked.
- Automated tests precede the scheduled collection job. Missing credentials, wrong database project, incomplete reports, and failed writes fail the job.
- Muse remains external, not an embedded dependency.

## Not verified or delivered by this patch

- Tests have been authored, not executed by the assistant. A passing workflow and browser render remain acceptance gates.
- GitHub secret availability, GA4 property identity/access, database public-read policies, and live homepage script inclusion must be verified. Do not relax RLS to make a test pass.
- Social publisher runtime/repository and its transactional lease protocol remain unresolved. Never infer that changing content_variants changes the live queue.
- No social platform publication, caption rewrite, spend, database migration, or permission change is authorized by this commit.
- data/signals.json, decisions.json and experiments.json remain social/dashboard contracts, not evidence that the web snapshot executed social changes.
- Social metrics ingestion, action receipts, durable experiments, directive consumption, attribution, and rollback still require implementation against the actual publisher.
- The adaptive-content-rendered browser event is local only; it is not a durable publication receipt or GA4 conversion event.

## Acceptance gates

1. CI unit tests pass.
2. A scheduled run records SNAPSHOT_STORED against the intended property and database.
3. Anonymous read returns only intended public content under existing RLS.
4. Browser renders valid resource links, rejects stale/invalid data, and preserves static content offline.
5. Resolve live publisher, then implement directive consumption and verified receipts without creating a second publisher.
6. Link content IDs, campaign IDs and outcome windows before claiming any measured adaptive win.
