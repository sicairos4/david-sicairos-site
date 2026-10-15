// Public configuration only. Private member data must never enter this overlay.
(()=>{
const script=document.currentScript;
const base=new URL('../',script&&script.src?script.src:new URL('assets/site-data.js',location.href));
async function json(url,options={}){
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),10000);
 try{const response=await fetch(url,{...options,signal:controller.signal});if(!response.ok)throw Error('HTTP '+response.status);return await response.json()}finally{clearTimeout(timer)}
}
window.SITE_DATA_STATUS={config:'loading',overlay:'pending',checked_at:null};
window.SITE_READY=(async()=>{
 let cfg;
 try{cfg=await json(new URL('data/site-config.json',base));if(!cfg||typeof cfg!=='object'||Array.isArray(cfg))throw Error('Invalid configuration');window.SITE_DATA_STATUS.config='loaded'}catch(error){window.SITE_DATA_STATUS.config='failed';window.SITE_DATA_STATUS.overlay='skipped';window.SITE_DATA_STATUS.checked_at=new Date().toISOString();document.dispatchEvent(new CustomEvent('sitedataerror',{detail:{stage:'config'}}));throw error}
 try{
 const rows=await json('https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/site_content?select=key,value',{headers:{apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN'}});
 if(!Array.isArray(rows))throw Error('Invalid overlay');
 rows.forEach(row=>{if(!row.value||typeof row.value!=='object'||Array.isArray(row.value))return;if(row.key==='site_config')cfg={...cfg,...row.value};if(row.key==='page_overrides')window.PAGE_OVERRIDES=row.value});
 window.SITE_DATA_STATUS.overlay=rows.length?'loaded':'empty';
 }catch{window.SITE_DATA_STATUS.overlay='unavailable';console.warn('Public content overlay unavailable; using static site configuration.');}
 window.SITE=cfg;window.SITE_DATA_STATUS.checked_at=new Date().toISOString();document.dispatchEvent(new CustomEvent('sitedata',{detail:cfg}));return cfg;
})();
window.SITE_READY.catch(()=>console.warn('Site configuration unavailable; page fallback handlers must display the error.'));
})();
