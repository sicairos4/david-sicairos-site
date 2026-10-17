const test=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/intelligence-data.js'),'utf8');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.text=''}
 set textContent(value){this.text=String(value);this.children=[]}
 get textContent(){return this.text+this.children.map(x=>x.textContent).join(' ')}
 set innerHTML(value){throw Error('Unsafe HTML insertion')}
 append(...items){for(const item of items)this.children.push(...(item.tag==='#fragment'?item.children:[item]))}
 replaceChildren(...items){this.text='';this.children=[];this.append(...items)}
}
const channel={name:'YouTube',metric:'subscribers',followers:44,followers28dAgo:null,source:'YouTube Data API',verified_on:'2026-10-17'};
const baseline={followers28dAgo:0,baseline_verified:true,baseline_source:'Historical API snapshot',baseline_measured_at:'2026-09-19T00:00:00Z'};
async function render(overrides){
 const elements=new Map();
 const document={currentScript:{src:'https://example.test/assets/intelligence-data.js'},getElementById:id=>{if(!elements.has(id))elements.set(id,new Element('div'));return elements.get(id)},createElement:tag=>new Element(tag),createDocumentFragment:()=>new Element('#fragment')};
 const clock=class extends Date{static now(){return Date.parse('2026-10-17T03:20:00Z')}};
 vm.runInNewContext(source,{document,window:{SITE_READY:Promise.resolve({records:[],socialPulse:[{...channel,...overrides}]})},location:{origin:'https://example.test',href:'https://example.test/intelligence/index.html'},URL,AbortController,setTimeout,clearTimeout,Date:clock,fetch:async()=>({ok:false,status:503}),console},{timeout:1000});
 await new Promise(setImmediate);await new Promise(setImmediate);
 return document.getElementById('pulseGrid').textContent;
}
const cases=[
 ['valid source displays count',{},'44 subscribers',true],
 ['blank source withheld',{source:'   '},'44 subscribers',false],
 ['tab-only source withheld',{source:'\t\n'},'44 subscribers',false],
 ['non-string source withheld',{source:{}},'44 subscribers',false],
 ['missing baseline withheld',{followers28dAgo:0},'44 change in 28 days',false],
 ['unverified baseline withheld',{...baseline,baseline_verified:false},'44 change in 28 days',false],
 ['blank baseline source withheld',{...baseline,baseline_source:'  '},'44 change in 28 days',false],
 ['missing baseline date withheld',{...baseline,baseline_measured_at:null},'44 change in 28 days',false],
 ['invalid baseline date withheld',{...baseline,baseline_measured_at:'invalid'},'44 change in 28 days',false],
 ['future baseline withheld',{...baseline,baseline_measured_at:'2026-10-18T00:00:00Z'},'44 change in 28 days',false],
 ['wrong-period baseline withheld',{...baseline,baseline_measured_at:'2026-10-01T00:00:00Z'},'44 change in 28 days',false],
 ['verified 28-day zero baseline accepted',baseline,'44 change in 28 days',true],
 ['real measured zero retained',{followers:0},'0 subscribers',true],
 ['verified zero growth retained',{...baseline,followers:0},'0 change in 28 days',true],
 ['stale current measurement withheld',{...baseline,verified_on:'2026-10-01'},'44 subscribers',false]
];
for(const [name,input,expected,present] of cases)test(name,async()=>assert.equal((await render(input)).includes(expected),present));
