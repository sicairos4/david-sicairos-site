/* Consolidated 209 Media top bar: Systems Hub separated, Sovereign University course pathways, reliable scroll reset */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const nav=`
<a href="index.html">Home</a>
<a href="aura.html">Lifestyle ID</a>
<div class="nav-group"><button type="button">209 Connect <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">209 MEDIA CONNECT</div><a href="index.html">Home</a><a href="working-record.html">Resume</a><a href="index.html#records">Records</a><a href="index.html#audit">209 Audit</a><a href="signal.html">Signal</a><a href="newsletter.html">Newsletter</a></div></div>
<a href="index.html#systems-hub">Systems Hub</a>
<div class="nav-group"><button type="button">Sovereign University <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">SYSTEMS THINKING & COURSES</div><a href="index.html#systems-hub">Start With Systems Thinking</a><a href="aura.html#realignment">Realignment & Daily Systems</a><a href="aura.html#personal-brand">Personal Brand & Identity</a><a href="aura.html#ai-setup">AI Assistant & Digital Twin</a><a href="studio.html">Creator & Business Systems</a><a href="dbeastco.html#paths">Wellness & Performance</a><a href="index.html#audit">Independent Journalism</a><a href="aura.html#credentials">Lifestyle ID Credentials</a></div></div>
<div class="nav-group"><button type="button">Stores <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">SHOP THE ECOSYSTEM</div><a href="store.html">All Products</a><a href="studio.html#store">Systems Studio Store</a><a href="dbeastco.html#store" class="dbeastco-link">dBeastco Wellness Store</a><a href="aura.html#realignment">The Realignment Room</a></div></div>
<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>`;
function render(){
document.querySelectorAll("header.top .nav").forEach(n=>{n.innerHTML=nav});
document.querySelectorAll(".nav-group>button").forEach(btn=>{btn.onclick=e=>{e.stopPropagation();const g=btn.parentElement;const open=g.classList.contains("open");document.querySelectorAll(".nav-group.open").forEach(x=>x.classList.remove("open"));if(!open)g.classList.add("open")}});
document.addEventListener("click",()=>document.querySelectorAll(".nav-group.open").forEach(g=>g.classList.remove("open")));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);else render();
if("scrollRestoration" in history)history.scrollRestoration="manual";
function resetScroll(){window.scrollTo(0,0);document.documentElement.scrollTop=0;document.body.scrollTop=0}
window.addEventListener("pageshow",()=>{if(!location.hash)resetScroll()});
window.addEventListener("popstate",()=>{if(!location.hash)resetScroll()});
document.addEventListener("click",e=>{const a=e.target.closest("a[href]");if(!a)return;const href=a.getAttribute("href");if(href&&!href.startsWith("#")&&!href.startsWith("http")&&!href.startsWith("mailto:")){resetScroll()}});
})();