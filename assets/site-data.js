// 209 Live Content — JSON base + Supabase site_content overlay
window.SITE_READY=(async()=>{
const SB_URL='https://uwidjnnhdgtrpsymuhwp.supabase.co';
const SB_KEY='sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN';
const H={'apikey':SB_KEY,'Authorization':'Bearer '+SB_KEY};
let cfg=await(await fetch('data/site-config.json').catch(()=>fetch('../data/site-config.json'))).json();
try{
const rows=await(await fetch(SB_URL+'/rest/v1/site_content?select=*',{headers:H})).json();
rows.forEach(r=>{
if(r.key==='site_config')cfg={...cfg,...r.value};
if(r.key==='page_overrides'){window.PAGE_OVERRIDES=r.value;}
});
}catch(e){}
window.SITE=cfg;
document.dispatchEvent(new CustomEvent('sitedata',{detail:cfg}));
return cfg;
})();