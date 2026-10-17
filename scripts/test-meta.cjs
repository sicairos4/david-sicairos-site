const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/meta.js'),'utf8');
function run(url,description='Specific page description',theme='valley-light',image){
 const elements=[],callbacks=[],html={dataset:{theme}};
 class Element{constructor(tag){this.tag=tag;this.attrs={}}setAttribute(k,v){this.attrs[k]=v}getAttribute(k){return this.attrs[k]??null}}
 const head={appendChild:e=>elements.push(e),querySelector:q=>elements.find(e=>{const m=q.match(/^(\w+)\[([^=\]]+)(?:="([^"]*)")?\]$/);return m&&e.tag===m[1]&&m[2] in e.attrs&&(m[3]===undefined||e.attrs[m[2]]===m[3])})||null};
 if(description!==null){const e=new Element('meta');e.setAttribute('name','description');e.setAttribute('content',description);head.appendChild(e)}
 if(image){const e=new Element('meta');e.setAttribute('property','og:image');e.setAttribute('content',image);head.appendChild(e)}
 const document={currentScript:{src:'https://example.test/project/assets/meta.js'},title:'Page title',head,documentElement:html,readyState:'complete',createElement:t=>new Element(t)};
 const colors={'valley-light':'#f4f8f4','midnight-ledger':'#14171b','civic-gold':'#faf7f2'};
 vm.runInNewContext(source,{document,URL,location:{href:url},getComputedStyle:()=>({getPropertyValue:()=>colors[html.dataset.theme]}),MutationObserver:class{constructor(cb){callbacks.push(cb)}observe(){}}});
 return {elements,head,html,callbacks};
}
const nested='https://example.test/project/intelligence/index.html?utm_source=test#analytics';
test('preserves page-specific description',()=>assert.equal(run(nested).head.querySelector('meta[name="description"]').getAttribute('content'),'Specific page description'));
test('nested favicon resolves to project root',()=>assert.equal(run(nested).head.querySelector('link[rel="icon"]').getAttribute('href'),'https://example.test/project/favicon.svg'));
test('nested manifest resolves to project root',()=>assert.equal(run(nested).head.querySelector('link[rel="manifest"]').getAttribute('href'),'https://example.test/project/manifest.json'));
test('canonical drops tracking, fragment and index alias',()=>assert.equal(run(nested).head.querySelector('link[rel="canonical"]').getAttribute('href'),'https://example.test/project/intelligence/'));
test('Open Graph uses clean canonical',()=>assert.equal(run(nested).head.querySelector('meta[property="og:url"]').getAttribute('content'),'https://example.test/project/intelligence/'));
test('favicon is not invented as social image',()=>assert.equal(run(nested).head.querySelector('meta[property="og:image"]'),null));
test('existing real social image reused',()=>assert.equal(run(nested,undefined,undefined,'https://example.test/card.jpg').head.querySelector('meta[name="twitter:image"]').getAttribute('content'),'https://example.test/card.jpg'));
test('theme color follows theme changes',()=>{const r=run(nested);r.html.dataset.theme='civic-gold';r.callbacks[0]();assert.equal(r.head.querySelector('meta[name="theme-color"]').getAttribute('content'),'#faf7f2')});
test('member surfaces marked noindex',()=>assert.equal(run('https://example.test/project/members/').head.querySelector('meta[name="robots"]').getAttribute('content'),'noindex, nofollow'));
test('public landing is not marked private',()=>assert.equal(run('https://example.test/project/209connect/').head.querySelector('meta[name="robots"]'),null));
test('WebSite JSON-LD points to project root',()=>assert.equal(JSON.parse(run(nested).head.querySelector('script[data-site-schema]').textContent).url,'https://example.test/project/'));
