const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const root=process.cwd(),out=path.join(root,'qa-artifacts');fs.mkdirSync(out,{recursive:true});
const skip=new Set(['.git','node_modules','.venv','venv','output','qa-artifacts']);
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>skip.has(e.name)?[]:e.isDirectory()?walk(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[]);}
const files=walk(root).map(f=>path.relative(root,f).split(path.sep).join('/')).sort();
const local='http://127.0.0.1:8765/',live='https://209connect.com/',widths=[320,360,390,768,1280];
const results=[],urls=new Set();let cursor=0;
function save(){fs.writeFileSync(path.join(out,'browser-audit.json'),JSON.stringify({scope:'Repository HTML including possible templates. Logged-out contexts. Five resized viewports, not five independent journeys. No submission or arbitrary button clicks. Visible text and controls require manual review.',widths,pages_total:files.length,pages_attempted:results.length,pages:results},null,2));}
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 async function worker(){while(cursor<files.length){const file=files[cursor++],record={file,errors:[],blocked_writes:0,layouts:[]};let context;
  try{
   context=await browser.newContext({viewport:{width:390,height:844},acceptDownloads:false,serviceWorkers:'block'});
   await context.route('**/*',route=>{if(!['GET','HEAD','OPTIONS'].includes(route.request().method())){record.blocked_writes++;return route.abort();}return route.continue();});
   const page=await context.newPage();page.on('pageerror',e=>record.errors.push(e.message));
   const response=await page.goto(local+file,{waitUntil:'domcontentloaded',timeout:15000});record.http_status=response?.status();await page.waitForTimeout(1800);record.final_url=page.url();
   record.dom=await page.evaluate(()=>({title:document.title,text:document.body?.innerText||'',links:[...document.querySelectorAll('a[href]')].map(a=>({label:(a.innerText||a.getAttribute('aria-label')||a.querySelector('img')?.alt||'').trim(),url:a.href,visible:!!a.getClientRects().length})),buttons:[...document.querySelectorAll('button,input[type=submit],input[type=button]')].map(b=>({label:(b.innerText||b.getAttribute('aria-label')||b.value||'').trim(),type:b.type,disabled:b.disabled,visible:!!b.getClientRects().length,id:b.id})),forms:[...document.forms].map(f=>({action:f.action,method:f.method})),frames:[...document.querySelectorAll('iframe')].map(f=>({src:f.src,title:f.title})),subscribe_slots:document.querySelectorAll('[data-subscribe-form]').length,subscribe_mounts:document.querySelectorAll('.subscribe-form-mount').length}));
   for(const width of widths){await page.setViewportSize({width,height:844});await page.waitForTimeout(250);record.layouts.push(await page.evaluate(()=>({width:innerWidth,document_width:document.documentElement.scrollWidth,horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,offenders:[...document.body.querySelectorAll('*')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&(r.right>innerWidth+2||r.left< -2);}).slice(0,20).map(e=>({tag:e.tagName,id:e.id,class_name:typeof e.className==='string'?e.className:'',left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))})));}
   for(const a of record.dom.links){try{const u=new URL(a.url);if(['http:','https:'].includes(u.protocol)&&!u.username&&!u.password)urls.add(u.href);}catch{}}
  }catch(e){record.failure=e.message;}finally{results.push(record);save();if(context)await context.close();}
 }}
 await Promise.all(Array.from({length:3},()=>worker()));
 const targets=[...urls],checks=[];let next=0;
 async function links(){while(next<targets.length){const address=targets[next++],u=new URL(address),isLocal=u.origin===new URL(local).origin,target=isLocal?new URL(u.pathname+u.search,live).href:u.href;const entry={url:target.split('?')[0].split('#')[0],kind:isLocal?'live_internal':'external'};
  try{const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);try{const response=await fetch(target,{method:'HEAD',redirect:'follow',signal:controller.signal});entry.status=response.status;entry.final_url=response.url.split('?')[0].split('#')[0];entry.result=[404,410].includes(response.status)?'missing_response':response.ok?'responded':'needs_review';}finally{clearTimeout(timer);}}catch(e){entry.result='unverified_network_or_redirect_failure';entry.error=e.name;}
  checks.push(entry);fs.writeFileSync(path.join(out,'link-responses.json'),JSON.stringify({scope:'HEAD checks; restricted/network responses are not proof of broken links. URL query values omitted. HTTP success does not establish correct content.',targets_total:targets.length,targets_attempted:checks.length,checks},null,2));
 }}
 await Promise.all(Array.from({length:5},()=>links()));
 let staticAudit;try{staticAudit=JSON.parse(fs.readFileSync(path.join(out,'static-audit.json'),'utf8'));}catch{}
 const summary={pages_total:files.length,pages_attempted:results.length,static_errors:staticAudit?.errors??null,static_warnings:staticAudit?.warnings??null,page_failures:results.filter(r=>r.failure||r.http_status>=400).length,browser_error_pages:results.filter(r=>r.errors.length).length,overflow_pages:results.filter(r=>r.layouts.some(v=>v.horizontal_overflow)).length,incomplete_layout_pages:results.filter(r=>r.layouts.length!==widths.length).length,link_targets:targets.length,link_checks:checks.length,missing_link_responses:checks.filter(r=>r.result==='missing_response').length,unverified_link_responses:checks.filter(r=>r.result==='unverified_network_or_redirect_failure'||r.result==='needs_review').length,submission_test:'NOT_PERFORMED',editorial_review:'NOT_PERFORMED',authenticated_journeys:'NOT_PERFORMED'};
 summary.failed=summary.pages_attempted!==summary.pages_total||summary.pages_total===0||summary.static_errors===null||summary.static_errors>0||summary.page_failures>0||summary.browser_error_pages>0||summary.overflow_pages>0||summary.incomplete_layout_pages>0||summary.missing_link_responses>0||summary.link_checks!==summary.link_targets;
 const text='# Site audit summary\n\n```json\n'+JSON.stringify(summary,null,2)+'\n```\n\nNo form submissions, email delivery tests, authenticated journeys, arbitrary button clicks or editorial certification were performed. Restricted links require review even if this job passes. Offscreen element candidates may be intentional. Templates may produce findings unrelated to published routes. Inspect the detailed reports before making fixes.\n';
 fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));fs.writeFileSync(path.join(out,'AUDIT-README.md'),text);if(process.env.GITHUB_STEP_SUMMARY)fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,text);console.log(JSON.stringify(summary));if(summary.failed)process.exitCode=1;
 }finally{await browser.close();}
})().catch(e=>{save();console.error(e);process.exitCode=1;});
