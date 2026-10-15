(async function(){
function base(){
const paths=['data/site-config.json','../data/site-config.json'];
return paths.reduce((p,c)=>p.catch(()=>fetch(c).then(r=>{if(!r.ok)throw 0;return r.json()})),Promise.reject());
}
let cfg={};
try{cfg=await base();}catch(e){}
try{
const res=await fetch('https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/site_content?select=*',{headers:{apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN',Authorization:'Bearer sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN'}});
const rows=await res.json();
const page=location.pathname.split('/').pop()||'index.html';
rows.forEach(row=>{
if(row.key.startsWith('el:')){
const parts=row.key.split(':');
if(parts[1]===page){const el=document.querySelector(parts[2]);if(el&&typeof row.value==='string')el.textContent=row.value;}
}else if(typeof row.value==='object'){cfg[row.key]=row.value;}
});
}catch(e){}
window.SITE_CONFIG=cfg;
document.dispatchEvent(new CustomEvent('site-config-ready',{detail:cfg}));
})();