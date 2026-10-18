(()=>{'use strict';
const $=id=>document.getElementById(id);if(!$('searchForm'))return;
if(!globalThis.WorkstationCore){$('status').textContent='Core modules failed to load. No account data was accessed.';return;}
const now=new Date(),localDay=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');$('day').value=localDay;const core=WorkstationCore.create(localDay);
const options=()=>({start:$('from').value,end:$('until').value,duration:Number($('duration').value),buffer:Number($('buffer').value)});
function say(text){$('status').textContent=text;}
function clear(){core.invalidate();$('results').replaceChildren();}
function run(fn){try{fn();}catch(error){clear();say(error.message);}}
function render(){clear();$('blocks').replaceChildren();for(const b of core.snapshot().blocks){const li=document.createElement('li'),text=document.createElement('span'),button=document.createElement('button');text.textContent=b.start+'–'+b.end+' · '+b.title;button.type='button';button.textContent='Remove '+b.title;button.onclick=()=>run(()=>{core.remove(b.id);render();say('Removed from memory only.');});li.append(text,button);$('blocks').append(li);}}
$('searchForm').onsubmit=event=>{event.preventDefault();run(()=>{clear();const slots=core.search(options());say(slots.length?'Earliest starts in up to eight gaps. Select times, then review and add a block.':'No matching opening. Nothing was moved.');slots.forEach((slot,index)=>{const button=document.createElement('button');button.type='button';button.textContent='Use '+slot.start+'–'+slot.end+' ('+slot.availableMinutes+' free minutes)';button.onclick=()=>run(()=>{const times=core.choose(index,options());$('start').value=times.start;$('end').value=times.end;clear();say('Times filled. Review the title and choose Add block. Nothing has been added.');$('title').focus();});$('results').append(button);});});};
for(const id of ['from','until','duration','buffer'])$(id).addEventListener('input',()=>{clear();say('Search changed. Find openings again.');});
$('addForm').onsubmit=event=>{event.preventDefault();run(()=>{core.add($('title').value,$('start').value,$('end').value);$('addForm').reset();render();say('Added to memory only. Reloading or changing day clears these blocks.');});};
$('day').onchange=()=>{const before=core.snapshot().day;run(()=>{WorkstationCore.validDay($('day').value);if($('day').value!==before&&core.snapshot().blocks.length&&!confirm('Discard these memory-only blocks and change day?')){$('day').value=before;clear();return;}core.setDay($('day').value);$('addForm').reset();render();say('Day selected. No saved records were loaded.');});$('day').value=core.snapshot().day;};
addEventListener('pagehide',clear);render();
})();
