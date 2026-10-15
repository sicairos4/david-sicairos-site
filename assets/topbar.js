/* Three-pillar navigation: Realignment, dBeastco Ecosystem, 209 Connect; Sovereign University as shared education destination */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const nav=`
<a href="index.html">Home</a>
<a href="aura.html">Lifestyle ID</a>
<div class="nav-group"><button type="button">209 Connect <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">209 MEDIA CONNECT</div><a href="index.html">Home</a><a href="working-record.html">Resume</a><a href="index.html#records">Records</a><a href="index.html#audit">209 Audit</a><a href="signal.html">Signal</a><a href="newsletter.html">Newsletter</a></div></div>
<div class="nav-group"><button type="button">dBeastco Ecosystem <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">WELLNESS & PERFORMANCE</div><a href="dbeastco.html">Wellness Experience</a><a href="dbeastco.html#store">Shop Wellness</a><a href="dbeastco.html#paths">Choose Your Path</a><a href="dbeastco.html#featured">Featured Products</a><a href="dbeastco.html#community">Community</a><a href="store.html">All Products</a></div></div>
<a href="studio.html">Systems Studio</a>
<a href="aura.html#sovereign-university">Sovereign University</a>
<div class="nav-group"><button type="button">Stores <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">SHOP THE ECOSYSTEM</div><a href="store.html">All Products</a><a href="studio.html#store">Systems Studio Store</a><a href="dbeastco.html#store">dBeastco Wellness Store</a><a href="aura.html#realignment">The Realignment Room</a></div></div>
<button id="themeToggle" class="theme-toggle" type="button" aria-label="Change theme">◐</button>
<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>`;
function render(){
document.querySelectorAll("header.top .nav").forEach(n=>{n.innerHTML=nav});
document.querySelectorAll(".nav-group>button").forEach(btn=>{btn.onclick=e=>{e.stopPropagation();const g=btn.parentElement;const open=g.classList.contains("open");document.querySelectorAll(".nav-group.open").forEach(x=>x.classList.remove("open"));if(!open)g.classList.add("open")}});
document.addEventListener("click",()=>document.querySelectorAll(".nav-group.open").forEach(g=>g.classList.remove("open")));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);else render();
if("scrollRestoration" in history)history.scrollRestoration="manual";
function resetScroll(){window.scrollTo(0,0);document.documentElement.scrollTop=0;document.body.scrollTop=0}
function resetAfterPaint(){requestAnimationFrame(()=>{resetScroll();setTimeout(resetScroll,50)})}
window.addEventListener("pageshow",()=>{if(!location.hash)resetAfterPaint()});
window.addEventListener("popstate",()=>{if(!location.hash)resetAfterPaint()});
window.addEventListener("load",()=>{if(!location.hash)resetAfterPaint()});
document.addEventListener("click",e=>{const a=e.target.closest("a[href]");if(!a)return;const href=a.getAttribute("href");if(href&&!href.startsWith("#")&&!href.startsWith("http")&&!href.startsWith("mailto:")){resetScroll()}});
})();