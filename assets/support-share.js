(()=>{
'use strict';
const url=new URL('../donations.html',document.currentScript.src).href;
const status=document.getElementById('share-status'),link=document.getElementById('share-link'),draft=document.getElementById('share-message'),host=document.getElementById('platform-shares'),section=document.getElementById('share');
if(!status||!link||!draft||!host||!section)return;
const preset='Independent reporting needs people behind it.\n\nThe Warchest supports public-records work, reporting and practical tools across the 209 ecosystem.\n\nGive if you can. Share if you cannot.';
link.value=url;draft.readOnly=false;draft.maxLength=2000;draft.value=preset;
const composer=document.createElement('div');composer.className='share-composer';
const label=document.querySelector('label[for="share-message"]');label.textContent='Make this caption yours';composer.append(label,draft);
const count=document.createElement('p');count.className='support-caption';composer.append(count);
section.insertBefore(composer,section.querySelector('.support-actions'));
section.insertBefore(host,composer.nextSibling);
const oldDetails=section.querySelector('details');if(oldDetails)oldDetails.querySelector('summary').textContent='Support page link';
const hint=document.createElement('p');hint.className='support-caption';hint.textContent='Edit the caption, then choose a platform. Facebook and LinkedIn share the link; use Copy message to paste your edited caption there. Final posting stays under your control.';host.before(hint);
function message(){const text=draft.value.trim();return text.includes(url)?text:(text+'\n\n'+url).trim();}
function update(){count.textContent=Array.from(message()).length+' characters including the support link';}draft.addEventListener('input',update);update();
async function copy(value,field=draft){try{await navigator.clipboard.writeText(value);status.textContent='Copied. Paste into your post and review before sharing.';return true;}catch(e){const details=field.closest('details');if(details)details.open=true;field.focus();field.select();status.textContent='Copy the selected text using your device controls, then paste it into your post.';return false;}}
document.getElementById('copy-support').onclick=()=>copy(url,link);document.getElementById('copy-message').onclick=()=>copy(message());
document.getElementById('native-share').onclick=async()=>{if(!navigator.share){await copy(message());return;}try{await navigator.share({title:'The Warchest',text:message()});status.textContent='Share menu closed. Posting is not verified by this site.';}catch(e){if(e.name!=='AbortError')status.textContent='Use Copy message or a platform icon below.';}};
const specs=[
 ['Threads','threads',text=>'https://www.threads.net/intent/post?text='+encodeURIComponent(text),false],
 ['Bluesky','bluesky',text=>'https://bsky.app/intent/compose?text='+encodeURIComponent(text),false],
 ['X','x',text=>'https://twitter.com/intent/tweet?text='+encodeURIComponent(text),false],
 ['Facebook','facebook',()=> 'https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url),true],
 ['LinkedIn',null,()=> 'https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(url),true],
 ['WhatsApp','whatsapp',text=>'https://wa.me/?text='+encodeURIComponent(text),false],
 ['Email',null,text=>'mailto:?subject='+encodeURIComponent('The Warchest — Support 209')+'&body='+encodeURIComponent(text),false]
];
const icons={LinkedIn:'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="1" width="22" height="22" rx="3" fill="#0a66c2"/><path fill="white" d="M5 9h3v10H5zm1.5-5a1.6 1.6 0 1 0 0 3.2 1.6 1.6 0 0 0 0-3.2zM10 9h3v1.4c.7-1.1 1.6-1.7 3-1.7 2.7 0 3 1.8 3 4.1V19h-3v-5.5c0-1.3-.3-2.1-1.4-2.1-1.3 0-1.6.9-1.6 2.1V19h-3z"/></svg>',Email:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="3"/><path d="m3 6 9 7 9-7"/></svg>'};
host.replaceChildren();specs.forEach(([name,slug,target,copyFirst])=>{const a=document.createElement('a');a.className='platform-icon';a.setAttribute('aria-label','Share on '+name);a.title=name+(copyFirst?' — copy caption, then paste':'');a.href=target(message());if(name!=='Email'){a.target='_blank';a.rel='noopener noreferrer';}
 if(slug){const img=document.createElement('img');img.src='https://cdn.simpleicons.org/'+slug;img.width=23;img.height=23;img.alt='';img.loading='lazy';img.onerror=()=>{img.remove();a.textContent=name;};a.append(img);}else{a.innerHTML=icons[name];}
 a.addEventListener('click',()=>{a.href=target(message());if(copyFirst){void copy(message());}else{status.textContent='Opening '+name+' with your caption. Review it there before posting.';}});host.append(a);});
const style=document.createElement('style');style.textContent='.share-composer{margin:18px 0}.share-composer label{display:block;font-weight:700;margin-bottom:8px}.share-composer textarea{display:block!important;width:100%;min-height:160px;resize:vertical;background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:12px}.support-actions .platform-icon{width:48px;height:48px;padding:10px;display:inline-flex;align-items:center;justify-content:center}.platform-icon svg,.platform-icon img{width:23px;height:23px}.platform-icon:focus-visible{outline:3px solid #2786c6;outline-offset:3px}';document.head.append(style);
})();
