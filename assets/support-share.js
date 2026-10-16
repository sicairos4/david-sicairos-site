(()=>{
'use strict';
const url=new URL('../donations.html',document.currentScript.src).href;
const text='Support independent reporting, public-records work and practical tools across the 209 ecosystem.';
const message=text+' '+url;
const status=document.getElementById('share-status');
const link=document.getElementById('share-link');
const draft=document.getElementById('share-message');
if(!status||!link||!draft)return;link.value=url;draft.value=message;
async function copy(value,field){try{await navigator.clipboard.writeText(value);status.textContent='Copied. Paste it into your preferred app.';}catch(e){field.focus();field.select();status.textContent='Select and copy the text above using your device controls.';}}
document.getElementById('copy-support').onclick=()=>copy(url,link);
document.getElementById('copy-message').onclick=()=>copy(message,draft);
document.getElementById('native-share').onclick=async()=>{if(!navigator.share){await copy(message,draft);return;}try{await navigator.share({title:'Support the 209',text,url});status.textContent='Share menu closed. Publication is not verified by this page.';}catch(e){if(e.name!=='AbortError'){status.textContent='Sharing unavailable. Use Copy link or Copy message.';}}};
const destinations=[['Facebook','https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url)],['LinkedIn','https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(url)],['Bluesky','https://bsky.app/intent/compose?text='+encodeURIComponent(message)],['WhatsApp','https://wa.me/?text='+encodeURIComponent(message)],['Email','mailto:?subject='+encodeURIComponent('Support the 209')+'&body='+encodeURIComponent(message)]];
const host=document.getElementById('platform-shares');
destinations.forEach(([name,href])=>{const a=document.createElement('a');a.textContent=name;a.href=href;if(!href.startsWith('mailto:')){a.target='_blank';a.rel='noopener noreferrer';}host.append(a);});
})();
