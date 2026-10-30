const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync(require('node:path').join(__dirname,'../assets/workstation/account-profile.js'),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function harness(){
 const nodes=[],events={};let authEvent,getUserImpl,fetchImpl,writes=0;
 class E{constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.style={};this.dataset={};this.value='';nodes.push(this);}append(...x){this.children.push(...x);}prepend(x){this.children.unshift(x);}after(){}setAttribute(){}removeAttribute(k){delete this[k];}querySelector(){return heading;}scrollIntoView(){}}
 const app=new E('main'),settings=new E('section'),heading=new E('h1'),nav=new E('a');
 let stored={id:'u1',email:'test@example.invalid',user_metadata:{display_name:'Saved Name',bio:'saved',workstation_photo_enabled:true}};
 getUserImpl=async()=>({data:{user:structuredClone(stored)},error:null});
 fetchImpl=async(_url,options)=>{stored.user_metadata={...stored.user_metadata,...JSON.parse(options.body).data};return {ok:true,json:async()=>({user:structuredClone(stored)})};};
 const context={document:{readyState:'complete',createElement:t=>new E(t),getElementById:id=>nodes.find(n=>n.id===id)||null,querySelector:s=>s==='.connect-app'?app:s==='[data-view="settings"]'?settings:nav},
 WorkstationAccountClient:{auth:{getUser:(...a)=>getUserImpl(...a),getSession:async()=>({data:{session:{user:{id:'u1'},access_token:'synthetic-offline-token'}},error:null}),onAuthStateChange:f=>{authEvent=f;}}},
 WorkstationApp:{busy:false,signOut:()=>{}},fetch:(...a)=>{writes++;return fetchImpl(...a);},URL,AbortController,setTimeout,clearTimeout,confirm:()=>true,addEventListener:(name,fn)=>{events[name]=fn;}};
 vm.runInNewContext(source,context);
 const fieldset=nodes.find(n=>n.id==='accountProfilePanel'),form=fieldset.children.find(n=>n.tag==='form');
 const labels=form.children.filter(n=>n.tag==='label');const name=labels[0].children[0],bio=labels[1].children[0],save=form.children.find(n=>n.tag==='button'),reload=nodes.find(n=>n.textContent==='Reload profile');
 const status=fieldset.children.at(-1);
 return {context,name,bio,save,reload,status,form,events,auth:(...a)=>authEvent(...a),setGet:f=>getUserImpl=f,setFetch:f=>fetchImpl=f,get writes(){return writes;},stored};
}
test('automatic same-account refresh preserves unsaved profile edits',async()=>{const h=harness();await flush();h.name.value='Unsaved Name';h.auth('SIGNED_IN',{user:{id:'u1'}});await new Promise(r=>setTimeout(r,5));assert.equal(h.name.value,'Unsaved Name');assert.match(h.status.textContent,/preserve/);});
test('failed profile read preserves edits and unlocks controls',async()=>{const h=harness();await flush();h.name.value='Unsaved';h.setGet(async()=>{throw Error('offline');});h.reload.onclick();await flush();assert.equal(h.name.value,'Unsaved');assert.equal(h.name.disabled,false);});
test('uncertain write disables resubmission until explicit reload',async()=>{const h=harness();await flush();h.name.value='New Name';h.setFetch(async()=>{throw Error('connection lost');});await h.form.onsubmit({preventDefault(){}});assert.equal(h.writes,1);assert.equal(h.save.disabled,true);assert.equal(h.name.value,'New Name');await h.form.onsubmit({preventDefault(){}});assert.equal(h.writes,1);h.reload.onclick();await flush();assert.equal(h.save.disabled,false);});
test('successful save requires matching server readback',async()=>{const h=harness();await flush();h.name.value='Verified Name';await h.form.onsubmit({preventDefault(){}});assert.equal(h.name.value,'Verified Name');assert.match(h.status.textContent,/saved and read back/);assert.equal(h.save.disabled,false);});
test('mismatched server readback is not reported as saved',async()=>{const h=harness();await flush();h.name.value='New Name';h.setFetch(async()=>({ok:true,json:async()=>({user:{id:'u1'}})}));await h.form.onsubmit({preventDefault(){}});assert.match(h.status.textContent,/uncertain/);assert.equal(h.save.disabled,true);});
test('cancelled reload makes no account request and retains edits',async()=>{const h=harness();await flush();h.name.value='Keep';let reads=0;h.setGet(async()=>{reads++;return {data:{user:h.stored}};});h.context.confirm=()=>false;h.reload.onclick();await flush();assert.equal(reads,0);assert.equal(h.name.value,'Keep');});
test('late read after sign-out cannot repopulate private fields',async()=>{const h=harness();await flush();let resolve;h.setGet(()=>new Promise(r=>resolve=r));h.reload.onclick();assert.equal(h.name.disabled,true);h.auth('SIGNED_OUT',null);resolve({data:{user:h.stored}});await flush();assert.equal(h.name.value,'');assert.equal(h.save.disabled,true);});
