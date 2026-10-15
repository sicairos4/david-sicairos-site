/* Shared toolbar: asset-relative routes, consistent breakpoint, keyboard support. */
(()=>{
const script=document.currentScript;
const base=new URL('../',script&&script.src?script.src:new URL('assets/topbar.js',location.href));
const toolRoutes=new Map([['members/','workspace'],['members/index.html','workspace'],['members/workspace.html','workspace'],['members/dashboard.html','profile'],['members/products.html','planner'],['members/chat.html','chat'],['https://sicairos4.github.io/209audit-index-tracker/','tracker'],['https://sicairos4.github.io/209audit-index-tracker/index.html','tracker'],['https://sicairos4.github.io/209audit-cpra-playbook/','cpra'],['https://sicairos4.github.io/209audit-cpra-playbook/index.html','cpra']].map(([p,id])=>[new URL(p,base).href,id]));
const href=p=>{const u=new URL(p,base);const tool=toolRoutes.get(u.href);return tool?new URL('tools.html#'+tool,base).href:u.href};
// Keep ordinary in-site tool navigation inside the shell. Downloads, deep links,
// explicit standalone links and modified clicks retain their original behavior.
document.addEventListener('click',e=>{if(e.defaultPrevented||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;const a=e.target.closest('a[href]');if(!a||a.hasAttribute('download')||a.hasAttribute('data-standalone'))return;let u;try{u=new URL(a.href)}catch{return}const tool=toolRoutes.get(u.href);if(!tool)return;e.preventDefault();location.assign(new URL('tools.html#'+tool,base).href)});
const subscribe='https://209connect.beehiiv.com/?modal=signup';
function ready(){
 const header=document.querySelector('header.top');if(!header||header.dataset.toolbarReady)return;
 const row=header.querySelector('.top-in'),nav=header.querySelector('.nav');if(!row||!nav)return;
 header.dataset.toolbarReady='true';header.classList.add('site-toolbar');
 const style=document.createElement('style');style.textContent=`
 .site-toolbar{position:sticky;top:0;z-index:1000;background:var(--bg,#fff);color:var(--text,#183e30);transform:none!important}
 .site-toolbar .top-in{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:nowrap;min-height:56px;box-sizing:border-box}
 .site-toolbar .brand{flex-shrink:0;white-space:nowrap}
 .site-toolbar .nav{display:flex;position:static;flex-direction:row;align-items:center;gap:10px;padding:0;overflow:visible;width:auto;flex:1;min-width:0}
 .site-toolbar .nav-left,.site-toolbar .nav-right{display:flex;align-items:center;flex-direction:row;gap:6px;flex-wrap:nowrap}
 .site-toolbar .nav-right{margin-left:auto}
 .site-toolbar a,.site-toolbar button{box-sizing:border-box}
 .site-toolbar .nav-left>a,.site-toolbar .nav-group>button{font:inherit;font-size:14px;color:inherit;background:transparent;border:0;border-radius:8px;min-height:44px;padding:10px;text-decoration:none;white-space:nowrap;cursor:pointer}
 .site-toolbar .nav-group{position:relative;width:auto}
 .site-toolbar .dropdown{display:none;position:absolute;top:100%;left:0;min-width:220px;max-height:65vh;overflow:auto;padding:8px;background:var(--panel,#fff);border:1px solid var(--line,#dfe7e1);border-radius:10px;opacity:1;visibility:visible;transform:none;z-index:1001}
 .site-toolbar .nav-group.open>.dropdown{display:block}
 .site-toolbar .dropdown a{display:block;min-height:44px;padding:10px;color:inherit;text-decoration:none;white-space:normal}
 .site-toolbar .nav-group:not(.open)>.dropdown{display:none}
 .site-toolbar .nav-burger{display:none;border:1px solid var(--line,#b8c8bf);background:var(--panel,#fff);color:inherit;border-radius:8px;width:44px;min-width:44px;height:44px;padding:0;font-size:22px;cursor:pointer}
 .site-toolbar .theme-toggle{width:44px;min-width:44px;height:44px;padding:0;color:inherit;background:var(--panel,#fff);border:1px solid var(--line,#b8c8bf);border-radius:8px;cursor:pointer}
 .site-toolbar .nav-cta{display:inline-flex;align-items:center;justify-content:center;width:auto;min-height:44px;padding:10px 16px;margin:0;background:var(--accent,#175c42);color:white!important;border-radius:8px;text-decoration:none}
 .site-toolbar [aria-current=page]{text-decoration:underline;font-weight:700}
 .site-toolbar :focus-visible{outline:3px solid #2786c6;outline-offset:3px}
 .mini-cta,.back-to-top{display:none!important}
 @media(max-width:1200px){
 .site-toolbar{padding:0!important}
 .site-toolbar .top-in{min-height:56px;padding-top:4px;padding-bottom:4px}
 .site-toolbar .brand{font-size:15px;min-width:0;white-space:normal}
 .site-toolbar .nav-burger{display:inline-flex;align-items:center;justify-content:center;order:2;margin-left:auto}
 .site-toolbar .nav{display:none;position:absolute;top:100%;left:0;right:0;bottom:auto;inset-inline:0;width:100%;max-height:calc(100dvh - var(--toolbar-height,56px));max-height:calc(100vh - var(--toolbar-height,56px));overflow-y:auto;overscroll-behavior:contain;flex-direction:column;align-items:stretch;gap:12px;padding:12px 16px calc(16px + env(safe-area-inset-bottom));background:var(--bg,#fff);box-sizing:border-box;border-bottom:1px solid var(--line,#b8c8bf)}
 .site-toolbar.menu-open .nav{display:flex}
 .site-toolbar .nav-left{flex-direction:column;align-items:stretch;gap:4px;width:100%}
 .site-toolbar .nav-group{width:100%}
 .site-toolbar .nav-left>a,.site-toolbar .nav-group>button{display:flex;align-items:center;justify-content:space-between;width:100%;text-align:left;font-size:16px;white-space:normal}
 .site-toolbar .dropdown{position:static;width:100%;min-width:0;max-height:none;box-shadow:none;box-sizing:border-box}
 .site-toolbar .nav-right{flex-direction:row;align-items:center;justify-content:flex-start;width:100%;margin:0;gap:12px}
 }
 @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}.site-toolbar *{transition:none!important}}
 `;document.head.append(style);
 function link(label,path,parent){const a=document.createElement('a');a.textContent=label;a.href=href(path);parent.append(a);return a}
 nav.replaceChildren();nav.id='site-primary-navigation';nav.setAttribute('aria-label','Main navigation');
 const left=document.createElement('div');left.className='nav-left';nav.append(left);
 link('209 Media','index.html',left);
 function group(label,items){const g=document.createElement('div');g.className='nav-group';const b=document.createElement('button');b.type='button';b.textContent=label+' ▾';b.setAttribute('aria-expanded','false');const panel=document.createElement('div');panel.className='dropdown';panel.id='site-menu-'+left.children.length;b.setAttribute('aria-controls',panel.id);items.forEach(([text,path])=>link(text,path,panel));g.append(b,panel);left.append(g);b.onclick=()=>{const open=!g.classList.contains('open');closeGroups();g.classList.toggle('open',open);b.setAttribute('aria-expanded',String(open))}}
 function closeGroups(){nav.querySelectorAll('.nav-group').forEach(g=>{g.classList.remove('open');g.querySelector('button').setAttribute('aria-expanded','false')})}
 group('dBeastco Wellness',[['Wellness Experience','dbeastco.html'],['Shop Wellness','dbeastco.html#store'],['Choose Your Path','dbeastco.html#paths'],['Featured Products','dbeastco.html#featured'],['Community','dbeastco.html#community']]);
 group('Systems Studio',[['Systems Studio','studio.html'],['Studio Store','studio.html#store'],['Realignment Room','aura.html#realignment'],['Lifestyle ID','aura.html'],['209 Connect Workspace','members/']]);
 group('209 Audit',[['209 Audit Story','209-audit.html'],['How It Works','209-audit.html#how-it-works'],['Tools and Assets','209-audit.html#tools'],['Audit Tracker','https://sicairos4.github.io/209audit-index-tracker/'],['Records','index.html#records'],['209 Intelligence','intelligence/'],['CPRA Playbook','https://sicairos4.github.io/209audit-cpra-playbook/']]);
 link('Sovereign University','sovereign-university.html',left);link('Media Library','library.html',left);link('Support','donations.html',left);
 const right=document.createElement('div');right.className='nav-right';const theme=document.createElement('button');theme.type='button';theme.id='themeToggle';theme.className='theme-toggle';theme.textContent='◐';theme.setAttribute('aria-label','Change color theme');theme.onclick=()=>{const choices=['valley-light','midnight-ledger','civic-gold'];const t=choices[(choices.indexOf(document.documentElement.dataset.theme)+1)%choices.length];document.documentElement.dataset.theme=t;try{localStorage.setItem('209-theme',t)}catch{}theme.textContent=({'valley-light':'◐','midnight-ledger':'☾','civic-gold':'☀'})[t]};right.append(theme);const c=document.createElement('a');c.href=subscribe;c.target='_blank';c.rel='noopener';c.className='nav-cta';c.textContent='Subscribe';right.append(c);nav.append(right);
 header.querySelectorAll('.nav-burger').forEach(b=>b.remove());const burger=document.createElement('button');burger.type='button';burger.className='nav-burger';burger.textContent='☰';burger.setAttribute('aria-controls',nav.id);burger.setAttribute('aria-expanded','false');burger.setAttribute('aria-label','Open navigation');row.append(burger);
 const mq=matchMedia('(max-width:1200px)');let overflow='',inertStates=[];
 function setOpen(open,restore=false){open=open&&mq.matches;header.classList.toggle('menu-open',open);document.body.classList.toggle('nav-open',open);burger.setAttribute('aria-expanded',String(open));burger.setAttribute('aria-label',open?'Close navigation':'Open navigation');burger.textContent=open?'×':'☰';if(open){overflow=document.body.style.overflow;document.body.style.overflow='hidden';inertStates=[...document.querySelectorAll('main,body>footer')].filter(x=>!x.contains(header)).map(x=>[x,x.inert]);inertStates.forEach(([x])=>x.inert=true)}else{document.body.style.overflow=overflow;inertStates.forEach(([x,v])=>x.inert=v);inertStates=[];closeGroups();if(restore)burger.focus()}nav.inert=mq.matches&&!open}
 burger.onclick=()=>setOpen(!header.classList.contains('menu-open'));
 nav.addEventListener('click',e=>{if(e.target.closest('a'))setOpen(false)});
 document.addEventListener('click',e=>{if(!header.contains(e.target)){if(header.classList.contains('menu-open'))setOpen(false);else closeGroups()}});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){setOpen(false,true);return}if(e.key==='Tab'&&header.classList.contains('menu-open')){const nodes=[...header.querySelectorAll('a,button')].filter(n=>n.getClientRects().length);const first=nodes[0],last=nodes[nodes.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}});
 mq.addEventListener('change',()=>setOpen(false));setOpen(false);
 if(window.ResizeObserver)new ResizeObserver(()=>header.style.setProperty('--toolbar-height',header.getBoundingClientRect().height+'px')).observe(header);
 const normal=p=>p.replace(/index\.html$/,'').replace(/\/$/,'');nav.querySelectorAll('a').forEach(a=>{const u=new URL(a.href);if(u.origin===location.origin&&!u.hash&&normal(u.pathname)===normal(location.pathname))a.setAttribute('aria-current','page')});
 const brand=header.querySelector('.brand');if(brand)brand.href=href('index.html');
 if(!document.head.querySelector('link[rel="icon"]')){const f=document.createElement('link');f.rel='icon';f.type='image/svg+xml';f.href=href('favicon.svg');document.head.append(f)}
 if(!document.head.querySelector('link[rel="manifest"]')){const m=document.createElement('link');m.rel='manifest';m.href=href('manifest.json');document.head.append(m)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();