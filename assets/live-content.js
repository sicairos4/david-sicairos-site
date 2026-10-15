(function(){
const SB_URL='https://uwidjnnhdgtrpsymuhwp.supabase.co';
const SB_KEY='sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN';
const prefix=(location.pathname.indexOf('/intelligence/')>-1)?'../':'';
window.LiveContent=(async()=>{
let base={};
try{base=await(await fetch(prefix+'data/site-config.json')).json();}catch(e){}
try{
const res=await fetch(SB_URL+'/rest/v1/site_content?select=*',{headers:{apikey:SB_KEY,Authorization:'Bearer '+SB_KEY}});
const rows=await res.json();
(Array.isArray(rows)?rows:[]).forEach(r=>{base[r.key]=r.value;});
}catch(e){}
return base;
});
})();