/* Consistent top bar for every page that includes this script */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const nav=`
<div class="nav-group"><a href="index.html">Home</a></div>
<div class="nav-group"><button type="button">209 Signal <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">209 Signal</div><a href="signal.html">Top Stories</a><a href="signal-archive.html">Archive</a><a href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a></div></div>
<div class="nav-group"><button type="button">Systems <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">Systems</div><a href="studio.html">Systems Studio</a><a href="working-record.html">Working Record</a><a href="https://sicairos4.github.io/209audit-index-tracker/" rel="noopener">209Audit Tracker</a><a href="https://sicairos4.github.io/209audit-cpra-playbook/" rel="noopener">CPRA Playbook</a><a href="aura.html">Lifestyle ID Aura</a></div></div>
<div class="nav-group"><a href="dbeastco.html">dBeastco</a></div>
<div class="nav-group"><a href="store.html">Store</a></div>
<div class="nav-group"><button type="button">About <span class="nav-caret">▼</span></button><div class="dropdown"><div class="dropdown-label">About</div><a href="index.html#leadership">Leadership</a><a href="index.html#contact">Contact</a><a href="index.html#support">Support</a></div></div>
<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>`;
function render(){
const navs=document.querySelectorAll("header.top .nav");
navs.forEach(n=>{n.innerHTML=nav});
document.querySelectorAll(".nav-group>button").forEach(btn=>{btn.onclick=e=>{e.stopPropagation();const g=btn.parentElement;const open=g.classList.contains("open");document.querySelectorAll(".nav-group.open").forEach(x=>x.classList.remove("open"));if(!open)g.classList.add("open")}});
document.addEventListener("click",()=>document.querySelectorAll(".nav-group.open").forEach(g=>g.classList.remove("open")));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);else render();
})();