(async()=>{
'use strict';
const source=document.currentScript?.src,intro=document.querySelector('.lessons-intro');if(!source||!intro||document.getElementById('courseAuthorBio'))return;
const base=new URL('../',source),paths=['sovereign-university/practice-lessons.html','sovereign-university/wellness-lessons.html'].map(path=>new URL(path,base).pathname);if(!paths.includes(location.pathname))return;
const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
try{const response=await fetch(new URL('data/course-author.json',base),{credentials:'omit',signal:controller.signal});if(!response.ok)throw Error();const data=await response.json();if(data?.version!==1||data.name!=='David Sicairos'||typeof data.bio!=='string'||!data.bio.trim()||data.bio.length>2500||document.getElementById('courseAuthorBio'))throw Error();const box=document.createElement('aside'),heading=document.createElement('h2'),p=document.createElement('p'),link=document.createElement('a');box.id='courseAuthorBio';heading.textContent='About the author';p.textContent=data.bio;link.href=new URL('working-record.html#author-bio',base).href;link.textContent='Read David’s background and education';box.append(heading,p,link);intro.append(box);}catch{}finally{clearTimeout(timer);}
})();
