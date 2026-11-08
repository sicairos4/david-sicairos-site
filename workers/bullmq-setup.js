import { QueuePro, WorkerPro } from '@taskforcesh/bullmq-pro';

const LANES = { ig: 2, 'fb-profile': 2, 'fb-page': 2, tiktok: 1, youtube: 2, linkedin: 1, threads: 4, bluesky: 4 };
let runtime;
export function configurePublishingRuntime({ connection, adapters, store }) {
  if (runtime) throw new Error('RUNTIME_ALREADY_CONFIGURED');
  if (!connection || !adapters || typeof store?.dispatchOnce !== 'function' || typeof store?.recordVerified !== 'function' || typeof store?.recordUncertain !== 'function') throw new Error('EXPLICIT_CONNECTION_ADAPTERS_AND_DURABLE_STORE_REQUIRED');
  runtime = { connection, adapters, store };
}
function adapterFor(lane) {
  if (!runtime) throw new Error('RUNTIME_NOT_CONFIGURED');
  const adapter = runtime.adapters[lane];
  if (!Object.hasOwn(LANES, lane) || typeof adapter?.preflight !== 'function' || typeof adapter?.publish !== 'function' || typeof adapter?.verify !== 'function') throw new Error('LANE_ADAPTER_NOT_CONFIGURED:' + lane);
  return adapter;
}
export const dispatchQueues = {};
export function startDispatchWorkers() {
  if (!runtime) throw new Error('RUNTIME_NOT_CONFIGURED');
  return Object.entries(LANES).filter(([lane]) => runtime.adapters[lane]).map(([lane, concurrency]) => {
    adapterFor(lane);
    dispatchQueues[lane] = new QueuePro('dispatch-' + lane, { connection: runtime.connection });
    return new WorkerPro('dispatch-' + lane, async job => {
      const adapter = adapterFor(lane);
      const post = job.data.post;
      if (!post?.id || !post.accountId || !post.idempotencyKey || post.authorization?.status !== 'approved' || !post.authorization.reference) throw new Error('APPROVED_JOB_AND_TARGET_REQUIRED');
      const due = Date.parse(post.scheduledAt), expiry = Date.parse(post.expiresAt);
      if (!Number.isFinite(due) || !Number.isFinite(expiry) || due > Date.now() || expiry <= Date.now() || expiry <= due) throw new Error('JOB_NOT_DUE_OR_EXPIRED');
      await adapter.preflight(structuredClone(post));
      if (Date.parse(post.expiresAt) <= Date.now()) throw new Error('JOB_EXPIRED_DURING_PREFLIGHT');
      // Store must atomically claim the approved canonical job, persist submission intent,
      // and never invoke send again for submitted, accepted, or uncertain jobs.
      // It must validate the canonical account, payload, approval, schedule and expiry.
      const receipt = await runtime.store.dispatchOnce({ lane, post: structuredClone(post), send: canonicalPost => adapter.publish(canonicalPost) });
      if (!receipt?.postId || receipt.accountId !== post.accountId || receipt.platform !== post.platform) {
        await runtime.store.recordUncertain({ lane, jobId: post.id, reason: 'Missing or mismatched receipt; reconcile before resend.' });
        throw new Error('MATCHING_RECEIPT_REQUIRED');
      }
      let verification;
      try { verification = await adapter.verify({ post: structuredClone(post), receipt }); }
      catch {
        await runtime.store.recordUncertain({ lane, jobId: post.id, receipt, reason: 'Verification failed; do not resend automatically.' });
        throw new Error('VERIFICATION_UNCERTAIN');
      }
      if (verification?.verified !== true || verification.postId !== receipt.postId || verification.accountId !== post.accountId) {
        await runtime.store.recordUncertain({ lane, jobId: post.id, receipt, reason: 'Public verification not established; do not resend automatically.' });
        throw new Error('PUBLIC_VERIFICATION_REQUIRED');
      }
      await runtime.store.recordVerified({ lane, jobId: post.id, receipt, verification });
      return { verified: true, receipt };
    }, { connection: runtime.connection, concurrency, maxStalledCount: 0 });
  });
}
export async function enqueuePublish(lane, postData) {
  adapterFor(lane);
  if (!postData?.id || !postData.idempotencyKey) throw new Error('JOB_ID_AND_IDEMPOTENCY_KEY_REQUIRED');
  const queue = dispatchQueues[lane] ||= new QueuePro('dispatch-' + lane, { connection: runtime.connection });
  return queue.add('publish-verify-record', { lane, post: postData }, { attempts: 1 });
}
export function startVerifyWorker() { throw new Error('VERIFICATION_RUNS_AFTER_DISPATCH_IN_SAME_JOB'); }
export function startRepairWorker() { throw new Error('REPAIR_REQUIRES_EXPLICIT_RECONCILIATION_NO_AUTOMATIC_RESEND'); }
export function wireFailureHandling() { throw new Error('AUTOMATIC_REPAIR_DISABLED_RECONCILE_UNCERTAIN_POSTS'); }
