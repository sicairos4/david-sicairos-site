(()=>{
'use strict';
const sections=Array.from(document.querySelectorAll('[data-shelf-section]'));
function rail(section){return section.id==='wellness'?(section.querySelector('#my-store-17851284 .grid__products')||section.querySelector('.brand-shelf')):section.querySelector('.brand-shelf');}
function refresh(){sections.forEach(section=>{const r=rail(section),controls=section.querySelector('.shelf-controls');if(!r||!controls)return;controls.hidden=r.scrollWidth<=r.clientWidth+4;if(section.id==='wellness'&&r.matches('.grid__products')){r.tabIndex=0;r.setAttribute('role','region');r.setAttribute('aria-label','dBeastco products; scroll horizontally for more');}});}
sections.forEach(section=>{section.querySelectorAll('[data-direction]').forEach(button=>{button.addEventListener('click',()=>{const r=rail(section);if(!r)return;r.scrollBy({left:Number(button.dataset.direction)*Math.max(230,r.clientWidth*.8),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});});});});
let pending=false;function schedule(){if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;refresh();});}
window.addEventListener('resize',schedule);
const store=document.getElementById('my-store-17851284');
new MutationObserver(schedule).observe(store,{childList:true,subtree:true});
const status=document.getElementById('wellness-status'),fallback=document.getElementById('wellness-fallback');
function ready(){fallback.hidden=true;status.textContent='Browse products below. Swipe the row or use the arrows. Product details and checkout use the live dBeastco store.';schedule();}
const script=document.createElement('script');script.src='https://app.ecwid.com/script.js?17851284&data_platform=code';script.charset='utf-8';script.setAttribute('data-cfasync','false');
script.onerror=()=>{status.textContent='The live catalog could not load. Product links below remain available; other brands are still browsable.';fallback.hidden=false;};
script.onload=()=>{try{if(typeof window.xProductBrowser!=='function')throw Error('Store unavailable');if(window.Ecwid?.OnPageLoaded?.add)window.Ecwid.OnPageLoaded.add(ready);window.xProductBrowser('id=my-store-17851284','views=grid(3,12) list(12) table(12)','categoryView=grid','searchView=grid');status.textContent='Connecting to the live product catalog…';}catch(e){status.textContent='The live catalog could not initialize. Use the product links below.';fallback.hidden=false;}};
document.body.append(script);refresh();
})();
