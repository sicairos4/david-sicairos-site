'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const css=fs.readFileSync(path.join(__dirname,'../assets/workstation/views.css'),'utf8');
test('active navigation sets foreground and background together',()=>{const rule=css.match(/\.connect-nav a\[aria-current=page\]\{([^}]+)\}/);assert.ok(rule);assert.match(rule[1],/background:var\(--panel/);assert.match(rule[1],/color:var\(--text\)/);});
test('mobile sections remain one horizontal navigation row',()=>{assert.match(css,/@media\(max-width:600px\)/);assert.match(css,/\.connect-nav\{flex-wrap:nowrap;overflow-x:auto/);assert.match(css,/scrollbar-width:thin/);});
test('forms can shrink without clipping long fields',()=>{assert.match(css,/min-inline-size:0/);assert.match(css,/grid-template-columns:repeat\(auto-fit,minmax\(min\(100%,10rem\),1fr\)\)/);assert.match(css,/overflow-wrap:anywhere/);assert.doesNotMatch(css,/overflow-x:hidden/);});
test('actions wrap and narrow list controls use bounded columns',()=>{assert.match(css,/flex:1 1 8rem;min-width:0/);assert.match(css,/grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);assert.match(css,/min-height:44px/);assert.match(css,/font-size:16px/);});
test('privacy visibility and non-overlay save controls are preserved',()=>{assert.match(css,/\[hidden\]\{display:none!important\}/);assert.match(css,/\.save-bar\{position:static/);assert.match(css,/@media print/);});
