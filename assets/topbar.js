/* Long, consistent top bar for every page */
(function(){
const SUBSCRIBE="https://209connect.beehiiv.com/?modal=signup";
const links=[
["Home","index.html"],
["Records","index.html#records"],
["Control Panel","index.html#panel"],
["Working Record","working-record.html"],
["Systems Hub","index.html#systems-hub"],
["209 Audit","index.html#audit"],
["Systems Studio","index.html#studio"],
["Lifestyle ID","aura.html"],
["dBeastco","dbeastco.html"],
["Store","store.html"],
["Support","index.html#support"]
];
const nav=links.map(([label,href])=>`<a href="${href}">${label}</a>`).join("")+`<a class="btn nav-cta" href="${SUBSCRIBE}" target="_blank" rel="noopener">Subscribe</a>`;
function render(){document.querySelectorAll("header.top .nav").forEach(n=>{n.innerHTML=nav})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);else render();
})();