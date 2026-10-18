'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),R=require('../assets/workstation/weekly-review.js');
const answers={helped:'Opening one document',friction:'Too many steps',choice:'shrink',step:'Write one sentence',cue:'After breakfast'};
test('review range is seven inclusive calendar days across year boundary',()=>{assert.deepEqual(R.range('2026-01-03'),{start:'2025-12-28',end:'2026-01-03'});});
test('real calendar dates are required',()=>{assert.throws(()=>R.range('2026-02-30'));assert.throws(()=>R.range('bad'));assert.deepEqual(R.range('2024-03-01'),{start:'2024-02-24',end:'2024-03-01'});});
test('guided reflection contains only explicitly supplied answers',()=>{const result=R.compose('2026-10-18',answers);assert.match(result,/Make it easier/);assert.match(result,/Write one sentence/);assert.match(result,/2026-10-12 to 2026-10-18/);});
test('empty answers and unsupported progression are rejected',()=>{assert.throws(()=>R.compose('2026-10-18',{helped:'',friction:'',step:'',cue:'',choice:'keep'}));assert.throws(()=>R.compose('2026-10-18',{...answers,choice:'double-everything'}));});
test('append preserves the existing review',()=>{assert.equal(R.append('Previous reflection','New reflection'),'Previous reflection\n\nNew reflection'.replaceAll('\n','
'));});
test('length guard rejects overflow without altering original',()=>{const existing='x'.repeat(19999);assert.throws(()=>R.append(existing,'New'));assert.equal(existing.length,19999);assert.throws(()=>R.compose('2026-10-18',{...answers,step:'x'.repeat(2001)}));});
