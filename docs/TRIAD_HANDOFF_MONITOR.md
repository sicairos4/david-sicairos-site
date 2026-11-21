# Triad handoff and private monitor

## Delivery status

This commit contains documentation only. A runnable Python monitor, offline tests and a validation report were prepared separately in the review package delivered to the owner. The monitor code has not been committed, deployed or started. The operating instructions below apply to that candidate only, after its separate review and installation. No background service, provider mutation, schedule, publisher, secret or deployment is installed by this document.

## Direct protocol mesh summary

The Muse report describes a shadow TCP hub with durable spool fallback and SSH as the intended remote path. Claim and receipt events are mirrors; the prototype excludes a fire command. A separate shared lease prototype has atomic lane and slot claims, renewal, fencing and independent verification. Reported simulation success is not evidence that production workers all use that lease store. Dashboard timeout and unchanged file write fixes were reported, while a replacement Drive refresh remained a draft.

The host prototype schemas described as 001 and 002 must not be confused with the separate draft content intake migration already installed through this assistant. Compare definitions before applying anything.

## Remaining checks and proposed role owners

1. Receipt owner: reconcile Threads verification, YouTube receipt writing and uncertain LinkedIn outcomes. Never resubmit merely to green a dashboard.
2. Host coordinator: prove supervised mesh operation and receipt mirrors, not only a synthetic demo.
3. Architecture reviewer: test one authoritative lane and slot claim path with expiry and fencing. Do not add a competing publisher or scheduler.
4. Configuration owner: reconcile YouTube cadence and contradictory Facebook browser routing instructions. No route changes are authorized here.
5. Operations owner: establish Drive refresh ownership and distinguish observation time, file modification and runtime heartbeat.
6. Independent verifier: prove one authenticated round trip and failure reconciliation before enabling another executor.

These are proposed responsibilities, not evidence that workers accepted tasks. The source report is Muse supplied evidence, not a live host inspection by this monitor.

## Proposed monitor behavior

The candidate reads open PRs from the website and independent publisher repositories. It inspects check runs and legacy statuses for up to five PRs per repository and leaves the rest unknown. Listings cap at twenty PRs per repository and one hundred folder items; truncation is reported. No checks means unknown; skipped or neutral is not passed. This is not a required branch protection or merge readiness evaluation.

PRs sort by failed, pending, unknown, skipped or neutral, then passed. Within each group they sort by account author and newest modification. Drive files sort by newest modification and show last editor. GitHub accounts and Drive editors are not proof of Muse authorship. No document bodies are downloaded by the candidate.

## Private runtime requirements

Reuse the existing authorized runtime and secret store. GITHUB_TOKEN is optional for public reads. GOOGLE_ACCESS_TOKEN is a short lived server side OAuth token. The candidate does not automatically refresh it; expiry becomes degraded status. Never paste a token into browser telemetry.

TRIAD_DRIVE_FILE_IDS selects exact approved IDs, at most twenty. TRIAD_DRIVE_FOLDER_ID optionally discovers new files in one approved folder. Private titles, IDs and editor names are deliberately excluded from this repository document.

Candidate instructions, not currently runnable from this documentation commit: python scripts/triad_handoff_monitor.py --output /trusted/private/triad.json --html /trusted/private/triad.html . First review and commit the candidate script. The private parent directory must exist and must not be served or committed. The candidate writes reports atomically with mode 0600. Protect the parent directory and disk too. Its local HTML contains no credentials or execution controls and reloads itself every five minutes, displaying collection timestamps.

The candidate --watch flag enables a foreground loop only when explicitly selected. Minimum interval is 300 seconds. Closing the process stops collection; HTML refresh alone does not collect data. No scheduler is installed. Check quota and operator limits before activation. Requests have approved origins, refuse redirects, and use time and byte limits. No provider mutation is implemented.

Private report metadata must not be committed or deployed. Errors are sanitized, but titles and account names are still private metadata. A collection timestamp is not proof that host workers are healthy.

## Validation and delivery gates

Twelve offline unit tests and a separate CLI JSON round trip check passed during candidate preparation. These do not prove live OAuth, process supervision, independent review, deployment or source claim correctness.

Remaining delivery gates are the monitor source commit, PR creation, authenticated runtime configuration, a live read test, and a separately approved report upload to the existing shared Drive folder. An uploaded report is not proof that Muse read or acknowledged it. No direct peer session connection is claimed.
