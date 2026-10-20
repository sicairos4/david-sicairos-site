const assert=require('node:assert/strict');
const {findRelease}=require('../assets/android-download.js');
const tag='android-preview-aaaaaaaaaaaa-123-1';
const base='https://github.com/sicairos4/david-sicairos-site/releases/download/'+tag+'/';
const names=['209-workstation-preview.apk','SHA256SUMS.txt','build-receipt.json','INSTALL.txt'];
function fixture(){return {draft:false,prerelease:true,tag_name:tag,name:'Preview',published_at:'2026-10-20T12:00:00Z',assets:names.map(name=>({name,state:'uploaded',size:1,browser_download_url:base+name}))};}
assert.equal(findRelease([fixture()]).files[names[0]],base+names[0]);
let r=fixture();r.assets.pop();assert.equal(findRelease([r]),null);
r=fixture();r.assets[0].browser_download_url='https://evil.example/app.apk';assert.equal(findRelease([r]),null);
r=fixture();r.draft=true;assert.equal(findRelease([r]),null);
r=fixture();r.prerelease=false;assert.equal(findRelease([r]),null);
r=fixture();r.assets[0].state='new';assert.equal(findRelease([r]),null);
r=fixture();r.tag_name='unrelated-release';assert.equal(findRelease([r]),null);
const newer=fixture();newer.name='Newer';newer.published_at='2026-10-20T13:00:00Z';assert.equal(findRelease([fixture(),newer]).name,'Newer');
assert.equal(findRelease(null),null);
console.log('9 download-discovery assertions passed');
