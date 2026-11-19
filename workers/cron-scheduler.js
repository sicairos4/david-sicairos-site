/**
 * Muse Automation Package — Cron Scheduler with Real Heartbeat, Queue Guards & Verification Sweep
 * Repo: sicairos4/david-sicairos-site
 * Timezone: America/Los_Angeles (PT)
 */

import cron from 'node-cron';
import fs from 'fs/promises';
import path from 'path';

const DATA_DIR = path.resolve(process.env.DATA_DIR || '../data');
const TZ = 'America/Los_Angeles';
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://uwidjnnhdgtrpsymuhwp.supabase.co';
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const WORKER_BASE_URL = process.env.CF_209_WORKER_URL || '';
const ZAPIER_WEBHOOK_SECRET = process.env.ZAPIER_WEBHOOK_SECRET || '';

const readJSON = async (file) =>
  JSON.parse(await fs.readFile(path.join(DATA_DIR, file), 'utf8'));

const writeJSON = async (file, data) =>
  fs.writeFile(path.join(DATA_DIR, file), JSON.stringify(data, null, 2));

const nowPT = () =>
  new Date(new Date().toLocaleString('en-US', { timeZone: TZ }));

const ptTime = () =>
  nowPT().toTimeString().slice(0, 5);

function supabaseHeaders(prefer) {
  const headers = {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    'Content-Type': 'application/json',
    'Accept-Profile': 'publishing_209',
    'Content-Profile': 'publishing_209',
  };
  if (prefer) headers.Prefer = prefer;
  return headers;
}

/**
 * Emits a durable heartbeat into data/site-config.json (museStatus),
 * data/muse-status.json, and publishing_209.ai_tasks in Supabase.
 */
async function writeHeartbeat({ state, lastRun, nextAction, detail }) {
  const stamp = lastRun || new Date().toISOString();
  const statusPayload = {
    state,
    lastRun: stamp,
    nextAction,
    detail: detail || null,
    updatedAtPT: nowPT().toISOString(),
  };

  try {
    const siteConfig = await readJSON('site-config.json');
    siteConfig.museStatus = {
      state,
      lastRun: stamp,
      nextAction,
    };
    await writeJSON('site-config.json', siteConfig);
  } catch (err) {
    console.error('[heartbeat] site-config.json update failed:', err.message);
  }

  try {
    await writeJSON('muse-status.json', statusPayload);
  } catch (err) {
    console.error('[heartbeat] muse-status.json update failed:', err.message);
  }

  if (SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY) {
    try {
      const taskRecord = {
        task_id: '00000000-0000-4000-8000-000000000209',
        content_id: 'muse_cadence_heartbeat',
        owner_agent: 'muse_dispatcher',
        vertical: 'personal_apex',
        status: state === 'Degraded' ? 'degraded' : 'in_progress',
        updated_at: stamp,
        output_payload: statusPayload,
      };
      const res = await fetch(`${SUPABASE_URL}/rest/v1/ai_tasks?on_conflict=task_id`, {
        method: 'POST',
        headers: supabaseHeaders('resolution=merge-duplicates,return=minimal'),
        body: JSON.stringify(taskRecord),
      });
      if (!res.ok) {
        console.error('[heartbeat] Supabase ai_tasks write failed:', res.status, await res.text());
      }
    } catch (err) {
      console.error('[heartbeat] Supabase ai_tasks error:', err.message);
    }
  }
}

// ─── 1. ADAPTIVE DIGEST ─────────────────────────────────────────────
async function runDigest(reason) {
  const signals = await readJSON('signals.json');
  const incidents = await readJSON('incidents.json');
  const decisions = await readJSON('decisions.json');

  const newDirectives = await interpretSignals(signals, incidents);

  decisions.directives.push(...newDirectives);
  decisions.updated_at = new Date().toISOString();
  await writeJSON('decisions.json', decisions);

  const digest = await readJSON('digest.json');
  digest.last_digest = new Date().toISOString();
  digest.next_digest = computeNextDigest(digest, incidents);
  digest.next_digest_reason = reason;
  await writeJSON('digest.json', digest);

  await writeHeartbeat({
    state: 'Active',
    lastRun: digest.last_digest,
    nextAction: `Next digest at ${digest.next_digest} (${reason})`,
    detail: `Generated ${newDirectives.length} directives`,
  });

  console.log(`[digest] ran (${reason}) — ${newDirectives.length} directives`);
}

function computeNextDigest(digest, incidents) {
  const hasFastTrigger = incidents.some(i =>
    digest.fast_triggers.includes(i.status === 'OPEN' ? 'open_incident' : '') ||
    (i.severity === 'HIGH' && i.status !== 'RESOLVED')
  );
  const intervalMin = hasFastTrigger ? digest.fast_interval_min : digest.base_interval_min;
  const next = new Date(Date.now() + intervalMin * 60000);

  for (const t of digest.best_times) {
    const [h, m] = t.split(':').map(Number);
    const candidate = new Date(nowPT());
    candidate.setHours(h, m, 0, 0);
    if (candidate > nowPT() && candidate < next) {
      next.setTime(candidate.getTime());
    }
  }
  return next.toISOString();
}

cron.schedule('*/5 * * * *', async () => {
  try {
    const digest = await readJSON('digest.json');
    const t = ptTime();
    const isBestTime = digest.best_times.includes(t);
    const intervalElapsed = digest.last_digest &&
      (Date.now() - new Date(digest.last_digest)) >=
      (digest.fast_triggers.length ? digest.fast_interval_min : digest.base_interval_min) * 60000;

    if (isBestTime || intervalElapsed || !digest.last_digest) {
      await runDigest(isBestTime ? `Best time ${t} PT` : 'Interval elapsed');
    }
  } catch (e) {
    console.error('[digest] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 2. CADENCE GUARD ────────────────────────────────────────────────
cron.schedule('*/15 * * * *', async () => {
  try {
    const report = await readJSON('muse-morning.json');
    const incidents = await readJSON('incidents.json');
    const MAX_GAP = 45;
    let breached = false;

    for (const lane of report.lanes || []) {
      if (lane.longest_gap_min > MAX_GAP) {
        breached = true;
        const exists = incidents.some(i =>
          i.title.includes(lane.lane) && i.status !== 'RESOLVED' &&
          i.cause.includes('Cadence breach'));
        if (!exists) {
          incidents.push({
            date: new Date().toISOString().slice(0, 10),
            title: `Cadence breach — ${lane.lane}`,
            severity: 'HIGH',
            cause: `Cadence breach — longest gap ${lane.longest_gap_min}m exceeded ${MAX_GAP}m max`,
            fix: 'Prioritized in next dispatch cycle',
            status: 'OPEN'
          });
          await prioritizeLane(lane.lane);
        }
      }
    }
    await writeJSON('incidents.json', incidents);
    await writeHeartbeat({
      state: breached ? 'Degraded' : 'Active',
      nextAction: breached ? 'Cadence breach detected; priority lane bumped' : '30m cadence nominal',
    });
  } catch (e) {
    console.error('[cadence-guard] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 3. QUEUE BUFFER GUARD ───────────────────────────────────────────
cron.schedule('*/15 * * * *', async () => {
  try {
    const report = await readJSON('muse-morning.json');
    const incidents = await readJSON('incidents.json');
    const MIN_BUFFER = 50;

    for (const lane of report.lanes || []) {
      if (lane.staged < MIN_BUFFER) {
        const exists = incidents.some(i =>
          i.title.includes(lane.lane) && i.status !== 'RESOLVED' &&
          i.cause.includes('Queue starvation'));
        if (!exists) {
          incidents.push({
            date: new Date().toISOString().slice(0, 10),
            title: `Queue starvation — ${lane.lane}`,
            severity: 'HIGH',
            cause: `Queue starvation — only ${lane.staged} staged (min ${MIN_BUFFER})`,
            fix: 'Paused expiry sweeps for this lane; flagged for refill',
            status: 'OPEN'
          });
          await pauseExpirySweeps(lane.lane);
        }
      }
    }
    await writeJSON('incidents.json', incidents);
  } catch (e) {
    console.error('[buffer-guard] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 4. VERIFICATION SWEEP ───────────────────────────────────────────
cron.schedule('*/5 * * * *', async () => {
  try {
    await sweepUnverifiedDispatches();
  } catch (e) {
    console.error('[verify-sweep] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 5. MORNING REPORT ────────────────────────────────────────────────
cron.schedule('30 5 * * *', async () => {
  try {
    await generateMorningReport();
    await writeHeartbeat({
      state: 'Active',
      nextAction: 'Morning report generated; 30m dispatch running',
    });
    console.log('[morning-report] generated');
  } catch (e) {
    console.error('[morning-report] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 6. WEEKLY REFRESH ────────────────────────────────────────────────
cron.schedule('0 18 * * 0', async () => {
  try {
    const decisions = await readJSON('decisions.json');
    const experiments = await readJSON('experiments.json');
    await weeklyRefresh(decisions, experiments);
    console.log('[weekly-refresh] directives updated');
  } catch (e) {
    console.error('[weekly-refresh] failed:', e.message);
  }
}, { timezone: TZ });

// ─── LIVE QUEUE, SUPABASE & REPAIR IMPLEMENTATIONS ───────────────────
async function interpretSignals(signals, incidents) {
  const list = Array.isArray(signals) ? signals : (signals.signals || []);
  const openHigh = (incidents || []).filter(i => i.severity === 'HIGH' && i.status !== 'RESOLVED');
  if (!list.length && !openHigh.length) return [];
  return [{
    type: 'CADENCE_DIRECTIVE',
    created_at: new Date().toISOString(),
    signal_count: list.length,
    open_high_incidents: openHigh.length,
    action: openHigh.length > 0 ? 'Prioritize degraded lanes and trigger repair sweep' : 'Maintain 30 minute cadence and zero dash check',
  }];
}

async function prioritizeLane(lane) {
  try {
    const pipeline = await readJSON('pipeline.json');
    pipeline.priority_lanes = Array.from(new Set([lane, ...(pipeline.priority_lanes || [])]));
    pipeline.updated_at = new Date().toISOString();
    await writeJSON('pipeline.json', pipeline);
  } catch {
    // Ignore if pipeline.json is not present in custom DATA_DIR
  }
}

async function pauseExpirySweeps(lane) {
  try {
    const pipeline = await readJSON('pipeline.json');
    pipeline.paused_expiry_lanes = Array.from(new Set([lane, ...(pipeline.paused_expiry_lanes || [])]));
    pipeline.updated_at = new Date().toISOString();
    await writeJSON('pipeline.json', pipeline);
  } catch {
    // Ignore if pipeline.json is not present in custom DATA_DIR
  }
}

async function sweepUnverifiedDispatches() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return;
  const tenMinAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const url = new URL(`${SUPABASE_URL}/rest/v1/ai_tasks`);
  url.searchParams.set('status', 'eq.in_progress');
  url.searchParams.set('updated_at', `lt.${tenMinAgo}`);

  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: supabaseHeaders(),
  });
  if (!res.ok) return;

  const staleTasks = await res.json();
  for (const task of staleTasks || []) {
    await fetch(`${SUPABASE_URL}/rest/v1/ai_tasks?task_id=eq.${encodeURIComponent(task.task_id)}`, {
      method: 'PATCH',
      headers: supabaseHeaders('return=minimal'),
      body: JSON.stringify({
        status: 'degraded',
        owner_agent: 'diagnostic_sentinel',
        updated_at: new Date().toISOString(),
      }),
    });

    if (WORKER_BASE_URL && ZAPIER_WEBHOOK_SECRET && task.output_payload?.surface === 'threads') {
      await fetch(`${WORKER_BASE_URL.replace(/\/$/, '')}/repair/threads`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${ZAPIER_WEBHOOK_SECRET}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task_id: task.task_id }),
      });
    }
  }
}

async function generateMorningReport() {
  const report = await readJSON('muse-morning.json');
  report.generated_at = new Date().toISOString();
  report.timezone = TZ;
  await writeJSON('muse-morning.json', report);
}

async function weeklyRefresh(decisions, experiments) {
  decisions.last_weekly_refresh = new Date().toISOString();
  decisions.experiment_count = Array.isArray(experiments) ? experiments.length : 0;
  await writeJSON('decisions.json', decisions);
}

console.log('[cron-scheduler] all 6 automations scheduled (TZ: ' + TZ + ')');
