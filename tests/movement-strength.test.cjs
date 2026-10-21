const test=require('node:test'),a=require('node:assert/strict'),c=require('../assets/workstation/movement.js');
test('original programs',()=>{a.equal(c.rows('alpha','Full body').length,5);a.deepEqual(c.rows('beta','A'),c.rows('beta','C'));a.equal(c.rows('beta','B')[2][2],'8');});
test('selection and numbers',()=>{a.throws(()=>c.rows('__proto__','A'));a.equal(c.number('',200,true),null);a.throws(()=>c.number(1.5,200,true));});
test('times and independent sets',()=>{a.deepEqual(c.times('17:00',45),{start:'17:00',end:'17:45'});a.throws(()=>c.times('23:50',30));const r=c.blank('beta','A');r.exercises[0].sets[0].load=50;a.equal(r.exercises[0].sets[1].load,null);});
