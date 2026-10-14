const THEME_KEY="209-theme";
const themes=["civic-gold","midnight-ledger","valley-light"];
function setTheme(t){if(!themes.includes(t))t="civic-gold";document.documentElement.dataset.theme=t;localStorage.setItem(THEME_KEY,t);document.querySelectorAll(".theme-dock .dot").forEach(d=>d.classList.toggle("active",d.dataset.theme===t))}
setTheme(localStorage.getItem(THEME_KEY)||"civic-gold");
document.querySelectorAll(".theme-dock .dot").forEach(dot=>dot.addEventListener("click",()=>setTheme(dot.dataset.theme)));
async function loadJSON(p){try{const r=await fetch(p);return await r.json()}catch(e){return null}}
(async()=>{const d=await loadJSON("data/site.json");const s=document.getElementById("latestSignal");if(d?.latest_signal&&s){s.innerHTML=`<h3>${d.latest_signal.title}</h3><p>${d.latest_signal.summary}</p><a class="btn ghost" href="${d.latest_signal.url}">Read the update</a>`}const f=document.getElementById("recordFeed");if(d?.records&&f){f.innerHTML=d.records.map(r=>`<div class="item"><strong>${r.date}</strong><br>${r.title}<br>${r.summary}<br><a class="btn ghost" href="${r.url}">Open</a></div>`).join("")}})();
const y=document.getElementById("y");if(y)y.textContent=new Date().getFullYear();