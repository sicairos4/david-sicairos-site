// Muse BullMQ worker setup — per-lane dispatch, shared verify/repair, flow-based lifecycle
import { QueuePro, WorkerPro, FlowProducer } from '@taskforcesh/bullmq-pro';
import IORedis from 'ioredis';

const connection = {
  host: process.env.REDIS_HOST,
  port: 6379,
  maxRetriesPerRequest: null,
  enableReadyCheck: true
};

const LANES = {
  ig: 2, 'fb-profile': 2, 'fb-page': 2, tiktok: 1,
  youtube: 2, linkedin: 1, threads: 4, bluesky: 4
};

// One queue per lane, grouped
export const dispatchQueues = Object.fromEntries(
  Object.keys(LANES).map(lane => [
    lane,
    new QueuePro(`dispatch-${lane}`, { connection })
  ])
);

export const verifyQueue = new QueuePro('verify', { connection });
export const repairQueue = new QueuePro('repair', { connection });
export const lifecycleQueue = new QueuePro('lifecycle', { connection });
export const loggingQueue = new QueuePro('logging', { connection });

// Per-lane dispatch workers — isolated processes
export function startDispatchWorkers() {
  return Object.entries(LANES).map(([lane, groupConc]) =>
    new WorkerPro(`dispatch-${lane}`, async job => {
      // 1. pull staged candidate for this lane
      // 2. publish via lane-specific adapter (API or browser)
      // 3. return dispatch receipt (postId, timestamp)
      return await publishToLane(lane, job.data);
    }, {
      connection,
      concurrency: groupConc * 2,
      group: { concurrency: groupConc },
      stalledInterval: 30000,
      maxStalledCount: 2
    })
  );
}

// Shared verify worker — confirms post actually landed
export function startVerifyWorker() {
  return new WorkerPro('verify', async job => {
    const ok = await verifyPostLanded(job.data.lane, job.data.receipt);
    if (!ok) throw new Error(`VERIFY_FAILED:${job.data.lane}:${job.data.postId}`);
    return { verified: true, lane: job.data.lane };
  }, { connection, concurrency: 8 });
}

// Repair worker — 2FA walls, browser recovery, retries
export function startRepairWorker() {
  return new WorkerPro('repair', async job => {
    return await repairLane(job.data.lane, job.data.originalJobId);
  }, {
    connection,
    concurrency: 2,
    limiter: { max: 3, duration: 60000 }
  });
}

// Flow: dispatch → verify → log (parent waits for all)
export async function enqueuePublish(lane, postData) {
  const flowProducer = new FlowProducer({ connection });
  return await flowProducer.add({
    name: 'publish-post',
    queueName: 'lifecycle',
    data: { lane, postId: postData.id },
    children: [
      {
        name: 'dispatch',
        queueName: `dispatch-${lane}`,
        data: { lane, post: postData },
        opts: { group: { id: lane }, groupAffinity: true }
      },
      {
        name: 'verify',
        queueName: 'verify',
        data: { lane, postId: postData.id },
        opts: { failParentOnFailure: true }
      },
      {
        name: 'log-result',
        queueName: 'logging',
        data: { lane, postId: postData.id },
        opts: { continueParentOnFailure: true }
      }
    ]
  });
}

// On recoverable dispatch failure → repair branch, don't fail whole flow
export function wireFailureHandling() {
  Object.entries(dispatchQueues).forEach(([lane, queue]) => {
    queue.on('failed', async (job, err) => {
      if (isRecoverable(err)) {
        await repairQueue.add('repair', {
          lane,
          originalJobId: job.id,
          error: err.message
        }, {
          attempts: 3,
          backoff: { type: 'exponential', delay: 60000 }
        });
      }
    });
  });
}

function isRecoverable(err) {
  return /2FA|browser|timeout|navigation/i.test(err.message);
}

// Placeholder adapters — replace with Muse's real lane implementations
async function publishToLane(lane, data) { /* lane-specific publish */ }
async function verifyPostLanded(lane, receipt) { /* check post exists */ }
async function repairLane(lane, jobId) { /* 2FA / browser recovery */ }