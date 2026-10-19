from pathlib import Path

changes = {}
def read(path):
    return changes.get(path, Path(path).read_text())
def replace(path, old, new):
    text = read(path)
    if text.count(old) != 1:
        raise RuntimeError('Source anchor changed: ' + path)
    changes[path] = text.replace(old, new, 1)

controller = 'assets/connect-app.js'
replace(controller, 'function lists(){', "function lists(){queueMicrotask(()=>window.dispatchEvent(new Event('workstation:render')));")
bridge = """window.WorkstationApp={get record(){return record;},get day(){return selected;},get context(){return accountEpoch+':'+generation;},get busy(){return busy||!loaded;},change(fn){if(busy||!loaded)throw Error('Wait for the selected day to finish loading.');capture();const result=fn(record);mark();lists();return result;}};
"""
replace(controller, "addEventListener('beforeunload',", bridge + "addEventListener('beforeunload',")

html = 'members/app.html'
free_tag = '<script defer src="../assets/workstation-free-time.js"></script>'
replace(html, free_tag, '')
replace(html, '<script defer src="../assets/connect-app.js"></script>', '<script defer data-record-only="true" src="../assets/workstation-free-time.js"></script><script defer src="../assets/workstation/record-scheduler.js"></script><script defer src="../assets/connect-app.js"></script>')
replace(html, '<script defer src="../assets/workstation/morning-ui.js"></script>', '<script defer src="../assets/workstation/morning-ui.js"></script><script defer src="../assets/workstation/planner-ui.js"></script>')
replace('assets/workstation-free-time.js', "if(typeof document==='undefined'||!document.getElementById('gapForm'))return;", "if(typeof document==='undefined'||document.currentScript?.dataset.recordOnly==='true'||!document.getElementById('gapForm'))return;")

engine = 'assets/workstation/record-scheduler.js'
protection = """function sleepRanges(){const value=record.plan.sleepWindow;if(!value?.enabled)return [];const start=F.minutes(value.start),end=F.minutes(value.end);if(start===end)throw Error('Sleep start and end must differ.');return start<end?[[start,end]]:[[start,1440],[0,end]];}
    function protect(block){const start=F.minutes(block.start),end=F.minutes(block.end);if(sleepRanges().some(([a,b])=>start<b&&end>a))throw Error('This block overlaps protected sleep. Change its times or explicitly change sleep protection.');}
    function protectedRows(options){const start=F.minutes(options.start),end=F.minutes(options.end);return sleepRanges().map(([a,b])=>[Math.max(start,a),Math.min(end,b)]).filter(([a,b])=>b>a).map(([a,b])=>({start:F.clock(a),end:F.clock(b)}));}
    """
replace(engine, 'function add(title,start,end,taskId){', protection + 'function add(title,start,end,taskId){')
replace(engine, 'list.push(block);invalidate();', 'protect(block);list.push(block);invalidate();')
replace(engine, 'list[index]=next;invalidate();', 'protect(next);list[index]=next;invalidate();')
replace(engine, 'JSON.stringify([day,rows()])', 'JSON.stringify([day,rows(),record.plan.sleepWindow])')
replace(engine, 'F.findSlots(rows(),settings)', 'F.findSlots([...rows(),...protectedRows(settings)],settings)')
replace(engine, 'return {add,update,remove,search,choose,invalidate,', 'return {add,update,remove,search,choose,invalidate,validateSleep:()=>rows().forEach(protect),')

morning = 'assets/workstation/morning-ui.js'
remember = """function remember(){ready();const app=window.WorkstationApp;if(!app)throw Error('Planner is unavailable.');app.change(record=>{record.plan.morningRoutine={start:$('morningStart').value,steps:structuredClone(steps)};});}
"""
replace(morning, "function reset(){steps=M.defaults();$('morningStart').value='07:00';", remember + "function reset(){const saved=window.WorkstationApp?.record.plan.morningRoutine;steps=saved?.steps?structuredClone(saved.steps):M.defaults();$('morningStart').value=saved?.start||'07:00';")
replace(morning, 'steps=M.update(steps,i,patch);render();', 'steps=M.update(steps,i,patch);remember();render();')
replace(morning, 'steps=M.move(steps,i,d);render();', 'steps=M.move(steps,i,d);remember();render();')
replace(morning, "$('morningStart').addEventListener('change',preview);", "$('morningStart').addEventListener('change',()=>{try{remember();preview();}catch(e){say(e.message);}});")
replace(morning, "row.className='morning-step';", "row.className='morning-step';row.draggable=true;row.ondragstart=e=>{if(window.WorkstationApp?.busy){e.preventDefault();return;}e.dataTransfer.setData('application/x-workstation-step',JSON.stringify({index:i,context:window.WorkstationApp.context}));};row.ondragover=e=>e.preventDefault();row.ondrop=e=>{e.preventDefault();try{ready();const value=JSON.parse(e.dataTransfer.getData('application/x-workstation-step'));if(value.context!==window.WorkstationApp.context||!Number.isInteger(value.index)||value.index<0||value.index>=steps.length)throw Error('The routine context changed.');let from=value.index;while(from!==i){const direction=from<i?1:-1;steps=M.move(steps,from,direction);from+=direction;}remember();render();}catch(error){say(error.message);}};")
text = read(morning)
start = text.index("$('morningAddBlocks').onclick=")
end = text.index('function watch()', start)
changes[morning] = text[:start] + """$('morningAddBlocks').onclick=()=>{try{ready();const rows=M.timeline($('morningStart').value,steps);if(!rows.length)throw Error('Enable at least one step.');if($('blockTitle').value.trim())throw Error('Finish or clear the Schedule block draft first.');if(!confirm('Add '+rows.length+' morning steps to '+$('day').value+' as unsaved blocks?'))return;ready();if(!window.WorkstationSchedule)throw Error('Scheduler is unavailable.');window.WorkstationSchedule.addMany(rows);say('Added the complete morning as unsaved blocks. Review Schedule and choose Save selected day.');}catch(error){say(error.message+' No partial morning was added.');}};
""" + text[end:]

changes['assets/workstation/planner-ui.js'] = r"""(()=>{'use strict';
const A=window.WorkstationApp,R=window.WorkstationRecordScheduler,F=window.WorkstationFreeTime,$=id=>document.getElementById(id);if(!A||!R||!F)return;
let engine=null,record=null,context=null,editing=null,history=[];const say=text=>$('status').textContent=text;
const controls=document.createElement('fieldset');controls.innerHTML='<legend>Protected sleep and schedule undo</legend><label><input id="protectSleep" type="checkbox"> Protect sleep from new blocks and free-time suggestions</label><label>Sleep starts<input id="sleepStart" type="time" value="22:00"></label><label>Sleep ends<input id="sleepEnd" type="time" value="07:00"></label><button id="applySleep" type="button">Apply sleep settings</button><button id="undoSchedule" type="button">Undo last schedule change</button><p>Sleep can cross midnight. Changes remain unsaved until Save selected day. Undo is scoped to the currently loaded record and clears on reload, save or account change.</p>';
$('blockForm').before(controls);const submit=$('blockForm').querySelector('button[type=submit]'),cancel=document.createElement('button');cancel.type='button';cancel.textContent='Cancel block edit';cancel.hidden=true;$('blockForm').append(cancel);
function clearGaps(text='Find openings for the selected day.'){engine?.invalidate();$('gapResults').replaceChildren();$('gapStatus').textContent=text;}
function endEdit(){editing=null;submit.textContent='Add block';cancel.hidden=true;$('blockTitle').value='';$('blockStart').value='';$('blockEnd').value='';$('blockTask').value='';}
function ensure(){if(record!==A.record||context!==A.context){engine?.dispose();record=A.record;context=A.context;engine=R.bind(A.day,record);history=[];endEdit();clearGaps('Loaded context changed. Find openings again.');const sleep=record.plan.sleepWindow||{};$('protectSleep').checked=!!sleep.enabled;$('sleepStart').value=sleep.start||'22:00';$('sleepEnd').value=sleep.end||'07:00';}return engine;}
function snapshot(){return {blocks:structuredClone(A.record.plan.scheduleBlocks),sleep:structuredClone(A.record.plan.sleepWindow??null)};}
function restore(value){A.record.plan.scheduleBlocks=structuredClone(value.blocks);if(value.sleep===null)delete A.record.plan.sleepWindow;else A.record.plan.sleepWindow=structuredClone(value.sleep);}
function change(work){ensure();if(A.busy)throw Error('Wait for the planner to finish.');const before=snapshot();try{A.change(()=>work(engine));history.push(before);if(history.length>30)history.shift();clearGaps('Schedule changed. Find openings again.');}catch(error){restore(before);engine.invalidate();throw error;}}
function attempt(fn){try{fn();}catch(error){say(error.message);}}
function button(host,text,fn){const b=document.createElement('button');b.type='button';b.textContent=text;b.onclick=()=>attempt(fn);host.append(b);return b;}
function render(){ensure();const host=$('blockList');host.replaceChildren();for(const block of [...A.record.plan.scheduleBlocks].sort((a,b)=>a.start.localeCompare(b.start))){const row=document.createElement('div');row.className='connect-item';const text=document.createElement('span'),task=A.record.plan.workspaceTasks.find(t=>t.id===block.taskId);text.textContent=block.start+'–'+block.end+' · '+block.title+(task?' · Task: '+task.text:'');row.append(text);button(row,'Edit',()=>{if(A.busy)throw Error('Wait for the planner.');editing=block.id;$('blockTitle').value=block.title;$('blockStart').value=block.start;$('blockEnd').value=block.end;$('blockTask').value=block.taskId||'';submit.textContent='Update block';cancel.hidden=false;$('blockTitle').focus();});button(row,'Remove',()=>{change(e=>e.remove(block.id));if(editing===block.id)endEdit();});const duration=F.minutes(block.end)-F.minutes(block.start);const moveLabel=document.createElement('label'),move=document.createElement('input');moveLabel.textContent='Move '+block.title+' (drag or use arrow keys)';move.type='range';move.min='0';move.max=String(1439-duration);move.step='1';move.value=String(F.minutes(block.start));move.setAttribute('aria-label','Start minute for '+block.title);move.onchange=()=>attempt(()=>{const start=Number(move.value);change(e=>e.update(block.id,block.title,F.clock(start),F.clock(start+duration),block.taskId));});moveLabel.append(move);row.append(moveLabel);const resizeLabel=document.createElement('label'),resize=document.createElement('input');resizeLabel.textContent='Resize '+block.title+' in minutes';resize.type='range';resize.min='1';resize.max=String(1439-F.minutes(block.start));resize.step='1';resize.value=String(duration);resize.setAttribute('aria-label','Duration in minutes for '+block.title);resize.onchange=()=>attempt(()=>change(e=>e.update(block.id,block.title,block.start,F.clock(F.minutes(block.start)+Number(resize.value)),block.taskId)));resizeLabel.append(resize);row.append(resizeLabel);host.append(row);}$('undoSchedule').disabled=A.busy||history.length===0;}
$('blockForm').onsubmit=event=>{event.preventDefault();attempt(()=>{const title=$('blockTitle').value,start=$('blockStart').value,end=$('blockEnd').value,task=$('blockTask').value;change(e=>editing?e.update(editing,title,start,end,task):e.add(title,start,end,task));endEdit();say('Schedule updated. Choose Save selected day to keep it.');});};cancel.onclick=()=>{if(!A.busy)endEdit();};
$('applySleep').onclick=()=>attempt(()=>{change(e=>{A.record.plan.sleepWindow={enabled:$('protectSleep').checked,start:$('sleepStart').value,end:$('sleepEnd').value};F.minutes(A.record.plan.sleepWindow.start);F.minutes(A.record.plan.sleepWindow.end);if(A.record.plan.sleepWindow.start===A.record.plan.sleepWindow.end)throw Error('Sleep start and end must differ.');e.validateSleep();});say('Sleep settings applied to this day. Save selected day to keep them.');});
$('undoSchedule').onclick=()=>attempt(()=>{ensure();if(A.busy||!history.length)throw Error('No available schedule undo.');const value=history.at(-1),ids=new Set(A.record.plan.workspaceTasks.map(t=>t.id));if(value.blocks.some(b=>b.taskId&&!ids.has(b.taskId)))throw Error('Undo would restore a deleted task link. Reload or edit the affected block instead.');A.change(()=>restore(value));history.pop();engine.invalidate();endEdit();const sleep=A.record.plan.sleepWindow||{};$('protectSleep').checked=!!sleep.enabled;$('sleepStart').value=sleep.start||'22:00';$('sleepEnd').value=sleep.end||'07:00';clearGaps('Schedule restored as unsaved edits.');say('Undid the last schedule change. Save selected day to keep it.');});
function options(){return {start:$('gapStart').value,end:$('gapEnd').value,duration:Number($('gapDuration').value),buffer:Number($('gapBuffer').value)};}
$('gapForm').onsubmit=event=>{event.preventDefault();attempt(()=>{ensure();if(A.busy)throw Error('Wait for the planner.');clearGaps();const owner=engine,settings=options(),slots=engine.search(settings);$('gapStatus').textContent=slots.length?'Openings for '+A.day+' excluding protected sleep. Review before adding.':'No opening fits. Nothing was moved.';slots.forEach((slot,index)=>{const row=document.createElement('div'),label=document.createElement('span');row.className='connect-item';label.textContent=slot.start+'–'+slot.end+' · '+slot.availableMinutes+' available minutes';row.append(label);button(row,'Use these times',()=>{ensure();if(A.busy||engine!==owner)throw Error('The planner context changed. Search again.');const times=engine.choose(index,options());$('blockStart').value=times.start;$('blockEnd').value=times.end;clearGaps('Times filled. Review the title and task, then add or update the block.');$('blockTitle').focus();});$('gapResults').append(row);});});};
for(const id of ['gapStart','gapEnd','gapDuration','gapBuffer'])$(id).addEventListener('input',()=>clearGaps('Search settings changed. Find openings again.'));$('gapClear').onclick=()=>clearGaps();$('day').addEventListener('change',()=>clearGaps('Day selection changed. Find openings again.'));
window.WorkstationSchedule={addMany(rows){if(!Array.isArray(rows)||!rows.length)throw Error('No morning steps selected.');change(e=>{for(const row of rows)e.add(row.title,row.start,row.end,null);});}};
addEventListener('workstation:render',render);addEventListener('pagehide',()=>{engine?.dispose();history=[];record=null;context=null;});addEventListener('pageshow',event=>{if(event.persisted)render();});render();
})();
"""

for path, content in changes.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
