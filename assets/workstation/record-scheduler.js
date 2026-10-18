(function(g){
'use strict';
const node=typeof module!=='undefined'&&module.exports;
const C=node?require('../connect-core.js'):g.ConnectCore;
const F=node?require('../workstation-free-time.js'):g.WorkstationFreeTime;
function bind(day,record){
    C.day(day);
    if(!record?.plan||!Array.isArray(record.plan.scheduleBlocks)||!Array.isArray(record.plan.workspaceTasks))throw Error('Load a valid selected-day record first.');
    let active=true,ticket=null;
    const copy=value=>structuredClone(value);
    function rows(){if(!active)throw Error('Scheduler was replaced; reload the current day.');return record.plan.scheduleBlocks;}
    function invalidate(){ticket=null;}
    function fingerprint(){return JSON.stringify([day,rows()]);}
    function task(id){if(id&&!record.plan.workspaceTasks.some(t=>t.id===id))throw Error('Linked task no longer exists.');return id||null;}
    function locate(id){const index=rows().findIndex(b=>b.id===id);if(index<0)throw Error('Block no longer exists.');return index;}
    function add(title,start,end,taskId){const list=rows(),link=task(taskId),block={...C.block(title,start,end,list),taskId:link};list.push(block);invalidate();return copy(block);}
    function update(id,title,start,end,taskId){const index=locate(id),list=rows(),previous=list[index],link=task(taskId===undefined?previous.taskId:taskId);const checked=C.block(title,start,end,list.filter((_,i)=>i!==index));const next={...previous,title:checked.title,start:checked.start,end:checked.end,taskId:link};list[index]=next;invalidate();return copy(next);}
    function remove(id){const index=locate(id);rows().splice(index,1);invalidate();}
    function search(options){invalidate();const settings=copy(options),slots=F.findSlots(rows(),settings);ticket={fingerprint:fingerprint(),settings:JSON.stringify(settings),slots:copy(slots)};return copy(slots);}
    function choose(index,options){if(!active||!ticket||ticket.fingerprint!==fingerprint()||ticket.settings!==JSON.stringify(options)||!Number.isInteger(index)||!ticket.slots[index]){invalidate();throw Error('The day or search changed. Find openings again.');}const slot=ticket.slots[index],times={start:slot.start,end:slot.end};invalidate();return times;}
    return {add,update,remove,search,choose,invalidate,snapshot:()=>({day,blocks:copy(rows())}),dispose(){active=false;invalidate();}};
}
const api={bind};if(node)module.exports=api;else g.WorkstationRecordScheduler=api;
})(globalThis);
