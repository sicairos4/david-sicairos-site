'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/workstation/review-share.js'),'utf8');
function boot(){
 const listeners={},loaded=[],notices=[];let preview=null;
 const status={textContent:''};
 const document={body:{},currentScript:{src:'https://example.test/site/assets/workstation/review-share.js'},scripts:[],
  getElementById:id=>id==='workstationPrintPreview'?preview:id==='morningStatus'?status:null,
  querySelector:()=>({append:node=>notices.push(node)}),
  createElement:()=>({setAttribute(){}}),head:{append:script=>{loaded.push(script);document.scripts.push(script);}},
  addEventListener:(name,callback,capture)=>{listeners[name]={callback,capture};}};
 let disconnected=0;
 class Observer{observe(){}disconnect(){disconnected++;}}
 const context={document,URL,MutationObserver:Observer,addEventListener:(name,callback)=>{listeners[name]={callback};}};
 vm.runInNewContext(source,context);
 return {listeners,loaded,notices,status,setPreview:value=>preview=value,disconnected:()=>disconnected};
}
test('loads existing guided review and print modules once from the same asset directory',()=>{
 const app=boot();assert.deepEqual(app.loaded.map(s=>s.src),['https://example.test/site/assets/workstation/weekly-review.js','https://example.test/site/assets/workstation/print.js']);
 assert.ok(app.loaded.every(s=>s.async===false));
});
test('blocks a second print preview without interfering with unrelated clicks',()=>{
 const app=boot();app.setPreview({});let prevented=0,stopped=0;
 const event={target:{closest:()=>({})},preventDefault:()=>prevented++,stopImmediatePropagation:()=>stopped++};
 app.listeners.click.callback(event);assert.equal(prevented,1);assert.equal(stopped,1);assert.match(app.status.textContent,/Close the existing/);
 app.listeners.click.callback({...event,target:{closest:()=>null}});assert.equal(prevented,1);
});
test('allows opening the first print preview',()=>{
 const app=boot();app.listeners.click.callback({target:{closest:()=>({})},preventDefault(){assert.fail('unexpected block');},stopImmediatePropagation(){assert.fail('unexpected block');}});
});
test('disconnects the sharing observer on every pagehide',()=>{
 const app=boot();app.listeners.pagehide.callback();app.listeners.pageshow.callback();app.listeners.pagehide.callback();assert.equal(app.disconnected(),2);
});
test('module load failure is visible without changing planner records',()=>{
 const app=boot();app.loaded[0].onerror();assert.match(app.notices[0].textContent,/could not load/);assert.match(app.notices[0].textContent,/unchanged/);
});
