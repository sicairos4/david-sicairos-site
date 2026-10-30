(function(g){'use strict';
function fields(name,bio){name=String(name||'').trim();bio=String(bio||'').trim();if(!name||Array.from(name).length>40||Array.from(bio).length>500)throw Error('Use a display name of 1–40 characters and a bio of up to 500 characters.');return {display_name:name,bio};}
if(typeof module!=='undefined')module.exports={fields};if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),n=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
function boot(){
 const app=document.querySelector('.connect-app'),settings=document.querySelector('[data-view="settings"]'),client=g.WorkstationAccountClient;
 if(!app||!settings||$('accountProfilePanel')||!client)return;
 let user=null,epoch=0,busy=false,baseline='',uncertain=false;
 const panel=n('fieldset'),legend=n('legend','Your profile'),photo=n('img'),initials=n('span'),email=n('p'),form=n('form'),name=n('input'),bio=n('textarea'),usePhoto=n('input'),save=n('button','Save profile'),status=n('p'),signout=n('button','Sign out'),reload=n('button','Reload profile'),link=n('a');
 panel.id='accountProfilePanel';photo.alt='Your profile picture';photo.width=photo.height=64;photo.referrerPolicy='no-referrer';photo.style.cssText='border-radius:50%;object-fit:cover';photo.hidden=true;initials.style.cssText='padding:16px;border:1px solid var(--line);border-radius:50%;font-weight:700';name.maxLength=80;name.required=true;bio.maxLength=1000;usePhoto.type='checkbox';usePhoto.checked=true;
 for(const [text,field] of [['Display name',name],['Bio — optional',bio],['Use my available Google profile photo',usePhoto]]){const label=n('label',text);label.append(field);form.append(label);}
 save.type='submit';form.append(save);signout.type=reload.type='button';signout.dataset.workstationSignout='true';status.setAttribute('role','status');
 panel.append(legend,photo,initials,email,form,n('p','Profile edits do not change your Google account or newsletter preferences. This screen does not publish your bio. Custom photo upload is not available yet.'),signout,reload,status);settings.prepend(panel);
 const nav=document.querySelector('.connect-nav a[href="#settings"]');if(nav)nav.textContent='Profile & settings';link.href='#settings';link.style.cssText='display:inline-flex;align-items:center;gap:8px;margin:8px 0;min-height:44px';app.querySelector('h1')?.after(link);link.onclick=()=>setTimeout(()=>panel.scrollIntoView({block:'start'}),0);
 function stamp(){return JSON.stringify([name.value,bio.value,usePhoto.checked]);}
 function dirty(){return !!user&&stamp()!==baseline;}
 function lock(){for(const field of [name,bio,usePhoto])field.disabled=busy||!user;save.disabled=busy||!user||uncertain;reload.disabled=busy;signout.disabled=busy||!user;}
 function clear(){epoch++;user=null;uncertain=false;name.value=bio.value=email.textContent='';status.textContent='';photo.hidden=true;photo.removeAttribute('src');initials.textContent='?';initials.hidden=false;usePhoto.checked=true;link.textContent='Profile & settings';baseline=stamp();lock();}
 function paint(value){
  user=value;const meta=user.user_metadata||{};name.value=typeof meta.display_name==='string'?meta.display_name:String(meta.full_name||meta.name||'');bio.value=typeof meta.bio==='string'?meta.bio:'';email.textContent=user.email||'Email unavailable';usePhoto.checked=meta.workstation_photo_enabled!==false;
  const letters=name.value.trim().split(/\s+/).slice(0,2).map(part=>Array.from(part)[0]||'').join('')||'?';initials.textContent=letters;initials.hidden=false;photo.hidden=true;photo.removeAttribute('src');
  const valueURL=meta.avatar_url||meta.picture;if(usePhoto.checked&&typeof valueURL==='string')try{const url=new URL(valueURL);if(url.protocol==='https:'&&!url.username&&!url.password){photo.onerror=()=>{photo.hidden=true;initials.hidden=false;};photo.src=url.href;photo.hidden=false;initials.hidden=true;}}catch{}
  link.textContent=letters+' · Profile & settings';baseline=stamp();lock();
 }
 async function bounded(promise){let timer;try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Account request timed out')),12000);})]);}finally{clearTimeout(timer);}}
 async function load(allowDiscard=false){
  if(busy)return;if(dirty()&&!allowDiscard){status.textContent='Profile refresh paused to preserve your unsaved edits. Choose Reload profile to review the saved version.';return;}
  busy=true;lock();const token=++epoch;status.textContent='Checking your profile…';
  try{const {data,error}=await bounded(client.auth.getUser());if(token!==epoch)return;if(error||!data?.user)throw Error();uncertain=false;paint(data.user);status.textContent='Profile loaded from the account service.';}
  catch{if(token!==epoch)return;status.textContent='Could not verify your profile. Current edits are retained; choose Reload profile when the account service is available.';}
  finally{busy=false;lock();}
 }
 form.onsubmit=async event=>{
  event.preventDefault();if(busy||!user||uncertain)return;let payload;
  try{payload=fields(name.value,bio.value);}catch(error){status.textContent=error.message;return;}
  const expected=user.id,token=epoch;payload.workstation_photo_enabled=usePhoto.checked;busy=true;lock();status.textContent='Saving profile…';let timer,attempted=false;
  try{
   const session=await bounded(client.auth.getSession());if(token!==epoch)return;if(session.error||session.data?.session?.user?.id!==expected)throw Error();
   const jwt=session.data.session.access_token,verified=await bounded(client.auth.getUser(jwt));if(token!==epoch)return;if(verified.error||verified.data?.user?.id!==expected)throw Error();
   const controller=new AbortController();timer=setTimeout(()=>controller.abort(),12000);attempted=true;
   const response=await fetch('https://uwidjnnhdgtrpsymuhwp.supabase.co/auth/v1/user',{method:'PUT',headers:{apikey:'sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN',Authorization:'Bearer '+jwt,'Content-Type':'application/json'},body:JSON.stringify({data:payload}),signal:controller.signal});
   if(!response.ok)throw Error();const result=await response.json(),saved=result.user||result;if(token!==epoch)return;if(saved.id!==expected)throw Error();clearTimeout(timer);
   const readback=await bounded(client.auth.getUser(jwt));if(token!==epoch)return;
   const actual=readback.data?.user,meta=actual?.user_metadata;
   if(readback.error||actual?.id!==expected||!meta||meta.display_name!==payload.display_name||meta.bio!==payload.bio||meta.workstation_photo_enabled!==payload.workstation_photo_enabled)throw Error();
   uncertain=false;paint(actual);status.textContent='Profile saved and read back. Your planner entries were not changed.';
  }catch{
   if(token===epoch){uncertain=attempted;status.textContent=attempted?'Profile save outcome is uncertain. Your edits are retained. Save is disabled until you choose Reload profile and check the server state; no automatic retry was made.':'Account verification failed before a save was sent. Your edits are retained; no profile write was attempted.';}
  }finally{clearTimeout(timer);busy=false;lock();}
 };
 reload.onclick=()=>{if(busy)return;if(dirty()&&!confirm('Discard unsaved profile edits and reload the saved profile?'))return;void load(true);};
 signout.onclick=()=>{if(busy||g.WorkstationApp?.busy){status.textContent='Wait for the current action to finish.';return;}if(dirty()&&!confirm('Discard unsaved profile edits and sign out?'))return;void g.WorkstationApp?.signOut?.();};
 client.auth.onAuthStateChange((event,session)=>{if(event==='SIGNED_OUT'||(user&&session?.user?.id&&session.user.id!==user.id))clear();if(['INITIAL_SESSION','SIGNED_IN'].includes(event))setTimeout(()=>{void load();},0);});
 addEventListener('beforeunload',event=>{if(dirty()){event.preventDefault();event.returnValue='';}});addEventListener('pagehide',clear);addEventListener('pageshow',event=>{if(event.persisted)void load();});clear();void load();
}
if(document.readyState==='complete')boot();else addEventListener('load',boot,{once:true});
})(globalThis);
if(typeof window!=='undefined')window.WorkstationModules?.run('account-controls.js');
