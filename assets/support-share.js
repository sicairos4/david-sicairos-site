(()=>{
'use strict';
const caps={Threads:500,Bluesky:300,X:280};
function message(text,url){text=String(text).trim();return text.includes(url)?text:(text+'\n\n'+url).trim();}
function count(text){return typeof Intl.Segmenter==='function'?Array.from(new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(text)).length:Array.from(text).length;}
function allowed(name,text){return !caps[name]||count(text)<=caps[name];}
if(typeof module!=='undefined'&&module.exports)module.exports={message,count,allowed};
if(typeof document==='undefined')return;
const url=new URL('../donations.html',document.currentScript.src).href;
const status=document.getElementById('share-status'),link=document.getElementById('share-link'),draft=document.getElementById('share-message'),host=document.getElementById('platform-shares'),section=document.getElementById('share');
if(!status||!link||!draft||!host||!section)return;
link.value=url;draft.readOnly=false;draft.maxLength=2000;
draft.value='Independent reporting needs people behind it.\n\nThe Warchest supports public-records work, reporting and practical tools across the 209 ecosystem.\n\nGive if you can. Share if you cannot.';
const composer=document.createElement('div');composer.className='share-composer';
const label=document.querySelector('label[for="share-message"]');if(!label)return;label.textContent='Make this caption yours';composer.append(label,draft);
const counter=document.createElement('p');counter.className='support-caption';composer.append(counter);
section.insertBefore(composer,section.querySelector('.support-actions'));section.insertBefore(host,composer.nextSibling);
const details=section.querySelector('details');if(details)details.querySelector('summary').textContent='Support page link';
const hint=document.createElement('p');hint.className='support-caption';hint.textContent='Edit first, then choose a platform. Short-post links use conservative limits: X 280, Bluesky 300, Threads 500 characters including the link. Facebook and LinkedIn need your caption pasted into their composer.';host.before(hint);
const current=()=>message(draft.value,url);
async function copy(value,field=draft){try{await navigator.clipboard.writeText(value);status.textContent='Caption copied. Review it before posting.';return true;}catch(e){const d=field.closest('details');if(d)d.open=true;field.focus();field.select();status.textContent='Copy the selected text manually. Nothing has been posted.';return false;}}
document.getElementById('copy-support').onclick=()=>copy(url,link);document.getElementById('copy-message').onclick=()=>copy(current());
document.getElementById('native-share').onclick=async()=>{if(!navigator.share){await copy(current());return;}try{await navigator.share({title:'The Warchest',text:current()});status.textContent='Share menu closed; posting is not verified by this site.';}catch(e){if(e.name!=='AbortError')status.textContent='Use Copy message or choose a platform.';}};
const specs=[['Threads','threads',t=>'https://www.threads.net/intent/post?text='+encodeURIComponent(t),false],['Bluesky','bluesky',t=>'https://bsky.app/intent/compose?text='+encodeURIComponent(t),false],['X','x',t=>'https://twitter.com/intent/tweet?text='+encodeURIComponent(t),false],['Facebook','facebook',()=> 'https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url),true],['LinkedIn',null,()=> 'https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(url),true],['WhatsApp','whatsapp',t=>'https://wa.me/?text='+encodeURIComponent(t),false],['Email',null,t=>'mailto:?subject='+encodeURIComponent('The Warchest')+'&body='+encodeURIComponent(t),false]];
const icons={LinkedIn:'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="1" width="22" height="22" rx="3" fill="#0a66c2"/><path fill="white" d="M5 9h3v10H5zm1.5-5a1.6 1.6 0 1 0 0 3.2 1.6 1.6 0 0 0 0-3.2zM10 9h3v1.4c.7-1.1 1.6-1.7 3-1.7 2.7 0 3 1.8 3 4.1V19h-3v-5.5c0-1.3-.3-2.1-1.4-2.1-1.3 0-1.6.9-1.6 2.1V19h-3z"/></svg>',Email:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="3"/><path d="m3 6 9 7 9-7"/></svg>'};
const entries=[];host.replaceChildren();
specs.forEach(([name,slug,target,copyFirst])=>{const a=document.createElement('a');a.className='platform-icon';a.setAttribute('aria-label','Share on '+name);a.target=name==='Email'?'_self':'_blank';a.rel='noopener noreferrer';
if(slug){const img=document.createElement('img');img.src='https://cdn.simpleicons.org/'+slug;img.width=23;img.height=23;img.alt='';img.loading='lazy';img.onerror=()=>{img.remove();a.textContent=name;};a.append(img);}else a.innerHTML=icons[name];
a.addEventListener('click',async e=>{const text=current();if(!allowed(name,text)){e.preventDefault();status.textContent='Shorten the caption for '+name+' to the conservative '+caps[name]+'-character limit, including the support link.';draft.focus();return;}if(copyFirst){e.preventDefault();const copied=await copy(text);const next=document.createElement('a');next.href=target(text);next.target='_blank';next.rel='noopener noreferrer';next.textContent='Continue to '+name;status.append(' ',next);if(copied)status.prepend('Paste the copied caption into your post. ');}else status.textContent='Review your caption in '+name+' before posting.';});
entries.push({a,name,target});host.append(a);});
function refresh(){const text=current();counter.textContent=count(text)+' characters including the support link';entries.forEach(({a,name,target})=>{const ok=allowed(name,text);a.href=ok?target(text):'#share';a.setAttribute('aria-disabled',String(!ok));a.title=ok?name:name+' — shorten caption';});}
draft.addEventListener('input',refresh);entries.forEach(({a})=>{a.addEventListener('focus',refresh);a.addEventListener('pointerdown',refresh);a.addEventListener('contextmenu',refresh);});refresh();
const style=document.createElement('style');style.textContent='.share-composer{margin:18px 0}.share-composer label{display:block;font-weight:700;margin-bottom:8px}.share-composer textarea{display:block!important;width:100%;min-height:160px;resize:vertical;background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:12px}.support-actions .platform-icon{width:48px;height:48px;padding:10px;display:inline-flex;align-items:center;justify-content:center;background:#fff;color:#17251d}.platform-icon svg,.platform-icon img{width:23px;height:23px}.platform-icon[aria-disabled=true]{opacity:.5}.platform-icon:focus-visible{outline:3px solid #2786c6;outline-offset:3px}';document.head.append(style);
})();
