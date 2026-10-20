(()=>{'use strict';
let sequence=0;
addEventListener('workstation:morning-routine-updated',()=>{
const status=document.getElementById('status');
if(status)status.textContent='Ready. Morning routine template applied ('+(++sequence)+'); review and save selected day.';
});
if(!document.currentScript?.src)return;
const base=document.currentScript.src;
for(const [name,label,selector] of [['carry-forward.js','Task carry-forward','[data-view=tasks]'],['day-tools.js','Habits, private notebook and day restore','[data-view=settings]']]){
const url=new URL(name,base).href;if([...document.scripts].some(script=>script.src===url))continue;
const script=document.createElement('script');script.src=url;script.async=false;
script.onerror=()=>{const host=document.querySelector(selector);if(!host)return;const notice=document.createElement('p');notice.setAttribute('role','status');notice.textContent=label+' could not load. Reload to retry. Existing records are unchanged.';host.append(notice);};
document.head.append(script);
}
})();
