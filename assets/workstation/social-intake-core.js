(function(g){
'use strict';
const obj=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const canonical=v=>Array.isArray(v)?'['+v.map(canonical).join(',')+']':obj(v)?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}':JSON.stringify(v);
function socialVariant(record,platform){
 const s=record?.plan?.creatorSocial,key=platform==='beehiiv'?'newsletter':platform;
 if(!obj(s)||s.version!==1||!obj(s.variants)||!obj(s.variants[key]))throw Error('Save a supported platform version first.');
 const v=s.variants[key];
 if(typeof v.text!=='string'||!v.text.trim()||v.text.length>20000)throw Error('Write and save the platform text first.');
 const result={text:v.text,url:v.url??'',cta:v.cta??'',media:[]};
 for(const [k,max] of [['url',2048],['cta',1000]])if(typeof result[k]!=='string'||result[k].length>max)throw Error('Invalid saved variant field.');
 const url=(value,required)=>{if(!value.trim()){if(required)throw Error('Attachment URL required.');return;}let u;try{u=new URL(value);}catch{throw Error('Invalid HTTPS reference.');}if(u.protocol!=='https:'||u.username||u.password)throw Error('Use HTTPS references without credentials.');};
 url(result.url,false);
 if(v.media!==undefined&&!Array.isArray(v.media))throw Error('Invalid attachment references.');
 if((v.media??[]).length>5)throw Error('Use at most five attachment references.');
 result.media=(v.media??[]).map(m=>{if(!obj(m)||!['image','video','file'].includes(m.kind)||typeof m.url!=='string'||m.url.length>2048||typeof m.description!=='string'||m.description.length>500)throw Error('Invalid attachment reference.');url(m.url,true);return {kind:m.kind,url:m.url,description:m.description};});
 return result;
}
function createController({client,readContext,randomUUID=()=>g.crypto.randomUUID()}){
 let generation=0,preview=null,inflight=false;
 const invalidate=()=>{generation++;preview=null;};
 function snapshot(){const c=readContext();if(!c||c.busy||!c.accountId||!c.record||!Number.isInteger(c.record.revision)||c.record.revision<1||typeof c.day!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(c.day))throw Error('Load and save an account day first.');return {owner:c.accountId,day:c.day,context:c.context,revision:c.record.revision};}
 function same(s){try{return canonical(snapshot())===canonical(s);}catch{return false;}}
 async function verify(s){if(!same(s))throw Error('Account, day or revision changed. Review again.');const {data,error}=await client.auth.getUser();if(error||data?.user?.id!==s.owner||!same(s))throw Error('Account changed. Review again.');}
 async function destination(s,id){const {data,error}=await client.from('desk_publish_destinations').select('id,owner_id,platform,platform_account_id,label,enabled,config_version').eq('owner_id',s.owner).eq('id',id).maybeSingle();if(error)throw Error('Destination lookup unavailable.');if(!data||!data.enabled||data.owner_id!==s.owner)throw Error('No authorized destination is available.');return data;}
 async function saved(s,d){const {data,error}=await client.from('intentional_days').select('plan,revision').eq('user_id',s.owner).eq('day',s.day).maybeSingle();if(error)throw Error('Saved-day read unavailable.');if(!data||data.revision!==s.revision)throw Error('Saved-day revision changed. Save or reload before review.');const v=socialVariant(data,d.platform);if(!same(s)||canonical(v)!==canonical(socialVariant(readContext().record,d.platform)))throw Error('The selected version has unsaved changes. Save and review again.');return v;}
 async function prepare(id){if(inflight)throw Error('A submission is already in flight.');invalidate();const serial=generation,s=snapshot();await verify(s);const d=await destination(s,id),v=await saved(s,d);await verify(s);if(serial!==generation)throw Error('Review was invalidated.');preview={serial,s,d,v,fingerprint:canonical(v),key:randomUUID()};return {day:s.day,revision:s.revision,destination:d.label,platform:d.platform,account:d.platform_account_id,variant:structuredClone(v)};}
 async function submit(){if(inflight)throw Error('A submission is already in flight.');if(!preview)throw Error('Preview the saved version first.');const p=preview;inflight=true;try{await verify(p.s);const d=await destination(p.s,p.d.id);if(canonical(d)!==canonical(p.d))throw Error('Destination changed. Review again.');await saved(p.s,d);await verify(p.s);if(preview!==p||generation!==p.serial||canonical(socialVariant(readContext().record,d.platform))!==p.fingerprint)throw Error('Review changed. Preview again.');let result;try{result=await client.rpc('desk_submit_social_v1',{p_request_key:p.key,p_day:p.s.day,p_expected_revision:p.s.revision,p_destination:d.id,p_requested_for:null});}catch{throw Error('Submission outcome uncertain. Retry this same reviewed request; do not create another key.');}if(result?.error)throw Error('Submission was not confirmed. Keep this review for retry or inspect existing requests.');if(!result?.data||typeof result.data.request_id!=='string'||typeof result.data.state!=='string')throw Error('Submission outcome uncertain: invalid receipt. Keep the same request key.');const receipt=result.data;if(!same(p.s)||preview!==p)throw Error('Account or view changed. A request may have been stored; inspect your requests before resubmitting.');preview=null;return {request_id:receipt.request_id,state:receipt.state};}finally{inflight=false;}}
 return {prepare,submit,invalidate};
}
const api={canonical,socialVariant,createController};if(typeof module!=='undefined')module.exports=api;else g.WorkstationSocialIntake=api;
})(globalThis);
