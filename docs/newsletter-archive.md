# Newsletter and public archive operations

## Identity and scope
- Publication: 209connect / 209 Media Connect.
- Beehiiv publication ID: pub_16f23338-bd23-443e-9a22-fad5e136629b.
- Editorial/source system: Beehiiv.
- Website repository: sicairos4/david-sicairos-site, main.
- Public reader: signal.html?issue=<slug>. Archive: signal-archive.html.
- Import destination: data/newsletters.json.

## Discovery on 2026-11-10
The connected Beehiiv published-post listing returned 47 records on one page. This is a published-post inventory, not a count of eligible free public newsletter editions. The repository archive inspected before this change contained one recovered September 22, 2026 edition and imported_at was null. No full import or deployment success is claimed by this document.

## Existing import path
.github/workflows/beehiiv-articles.yml invokes scripts/import-beehiiv.py. The existing schedule remains minute 17 of every hour (UTC cron). A manual workflow_dispatch is also available. Changes to this document trigger that same workflow; no second importer or scheduler is introduced.

The workflow reads BEEHIIV_API_KEY from GitHub Actions secrets. Never put its value in source, documentation, reports, or logs. Credential validity has not been established merely by reading the workflow.

The importer paginates the Beehiiv API and selects confirmed, free-audience, non-hidden posts intended for web or both channels, with a past numeric publish date, valid slug, and nonempty public web body. It sanitizes imported HTML, retains original historical wording, preserves source links and available thumbnails, and localizes links among imported issues. It does not invent missing images. It writes a replacement public snapshot atomically only after preparing eligible articles. Failures or an empty eligible result leave the previous archive unchanged. Previously archived records absent from a successful new source snapshot are not automatically retained; review source removals before claiming permanent historical retention.

## Catalog handoff
The existing media-catalog-sync.yml workflow runs at minute 37 each hour. scripts/merge-newsletter-catalog.py consumes data/newsletters.json after source collection, maps issues to beehiiv:<post-id>, and creates review-only draft briefs. It requires a non-null timezone-aware imported_at. The currently recovered null-timestamp archive cannot satisfy that requirement until a successful import.

Cached archive availability must not mask a broken live RSS source. Archive import timestamps are not new publication times. Catalog import does not authorize social posting, email sending, or reuse without freshness, rights, and factual review.

## Verification
1. Identify the Beehiiv public-article workflow run associated with this commit.
2. Confirm the importer step succeeds; record returned eligible count and archive imported_at.
3. Review any gap between 47 published records observed during discovery and eligible imported articles. Do not fill missing bodies with invented text.
4. Confirm unique issue IDs and slugs, nonempty HTML, source URLs, and historical dates.
5. Confirm the generated archive commit and exact-revision Pages build.
6. Confirm deployed data/newsletters.json matches the repository snapshot.
7. Confirm the subsequent catalog merge and review-only briefs.
8. Separately browser-test archive search, individual issue rendering, images, navigation, and signup. HTTP success alone does not prove those interactions.

## Failure handling and rollback
- Missing/invalid API key: fix only through the private secret store; do not replace the archive with placeholders.
- Missing public body, API failure, or pagination error: preserve the prior archive and investigate.
- Concurrent Git writers: reconcile commits; do not force-push.
- Build timeout or uncertain deployment: check the existing run and exact deployed revision before requesting another build.
- Bad imported content: review and restore the last verified archive commit through an approved change.
- Documentation changes trigger an import attempt, not a guarantee of completion.

## Authorization boundaries
This workflow imports public history to the website. It does not send newsletters, schedule Beehiiv posts, publish drafts, import subscriber information, expose paywalled content, or modify newsletter editorial policy. Historical Tuesday drafting and send-approval instructions must be reconciled against current authorizations before any future publishing change.
