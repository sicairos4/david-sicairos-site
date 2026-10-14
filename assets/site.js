const THEME_KEY="209-theme",LENS_KEY="209-lens";
function setTheme(t){document.documentElement.dataset.theme=t;localStorage.setItem(THEME_KEY,t)}
setTheme(localStorage.getItem(THEME_KEY)||"civic-gold");
document.getElementById("themeToggle")?.addEventListener("click",()=>{const c=document.documentElement.dataset.theme;setTheme(c==="midnight-ledger"?"civic-gold":"midnight-ledger")});
async function loadJSON(p){try{const r=await fetch(p);return await r.json()}catch(e){return null}}
(async()=>{const d=await loadJSON("data/site.json");const s=document.getElementById("latestSignal");if(d?.latest_signal&&s){s.innerHTML=`<h3>${d.latest_signal.title}</h3><p>${d.latest_signal.summary}</p><a class="btn ghost" href="${d.latest_signal.url}">Read the update</a>`}const f=document.getElementById("recordFeed");if(d?.records&&f){f.innerHTML=d.records.map(r=>`<div class="item"><strong>${r.date}</strong><br>${r.title}<br>${r.summary}<br><a class="btn ghost" href="${r.url}">Open</a></div>`).join("")}})();
document.getElementById("y")&&(document.getElementById("y").textContent=new Date().getFullYear());