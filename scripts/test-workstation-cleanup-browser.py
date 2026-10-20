import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'test-results' / 'workstation-cleanup'
REPORT.mkdir(parents=True, exist_ok=True)
results = []
blocked = []

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)

def check(name, work):
    try:
        work()
        results.append({'check': name, 'status': 'passed'})
    except Exception as error:
        results.append({'check': name, 'status': 'failed', 'error': str(error)})
        raise

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in [1280, 390]:
            context = browser.new_context(viewport={'width': width, 'height': 900}, accept_downloads=True)
            def route(request):
                if urlparse(request.request.url).netloc == urlparse(base).netloc:
                    request.continue_()
                else:
                    blocked.append(urlparse(request.request.url).hostname)
                    request.abort()
            context.route('**/*', route)
            context.add_init_script("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__testClipboard=text;}}});")
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(base + '/members/app.html', wait_until='load')
            page.wait_for_selector('#workspaceCleanupMarker', state='attached', timeout=30000)
            page.evaluate("document.documentElement.dataset.memberState='demo';document.getElementById('memberGate').hidden=true;")
            page.wait_for_function("window.WorkstationApp && !window.WorkstationApp.busy")
            expect(page.locator('#mode')).to_have_text('Synthetic demo · memory only')
            suffix = str(width)
            for view in ['today', 'goals', 'focus', 'journal', 'review', 'create', 'learn', 'settings']:
                def view_check(view=view):
                    page.evaluate('(view)=>{location.hash=view;}', view)
                    expect(page.locator('[data-view="' + view + '"]')).to_be_visible()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), 'Horizontal overflow: ' + view
                    page.screenshot(path=str(REPORT / (view + '-' + suffix + '.png')))
                check('view-' + view + '-' + suffix, view_check)
            def groups():
                for key in ['settingsAccount','settingsPreferences','settingsSecurity','settingsData','settingsConnections','settingsAdvanced']:
                    expect(page.locator('#' + key)).to_have_count(1)
                expect(page.locator('#settingsPreferences #timezone')).to_have_count(1)
                expect(page.locator('#settingsSecurity #logout')).to_have_count(1)
                expect(page.locator('#reviewDailySection #dailyEveningCloseout')).to_have_count(1)
                expect(page.locator('#reviewWeeklySection [data-bind="plan.weeklyReview"]')).to_have_count(1)
            check('grouping-' + suffix, groups)
            draft = page.locator('[data-bind="plan.draft"]')
            lesson = page.locator('[data-bind="lesson"]')
            def imports():
                page.evaluate("location.hash='journal'")
                page.locator('#reflectionLesson').evaluate('(el)=>el.open=true')
                lesson.fill('Reviewed test lesson')
                page.evaluate("location.hash='create'")
                draft.fill('Existing test draft')
                page.locator('#creatorLessonImport').evaluate('(el)=>el.open=true')
                page.get_by_role('button', name='Append to draft', exact=True).click()
                expect(draft).to_have_value('Existing test draft' + chr(10) + chr(10) + 'Reviewed test lesson')
                page.once('dialog', lambda dialog: dialog.dismiss())
                page.get_by_role('button', name='Replace draft', exact=True).click()
                assert draft.input_value().startswith('Existing test draft')
                page.once('dialog', lambda dialog: dialog.accept())
                page.get_by_role('button', name='Replace draft', exact=True).click()
                expect(draft).to_have_value('Reviewed test lesson')
                draft.fill('x' * 19999)
                page.get_by_role('button', name='Append to draft', exact=True).click()
                assert draft.input_value() == 'x' * 19999
                expect(page.locator('#creatorLessonImport [role="status"]')).to_contain_text('exceeds')
            check('lesson-imports-' + suffix, imports)
            def outputs():
                draft.fill('Private test draft')
                page.get_by_role('button', name='Copy draft', exact=True).click()
                page.wait_for_function("window.__testClipboard==='Private test draft'")
                with page.expect_download() as event:
                    page.get_by_role('button', name='Download text', exact=True).click()
                download = event.value
                assert download.suggested_filename.endswith('.txt')
                assert Path(download.path()).read_text() == 'Private test draft'
                draft.fill('')
                expect(page.get_by_role('button', name='Copy draft', exact=True)).to_be_disabled()
                expect(page.get_by_role('button', name='Download text', exact=True)).to_be_disabled()
            check('copy-and-download-' + suffix, outputs)
            def save_reload():
                draft.fill('Saved demo draft')
                page.locator('#save').click()
                expect(page.locator('#saveState')).to_contain_text('Saved in demo memory')
                page.locator('#reload').click()
                page.wait_for_function('!window.WorkstationApp.busy')
                expect(draft).to_have_value('Saved demo draft')
            check('demo-save-reload-' + suffix, save_reload)
            def switch_day():
                draft.fill('Unsaved previous-day text')
                day = page.evaluate('window.WorkstationApp.day')
                target = '2026-10-19' if day != '2026-10-19' else '2026-10-18'
                page.once('dialog', lambda dialog: dialog.accept())
                page.evaluate("target=>{const day=document.getElementById('day');day.value=target;day.dispatchEvent(new Event('change',{bubbles:true}));}", target)
                page.wait_for_function('(target)=>!window.WorkstationApp.busy&&window.WorkstationApp.day===target', arg=target)
                expect(draft).to_have_value('')
                expect(page.locator('#creatorLessonPreview')).to_have_text('')
            check('day-switch-clearing-' + suffix, switch_day)
            def no_errors():
                assert not errors, json.dumps(errors)
            check('no-page-errors-' + suffix, no_errors)
            context.close()
        browser.close()
finally:
    server.shutdown()
    report = {'source': os.environ.get('GITHUB_SHA', 'local'), 'scope': 'isolated-demo-not-live-account-acceptance', 'results': results, 'blocked_external_hosts': sorted(set(blocked))}
    (REPORT / 'results.json').write_text(json.dumps(report, indent=2))
