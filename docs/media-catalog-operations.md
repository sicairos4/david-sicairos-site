# Integrated media catalog

The collector reads public YouTube, outgoing Beehiiv RSS, and Spotify show episode records. The page is media-catalog.html. It links to the existing library and multimedia pages. No existing publisher, token or queue is replaced.

## Configuration
Set Actions secrets SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET using an authorized Spotify app. Existing chat connector credentials are not transferred. Without them Spotify is blocked and prior data is retained. Set repository variable BEEHIIV_PUBLIC_RSS_URL to the real outgoing publication feed if RSS discovery fails. No feed endpoint is guessed.

## Execution
The workflow runs hourly at minute 37, manually, or on authenticated repository_dispatch type media-catalog-refresh. No tests are added or run by this workflow. Existing repository workflows may run on the source commit. GitHub scheduling is not an exact-time publication guarantee.

The workflow commits only catalog and brief files, then requests the existing main/root legacy Pages build because GITHUB_TOKEN commits do not ordinarily trigger another Actions workflow. It does not change Pages settings or DNS, nor claim build acceptance from a request receipt.

## Data and status
Stable source IDs merge records. Source failures preserve prior items and last successful collection time. YouTube and RSS are windows, not full inventories. Missing items are not automatically deleted. The UI labels sources stale after three hours. Source-publication observations are not evidence of original Muse worker health.

Spotify's US public API catalog is separate from Creator upload/draft/processing state. Eight uploads is the owner's report, not a verified catalog count. Reconcile states and show identity before claiming missing episodes. No fictional episode records are seeded.

Draft briefs require editorial review and are not completed audio/video generation, publishing approval, or automatic social posts. Full repurposing and the original Muse engine repair remain separate live-runtime work.

## Webhooks
repository_dispatch is an authenticated refresh signal, not a generic public webhook receiver. Real source webhooks require supported events, signed deliveries, deduplication, a bounded receiver and restricted dispatch credentials. No unauthenticated remote-command endpoint is installed.

## Rollback
Disable only media-catalog-sync.yml to stop these collectors. Restore data from Git history if needed. Removing these added files rolls back this feature without altering original publishing schedules.
