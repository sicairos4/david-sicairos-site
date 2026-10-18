const test=require('node:test');
const assert=require('node:assert/strict');
const {shareSnapshot}=require('../assets/workstation/review-share.js');
test('uses text when file sharing is unavailable',async()=>{
 let payload;const result=await shareSnapshot('Exact preview',{navigator:{share:async p=>{payload=p;}}});
 assert.equal(result.mode,'text');assert.equal(payload.text,'Exact preview');assert.equal(payload.files,undefined);
});
test('shares only the preview file when supported',async()=>{
 let payload;class FileMock{constructor(parts,name,options){this.parts=parts;this.name=name;this.type=options.type;}}
 const result=await shareSnapshot('Only selected review',{File:FileMock,navigator:{canShare:()=>true,share:async p=>{payload=p;}}});
 assert.equal(result.mode,'file');assert.deepEqual(payload.files[0].parts,['Only selected review']);assert.equal(payload.text,undefined);
});
test('cancellation is terminal and does not start another share',async()=>{
 let calls=0;const result=await shareSnapshot('Preview',{navigator:{share:async()=>{calls++;throw Object.assign(Error(),{name:'AbortError'});}}});
 assert.equal(result.status,'cancelled');assert.equal(calls,1);
});
test('reports unsupported environments without losing preview',async()=>{
 assert.equal((await shareSnapshot('Preview',{navigator:{}})).status,'unavailable');
});
test('capability errors fall back before opening the share dialog',async()=>{
 class FileMock{};let payload;
 const result=await shareSnapshot('Preview',{File:FileMock,navigator:{canShare:()=>{throw Error();},share:async p=>{payload=p;}}});
 assert.equal(result.mode,'text');assert.equal(payload.text,'Preview');
});
test('errors do not expose platform details or private content',async()=>{
 await assert.rejects(shareSnapshot('Private text',{navigator:{share:async()=>{throw Error('Private text');}}}),/Sharing did not finish/);
});
test('rejects absent or oversized content before sharing',async()=>{
 await assert.rejects(shareSnapshot(''),/missing/);await assert.rejects(shareSnapshot('x'.repeat(100001)),/large/);
});
