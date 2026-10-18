(()=>{'use strict';
const root=document.documentElement,app=document.querySelector('.connect-app'),nav=document.querySelector('.connect-nav');
if(!app||!nav||root.dataset.workstationLayout==='calm')return;
const anchors=[...nav.querySelectorAll('a')],primary=new Set(['#today','#schedule','#tasks','#focus']);
if(!['#today','#schedule','#tasks','#focus'].every(hash=>anchors.some(a=>a.hash===hash)))return;
root.dataset.workstationLayout='calm';
const themes=[['valley-light','Valley Light'],['midnight-ledger','Midnight Ledger'],['civic-gold','Civic Gold']];
const label=document.createElement('label'),select=document.createElement('select');label.className='calm-theme';label.append(document.createTextNode('Color theme'));
select.id='workstationColorTheme';for(const [value,text] of themes){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}
let theme=root.dataset.theme||'valley-light';try{const saved=localStorage.getItem('209-theme');if(themes.some(t=>t[0]===saved))theme=saved;}catch{}
if(!themes.some(t=>t[0]===theme))theme='valley-light';root.dataset.theme=theme;select.value=theme;
select.onchange=()=>{root.dataset.theme=select.value;try{localStorage.setItem('209-theme',select.value);}catch{}};label.append(select);app.prepend(label);
const more=document.createElement('details'),summary=document.createElement('summary'),links=document.createElement('div');more.className='calm-more';summary.textContent='More tools';more.append(summary,links);
for(const anchor of anchors)if(!primary.has(anchor.hash))links.append(anchor);nav.append(more);
const updateMore=()=>{const current=links.querySelector('[aria-current=page]');summary.textContent=current?'More tools · '+current.textContent:'More tools';};
nav.addEventListener('click',event=>{if(event.target.closest('a')){more.open=false;setTimeout(updateMore,0);}});addEventListener('hashchange',()=>setTimeout(updateMore,0));updateMore();
for(const details of app.querySelectorAll('details.quick-capture'))details.open=false;
const account=document.getElementById('account'),demo=document.getElementById('demo');
if(account&&demo&&account.parentElement===demo.parentElement){const details=document.createElement('details'),caption=document.createElement('summary');details.className='calm-account';caption.textContent='Account and demo options';account.parentElement.append(details);details.append(caption,account,demo);}
const schedule=document.querySelector('[data-view=schedule]');
if(schedule){const link=document.createElement('a');link.href='#schedule';link.textContent='Open today’s schedule';link.className='btn ghost';const today=document.querySelector('[data-view=today]');if(today)today.append(link);}
})();
