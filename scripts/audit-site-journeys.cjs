const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const root=process.cwd(),out=path.join(root,'qa-artifacts');fs.mkdirSync(out,{recursive:true});
const skip=new Set(['.git','node_modules','.venv','venv','output','qa-artifacts']);
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>skip.has(e.name)?[]:e.isDirectory()?walk(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[]);}
const files=walk(root).map(f=>path.relative(root,f).split(path.sep).join('/')).sort();
const local='http://127.0.0.1:8765/',live='https://209connect.com/';
const results=[],urls=new Set();let cursor=0;
function save(){fs.writeFileSync(path.join(out,'browser-audit.json'),JSON.stringify({scope:'All repository HTML files, including potential templates/fixtures. Fresh logged-out browsers. No form submissions or arbitrary button clicks. Rendered text and controls are inventories, not semantic or functional approval.',pages_total:files.length,pages_attempted:results.length,pages:results},null,2));}
(async()=>{
 const browser=await chromium.launch({headless:true});
 async function worker(){
  while(cursor<files.length){const file=files[cursor++],record={file,errors:[],blocked_writes:0};
   const context=await browser.newContext({viewport:{width:390,height:844},acceptDownloads:false,serviceWorkers:'block'});
   await context.route('**/*',route=>{if(!['GET','HEAD','OPTIONS'].includes(route.request().method())){record.blocked_writes++;return route.abort();}return route.continue();});
   const page=await context.newPage();page.on('pageerror',e=>record.errors.push(e.message));
   try{
    const response=await page.goto(local+file,{waitUntil:'domcontentloaded',timeout:15000});record.http_status=response?.status();
    await page.waitForTimeout(1800);
    record.final_url=page.url();
    record.dom=await page.evaluate(()=>({title:document.title,text:document.body?.innerText||'',horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,links:[...document.querySelectorAll('a[href]')].map(a=>({label:(a.innerText||a.getAttribute('aria-label')||a.querySelector('img')?.alt||'').trim(),url:a.href,visible:!!a.getClientRects().length})),buttons:[...document.querySelectorAll('button,input[type=submit],input[type=button]')].map(b=>({label:(b.innerText||b.getAttribute('aria-label')||b.value||'').trim(),type:b.type,disabled:b.disabled,visible:!!b.getClientRects().length,id:b.id})),forms:[...document.forms].map(f=>({action:f.action,method:f.method})),frames:[...document.querySelectorAll('iframe')].map(f=>({src:f.src,title:f.title})),subscribe_slots:document.querySelectorAll('[data-subscribe-form]').length,subscribe_mounts:document.querySelectorAll('.subscribe-form-mount').length}));
    for(const a of record.dom.links){try{const u=new URL(a.url);if(['http:','https:'].includes(u.protocol)&&!u.username&&!u.password)urls.add(u.href);}catch{}}
   }catch(e){record.failure=e.message;}
   finally{results.push(record);save();await context.close();}
  }
 }
 await Promise.all(Array.from({length:3},()=>worker()));
 const targets=[...urls],checks=[];let next=0;
 async function links(){while(next<targets.length){const address=targets[next++];const u=new URL(address),isLocal=u.origin===new URL(local).origin;const target=isLocal?new URL(u.pathname+u.search,live).href:u.href;
  const entry={url:target.split('?')[0].split('#')[0],kind:isLocal?'live_internal':'external'};
  try{const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
   try{const response=await fetch(target,{method:'HEAD',redirect:'follow',signal:controller.signal});entry.status=response.status;entry.final_url=response.url.split('?')[0].split('#')[0];entry.result=[404,410].includes(response.status)?'missing_response':response.ok?'responded':'needs_review';}finally{clearTimeout(timer);}
  }catch(e){entry.result='unverified_network_or_redirect_failure';entry.error=e.name;}
  checks.push(entry);fs.writeFileSync(path.join(out,'link-responses.json'),JSON.stringify({scope:'HEAD requests only. Restricted responses and network errors are not proof of broken links. Query values are omitted from report URLs. Successful status does not prove meaningful content or correct behavior.',checks},null,2));
 }}
 await Promise.all(Array.from({length:5},()=>links()));
 await browser.close();
 fs.writeFileSync(path.join(out,'AUDIT-README.md'),'# Site audit findings\n\nRead static-audit.json, browser-audit.json and link-responses.json together. Inspect pages_total versus pages_attempted before claiming coverage. Browser captures use mobile width and fresh logged-out contexts; templates and fixtures may appear. All non-read HTTP requests are blocked, including analytics and subscription requests. No email is subscribed, account changed, button workflow completed or paid feature exercised. Review blocked requests and browser errors in context. A mounted iframe is not evidence of successful signup. Live HEAD checks cannot certify article content, authentication, email delivery, provider settings, desktop layout, accessibility or editorial accuracy.\n\nFor the reported newsletter loop, inspect the Subscribe links, final URLs and frames on index.html, newsletter.html, signal.html, signal-subscribe.html and signal-archive.html. A real opt-in test needs a separately approved address and submission; do not infer success from source or a page loading.\n');
})().catch(e=>{save();console.error(e);process.exitCode=1;});
