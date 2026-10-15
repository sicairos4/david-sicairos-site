// Live content layer: merges Supabase site_content overrides into the static site config.
// Any page that fetches 'site-config.json' automatically receives the merged, admin-editable version.
(function(){
const SB_URL='https://uwidjnnhdgtrpsymuhwp.supabase.co';
const SB_KEY='sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN';
const origFetch=window.fetch.bind(window);
window.fetch=async function(url,opts){
const s=String(url);
if(s.includes('site-config.json')){
const staticRes=await origFetch(url,opts);
const cfg=await staticRes.json();
try{
const res=await origFetch(SB_URL+'/rest/v1/site_content?select=*',{headers:{apikey:SB_KEY,Authorization:'Bearer '+SB_KEY}});
const rows=await res.json();
rows.forEach(r=>{
if(r.key.startsWith('element:')){
const id=r.key.split(':')[1];
const el=document.getElementById(id);
if(el&&typeof r.value==='string')el.textContent=r.value;
}else if(r.key==='pageText'&&r.value&&typeof r.value==='object'){
Object.entries(r.value).forEach(([id,txt])=>{const el=document.getElementById(id);if(el&&typeof txt==='string')el.textContent=txt;});
}else{
cfg[r.key]=r.value;
}
});
}catch(e){/* fall back to static config */}
return new Response(JSON.stringify(cfg),{status:200,headers:{'Content-Type':'application/json'}});
}
return origFetch(url,opts);
};
})();