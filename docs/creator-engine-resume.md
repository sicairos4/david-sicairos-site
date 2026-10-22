# Creator Engine local checkpoints and pause controls

Source-only implementation. No tests or execution were performed.

## Opt in

Supply both `--state-dir` and `--run-key` to the existing main runner. The state directory must already exist in trusted private storage, preferably outside the repository. It contains research and generated text, not API keys. The owner must manage permissions, retention, backup, and deletion.

The run identity hashes the supplied freshness key, research and generation settings, draft digest, and source/prompt fingerprints. Identical settings and source reuse completed stage files. Change the run key deliberately for fresh research, even when the query is unchanged. Cached research is not automatically refreshed by date. A source or prompt change creates a different run identity.

## Resume

Reinvoke with the same settings, source, state directory, and run key, and a new output filename. Research is checkpointed before generation. Completed generation is also checkpointed. A failure during payload assembly or final output writing therefore need not repeat saved provider stages. Configured generation credentials are still required when generation is requested, even when its checkpoint exists. Missing stages are executed on explicit invocation.

## Lock and pause

A per-run exclusive `RUNNING` file prevents concurrent use of the same identity in the same state directory. Normal completion or handled failure releases the lock. A killed process can leave a stale lock. Do not remove a lock until the owner establishes no process is using it. The runner never automatically breaks locks.

Create a file named `PAUSED` in the state root to pause all identities there, or inside one run directory to pause that identity. Pause is checked at run entry, before each stage, and before final output. It does not cancel an in-flight provider request. Remove the pause file deliberately to permit execution again.

## Limits

This is local stage reuse and concurrency protection, not provider-side idempotency or publication deduplication. A crash after a provider accepts a request but before its response is saved can result in another charge on explicit retry. Checkpoints must not be edited or supplied by untrusted users. The state root must not be shared with untrusted processes. There is no background retry, database write, email, or posting.

The GitHub workflow does not supply a state directory or restore checkpoints. Therefore this commit does not establish cross-workflow-run deduplication or durable Actions state. The earlier operating guide's no-checkpoint limitation applies to non-checkpointed runs; this document describes the new opt-in mode. Live operation remains unestablished.
