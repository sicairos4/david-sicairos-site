(()=>{'use strict';
let sequence=0;
addEventListener('workstation:morning-routine-updated',()=>{
const status=document.getElementById('status');
if(status)status.textContent='Ready. Morning routine template applied ('+(++sequence)+'); review and save selected day.';
});
if(document.currentScript?.src){const url=new URL('carry-forward.js',document.currentScript.src).href;if(![...document.scripts].some(script=>script.src===url)){const script=document.createElement('script');script.src=url;script.async=false;script.onerror=()=>{const host=document.querySelector('[data-view=tasks]');if(host){const notice=document.createElement('p');notice.setAttribute('role','status');notice.textContent='Task carry-forward could not load. Reload to retry. Existing tasks are unchanged.';host.append(notice);}};document.head.append(script);}}
})();
