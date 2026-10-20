// Compatibility bridge: reset the routine editor through its existing context observer.
addEventListener('workstation:morning-routine-updated',()=>{
const status=document.getElementById('status');
if(status)status.textContent='Ready. Morning routine template applied; review and save selected day.';
});
