'use strict';
const crypto = require('node:crypto');
const ALLOWED = ['/resume-builder.html','/studio.html','/tools.html','/library.html'];
function normalize(rows) {
 return (rows || []).map(r => {
  const path = r.dimensionValues?.[0]?.value;
  const sessions = Number(r.metricValues?.[0]?.value);
  const engaged = Number(r.metricValues?.[1]?.value);
  if (!ALLOWED.includes(path) || !Number.isInteger(sessions) || !Number.isInteger(engaged) || sessions < 0 || engaged < 0 || engaged > sessions) throw new Error('Invalid GA4 aggregate');
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
 const eligible = observations.filter(r => r.sessions >= 100 && r.baseline_sessions >= 100 && r.engagement_lift_pct >= 20).sort((a,b) => b.engagement_lift_pct-a.engagement_lift_pct || a.path.localeCompare(b.path));
 const signature = JSON.stringify(observations.slice().sort((a,b)=>a.path.localeCompare(b.path)));
 return {version:1, source:'GA4', collected_at:now.toISOString(), expires_at:new Date(now.getTime()+86400000).toISOString(), report_window:'Previous 7 complete property-calendar days versus preceding 7 complete days; not rolling 48h', metric:'Relative engagement-rate lift; descriptive, not causal', min_sessions_per_window:100, lift_threshold_pct:20, evidence_id:crypto.createHash('sha256').update(signature).digest('hex'), observations, outcome:eligible.length?'ELIGIBLE_FOR_WEB_PROMOTION':'INSUFFICIENT_EVIDENCE_OR_NO_THRESHOLD_CROSSING', featured:eligible.slice(0,3).map(r=>({path:r.path,reason:'At least 100 sessions in each window and at least 20% relative engagement-rate lift'})), social_execution:'NOT_CONNECTED', publication_verified:false};
}
async function main() {
 require('dotenv').config();
 for (const k of ['SUPABASE_URL','SUPABASE_SERVICE_KEY','GA4_PROPERTY_ID','GA4_CREDENTIALS']) if (!process.env[k]) throw new Error('Missing required environment variable: '+k);
 const target = new URL(process.env.SUPABASE_URL);
 if (target.origin !== 'https://uwidjnnhdgtrpsymuhwp.supabase.co') throw new Error('Unexpected Supabase project; refusing write');
 const {BetaAnalyticsDataClient} = require('@google-analytics/data');
 const {createClient} = require('@supabase/supabase-js');
 const ga = new BetaAnalyticsDataClient({credentials:JSON.parse(process.env.GA4_CREDENTIALS)});
 async function report(startDate,endDate) {
  const [result] = await ga.runReport({property:'properties/'+process.env.GA4_PROPERTY_ID,dateRanges:[{startDate,endDate}],dimensions:[{name:'pagePath'}],metrics:[{name:'sessions'},{name:'engagedSessions'}],dimensionFilter:{filter:{fieldName:'pagePath',inListFilter:{values:ALLOWED,caseSensitive:true}}},limit:100});
  if (result.metadata?.subjectToThresholding || result.metadata?.dataLossFromOtherRow || (result.rowCount || 0) > 100) throw new Error('Incomplete or thresholded GA4 report; refusing adaptation');
  return {rows:normalize(result.rows),timezone:result.metadata?.timeZone || null};
 }
 const [current,baseline] = await Promise.all([report('7daysAgo','yesterday'),report('14daysAgo','8daysAgo')]);
 const snapshot = {...derive(current.rows,baseline.rows),property_timezone:current.timezone};
 const db = createClient(process.env.SUPABASE_URL,process.env.SUPABASE_SERVICE_KEY,{auth:{persistSession:false,autoRefreshToken:false}});
 const {data,error} = await db.from('site_content').upsert({key:'adaptive_web',value:snapshot,updated_at:snapshot.collected_at},{onConflict:'key'}).select('key');
 if (error) throw new Error('Adaptive snapshot write failed: '+error.message);
 if (data?.length !== 1 || data[0].key !== 'adaptive_web') throw new Error('Adaptive write receipt missing');
 console.log(JSON.stringify({status:'SNAPSHOT_STORED',evidence_id:snapshot.evidence_id,eligible:snapshot.featured.length,social_execution:'NOT_CONNECTED'}));
}
module.exports={normalize,derive};
if (require.main === module) main().catch(e=>{console.error(e.message);process.exitCode=1;});
