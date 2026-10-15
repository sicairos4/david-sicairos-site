const SB_URL='https://uwidjnnhdgtrpsymuhwp.supabase.co';
const SB_KEY='sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN';
window.SITE_CONFIG=window.SITE_CONFIG||null;
(async function(){
const prefix=location.pathname.includes('/intelligence/')||location.pathname.includes('/ops/')?'../':'';
let cfg={};
try{cfg=await(await fetch(prefix+'data/site-config.json')).json();}catch(e){}
try{
const res=await fetch(SB_URL+'/rest/v1/site_content?select=*',{headers:{apikey:SB_KEY,Authorization:'Bearer '+SB_KEY}});
if(res.ok){const rows=await res.json();rows.forEach(r=>{cfg[r.key]=r.value;});}
}catch(e){}
window.SITE_CONFIG=cfg;
document.dispatchEvent(new CustomEvent('site-config-ready',{detail:cfg}));
})();