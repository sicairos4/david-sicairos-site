(function(g){
'use strict';
const F=typeof module!=='undefined'?require('../workstation-free-time.js'):g.WorkstationFreeTime;
function validDay(value){if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))throw Error('Use a valid calendar day.');const d=new Date(value+'T00:00:00Z');if(!Number.isFinite(d.getTime())||d.toISOString().slice(0,10)!==value)throw Error('Use a valid calendar day.');return value;}
function create(day){let selected=validDay(day),blocks=[],ticket=null,nextId=1;
const copy=value=>JSON.parse(JSON.stringify(value));
const invalidate=()=>{ticket=null;};
const snapshot=()=>({day:selected,blocks:copy(blocks)});
function search(options){invalidate();const settings=copy(options),slots=F.findSlots(blocks,settings);ticket={settings:JSON.stringify(settings),slots:copy(slots)};return copy(slots);}
function choose(index,options){if(!ticket||ticket.settings!==JSON.stringify(options)||!Number.isInteger(index)||!ticket.slots[index]){invalidate();throw Error('Find openings again; this selection is no longer valid.');}const slot=copy(ticket.slots[index]);invalidate();return {start:slot.start,end:slot.end};}
function add(title,start,end){if(typeof title!=='string'||!title.trim()||title.trim().length>300)throw Error('Enter a title of 1 to 300 characters.');const a=F.minutes(start),b=F.minutes(end);if(b<=a)throw Error('End must be later on the same day.');if(blocks.some(x=>a<F.minutes(x.end)&&b>F.minutes(x.start)))throw Error('This block overlaps an existing block.');const block={id:String(nextId++),title:title.trim(),start,end};blocks.push(block);blocks.sort((x,y)=>x.start.localeCompare(y.start));invalidate();return copy(block);}
function remove(id){const index=blocks.findIndex(x=>x.id===id);if(index<0)throw Error('Block no longer exists.');blocks.splice(index,1);invalidate();}
function setDay(day){const value=validDay(day);if(value!==selected){selected=value;blocks=[];}invalidate();}
return {snapshot,search,choose,add,remove,setDay,invalidate};}
const api={create,validDay};if(typeof module!=='undefined')module.exports=api;else g.WorkstationCore=api;
})(globalThis);
