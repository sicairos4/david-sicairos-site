'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8'),nav=read('assets/topbar.js'),legacy=read('assets/site.js'),css=read('assets/navigation-install.css');
test('Workspace offers open, install choice and guest links',()=>{for(const pair of ["['Open Workstation','login.html']","['Install app','android-download.html']","['Continue as guest','members/guest.html']"])assert.ok(nav.includes(pair));});
test('shared toolbar has one theme owner and no second mobile theme button',()=>{assert.ok(nav.includes("theme.dataset.themeOwner='shared-toolbar'"));assert.ok(!nav.includes('const mobileTheme='));assert.ok(nav.includes("actions.append(theme)"));});
test('legacy listener yields to shared theme ownership',()=>{assert.ok(legacy.includes('event.currentTarget.dataset.themeOwner!=="shared-toolbar"'));});
test('compact mode keeps Subscribe in menu and supports overflow',()=>{assert.ok(nav.includes("link('Subscribe free'"));assert.ok(nav.includes('row.scrollWidth>row.clientWidth+1'));assert.ok(css.includes('.site-actions>.nav-cta{display:none!important}'));});
test('keyboard and resize behavior remain present',()=>{assert.ok(nav.includes("event.key==='Escape'"));assert.ok(nav.includes("event.key!=='Tab'"));assert.ok(nav.includes("else if(overlay.contains(document.activeElement))nav.querySelector('a')?.focus()"));});
