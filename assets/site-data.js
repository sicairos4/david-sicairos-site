// Public snapshots only. No private member data or server credentials belong here.
(()=>{
const script=document.currentScript;
const base=new URL('../',script&&script.src?script.src:new URL('assets/site-data.js',location.href));
async function json(url,options={}){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);try{const r=await fetch(url,{...options,signal:controller.signal});if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(timer)}}
const ready=document.readyState==='loading'?new Promise(resolve=>document.addEventListener('DOMContentLoaded',resolve,{once:true})):Promise.resolve();
window.SITE_DATA_STATUS={config:'loading',overlay:'pending',checked_at:null};
window.SITE_READY=(async()=>{
let cfg;
try{cfg=await json(new URL('data/site-config.json',base));if(!cfg||typeof cfg!=='object'||Array.isArray(cfg))throw Error('Invalid configuration');window.SITE_DATA_STATUS.config='loaded'}catch(error){window.SITE_DATA_STATUS.config='failed';window.SITE_DATA_STATUS.overlay='skipped';window.SITE_DATA_STATUS.checked_at=new Date().toISOString();document.dispatchEvent(new CustomEvent('sitedataerror',{detail:{stage:'config'}}));throw error}
const snapshot={};for(const key of ['socialPulse','museStatus','announcements','whatsWorking','podcasts'])snapshot[key]=cfg[key];
try{const rows=await json('https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/site_content?select=key,value',{headers:{apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN'}});if(!Array.isArray(rows))throw Error('Invalid overlay');for(const row of rows){if(!row.value||typeof row.value!=='object'||Array.isArray(row.value))continue;if(row.key==='site_config')cfg={...cfg,...row.value};if(row.key==='page_overrides')window.PAGE_OVERRIDES=row.value}window.SITE_DATA_STATUS.overlay=rows.length?'loaded':'empty'}catch{window.SITE_DATA_STATUS.overlay='unavailable';console.warn('Public content overlay unavailable; using static site configuration.')}
// Legacy overlays are editorial snapshots, not telemetry receipts. They cannot override verified metrics or connection states.
Object.assign(cfg,snapshot);window.SITE=cfg;window.SITE_DATA_STATUS.checked_at=new Date().toISOString();document.dispatchEvent(new CustomEvent('sitedata',{detail:cfg}));return cfg;
})();
function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);return n}
// Compatibility with the legacy inline dashboard renderer: run after its promise callback, before the next paint.
Promise.all([window.SITE_READY,ready]).then(([cfg])=>queueMicrotask(()=>{
const box=document.getElementById('pulseGrid');if(!box)return;const fragment=document.createDocumentFragment();
for(const p of Array.isArray(cfg.socialPulse)?cfg.socialPulse:[]){const card=node('article');card.className='card';card.append(node('h3',p.name||'Channel'));
const measured=p.verified===true&&typeof p.source==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(p.measurement_date||'')&&Number.isInteger(p.followers)&&p.followers>=0;
card.append(node('p',measured?p.followers+' '+(p.name==='YouTube'?'subscribers':'followers')+' — snapshot '+p.measurement_date:'No verified follower measurement'));
const baseline=measured&&p.baseline_verified===true&&typeof p.baseline_measured_at==='string'&&Number.isInteger(p.followers28dAgo)&&p.followers28dAgo>=0;
if(baseline){const d=p.followers-p.followers28dAgo;card.append(node('p',(d>0?'+':'')+d+' versus verified 28-day baseline'))}else card.append(node('p','28-day growth unavailable: no verified baseline.'));
if(p.name==='YouTube'){const a=node('a','Open verified YouTube channel →');a.href='https://www.youtube.com/channel/UCDMa9oEWj4i6KFOkjF79qLg';a.className='btn ghost';a.target='_blank';a.rel='noopener';card.append(a)}
fragment.append(card)}if(!fragment.childNodes.length)fragment.append(node('p','No verified channel snapshots configured.'));box.replaceChildren(fragment);
})).catch(()=>console.warn('Verified social snapshot unavailable.'));
window.SITE_READY.catch(()=>console.warn('Site configuration unavailable; page fallback handlers must display the error.'));
})();
