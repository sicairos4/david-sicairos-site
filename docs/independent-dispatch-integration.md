# AI-independent dispatch integration

Status: source-code component only. No adapters, worker process, schedules, secrets, or platform publications are activated by this commit. This module is not yet wired into the existing BullMQ worker.

## Execution boundary
Muse, Gemini, and Perplexity may propose content. The dispatch execution path does not invoke them. A ready job must carry a previously approved authorization reference, platform, accountId, scheduledAt, expiresAt, and stable idempotencyKey. The server must validate authorization against its own approval records; caller-supplied approval text is not sufficient. Preserve all applicable platform permissions and action-approval requirements.

## Persistent-store contract
Implement claim, markSubmitted, complete, fail, and markUncertain against the authoritative database. claim must atomically enforce uniqueness and prevent concurrent or repeated submissions for the same account/platform/idempotency key. Return a claim token only to the winning worker. All transitions must require that token and the expected previous state. Do not allow caller-controlled strings to bypass the state machine.

markSubmitted must durably record submission intent before any platform call. Never automatically requeue submitted or uncertain records when a worker lease expires. A process crash after submission intent may have occurred before or after the external side effect; reconciliation is required. Restrict the store to server-side access and workspace-scoped identities. Do not distribute the database service-role key to AI agents.

## Platform-adapter contract
Each adapter implements preflight(job) and publish(job, options). preflight validates platform/account authorization, credentials, assets, and platform requirements without publishing. publish uses the provider's supported API and its idempotency facility when available. Its receipt must contain postId, accountId, and platform. Never return invented identifiers. Credentials stay in server-side secret storage.

A receipt means platform acceptance, not independent public-visibility verification. Add a separate reconciliation/verification process. Do not republish merely because a visibility check is delayed.

## Runtime integration still required
1. Connect the actual persistent store and platform adapters.
2. Invoke this handler from an existing supervised worker for due jobs.
3. Keep failures isolated by platform.
4. Configure timezone-aware scheduling and independent worker restart/heartbeat monitoring.
5. Reconcile uncertain submissions before any retry.
6. Preserve expiration checks during queue shortages.
7. Confirm configured routes and authorization before enabling execution.

The inspected workers/bullmq-setup.js still contains empty adapter functions and sibling dispatch/verify/log jobs. workers/cron-scheduler.js still contains placeholder task implementations. This addition does not fix or activate those files by itself. No live publication or production-readiness claim is made.
