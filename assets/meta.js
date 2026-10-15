/* Global meta tag + favicon injection — runs on every page via topbar.js */
(function(){
function ensureMeta(attr,key,content){
let el=document.head.querySelector('meta['+attr+'="'+key+'"]');
if(!el){el=document.createElement('meta');el.setAttribute(attr,key);document.head.appendChild(el)}
el.setAttribute('content',content);
}
function inject(){
const title=document.title||'209 Media';
const desc='209 Media — David Sicairos. Wellness, systems, receipts, and sovereign education.';
const url=location.href;
const img='https://sicairos4.github.io/david-sicairos-site/favicon.svg';
ensureMeta('name','description',desc);
ensureMeta('property','og:title',title);
ensureMeta('property','og:description',desc);
ensureMeta('property','og:type','website');
ensureMeta('property','og:url',url);
ensureMeta('property','og:image',img);
ensureMeta('name','twitter:card','summary');
ensureMeta('name','twitter:title',title);
ensureMeta('name','twitter:description',desc);
ensureMeta('name','twitter:image',img);
if(!document.head.querySelector('link[rel="icon"]')){
const f=document.createElement('link');f.rel='icon';f.href='favicon.svg';f.type='image/svg+xml';document.head.appendChild(f);
}
if(!document.head.querySelector('link[rel="manifest"]')){
const m=document.createElement('link');m.rel='manifest';m.href='manifest.json';document.head.appendChild(m);
}
if(!document.head.querySelector('link[rel="canonical"]')){
const c=document.createElement('link');c.rel='canonical';c.href=url;document.head.appendChild(c);
}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',inject);else inject();
})();