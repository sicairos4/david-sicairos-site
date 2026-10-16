(async()=>{
'use strict';
const grid=document.getElementById('videos'),status=document.getElementById('catalog-status');if(!grid||!status)return;
const channel='UCDMa9oEWj4i6KFOkjF79qLg';
const fallback=[{id:'L3K9sP8yprM',title:'Holding Local Government Institutions Accountable'},{id:'KGAoSq8mAis',title:'Entrepreneurial Kickstart: How To Cultivate A Growth Mindset'},{id:'iWsc_i89XF8',title:'Turning social media noise into an SEO powerhouse'},{id:'JQaYI2aLZIw',title:'How To Build Strategic Partnerships — Entrepreneurial Kickstart'}];
function valid(v){return v&&/^[A-Za-z0-9_-]{11}$/.test(v.id)&&typeof v.title==='string'&&v.title.trim()&&v.title.length<=500;}
function render(videos){
 grid.replaceChildren();
 videos.forEach(video=>{
  const card=document.createElement('article');card.className='media-card';
  const stage=document.createElement('div');stage.className='video-stage';
  const button=document.createElement('button');button.type='button';button.setAttribute('aria-label','Play '+video.title+' on this page');
  const image=document.createElement('img');image.src='https://i.ytimg.com/vi/'+video.id+'/hqdefault.jpg';image.alt='';image.loading='lazy';image.width=480;image.height=360;image.onerror=()=>{image.hidden=true;};
  const label=document.createElement('span');label.className='play-label';label.textContent='▶ Play here';button.append(image,label);stage.append(button);
  const heading=document.createElement('h2');heading.textContent=video.title;
  const note=document.createElement('p');note.className='media-note';note.textContent='Click to play without leaving this page.';card.append(stage,heading,note);
  if(video.published_at){const date=new Date(video.published_at);if(Number.isFinite(date.getTime())){const time=document.createElement('p');time.className='media-note';time.textContent='Published '+date.toLocaleDateString();card.append(time);}}
  grid.append(card);
  button.onclick=()=>{
   const iframe=document.createElement('iframe');iframe.title=video.title;iframe.src='https://www.youtube-nocookie.com/embed/'+video.id+'?autoplay=1&playsinline=1&rel=0';iframe.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';stage.replaceChildren(iframe);iframe.focus();
   note.textContent='YouTube playback restrictions may still apply. If a video is unavailable, choose another below.';
   const reset=document.createElement('button');reset.type='button';reset.textContent='Close player';reset.onclick=()=>{stage.replaceChildren(button);reset.remove();button.focus();};note.append(' ',reset);
  };
 });
}
function validate(c){
 if(!c||c.version!==1||c.channel_id!==channel||!Array.isArray(c.videos)||c.videos.length<1||c.videos.length>15||!c.videos.every(valid)||new Set(c.videos.map(v=>v.id)).size!==c.videos.length)throw Error('Invalid catalog');
 const age=Date.now()-Date.parse(c.collected_at),expiry=Date.parse(c.expires_at);
 if(!Number.isFinite(age)||!Number.isFinite(expiry)||age< -300000||age>172800000||expiry<=Date.now())throw Error('Stale catalog');
 return c;
}
let cached=null;try{cached=validate(JSON.parse(localStorage.getItem('209-youtube-public-catalog')));}catch(e){}
render(cached?cached.videos:fallback);
status.textContent=cached?'Saved catalog from '+new Date(cached.collected_at).toLocaleString()+'. Checking for updates…':'Featured selections. Checking for the latest catalog…';
try{
 const key='sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN';
 const response=await fetch('https://uwidjnnhdgtrpsymuhwp.supabase.co/rest/v1/site_content?key=eq.youtube_catalog&select=value',{headers:{apikey:key,Authorization:'Bearer '+key},cache:'no-store',signal:AbortSignal.timeout(8000)});
 if(!response.ok)throw Error('Catalog unavailable');
 const rows=await response.json();const catalog=validate(rows?.[0]?.value);
 render(catalog.videos);status.textContent='Latest catalog collected '+new Date(catalog.collected_at).toLocaleString()+'. Scheduled hourly; this page updates on reload.';
 try{localStorage.setItem('209-youtube-public-catalog',JSON.stringify(catalog));}catch(e){}
}catch(e){status.textContent=cached?'Live refresh unavailable. Showing the saved catalog collected '+new Date(cached.collected_at).toLocaleString()+'.':'Live catalog unavailable. Showing featured selections instead.';}
})();
