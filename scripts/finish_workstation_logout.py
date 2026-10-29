"""Apply bounded logout corrections; no authentication calls or tests."""
from pathlib import Path


def replace(path, old, new):
    file = Path(path)
    text = file.read_text(encoding='utf-8')
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError('Unexpected source; refusing edit: ' + path)
    file.write_text(text.replace(old, new, 1), encoding='utf-8')


replace('assets/connect-app.js', 'remaining=1500;\nfunction say', 'remaining=1500,sessionUserId=null;\nfunction say')
replace('assets/connect-app.js', "client=window.supabase.createClient('https://uwidjnnhdgtrpsymuhwp.supabase.co','sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN');subscription=", "client=window.WorkstationAccountClient||window.supabase.createClient('https://uwidjnnhdgtrpsymuhwp.supabase.co','sb_publishable_4p80QT7444VeKUlp4ncNvg_OFa9ptaN');window.WorkstationAccountClient=client;subscription=")
replace('assets/connect-app.js', "subscription=client.auth.onAuthStateChange((event,session)=>{if(event==='SIGNED_OUT'||(uid&&session?.user?.id!==uid)){wipe();say('Account state changed; private fields cleared.');}}).data.subscription;", "subscription=client.auth.onAuthStateChange((event,session)=>{sessionUserId=session?.user?.id||null;if(event==='SIGNED_OUT'||(uid&&session?.user?.id!==uid)){wipe();say('Account state changed; private fields cleared.');}if(event==='SIGNED_OUT'){try{sessionStorage.removeItem('209-workstation-before-signin-v1');}catch{}queueMicrotask(()=>window.dispatchEvent(new Event('workstation:signed-out')));}queueMicrotask(()=>window.dispatchEvent(new Event('workstation:account')));}).data.subscription;")
old = "$('logout').onclick=()=>action(async()=>{if(dirty&&!confirm('Discard unsaved edits and sign out?'))return;if(client){const {error}=await client.auth.signOut();if(error)throw error;}wipe();say('Signed out; private fields cleared.');});"
new = """function accountDeadline(promise){let timer;return Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Account operation timed out. Sign-out is not confirmed; the request may still finish.')),12000);})]).finally(()=>clearTimeout(timer));}
async function signOut(){if(busy)return false;await action(async()=>{if(!client){say('You are not connected to an account. Your current tab work is unchanged.');return;}const session=await accountDeadline(client.auth.getSession());if(session.error)throw session.error;if(!session.data?.session){sessionUserId=null;if(uid)wipe();say('No active account session. Current signed-out work has not been cleared.');window.dispatchEvent(new Event('workstation:account'));return;}if(dirty&&!confirm('Sign out on this device and discard unsaved planner edits? Export the day first if you want to keep them.'))return;const result=await accountDeadline(client.auth.signOut({scope:'local'}));if(result.error)throw result.error;sessionUserId=null;try{sessionStorage.removeItem('209-workstation-before-signin-v1');}catch{}wipe();window.dispatchEvent(new Event('workstation:signed-out'));window.dispatchEvent(new Event('workstation:account'));say('Signed out on this device. Private planner fields were cleared. You can keep using Workstation.');});return !uid&&!sessionUserId;}
$('logout').onclick=()=>{void signOut();};"""
replace('assets/connect-app.js', old, new)
replace('assets/connect-app.js', 'get accountId(){return uid;},snapshot()', 'get accountId(){return uid;},get sessionAccountId(){return sessionUserId;},signOut,snapshot()')
replace('assets/workstation/account-profile.js', "signout.type=reload.type='button';", "signout.type=reload.type='button';signout.dataset.workstationSignout='true';")
replace('assets/workstation/account-profile.js', 'signout.disabled=busy;', 'signout.disabled=busy||!user;')
replace('assets/workstation/account-profile.js', "$('logout')?.click();", "void g.WorkstationApp?.signOut?.();")
replace('assets/workstation/account-entry.js', "function refresh(){state.textContent=", "function refresh(){const active=!!(A.accountId||A.sessionAccountId);for(const button of document.querySelectorAll('#logout,[data-workstation-signout]'))button.hidden=!active;state.textContent=")
replace('assets/workstation/account-entry.js', "addEventListener('workstation:render',()=>queueMicrotask(refresh));", "addEventListener('workstation:account',()=>queueMicrotask(refresh));addEventListener('workstation:signed-out',()=>{forget();notice.textContent='Signed out on this device. The preserved sign-in copy was cleared.';refresh();});addEventListener('workstation:render',()=>queueMicrotask(refresh));")
