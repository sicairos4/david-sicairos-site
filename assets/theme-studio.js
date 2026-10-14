const KEY="209-theme-studio";
const defaults={theme:"civic-gold",accent:"#c9a227",heroTitle:"The Central Valley is changing.",heroSubtitle:"See the system behind the headlines.",signalTitle:"209Audit: Public records, transparency, and accountability",signalSummary:"A citizen-led framework for following the systems behind public decisions.",primaryCtaText:"Open the 209 Signal",primaryCtaUrl:"https://209connect.beehiiv.com/",trackerUrl:"https://sicairos4.github.io/209audit-index-tracker/",cpraUrl:"https://sicairos4.github.io/209audit-cpra-playbook/"};
let config=JSON.parse(localStorage.getItem(KEY)||"null")||structuredClone(defaults);
function apply(){document.documentElement.dataset.theme=config.theme;document.documentElement.style.setProperty("--accent",config.accent);for(const id of["heroTitle","heroSubtitle","signalTitle","signalSummary","primaryCtaText","primaryCtaUrl","trackerUrl","cpraUrl"]){const el=document.getElementById(id);if(el)el.value=config[id]}}
function save(){localStorage.setItem(KEY,JSON.stringify(config))}
document.querySelectorAll(".theme-preset").forEach(b=>b.addEventListener("click",()=>{config.theme=b.dataset.theme;apply();save()}));
document.getElementById("accentColor").addEventListener("input",e=>{config.accent=e.target.value;apply();save()});
for(const id of["heroTitle","heroSubtitle","signalTitle","signalSummary","primaryCtaText","primaryCtaUrl","trackerUrl","cpraUrl"]){document.getElementById(id).addEventListener("input",e=>{config[id]=e.target.value;save()})}
document.getElementById("saveLocal").addEventListener("click",()=>{save();alert("Saved in this browser.")});
document.getElementById("exportJson").addEventListener("click",()=>{const blob=new Blob([JSON.stringify(config,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="site.json";a.click()});
document.getElementById("reset").addEventListener("click",()=>{config=structuredClone(defaults);save();apply()});
apply();