# Workstation shared module-loader finishing

This patch addresses the shared dynamic loader in assets/member-session.js. No tests, live browser sessions, build, database migration or deployment checks were run. A commit is not runtime acceptance.

## Implemented source behavior

Module URLs share a single in-flight promise and declared dependencies retain their existing order. A repeated run request with the same ordered canonical module URLs and same callback function reference shares its promise; completed setup is not repeated for that identity. Distinct callback references remain distinct intentional consumers. Async callbacks are awaited. A callback failure is uncertain because partial side effects may have occurred; the loader offers reload rather than rerunning setup blindly.

Each actual script wait is bounded to 20 seconds after dependency readiness. Browser window load itself remains the existing prerequisite and has no added timeout here. Observed script-network errors permit an explicit retry. Timeout is not cancellation: the browser may still execute that script later, so uncertain module entries are not reinjected in this document. An existing unmarked script has unknown execution history and requires reload instead of waiting forever or re-executing it. This conservative refusal can expose legacy/static loading gaps; coordinating all callers and marking preloaded modules remains further work. Script load acknowledgement does not prove successful module initialization, and runtime exceptions inside a script are not fully diagnosed by this loader.

Recovery notices distinguish retryable network failures from uncertain initialization. Reload has a warning to preserve unsaved work and uses the normal page navigation/unload safeguards. The loader never saves, migrates or deletes account records. Authentication gate, theme, section navigation, module names/dependencies, privacy rules and legal links are preserved.

## Remaining Workstation gaps

This is not complete loading/state-ownership consolidation. The controller and gate still create their existing account clients; shared account/day state and stale-operation locking need separate concrete changes. Remaining work includes caller-wide dependency/callback reconciliation, partial initialization cleanup, state ownership, account export/deletion coverage and specific product-flow gaps. Existing cross-day-move.js already provides transactional RPC integration for unfinished unlinked tasks and guarded reversal; inspect backend activation and linked-task limitations rather than label all cross-day movement absent. No backend installation or task move was performed by this patch.
