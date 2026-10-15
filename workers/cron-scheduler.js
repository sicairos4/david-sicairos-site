/**
 * Muse Automation Package — Cron Scheduler
 * 
 * Runs six automations:
 *   1. Adaptive digest      — reads signals/incidents, writes decisions (adaptive interval)
 *   2. Cadence guard        — every 15 min, checks gap times, breach → priority + incident
 *   3. Queue buffer guard   — every 15 min, checks staged counts, <50 → pause expiry + flag
 *   4. Verification sweep   — every 5 min, catches unverified dispatches → repair queue
 *   5. Morning report       — daily 05:30 PT
 *   6. Weekly refresh       — Sundays 18:00 PT, shifts calendar/CTA mix toward winners
 *
 * Timezone: America/Los_Angeles (PT)
 * 
 * Usage: node workers/cron-scheduler.js
 * Requires: node-cron (npm i node-cron), fs/promises
 * 
 * Replace the TODO placeholders with Muse's real lane implementations.
 */

import cron from 'node-cron';
import fs from 'fs/promises';
import path from 'path';

const DATA_DIR = path.resolve(process.env.DATA_DIR || '../data');
const TZ = 'America/Los_Angeles';

const readJSON = async (file) =>
  JSON.parse(await fs.readFile(path.join(DATA_DIR, file), 'utf8'));

const writeJSON = async (file, data) =>
  fs.writeFile(path.join(DATA_DIR, file), JSON.stringify(data, null, 2));

const nowPT = () =>
  new Date(new Date().toLocaleString('en-US', { timeZone: TZ }));

const ptTime = () =>
  nowPT().toTimeString().slice(0, 5); // "HH:MM"

// ─── 1. ADAPTIVE DIGEST ─────────────────────────────────────────────
// Checks every 5 min whether a digest is due; fires at best times or
// after the active interval (fast if triggers, else base).
async function runDigest(reason) {
  const signals = await readJSON('signals.json');
  const incidents = await readJSON('incidents.json');
  const decisions = await readJSON('decisions.json');

  // TODO: Muse's interpretation logic — turn signals into directives.
  // Example: if CTA variant A outperforms B by >20% on a lane with 100+ samples,
  // push a CTA directive.
  const newDirectives = await interpretSignals(signals, incidents);

  decisions.directives.push(...newDirectives);
  decisions.updated_at = new Date().toISOString();
  await writeJSON('decisions.json', decisions);

  const digest = await readJSON('digest.json');
  digest.last_digest = new Date().toISOString();
  digest.next_digest = computeNextDigest(digest, incidents);
  digest.next_digest_reason = reason;
  await writeJSON('digest.json', digest);

  console.log(`[digest] ran (${reason}) — ${newDirectives.length} directives`);
}

function computeNextDigest(digest, incidents) {
  const hasFastTrigger = incidents.some(i =>
    digest.fast_triggers.includes(i.status === 'OPEN' ? 'open_incident' : '') ||
    (i.severity === 'HIGH' && i.status !== 'RESOLVED')
  );
  const intervalMin = hasFastTrigger ? digest.fast_interval_min : digest.base_interval_min;
  const next = new Date(Date.now() + intervalMin * 60000);

  // Best times always win if sooner
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

// Check every 5 min: is it a best time, or has the interval elapsed?
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
// Every 15 min: check gap times per lane; breach → priority dispatch + incident.
cron.schedule('*/15 * * * *', async () => {
  try {
    const report = await readJSON('muse-morning.json');
    const incidents = await readJSON('incidents.json');
    const MAX_GAP = 45;

    for (const lane of report.lanes) {
      if (lane.longest_gap_min > MAX_GAP) {
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
          await prioritizeLane(lane.lane); // TODO: bump lane in dispatch queue
        }
      }
    }
    await writeJSON('incidents.json', incidents);
  } catch (e) {
    console.error('[cadence-guard] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 3. QUEUE BUFFER GUARD ───────────────────────────────────────────
// Every 15 min: staged count < 50 → pause expiry sweeps + flag refill.
cron.schedule('*/15 * * * *', async () => {
  try {
    const report = await readJSON('muse-morning.json');
    const incidents = await readJSON('incidents.json');
    const MIN_BUFFER = 50;

    for (const lane of report.lanes) {
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
          await pauseExpirySweeps(lane.lane); // TODO: Muse's expiry controller
        }
      }
    }
    await writeJSON('incidents.json', incidents);
  } catch (e) {
    console.error('[buffer-guard] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 4. VERIFICATION SWEEP ───────────────────────────────────────────
// Every 5 min: find dispatches older than 10 min without verification → repair queue.
cron.schedule('*/5 * * * *', async () => {
  try {
    // TODO: query BullMQ for jobs in 'dispatch-*' queues completed >10min ago
    //       without a corresponding 'verify' completion → enqueue repair.
    // This is the backstop that kills false "success" reports.
    await sweepUnverifiedDispatches();
  } catch (e) {
    console.error('[verify-sweep] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 5. MORNING REPORT ────────────────────────────────────────────────
// Daily 05:30 PT: generate verified-publishing report + incident summary.
cron.schedule('30 5 * * *', async () => {
  try {
    // TODO: Muse's report generator — reads the 12h window, writes muse-morning.json,
    //       produces the text report in the established format.
    await generateMorningReport();
    console.log('[morning-report] generated');
  } catch (e) {
    console.error('[morning-report] failed:', e.message);
  }
}, { timezone: TZ });

// ─── 6. WEEKLY REFRESH ────────────────────────────────────────────────
// Sundays 18:00 PT: shift calendar/CTA mix toward what won this week.
cron.schedule('0 18 * * 0', async () => {
  try {
    const decisions = await readJSON('decisions.json');
    const experiments = await readJSON('experiments.json');
    // TODO: read winning variants/formats/timings from experiments + signals,
    //       write FORMAT/CTA/TIMING directives for next week.
    await weeklyRefresh(decisions, experiments);
    console.log('[weekly-refresh] directives updated');
  } catch (e) {
    console.error('[weekly-refresh] failed:', e.message);
  }
}, { timezone: TZ });

// ─── PLACEHOLDER IMPLEMENTATIONS (replace with Muse's real logic) ────
async function interpretSignals(signals, incidents) { return []; }
async function prioritizeLane(lane) { /* bump lane priority in BullMQ */ }
async function pauseExpirySweeps(lane) { /* disable expiry for lane */ }
async function sweepUnverifiedDispatches() { /* enqueue repairs */ }
async function generateMorningReport() { /* write muse-morning.json */ }
async function weeklyRefresh(decisions, experiments) { /* write directives */ }

console.log('[cron-scheduler] all 6 automations scheduled (TZ: ' + TZ + ')');