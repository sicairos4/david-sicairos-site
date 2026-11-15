(()=>{
'use strict';
const base=new URL('../data/',document.currentScript.src);
const sb='https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/';
const headers={apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN'};
function hasSource(value){return typeof value==='string'&&value.trim().length>0}
function verifiedBaseline(p){const baseline=Date.parse(p.baseline_measured_at),measured=Date.parse(p.verified_on);return p.baseline_verified===true&&hasSource(p.baseline_source)&&Number.isFinite(baseline)&&Number.isFinite(measured)&&Math.floor(measured/86400000)-Math.floor(baseline/86400000)===28}
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n}
function message(id,text){document.getElementById(id)?.replaceChildren(node('p',text,'muted'))}
function link(label,value){try{if(typeof value!=='string'||!value)return null;const u=new URL(value,new URL('../',base));if(u.protocol!=='https:'&&u.origin!==location.origin)return null;const a=node('a',label,'btn ghost');a.href=u.href;if(u.origin!==location.origin){a.target='_blank';a.rel='noopener noreferrer'}return a}catch{return null}}
async function json(url,options={}){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);try{const r=await fetch(url,{...options,signal:controller.signal});if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(timer)}}
function list(id,rows,format,empty='No verified entries available.'){if(!Array.isArray(rows))throw Error('Invalid rows');const box=document.getElementById(id),f=document.createDocumentFragment();for(const row of rows.slice(0,30)){const card=node('article',undefined,'item');format(card,row);f.append(card)}box.replaceChildren(f);if(!rows.length)message(id,empty)}
let cacheBust=0;
try{const v=new URLSearchParams(location.search).get('v');if(v)cacheBust=Number(v)||Date.now();}catch{}
async function load(id,file,render){try{await render(await json(new URL(file+(cacheBust?'?t='+cacheBust:''),base)))}catch{message(id,'Data unavailable. No connection or zero measurement is inferred.')}}
const tasks=[
()=>load('pipeList','pipeline.json',p=>list('pipeList',p.sources,(c,s)=>{c.append(node('h3',s.name||'Source'),node('p','Reported state: '+(s.status||'UNVERIFIED')),node('p','Reported last sync: '+(s.last_sync||'Not supplied'),'source-note'));c.append(node('p','A configuration snapshot is not a live health check.','source-note'))})),
()=>load('digestCard','digest.json',d=>message('digestCard','Configured next digest: '+(d.next_digest||'Not supplied')+'. Execution has not been verified here.')),
()=>load('incList','incidents.json',rows=>list('incList',rows,(c,r)=>c.append(node('h3',r.title||'Recorded incident'),node('p',(r.date||'Undated')+' · '+(r.status||'Unverified'))),'No incidents recorded in this snapshot.')),
()=>load('museList','muse-morning.json',m=>{if(!m.source||!m.verified_at){message('museList','No source and verification timestamp supplied. Publishing is not verified.');return}list('museList',m.lanes,(c,r)=>c.append(node('h3',r.lane||'Lane'),node('p','Reported verified count: '+(Number.isFinite(r.verified)?r.verified:'Not supplied')),node('p','Source: '+m.source+' · '+m.verified_at,'source-note')))}),
()=>load('calList','calendar.json',rows=>list('calList',rows,(c,r)=>c.append(node('h3',r.mission||'Planned activity'),node('p',(r.date||'Unscheduled')+' · '+(r.platform||'Platform not supplied'))))),
()=>load('shiftList','shift.json',s=>list('shiftList',(s.shift_log||[]).filter(r=>r.evidence_id&&r.source),(c,r)=>c.append(node('h3',r.date||'Recorded change'),node('p',r.trigger||'Evidence-backed change'),node('p','Source: '+r.source+' · Evidence: '+r.evidence_id,'source-note')))),
()=>load('analyticsGrid','analytics.json',a=>{
  const box=document.getElementById('analyticsGrid');box.replaceChildren();
  const gen=Date.parse(a.generated_at),genAge=Date.now()-gen;
  const fresh=Number.isFinite(genAge)&&genAge>=-300000&&genAge<=3600000;
  const head=node('p',fresh
    ? '● LIVE — updated '+Math.max(0,Math.round(genAge/60000))+' minutes ago · generated '+(a.generated_at_pt||a.generated_at)+' · feed every '+(a.refresh_cadence_minutes||15)+' min'
    : '● STALE — last generated '+(a.generated_at_pt||a.generated_at||'unknown')+'. These numbers are frozen until the feed runs again — press Refresh now above.');
  head.className=fresh?'status-banner status-live':'status-banner status-stale';box.append(head);
  const ok=(x,field)=>{const t=Date.parse(x.collected_at),age=Date.now()-t;
    return typeof x.source==='string'&&x.source.trim()&&Number.isFinite(t)&&age>=-300000&&age<=172800000
      &&typeof x[field]==='number'&&Number.isFinite(x[field])&&x[field]>=0;};
  const sectionFresh=x=>{const t=Date.parse(x.collected_at),age=Date.now()-t;
    return typeof x.source==='string'&&x.source.trim()&&Number.isFinite(t)&&age>=-300000&&age<=172800000;};
  const card=(name,text,sourceNote)=>{const c=node('article',undefined,'card');
    c.append(node('h3',name));c.append(node('p',text));
    if(sourceNote)c.append(node('p',sourceNote,'source-note'));box.append(c);};
  for(const [key,name,field,label] of [['beehiiv','Beehiiv','subscribers','subscribers'],['ga4','GA4','sessions_28d','sessions (28 days)'],['youtube','YouTube','views_28d','views (28 days)'],['meta','Facebook reach (28 days)','fb_reach_28d','people reached']]){
    const x=a[key]||{};
    card(name,ok(x,field)?x[field].toLocaleString()+' '+label:'No fresh source-backed measurement',
      ok(x,field)?x.source+' · '+x.collected_at:null);}
  const m=a.meta||{};
  card('Facebook engagements (28d)',ok(m,'post_engagements_28d')?m.post_engagements_28d.toLocaleString()+' post engagements':'No fresh source-backed measurement',
    ok(m,'post_engagements_28d')?m.source+' · '+m.collected_at:null);
  const v=a.verified_publishes||{};
  const sum=o=>Object.values(o||{}).reduce((s,n)=>s+(typeof n==='number'?n:0),0);
  card('Verified publishes (24h)',sectionFresh(v)?sum(v.verified_24h).toLocaleString()+' verified':'No fresh source-backed measurement',
    sectionFresh(v)?v.source+' · '+v.collected_at:null);
  card('Verified publishes (7d)',sectionFresh(v)?sum(v.verified_7d).toLocaleString()+' verified':'No fresh source-backed measurement',
    sectionFresh(v)?v.source+' · '+v.collected_at:null);
  const lab=a.top_posts_lab||{},top=(lab.top_unified||[])[0];
  card('Top scored post',top&&typeof top.unified_score==='number'?top.platform+' · Unified '+top.unified_score+' · '+(top.views||'?')+' views':'No fresh source-backed measurement',
    top?lab.source+' · '+lab.collected_at:null);
  const st=a.steering||{};
  card('Posts last 24h (all lanes)',sectionFresh(st)?sum(st.posts_last_24h_by_lane).toLocaleString()+' posts':'No fresh source-backed measurement',
    sectionFresh(st)?st.source+' · '+st.collected_at:null);
  message('recList','Recommendations are withheld until their underlying measurements and evidence are verified.');
}),
()=>load('rankingsGrid','unified-analytics.json',u=>{
  const box=document.getElementById('rankingsGrid');box.replaceChildren();
  const gen=Date.parse(u.generated_at),genAge=Date.now()-gen;
  const fresh=Number.isFinite(genAge)&&genAge>=-300000&&genAge<=3600000;
  const head=node('p',fresh
    ? '● LIVE — updated '+Math.max(0,Math.round(genAge/60000))+' minutes ago · '+u.generated_at_pt+' · one method: '+u.method
    : '● STALE — last generated '+(u.generated_at_pt||'unknown')+'. These numbers are frozen until the refresh runs again.');
  head.className=fresh?'status-banner status-live':'status-banner status-stale';box.append(head);
  const card=(name,text,sourceNote)=>{const c=node('article',undefined,'card');
    c.append(node('h3',name));c.append(node('p',text));
    if(sourceNote)c.append(node('p',sourceNote,'source-note'));box.append(c);};
  const srcNote=u.source+' · '+(u.collected_at||u.generated_at_pt||'');
  const t=u.totals||{};
  card('Verified publishes (24h, unified recompute)',typeof t.verified_24h==='number'?t.verified_24h.toLocaleString()+' verified':'No fresh source-backed measurement',srcNote);
  const top=(u.top_posts||[])[0];
  card('Top scored post',top&&typeof top.unified==='number'?top.platform+' · Unified '+top.unified+' · '+(top.views||'?')+' views · '+(top.topic||'no topic'):'No fresh source-backed measurement',top?srcNote:null);
  const topics=Object.entries(u.per_topic||{}).sort((a,b)=>b[1].median_unified-a[1].median_unified);
  card('Best topic (median Unified)',topics.length?topics[0][0]+' · median '+topics[0][1].median_unified+' over '+topics[0][1].n+' scored posts':'No fresh source-backed measurement',topics.length?srcNote:null);
  const s=u.supply||{},nr=s.newsroom_ready||{};
  card('Staged supply','IG '+((typeof s.ig_staged_total==='number')?s.ig_staged_total:'?')+' · FB '+((typeof s.fb_staged==='number')?s.fb_staged:'?')+' · Video '+((typeof s.video_staged==='number')?s.video_staged:'?')+' · Threads READY '+((typeof nr.threads==='number')?nr.threads:'?')+' · Bluesky READY '+((typeof nr.bluesky==='number')?nr.bluesky:'?'),srcNote);
  card('Open gaps',(u.gaps||[]).length?(u.gaps||[]).length+' recorded gaps — see the unified report':'No gaps recorded',srcNote);
}),
async()=>{try{const data=await Promise.all(['signals.json','decisions.json','experiments.json'].map(f=>json(new URL(f,base))));const entries=[['Signals',data[0].posts],['Decisions',data[1].directives],['Experiments',data[2].experiments]];list('loopGrid',entries,(c,[name,rows])=>c.append(node('h3',name),node('p',Array.isArray(rows)?rows.length+' configured entries; execution not inferred.':'No valid snapshot supplied.')))}catch{message('loopGrid','Growth-loop snapshots unavailable.')}}
];
async function remote(id,path,format){try{list(id,await json(sb+path,{headers}),format)}catch{message(id,'Public feed unavailable. No successful ingestion or zero count is inferred.')}}
tasks.push(()=>remote('adaptationFeed','adaptation_log?select=trigger,observation,action&order=created_at.desc&limit=10',(c,r)=>c.append(node('h3',r.trigger||'Recorded observation'),node('p',r.observation||''),node('p','Recorded action: '+(r.action||'None supplied')),node('p','This log alone does not verify execution.','source-note'))));
tasks.push(()=>remote('topPosts','top_posts_48h?select=title,platform&order=engagement_delta.desc&limit=5',(c,r)=>c.append(node('h3',r.title||'Post observation'),node('p',r.platform||'Platform not supplied'))));
window.SITE_READY.then(cfg=>{list('intelRecords',cfg.records||[],(c,r)=>{c.append(node('h3',r.headline||'Public record'),node('p',(r.date||'Undated')+' · '+(r.source||'Source not supplied')));const a=link('Open record',r.link);if(a)c.append(a)});list('pulseGrid',cfg.socialPulse||[],(c,p)=>{c.className='card';c.append(node('h3',p.name||'Channel'));const count=typeof p.followers==='number'&&Number.isFinite(p.followers)&&p.followers>=0?p.followers:null;const previous=typeof p.followers28dAgo==='number'&&Number.isFinite(p.followers28dAgo)&&p.followers28dAgo>=0&&verifiedBaseline(p)?p.followers28dAgo:null;const age=Date.now()-Date.parse(p.verified_on);const verified=hasSource(p.source)&&Number.isFinite(age)&&age>=0&&age<=172800000;c.append(node('p',verified&&count!==null?count.toLocaleString()+' '+(p.metric||'followers'):'No fresh verified measurement'));c.append(node('p',verified&&count!==null&&previous!==null?String(count-previous)+' change in 28 days':'28-day change unavailable; no verified baseline.'));if(hasSource(p.source))c.append(node('p',p.source+' · '+(p.verified_on||'Date unavailable')+' UTC. Snapshot, not continuous sync.','source-note'));const a=link('Open channel',p.url);if(a)c.append(a)});if(Array.isArray(cfg.unverifiedPlatforms)&&cfg.unverifiedPlatforms.length)document.getElementById('pulseGrid').append(node('p','Unverified platform metrics: '+cfg.unverifiedPlatforms.join(', '),'source-note'))}).catch(()=>{message('intelRecords','Configuration unavailable.');message('pulseGrid','Verified channel snapshots unavailable.')});
message('recList','Recommendations require verified source data.');
function refreshGrids(){cacheBust=Date.now();return Promise.allSettled(tasks.map(task=>task()));}
const refreshBtn=document.getElementById('refreshAnalytics');
if(refreshBtn)refreshBtn.addEventListener('click',()=>{refreshBtn.disabled=true;refreshBtn.textContent='Refreshing…';refreshGrids().finally(()=>{refreshBtn.disabled=false;refreshBtn.textContent='Refresh now';});});
setInterval(()=>{if(!document.hidden)refreshGrids();},300000);
Promise.allSettled(tasks.map(task=>task()));
})();
