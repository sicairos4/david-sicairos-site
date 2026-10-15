# BullMQ Scaling & Concurrency Architecture — Muse Multi-Lane Publishing

## Goal
Split the single-thread bottleneck (one main-agent thread serving 8 lanes) into isolated per-lane workers with separate dispatch, verification, and repair flows.

## Queue topology

- `dispatch-{lane}` — 8 queues (ig, fb-profile, fb-page, tiktok, youtube, linkedin, threads, bluesky), one worker per lane, BullMQ Pro groups for per-lane FIFO + cross-lane round-robin.
- `verify` — shared queue, high concurrency, independently confirms each post landed (kills false-success).
- `repair` — retries, 2FA walls, browser recovery; exponential backoff.
- `lifecycle` — parent jobs coordinating dispatch → verify → log via FlowProducer.
- `logging` — writes results to analytics/shift/incident logs.

## Concurrency tuning

| Queue | Worker concurrency | Group concurrency | Rationale |
|---|---|---|---|
| dispatch-ig | 2 | 2 | 40m avg gap |
| dispatch-fb-profile | 2 | 2 | 127m gap |
| dispatch-fb-page | 2 | 2 | starvation-prone |
| dispatch-tiktok | 2 | 1 | 221m breach — isolate |
| dispatch-youtube | 2 | 2 | 81m gap |
| dispatch-linkedin | 2 | 1 | 114m breach — isolate |
| dispatch-threads | 4 | 4 | 61 posts, 9m gaps |
| dispatch-bluesky | 4 | 4 | 58 posts, 9.5m gaps |
| verify | 8 | n/a | must keep up with all lanes |
| repair | 2 | n/a | low volume |
| scheduler | 1 | n/a | single decision-maker |

Rule: worker concurrency × instances ≥ peak jobs/min per lane. Group concurrency is global — no lane exceeds its cap regardless of worker count.

## Redis connection pooling

- Each Worker needs `concurrency + 1` connections (1 blocking + N parallel).
- Set `maxRetriesPerRequest: null` on worker connections (required for blocking pickup).
- Budget ~75 connections total: scheduler 2, dispatch ~50, verify ~10, repair ~4, QueueEvents 8.
- Use one shared ioredis connection per process where possible; BullMQ duplicates blocking connections automatically.

## Group sharding (BullMQ Pro)

- `group: { id: lane }` on every dispatch job — FIFO within lane, round-robin across lanes.
- `setGroupConcurrency(lane, n)` for per-lane caps stored in Redis (no redeploy to tune).
- `groupAffinity: true` for batch jobs in the same lane (cache locality).
- Groups guarantee TikTok's slow dispatch never blocks LinkedIn.

## Parent-child flows (FlowProducer)

Per post:

```text
Parent: publish-post
├── dispatch (per-lane queue, grouped)
├── verify (shared queue, runs after dispatch)
└── log-result (logging queue, runs after verify)
```

Parent completes only when all children succeed — verification is structurally required before a post counts as done.

## Failure handling

1. `failParentOnFailure: true` on verify — failed verification fails the whole flow loudly.
2. `continueParentOnFailure: true` on logging — non-critical steps don't block the parent.
3. Repair branch: on recoverable dispatch failure, enqueue repair with exponential backoff (3 attempts, 60s base).
4. Stalled-job detection: `stalledInterval: 30000`, `maxStalledCount: 2` — no more silent cron "success" without execution.
5. Heartbeats: worker liveness key with 60s TTL; missing heartbeat triggers alert.

## Monitoring

- Queue depth per lane > 50 for 5 min → alert.
- Stalled jobs > 0 → alert.
- Failed jobs > 3 per lane per 10 min → alert.
- Group wait time > lane target gap → alert.
- Wire `data/pipeline.json` to real queue depths; wire `data/incidents.json` to repair/verify failures.
