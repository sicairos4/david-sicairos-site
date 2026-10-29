"""Apply explicit entry-flow source edits. No backend requests or tests."""
from pathlib import Path


def replace(path, old, new):
    file = Path(path)
    text = file.read_text(encoding='utf-8')
    if old not in text:
        if new in text:
            return
        raise RuntimeError('Source changed; refusing an unexpected edit: ' + path)
    file.write_text(text.replace(old, new), encoding='utf-8')


replace('assets/connect-core.js', "function demo(){return normalize({plan:{capacity:'Steady',priority:'Make one useful thing',microstep:'Open the project and choose a small action',workspaceTasks:[{text:'Try this synthetic example',area:'Brand and business',done:false}],scheduleBlocks:[{title:'A flexible focus block',start:'09:00',end:'10:00'}]}});}", "function demo(){return normalize({plan:{capacity:'Steady'}});}")
replace('assets/connect-core.js', "this.kind='demo'", "this.kind='local'")
for old, new in [
    ('Synthetic demo · memory only', 'Not signed in'),
    ('Demo changes stay in memory and clear when this page closes.', 'Your work stays in this tab. Save keeps it in tab memory; export a copy before closing. Sign in for account saving.'),
    ('Saved in demo memory only.', 'Saved in this tab only, not to an account. Export a copy before closing.'),
    ('Account library unavailable; demo remains usable.', 'Account service unavailable; the tools remain usable in this tab.'),
    ('No verified account session. Use Sign in; demo data will not be uploaded.', 'Not signed in. Use the tools here, or sign in to load and save account records.'),
    ('Discard unsaved edits and reset synthetic demo?', 'Clear the current tab workspace? Export any work you want to keep first.'),
    ('Synthetic demo reset. No account records changed.', 'Current tab workspace cleared. No account records changed.'),
    ('Valid demo preferences; not saved to an account.', 'Preferences are valid but have not been saved to an account.'),
    ('Synthetic demo ready. No account library is available.', 'Tools ready. Account service is unavailable; work stays in this tab.'),
    ("get context(){return accountEpoch+':'+generation;}", "get accountId(){return uid;},snapshot(){return C.normalize(capture());},get context(){return accountEpoch+':'+generation;}"),
]:
    replace('assets/connect-app.js', old, new)

file = Path('assets/member-session.js')
text = file.read_text(encoding='utf-8')
start_marker = "if(!$('memberGate'))return;"
end_marker = '(()=>{const M=globalThis.WorkstationModules;'
if start_marker in text:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    text = text[:start] + "root.dataset.memberState='ready';$('memberGate')?.remove();})();\n" + text[end:]
    file.write_text(text, encoding='utf-8')
elif "root.dataset.memberState='ready';$('memberGate')?.remove();" not in text:
    raise RuntimeError('Unexpected member entry controller; refusing edit')

for path in ['members/app.html', 'assets/member-session.js']:
    replace(path, '209. Connect Workspace', '209 Connect Workstation')
    replace(path, '209. CONNECT WORKSPACE', '209 CONNECT WORKSTATION')

replace('members/app.html', '<title>209 Connect Workstation | Workstation</title>', '<title>209 Connect Workstation</title>')
replace('members/app.html', '<h1>Workstation</h1>', '<h1>209 Connect Workstation</h1>')
replace('members/app.html', 'data-member-state="loading"', 'data-member-state="ready"')
replace('members/app.html', '<button id="demo" type="button">Use demo</button>', '<button id="demo" type="button">Clear current tab workspace</button>')
replace('members/app.html', '<button id="account" type="button">Reload account</button>', '<button id="account" type="button">Load saved account</button>')
replace('members/app.html', '<p id="mode" class="mode-badge">Connecting account</p>', '<p id="mode" class="mode-badge">Opening Workstation</p>')
replace('members/app.html', '<script defer src="../assets/connect-app.js"></script>', '<script defer src="../assets/connect-app.js"></script><script defer src="../assets/workstation/account-entry.js"></script>')
file = Path('members/app.html')
text = file.read_text(encoding='utf-8')
opening = '<aside id="memberGate"'
if opening in text:
    start = text.index(opening)
    end = text.index('</aside>', start) + len('</aside>')
    file.write_text(text[:start] + text[end:], encoding='utf-8')
replace('assets/workstation/entry-flow.js', 'Advanced account and demo tools', 'Account options')
replace('assets/workstation/entry-flow.js', "[['Explore website','index.html'],['Guest planner','members/guest.html']]", "[['Explore website','index.html']]")
replace('android/app/src/main/AndroidManifest.xml', 'android:label="209 Workstation"', 'android:label="209 Connect Workstation"')
