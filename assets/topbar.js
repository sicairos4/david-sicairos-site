/* Three-pillar hierarchy: 209 Media homepage, dBeastco Wellness, Systems Studio, 209 Audit, Sovereign University */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const nav=`
<div class="nav-left">
<a href="index.html">209 Media</a>
<div class="nav-group"><button type="button">dBeastco Wellness <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">WELLNESS & PERFORMANCE</div><a href="dbeastco.html">Wellness Experience</a><a href="dbeastco.html#store">Shop Wellness</a><a href="dbeastco.html#paths">Choose Your Path</a><a href="dbeastco.html#featured">Featured Products</a><a href="dbeastco.html#community">Community</a></div></div>
<div class="nav-group"><button type="button">Systems Studio <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">BUILDER SYSTEMS</div><a href="studio.html">Systems Studio</a><a href="studio.html#store">Studio Store</a><a href="aura.html#realignment">The Realignment Room</a><a href="aura.html">Lifestyle ID</a></div></div>
<div class="nav-group"><button type="button">209 Audit <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">RECEIPTS & ACCOUNTABILITY</div><a href="209-audit.html">209 Audit Story</a><a href="209-audit.html#how-it-works">How It Works</a><a href="209-audit.html#tools">Tools & Assets</a><a href="index.html#records">Records</a><a href="https://sicairos4.github.io/209audit-cpra-playbook/" rel="noopener">CPRA Playbook</a></div></div>
<a href="sovereign-university.html">Sovereign University</a>
</div>
<div class="nav-right">
<button id="themeToggle" class="theme-toggle" type="button" aria-label="Change theme">◐</button>
<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>
</div>`;
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