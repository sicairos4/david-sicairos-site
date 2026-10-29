'use strict';
const crypto = require('node:crypto');
const ALLOWED = ['/resume-builder.html','/studio.html','/tools.html','/library.html'];
function normalize(rows) {
 const seen = new Set();
 return (rows || []).map(r => {
  const path = r.dimensionValues?.[0]?.value;
  const sessions = Number(r.metricValues?.[0]?.value);
  const engaged = Number(r.metricValues?.[1]?.value);
  if (!ALLOWED.includes(path) || seen.has(path) || !Number.isInteger(sessions) || !Number.isInteger(engaged) || sessions < 0 || engaged < 0 || engaged > sessions) throw new Error('Invalid or duplicate GA4 aggregate');
  seen.add(path);
  return {path, sessions, engaged, engagement_rate: sessions ? engaged / sessions : null};
 });
}
function derive(current, baseline, now = new Date()) {
 const previous = new Map(baseline.map(r => [r.path,r]));
 const observations = current.map(r => {
  const b = previous.get(r.path);
  const lift = b?.engagement_rate > 0 && r.engagement_rate !== null ? (r.engagement_rate / b.engagement_rate - 1) * 100 : null;
  return {...r, baseline_sessions:b?.sessions ?? 0, baseline_engagement_rate:b?.engagement_rate ?? null, engagement_lift_pct:lift};
 });
 const candidates = observations.filter(r => r.sessions >= 100 && r.baseline_sessions >= 100 && r.engagement_lift_pct >= 20).sort((a,b) => b.engagement_lift_pct-a.engagement_lift_pct || a.path.localeCompare(b.path));
 const signature = JSON.stringify(observations.slice().sort((a,b)=>a.path.localeCompare(b.path)));
 return {version:2, source:'GA4', collected_at:now.toISOString(), expires_at:new Date(now.getTime()+86400000).toISOString(), report_window:'Previous 7 complete property-calendar days versus preceding 7 complete days; not rolling 48h', attribution_window:'Aggregate page engagement only; no person-level or campaign-conversion attribution', metric:'Relative engagement-rate lift; descriptive, not causal', min_sessions_per_window:100, lift_threshold_pct:20, evidence_id:crypto.createHash('sha256').update(signature).digest('hex'), observations, outcome:candidates.length?'REVIEW_REQUIRED':'INSUFFICIENT_EVIDENCE_OR_NO_THRESHOLD_CROSSING', candidates:candidates.slice(0,3).map(r=>({path:r.path,reason:'At least 100 sessions in each window and at least 20% relative engagement-rate lift'})), featured:[], social_execution:'NOT_CONNECTED', publication_verified:false, automatic_promotion:false};
}
function experimentPolicy(raw, now = new Date()) {
 let p;
 try { p = JSON.parse(raw || 'null'); } catch { throw new Error('Invalid analytics experiment policy'); }
 if (!p || p.enabled !== true || p.collection_consent_attested !== true || typeof p.consent_evidence_ref !== 'string' || !p.consent_evidence_ref.trim() || typeof p.approval_ref !== 'string' || !p.approval_ref.trim() || typeof p.experiment_id !== 'string' || !p.experiment_id.trim()) throw new Error('Analytics requires an enabled experiment and consent/owner approval references');
 const start = Date.parse(p.starts_at), end = Date.parse(p.ends_at), approved = Date.parse(p.approved_at);
 if (![start,end,approved,now.getTime()].every(Number.isFinite) || ![p.starts_at,p.ends_at,p.approved_at].every(v=>typeof v==='string' && /(Z|[+-]\d{2}:\d{2})$/.test(v)) || approved > start || end <= start || now.getTime() < start || now.getTime() >= end) throw new Error('Experiment is not within its approved timezone-qualified window');
 if (!Number.isInteger(p.max_duration_hours) || p.max_duration_hours < 1 || p.max_duration_hours > 744 || end-start > p.max_duration_hours*3600000) throw new Error('Experiment duration exceeds its explicit cap');
 if (p.action !== 'review_only' || p.attribution_model !== 'aggregate_page_engagement' || p.private_writing_allowed !== false || typeof p.property_timezone !== 'string' || !p.property_timezone.trim()) throw new Error('Unsupported analytics scope; private writing and automatic promotion are prohibited');
 if (p.stop_on_no_data !== true || p.stop_on_incomplete !== true || p.stop_on_consent_withdrawal !== true) throw new Error('Required experiment stop conditions missing');
 return p;
}
async function main() {
 require('dotenv').config();
 if (process.env.ANALYTICS_EXPERIMENT_PAUSED === 'true') throw new Error('Analytics experiment paused; no query or write performed');
 const policy = experimentPolicy(process.env.ANALYTICS_EXPERIMENT_POLICY);
 for (const k of ['SUPABASE_URL','SUPABASE_SERVICE_KEY','GA4_PROPERTY_ID','GA4_CREDENTIALS']) if (!process.env[k]) throw new Error('Missing required environment variable: '+k);
 const target = new URL(process.env.SUPABASE_URL);
 if (target.href.replace(/\/$/,'') !== 'https://uwidjnnhdgtrpsymuhwp.supabase.co') throw new Error('Unexpected Supabase project; refusing write');
 const {BetaAnalyticsDataClient} = require('@google-analytics/data');
 const {createClient} = require('@supabase/supabase-js');
 const ga = new BetaAnalyticsDataClient({credentials:JSON.parse(process.env.GA4_CREDENTIALS)});
 async function report(startDate,endDate) {
  const [result] = await ga.runReport({property:'properties/'+process.env.GA4_PROPERTY_ID,dateRanges:[{startDate,endDate}],dimensions:[{name:'pagePath'}],metrics:[{name:'sessions'},{name:'engagedSessions'}],dimensionFilter:{filter:{fieldName:'pagePath',inListFilter:{values:ALLOWED,caseSensitive:true}}},limit:100});
  if (result.metadata?.subjectToThresholding || result.metadata?.dataLossFromOtherRow || (result.rowCount || 0) > 100) throw new Error('Incomplete or thresholded GA4 report; stop experiment');
  const rows=normalize(result.rows);
  if (!rows.length || rows.every(r=>r.sessions===0)) throw new Error('No usable analytics data; stop without recommendations');
  if (result.metadata?.timeZone !== policy.property_timezone) throw new Error('Property timezone differs from approved experiment');
  return {rows,timezone:result.metadata.timeZone};
 }
 const [current,baseline] = await Promise.all([report('7daysAgo','yesterday'),report('14daysAgo','8daysAgo')]);
 experimentPolicy(process.env.ANALYTICS_EXPERIMENT_POLICY);
 if (process.env.ANALYTICS_EXPERIMENT_PAUSED === 'true') throw new Error('Experiment paused before storage');
 const derived=derive(current.rows,baseline.rows);
 const snapshot = {...derived,expires_at:new Date(Math.min(Date.parse(derived.expires_at),Date.parse(policy.ends_at))).toISOString(),property_timezone:current.timezone,experiment_id:policy.experiment_id,experiment_ends_at:policy.ends_at,approval_ref:policy.approval_ref,consent_evidence_ref:policy.consent_evidence_ref,consent_basis:'Operator attestation; this worker does not implement or verify browser consent',stop_conditions:['pause','consent withdrawal','expiry','no usable data','incomplete or thresholded report','timezone mismatch']};
 const db = createClient(process.env.SUPABASE_URL,process.env.SUPABASE_SERVICE_KEY,{auth:{persistSession:false,autoRefreshToken:false}});
 const {data,error} = await db.from('site_content').upsert({key:'adaptive_web',value:snapshot,updated_at:snapshot.collected_at},{onConflict:'key'}).select('key');
 if (error) throw new Error('Adaptive snapshot write outcome uncertain; inspect before retry');
 if (data?.length !== 1 || data[0].key !== 'adaptive_web') throw new Error('Adaptive write receipt missing; inspect before retry');
 console.log(JSON.stringify({status:'REVIEW_SNAPSHOT_STORED',evidence_id:snapshot.evidence_id,candidates:snapshot.candidates.length,featured:0,social_execution:'NOT_CONNECTED'}));
}
module.exports={normalize,derive,experimentPolicy};
if (require.main === module) main().catch(e=>{console.error(e.message);process.exitCode=1;});
