# Browser209 security v2

Source-only, additive package. NOT installed, deployed, or activated.
The api(operation,jsonb) interface replaces the earlier draft's separate function names.
Existing browser_209 jobs, worker, installer, profiles and schedules remain unchanged.
Do not dispatch a publication into both queues.

Includes account ACL/group checks, read RLS, immutable jobs, proposer/approver separation,
payload and approval-envelope SHA-256, lifecycle validation, atomic account/job claims,
30-second token/generation leases, cancellation, completion, independent reconciliation
and append-only event/evidence references. The worker defaults disabled, enforces
sslmode=verify-full, verifies exact payload bytes, reuses the existing private account
configuration/profile locks, uses sandboxed Chromium, heartbeats every five seconds
and before actions, and never blindly retries.

Final candidate: Python compilation and 11 mock-only tests passed. These tests block
socket creation, DNS, connections and subprocess launching after creating local event
loops. Run: python test_secure_worker.py. This supersedes the preceding candidate's
15-test count. PostgreSQL/RLS/concurrency/browser/platform behavior was NOT tested.
The build environment has no PostgreSQL server/client/container runtime or psycopg.

authorization_valid(j) deliberately returns false. Replace ONLY after inspecting the
actual authoritative ledger: validate identity, account/action/digest, expiry,
revocation, caps, quiet hours and route ownership. Never use constant true in production.
Provision distinct scoped LOGIN identities and ACLs; accounts default disabled.
Never grant runtime users owner membership, shared service-role access, or approval
plus execution capabilities. session_user requires dedicated DB identities, not a
shared PostgREST login. The old installer does not install this new directory.

Runtime is opt-in: BROWSER_V2_EXECUTION_ENABLED=1 plus scoped BROWSER_V2_DATABASE_URL
with sslmode=verify-full, existing private account/state configuration and a reviewed
ledger adapter. No migration, timer change or execution is authorized by this commit.

Every execution blocks its account until independent reconciliation records a
disposition and confirms the prior executor stopped. Lease expiry is not process
death. Tokens fence DB writes, not third-party clicks. Unresolved outcomes remain
blocked. This is not yet an unattended publishing rollout. Evidence references are
not independently verified platform receipts.

Before rollout run real PostgreSQL tests for role isolation, concurrent claims, stale
generations, cancellation, self-approval, digest vectors, expiry, crashes and recovery.
Review all actual grants, policies, ledger schema and backups. Migration is one-time
and fails on role/schema collisions rather than silently modifying existing objects.
Rollback: stop consumption, revoke v2 login, disable accounts, preserve all evidence,
reconcile external effects before reusing another route. No DROP/CASCADE cleanup.
A source rollback cannot undo an external action. Keep credentials, payloads, profiles
and claim tokens out of logs and shared Drive.
