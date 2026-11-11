// Projection only; never executes recommendations or exposes arbitrary fields.
const paths=new Set(['/resume-builder.html','/studio.html','/tools.html','/library.html']);
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const text=x=>typeof x==='string'&&x.trim().length>0;
const iso=x=>typeof x==='string'&&/(Z|[+-]\d{2}:\d{2})$/.test(x)&&Number.isFinite(Date.parse(x));
const count=x=>Number.isSafeInteger(x)&&x>=0;
const expiryCleanups=new WeakMap();
export function project(s,now=Date.now()){
 const empty=state=>({state,candidates:[]});
 if(s==null)return empty('missing');
 if(!object(s)||s.version!==2||s.source!=='GA4'||!iso(s.collected_at)||!iso(s.expires_at)||!iso(s.experiment_ends_at)||!text(s.evidence_id)||!/^[a-f0-9]{64}$/.test(s.evidence_id)||!text(s.experiment_id)||!text(s.approval_ref)||!text(s.consent_evidence_ref)||!text(s.property_timezone)||s.automatic_promotion!==false||s.publication_verified!==false||s.social_execution!=='NOT_CONNECTED'||!Array.isArray(s.featured)||s.featured.length||!Array.isArray(s.observations)||s.observations.length>4||!Array.isArray(s.candidates)||s.candidates.length>3||!Number.isFinite(now))return empty('invalid');
 const start=Date.parse(s.collected_at),end=Date.parse(s.expires_at),limit=Date.parse(s.experiment_ends_at);
 if(start>now+300000||end<=start||end>limit||end-start>86400000)return empty('invalid');
 const seen=new Set();
 for(const r of s.observations){
  if(!object(r)||!paths.has(r.path)||seen.has(r.path)||!count(r.sessions)||!count(r.engaged)||r.engaged>r.sessions||!count(r.baseline_sessions))return empty('invalid');
  seen.add(r.path);
  const rate=r.sessions?r.engaged/r.sessions:null,b=r.baseline_engagement_rate;
  if(r.engagement_rate!==rate||!(b===null||(Number.isFinite(b)&&b>=0&&b<=1)))return empty('invalid');
  const lift=b>0&&rate!==null?(rate/b-1)*100:null;
  if(lift===null?r.engagement_lift_pct!==null:!Number.isFinite(r.engagement_lift_pct)||Math.abs(lift-r.engagement_lift_pct)>0.000001)return empty('invalid');
 }
 const rows=s.observations.filter(r=>r.sessions>=100&&r.baseline_sessions>=100&&r.engagement_lift_pct>=20).sort((a,b)=>b.engagement_lift_pct-a.engagement_lift_pct||a.path.localeCompare(b.path)).slice(0,3);
 if(s.outcome!==(rows.length?'REVIEW_REQUIRED':'INSUFFICIENT_EVIDENCE_OR_NO_THRESHOLD_CROSSING')||s.candidates.length!==rows.length||s.candidates.some((r,i)=>!object(r)||r.path!==rows[i].path))return empty('invalid');
 if(now>=end||now>=limit||now-start>86400000)return empty('stale');
 return {state:'fresh',collectedAt:s.collected_at,expiresAt:s.expires_at,evidenceId:s.evidence_id,candidates:rows.map(r=>({path:r.path,sessions:r.sessions,lift:r.engagement_lift_pct}))};
}
export function render(target,model){
 const previous=expiryCleanups.get(target);if(previous)previous();
 const deadline=model.state==='fresh'?Date.parse(model.expiresAt):NaN;
 if(model.state==='fresh'&&!Number.isFinite(deadline))model={state:'invalid',candidates:[]};
 else if(model.state==='fresh'&&Date.now()>=deadline)model={state:'stale',candidates:[]};
 const d=target.ownerDocument,f=d.createDocumentFragment();
 const add=(tag,value)=>{const e=d.createElement(tag);e.textContent=value;f.append(e);};
 const labels={fresh:'Current adaptive review snapshot.',missing:'No adaptive snapshot is stored.',stale:'Snapshot expired; candidates withheld.',invalid:'Unsupported or inconsistent snapshot.',unavailable:'Snapshot unavailable; no healthy or empty state inferred.'};
 add('h3','Adaptive website intelligence');add('p',labels[model.state]||'Unknown snapshot state.');
 if(model.state==='fresh'){
  add('p','Collected: '+model.collectedAt+'; expires: '+model.expiresAt);add('p','Evidence: '+model.evidenceId);
  if(!model.candidates.length)add('p','No page met the review threshold.');
  for(const r of model.candidates)add('p',r.path+' — '+r.sessions+' sessions; '+r.lift.toFixed(1)+'% descriptive relative engagement-rate lift.');
 }
 add('p','Review only. No recommendations executed; social publication is not established by this snapshot.');
 target.replaceChildren(f);
 if(model.state==='fresh'){
  const view=d.defaultView;let timer;
  const release=()=>{clearTimeout(timer);d.removeEventListener('visibilitychange',refresh);if(view)view.removeEventListener('pageshow',refresh);expiryCleanups.delete(target);};
  const refresh=()=>{
   if(target.isConnected===false){release();return;}
   if(Date.now()>=deadline){render(target,{state:'stale',candidates:[]});return;}
   clearTimeout(timer);timer=setTimeout(refresh,Math.min(deadline-Date.now()+1,2147483647));
  };
  expiryCleanups.set(target,release);d.addEventListener('visibilitychange',refresh);if(view)view.addEventListener('pageshow',refresh);refresh();
 }
}
