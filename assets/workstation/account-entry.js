(()=>{'use strict';
const A=globalThis.WorkstationApp,C=globalThis.ConnectCore,main=document.getElementById('workstationMain');
if(!A||!C||!main)return;
const key='209-workstation-before-signin-v1',el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
const strip=el('section'),state=el('p'),signin=el('a','Sign in'),notice=el('p');
strip.id='workstationAccountEntry';strip.setAttribute('aria-label','Account access');state.setAttribute('role','status');notice.setAttribute('role','status');
signin.href=new URL('../login.html',location.href).href;strip.append(state,signin,notice);main.prepend(strip);
const panel=el('section'),heading=el('h2','Your work from before sign-in'),detail=el('p'),restore=el('button','Use this work in the selected day'),download=el('button','Export this work'),keep=el('button','Discard preserved copy; keep current workspace');
panel.hidden=true;for(const button of [restore,download,keep])button.type='button';panel.append(heading,detail,restore,download,keep);strip.after(panel);
let saved=null;
try{const raw=sessionStorage.getItem(key);if(raw&&raw.length<=2000000){const value=JSON.parse(raw);if(value.version===1&&typeof value.day==='string'&&value.record&&Array.isArray(value.record.plan?.workspaceTasks)&&Array.isArray(value.record.plan?.scheduleBlocks)&&Array.isArray(value.record.plan?.goalEntries)){C.day(value.day);saved={...value,record:C.normalize(value.record)};}}}catch{notice.textContent='A previous sign-in draft could not be read. It has not been imported.';}
function remember(event){if(A.accountId)return;
 if(A.busy){event.preventDefault();notice.textContent='Wait for the selected day to finish loading before signing in.';return;}
 try{const value={version:1,day:A.day,hash:location.hash,record:A.snapshot()};const raw=JSON.stringify(value);if(raw.length>2000000)throw Error();sessionStorage.setItem(key,raw);}
 catch{event.preventDefault();notice.textContent='Your work could not be preserved for sign-in. Export it with Export day before leaving.';}
}
signin.addEventListener('click',remember);
function refresh(){const active=!!(A.accountId||A.sessionAccountId);for(const button of document.querySelectorAll('#logout,[data-workstation-signout]'))button.hidden=!active;state.textContent=A.accountId?'Signed in. Save selected day to keep changes in your account.':'Use the tools here. Sign in when you want to load or save account records.';signin.hidden=!!A.accountId;
 const identity=document.getElementById('memberIdentity');if(identity)identity.textContent=A.accountId?'YOUR ACCOUNT WORKSPACE':'209 CONNECT WORKSTATION';
 panel.hidden=!saved;if(saved){const same=A.day===saved.day;detail.textContent='Preserved day: '+saved.day+'. '+(same?'Choose whether to use it here. Replacing the selected day requires confirmation; it will still need Save selected day.':'Choose that date with Change day before using this work, or export it.')+' Restoring does not discard this recovery copy. Export it before closing the tab or signing out; discard it explicitly only when you no longer need it.';restore.disabled=A.busy||!same;download.disabled=A.busy;keep.disabled=A.busy;}
}
function forget(){try{sessionStorage.removeItem(key);}catch{}saved=null;panel.hidden=true;}
restore.onclick=()=>{if(!saved||A.busy||A.day!==saved.day)return;if(!confirm('Replace the current selected day with your preserved work? This does not save to your account. Export the current day first if you want both copies.'))return;const draft=C.normalize(saved.record);try{A.change(record=>{record.plan=draft.plan;record.journal=draft.journal;record.lesson=draft.lesson;});document.querySelectorAll('[data-bind]').forEach(field=>{field.value=field.dataset.bind.split('.').reduce((value,key)=>value?.[key],draft)??(field.dataset.bind==='plan.capacity'?'Steady':'');});document.querySelectorAll('[data-routine]').forEach(field=>{field.checked=!!draft.plan.routineChecks?.[field.dataset.routine];});notice.textContent='Preserved work restored as unsaved edits. Choose Save selected day to keep it. The recovery copy remains available here for export or another restore; discard it explicitly only after confirming you no longer need it.';}catch{notice.textContent='The preserved work could not be fully restored. The recovery copy remains available for export; review current edits before retrying.';}refresh();};
download.onclick=()=>{if(!saved||A.busy)return;const url=URL.createObjectURL(new Blob([JSON.stringify(saved,null,2)],{type:'application/json'})),link=el('a');link.href=url;link.download='209-workstation-preserved-'+saved.day+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notice.textContent='Unencrypted export requested. Keep the file private.';};
keep.onclick=()=>{if(A.busy||!saved)return;if(!confirm('Discard the preserved pre-sign-in copy and keep the current workspace? Export that copy first if you need it.'))return;forget();notice.textContent='Current workspace kept. Nothing was uploaded or saved by this choice.';};
addEventListener('workstation:account',()=>queueMicrotask(refresh));addEventListener('workstation:signed-out',()=>{forget();notice.textContent='Signed out on this device. The preserved sign-in copy was cleared.';refresh();});addEventListener('workstation:render',()=>queueMicrotask(refresh));addEventListener('pageshow',refresh);refresh();
})();
