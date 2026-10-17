(()=>{
'use strict';
const root=new URL('../',document.currentScript.src);
function tag(attr,key,value,replace=false){let el=document.head.querySelector('meta['+attr+'="'+key+'"]');if(!el){el=document.createElement('meta');el.setAttribute(attr,key);document.head.appendChild(el)}if(replace||!el.getAttribute('content')?.trim())el.setAttribute('content',value);return el}
function asset(rel,path,type){if(document.head.querySelector('link[rel="'+rel+'"]'))return;const el=document.createElement('link');el.setAttribute('rel',rel);el.setAttribute('href',new URL(path,root).href);if(type)el.setAttribute('type',type);document.head.appendChild(el)}
function themeColor(){const color=getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();if(color)tag('name','theme-color',color,true)}
function inject(){
 const title=document.title||'209 Media';
 const desc=document.head.querySelector('meta[name="description"]')?.getAttribute('content')?.trim()||'209 Media: Central Valley public records, accountability, education, and systems thinking.';
 tag('name','description',desc);asset('icon','favicon.svg','image/svg+xml');asset('manifest','manifest.json');
 const canonical=new URL(location.href);canonical.search='';canonical.hash='';canonical.pathname=canonical.pathname.replace(/\/index\.html$/,'/');
 let link=document.head.querySelector('link[rel="canonical"]');if(!link){link=document.createElement('link');link.setAttribute('rel','canonical');document.head.appendChild(link)}link.setAttribute('href',canonical.href);
 tag('property','og:title',title);tag('property','og:description',desc);tag('property','og:type','website');tag('property','og:url',canonical.href,true);
 tag('name','twitter:title',title);tag('name','twitter:description',desc);
 const image=document.head.querySelector('meta[property="og:image"]')?.getAttribute('content');
 let usableImage=false;if(image){try{const u=new URL(image,root);usableImage=u.protocol==='https:'&&/\.(png|jpe?g|webp)$/i.test(u.pathname);if(usableImage)tag('name','twitter:image',u.href)}catch{}}
 tag('name','twitter:card',usableImage?'summary_large_image':'summary');
 const path=canonical.pathname.slice(root.pathname.length);
 if(/^(members\/|ops\/|login\.html$|dashboard\.html$|update-site\.html$)/.test(path))tag('name','robots','noindex, nofollow',true);
 if(!document.head.querySelector('script[data-site-schema]')){const schema=document.createElement('script');schema.setAttribute('type','application/ld+json');schema.setAttribute('data-site-schema','website');schema.textContent=JSON.stringify({'@context':'https://schema.org','@type':'WebSite',name:'209 Media',url:root.href});document.head.appendChild(schema)}
 themeColor();new MutationObserver(themeColor).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',inject,{once:true});else inject();
})();
