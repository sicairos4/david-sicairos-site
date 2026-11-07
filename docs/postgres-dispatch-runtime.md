# PostgreSQL dispatch runtime

Implementation status: this module connects to the installed private ledger using an injected server-side PostgreSQL client. It does not start a process or enable a schedule. No platform adapters are included. No live publishing or production-readiness claim is made. Existing BullMQ and cron placeholder files remain unchanged.

## Wiring
Import createPostgresDispatcher from workers/postgres-dispatch.mjs. Supply a backend database client authorized to SELECT the authorization, execution, and workspace tables and EXECUTE claim_dispatch and transition_dispatch. Supply an explicit map of authorized platform adapters. Invoke dispatchDue from a supervised scheduled runtime. Do not run it from browser code, expose database credentials, or distribute a service-role key to AI agents.

Jobs are loaded from dispatch_authorizations. Caller-supplied content is never accepted by dispatchOne; it accepts only a job ID. The canonical payload and target come from the atomic database claim. Approval creation, revocation, and any payload changes must be restricted to trusted server-side workflows. Authorizations must be immutable while claimed or submitted; no automatic authorization-ingress endpoint is implemented here.

Adapters receive a job object with payload, platform, accountId, idempotencyKey, scheduledAt, expiresAt, and authorization reference. preflight must check assets, account authorization, and credentials without publishing. publish must return a genuine receipt with postId, accountId, and platform. The ledger validates receipt fields before acceptance. Each adapter must enforce network timeouts and respect provider rate limits. No generic adapter endpoint or credential has been invented.

Only enabled workspaces with approved, due, unexpired records are considered. Existing workspace switches remain disabled. Unknown platform adapters are skipped without claiming their jobs. Independent ready jobs are processed through Promise.allSettled so a rejected promise does not cancel other attempts. An adapter that never settles still requires runtime timeout handling; this module alone does not guarantee timing isolation.

The database refuses duplicate claims. The runtime does not automatically retry failed, submitted, or uncertain records. A network error after submission may mean a post exists. Reconcile before any retry. A stale claim is not proof no post was sent. Store platform receipts separately from public-visibility verification.

Remaining deployment work: platform adapters, secure credentials, a supervised runtime, scheduler registration, timeouts, reconciliation, role-scoped authorization ingress, immutable-authorization enforcement, and the outstanding existing-table security review. No paid upgrade or background AI connection is activated by this commit.
