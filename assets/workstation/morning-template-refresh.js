(()=>{'use strict';
let sequence=0;
addEventListener('workstation:morning-routine-updated',()=>{
const status=document.getElementById('status');
if(status)status.textContent='Ready. Morning routine template applied ('+(++sequence)+'); review and save selected day.';
});
})();
