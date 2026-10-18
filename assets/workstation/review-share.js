(function(g){'use strict';
async function shareSnapshot(content, env={}) {
  if(typeof content!=='string'||!content.length||content.length>100000)throw Error('Preview content is missing or too large.');
  const nav=env.navigator||g.navigator, FileType=env.File||g.File;
  if(!nav||typeof nav.share!=='function')return {status:'unavailable'};
  const title='209 Workstation - Weekly Review';
  let payload={title,text:content},mode='text';
  if(typeof FileType==='function'&&typeof nav.canShare==='function'){
    try{const file=new FileType([content],'209-weekly-review.txt',{type:'text/plain'});
      if(nav.canShare({files:[file]})){payload={title,files:[file]};mode='file';}
    }catch{}
  }
  try{await nav.share(payload);return {status:'shared',mode};}
  catch(error){if(error?.name==='AbortError')return {status:'cancelled'};throw Error('Sharing did not finish. Use Copy text or Save file.');}
}
if(typeof module!=='undefined'&&module.exports){module.exports={shareSnapshot};return;}
if(typeof document==='undefined'||g.WorkstationReviewShare)return;
g.WorkstationReviewShare={shareSnapshot};
function attach(){
  const panel=document.getElementById('workstationPrintPreview');
  if(!panel||panel.querySelector('[data-review-share]'))return;
  const field=panel.querySelector('textarea[aria-label="Exact export contents"]'),controls=panel.querySelector('.print-actions');
  if(!field||!controls)return;
  const button=document.createElement('button');button.type='button';button.dataset.reviewShare='true';button.textContent='Share preview';
  const status=document.createElement('p');status.setAttribute('role','status');status.textContent='Sharing includes only this preview. Choose a trusted destination.';
  controls.append(button);panel.append(status);
  button.onclick=async()=>{if(!panel.isConnected||button.disabled)return;button.disabled=true;
    try{const result=await shareSnapshot(field.value);if(!panel.isConnected)return;
      status.textContent=result.status==='cancelled'?'Sharing cancelled.':result.status==='unavailable'?'System sharing is unavailable. Use Copy text or Save file.':'Share dialog completed. Delivery or saving has not been verified.';
    }catch(error){if(panel.isConnected)status.textContent=error.message;}
    finally{if(panel.isConnected)button.disabled=false;}
  };
}
const observer=new MutationObserver(attach);observer.observe(document.body,{childList:true,subtree:true});attach();
g.addEventListener('pagehide',()=>observer.disconnect(),{once:true});
g.addEventListener('pageshow',()=>{observer.observe(document.body,{childList:true,subtree:true});attach();});
})(globalThis);
