/* Reduced, consistent top bar */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const nav=`
<a href="index.html">Home</a>
<a href="index.html#records">Records</a>
<div class="nav-group"><button type="button">Systems <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">SYSTEMS</div><a href="index.html#panel">Control Panel</a><a href="working-record.html">Working Record</a><a href="index.html#systems-hub">Systems Hub</a><a href="index.html#audit">209 Audit</a><a href="index.html#studio">Systems Studio</a><a href="209connect/index.html">209 Connect</a></div></div>
<div class="nav-group"><button type="button">Lifestyle ID <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">WHAT YOU’RE BUILDING</div><a href="aura.html">What We’re Building</a><a href="aura.html#framework">Personal Brand</a><a href="aura.html#assistant">Train Your AI</a><a href="aura.html#habits">Intentional Habits</a><a href="aura.html#sovereign">Sovereign University</a></div></div>
<div class="nav-group"><button type="button">dBeastco <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">DBEASTCO WELLNESS</div><a href="dbeastco.html">Wellness Experience</a><a href="dbeastco.html#store">Shop Wellness</a><a href="dbeastco.html#paths">Choose Your Path</a><a href="dbeastco.html#featured">Featured Products</a><a href="store.html">Open Full Store</a></div></div>
<a href="index.html#support">Support</a>
<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>`;
function render(){
document.querySelectorAll("header.top .nav").forEach(n=>{n.innerHTML=nav});
document.querySelectorAll(".nav-group>button").forEach(btn=>{btn.onclick=e=>{e.stopPropagation();const g=btn.parentElement;const open=g.classList.contains("open");document.querySelectorAll(".nav-group.open").forEach(x=>x.classList.remove("open"));if(!open)g.classList.add("open")}});
document.addEventListener("click",()=>document.querySelectorAll(".nav-group.open").forEach(g=>g.classList.remove("open")));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);else render();
})();