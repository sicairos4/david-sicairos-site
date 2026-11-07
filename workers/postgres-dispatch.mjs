// Server-only. Inject a PostgreSQL pool with query(sql, parameters) and real platform adapters.
// No AI calls, embedded credentials, automatic startup, or approval creation.
export function createPostgresDispatcher({ db, adapters }) {
  if (typeof db?.query !== 'function') throw new Error('POSTGRES_CLIENT_REQUIRED');
  const transition = async (id, token, state, receipt = null, reason = null) => {
    const result = await db.query('SELECT ai_coordination.transition_dispatch($1,$2::uuid,$3,$4::jsonb,$5) AS result', [id, token, state, receipt === null ? null : JSON.stringify(receipt), reason]);
    return result.rows[0].result;
  };
  async function dispatchOne(jobId) {
    if (typeof jobId !== 'string' || !jobId.trim()) throw new Error('JOB_ID_REQUIRED');
    const claimed = await db.query('SELECT ai_coordination.claim_dispatch($1) AS result', [jobId]);
    const claim = claimed.rows[0]?.result;
    if (claim?.status !== 'claimed') return { jobId, status: claim?.status ?? 'not_claimed' };
    const job = { id: claim.job_id, platform: claim.platform, accountId: claim.account_id, idempotencyKey: claim.idempotency_key, scheduledAt: claim.scheduled_at, expiresAt: claim.expires_at, payload: claim.payload, authorization: { status: 'approved', reference: claim.approval_reference } };
    let submitted = false;
    try {
      const adapter = adapters?.[job.platform];
      if (typeof adapter?.preflight !== 'function' || typeof adapter?.publish !== 'function') throw new Error('PLATFORM_ADAPTER_NOT_CONFIGURED');
      await adapter.preflight(structuredClone(job));
      await transition(job.id, claim.token, 'submitted');
      submitted = true;
      const receipt = await adapter.publish(structuredClone(job), { idempotencyKey: job.idempotencyKey });
      await transition(job.id, claim.token, 'platform_accepted', receipt);
      return { jobId: job.id, status: 'platform_accepted', receipt };
    } catch {
      const status = submitted ? 'uncertain' : 'failed';
      try {
        await transition(job.id, claim.token, status, null, submitted ? 'Submission or receipt persistence failed; reconcile before retry.' : 'Preflight or submission-intent persistence failed; inspect before retry.');
      } catch {
        return { jobId: job.id, status: 'persistence_uncertain', automaticRetryAllowed: false };
      }
      return { jobId: job.id, status, automaticRetryAllowed: false };
    }
  }
  async function dispatchDue({ limit = 10 } = {}) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error('LIMIT_MUST_BE_1_TO_100');
    const due = await db.query(`SELECT a.job_id, a.platform FROM ai_coordination.dispatch_authorizations a JOIN ai_coordination.workspaces w ON w.slug=a.workspace_slug WHERE w.enabled=true AND a.approved_at IS NOT NULL AND a.revoked_at IS NULL AND a.scheduled_at<=now() AND a.expires_at>now() AND NOT EXISTS (SELECT 1 FROM ai_coordination.dispatch_executions e WHERE e.job_id=a.job_id) ORDER BY a.scheduled_at,a.job_id LIMIT $1`, [limit]);
    const runnable = due.rows.filter(row => typeof adapters?.[row.platform]?.preflight === 'function' && typeof adapters?.[row.platform]?.publish === 'function');
    const results = await Promise.allSettled(runnable.map(row => dispatchOne(row.job_id)));
    return { inspected: due.rows.length, attempted: runnable.length, skippedUnconfigured: due.rows.length - runnable.length, results: results.map((result, index) => result.status === 'fulfilled' ? result.value : { jobId: runnable[index].job_id, status: 'worker_error', automaticRetryAllowed: false }) };
  }
  return { dispatchOne, dispatchDue };
}
