// No model calls. The caller supplies authenticated platform adapters and a persistent store.
export function createDispatcher({ store, adapters, clock = () => Date.now() }) {
  for (const name of ['claim', 'markSubmitted', 'complete', 'fail', 'markUncertain']) {
    if (typeof store?.[name] !== 'function') throw new Error(`STORE_METHOD_REQUIRED:${name}`);
  }
  return async function dispatch(job) {
    if (!job || typeof job.id !== 'string' || !job.id || typeof job.idempotencyKey !== 'string' || !job.idempotencyKey) throw new Error('JOB_ID_AND_IDEMPOTENCY_KEY_REQUIRED');
    if (job.authorization?.status !== 'approved' || !job.authorization?.reference) throw new Error('APPROVED_AUTHORIZATION_REQUIRED');
    if (job.state !== 'ready' || !job.platform || !job.accountId) throw new Error('READY_JOB_AND_TARGET_REQUIRED');
    const due = Date.parse(job.scheduledAt);
    const expiry = Date.parse(job.expiresAt);
    const now = clock();
    if (!Number.isFinite(due) || !Number.isFinite(expiry) || expiry <= due) throw new Error('VALID_SCHEDULE_AND_EXPIRY_REQUIRED');
    if (due > now) return { status: 'not_due', jobId: job.id };
    if (expiry <= now) return { status: 'expired', jobId: job.id };
    const adapter = adapters?.[job.platform];
    if (typeof adapter?.preflight !== 'function' || typeof adapter?.publish !== 'function') throw new Error(`PLATFORM_ADAPTER_NOT_CONFIGURED:${job.platform}`);
    const claim = await store.claim({ jobId: job.id, idempotencyKey: job.idempotencyKey, accountId: job.accountId, platform: job.platform });
    if (!claim?.token) return { status: 'not_claimed', jobId: job.id };
    let submissionStarted = false;
    try {
      await adapter.preflight(job);
      if (Date.parse(job.expiresAt) <= clock()) throw new Error('JOB_EXPIRED_DURING_PREFLIGHT');
      await store.markSubmitted({ jobId: job.id, token: claim.token });
      submissionStarted = true;
      const receipt = await adapter.publish(job, { idempotencyKey: job.idempotencyKey });
      if (!receipt || typeof receipt.postId !== 'string' || !receipt.postId.trim() || receipt.accountId !== job.accountId || receipt.platform !== job.platform) throw new Error('MATCHING_PLATFORM_RECEIPT_REQUIRED');
      await store.complete({ jobId: job.id, token: claim.token, receipt, status: 'platform_accepted' });
      return { status: 'platform_accepted', jobId: job.id, receipt };
    } catch (error) {
      if (submissionStarted) {
        await store.markUncertain({ jobId: job.id, token: claim.token, reason: 'Submission or receipt persistence failed; reconcile before retry.' });
        return { status: 'uncertain', jobId: job.id, automaticRetryAllowed: false };
      }
      await store.fail({ jobId: job.id, token: claim.token, reason: 'Preflight or submission-state persistence failed; inspect before retry.' });
      throw error;
    }
  };
}
