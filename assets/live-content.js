(async function(){
 const auditHero=document.getElementById('engine');
 const preserveAuditHero=!!auditHero?.querySelector('#featuredTitle');
 function base(){
  const paths=['data/site-config.json','../data/site-config.json'];
  return paths.reduce((p,c)=>p.catch(()=>fetch(c).then(r=>{if(!r.ok)throw new Error('Config unavailable');return r.json();})),Promise.reject());
 }
 let cfg={};
 try{cfg=await base();}catch(e){}
 try{
  const res=await fetch('https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/site_content?select=*',{headers:{apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN',Authorization:'Bearer sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN'},signal:AbortSignal.timeout(8000)});
  if(!res.ok)throw new Error('Live content unavailable');
  const rows=await res.json();
  if(!Array.isArray(rows))throw new Error('Invalid live content response');
  const page=location.pathname.split('/').pop()||'index.html';
  rows.forEach(row=>{
   if(typeof row.key!=='string')return;
   if(row.key.startsWith('el:')){
    const parts=row.key.split(':');
    if(parts[1]===page&&typeof row.value==='string'){try{const el=document.querySelector(parts[2]);if(el&&!(preserveAuditHero&&(auditHero.contains(el)||el.contains(auditHero))))el.textContent=row.value;}catch(e){}}
   }else if(row.value&&typeof row.value==='object'){cfg[row.key]=row.value;}
  });
 }catch(e){console.warn('Live content unavailable; retaining static content.');}
 // The homepage Audit introduction is editorial copy in index.html, not a rotating featured story.
 if(preserveAuditHero)delete cfg.featuredStory;
 window.SITE_CONFIG=cfg;
 document.dispatchEvent(new CustomEvent('site-config-ready',{detail:cfg}));
 function render(){
  const s=cfg.adaptive_web;
  const titles={'/resume-builder.html':'Resume Builder','/studio.html':'209 Connect Studio','/tools.html':'209 Tools','/library.html':'Media Library'};
  const now=Date.now(),collected=Date.parse(s?.collected_at),expires=Date.parse(s?.expires_at);
  if(!s||s.version!==1||s.source!=='GA4'||!Number.isFinite(collected)||!Number.isFinite(expires)||collected>now+300000||expires<=now||now-collected>86400000||!Array.isArray(s.featured))return;
  const loader=Array.from(document.scripts).find(x=>x.src&&new URL(x.src).pathname.endsWith('/assets/live-content.js'));
  if(!loader)return;
  const root=new URL('../',loader.src);
  if(location.pathname!==root.pathname&&location.pathname!==new URL('index.html',root).pathname)return;
  const features=s.featured.filter(x=>x&&Object.hasOwn(titles,x.path)).slice(0,3);
  if(!features.length)return;
  let host=document.getElementById('adaptive-web-recommendations');
  if(!host){host=document.createElement('section');host.id='adaptive-web-recommendations';host.className='section wrap';(document.querySelector('main')||document.body).append(host);}
  host.replaceChildren();host.setAttribute('aria-label','Recommended resources');
  const h=document.createElement('h2');h.textContent='Explore these resources';host.append(h);
  const list=document.createElement('ul');
  features.forEach(x=>{const li=document.createElement('li'),a=document.createElement('a');a.href=new URL(x.path.slice(1),root).href;a.textContent=titles[x.path];li.append(a);list.append(li);});
  host.append(list);
  host.dataset.evidenceId=String(s.evidence_id||'');
  document.dispatchEvent(new CustomEvent('adaptive-content-rendered',{detail:{evidence_id:s.evidence_id,paths:features.map(x=>x.path)}}));
  setTimeout(()=>host.remove(),Math.max(0,Math.min(expires-collected,86400000)-(Date.now()-collected)));
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',render,{once:true});else render();
})();
