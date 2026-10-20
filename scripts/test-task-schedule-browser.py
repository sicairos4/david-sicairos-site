import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa-artifacts' / 'task-schedule'
BASE = 'http://127.0.0.1:4176'

async def run_case(browser, width, height):
    context = await browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
    page = await context.new_page()
    errors = []
    checks = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    async def local_only(route):
        url = route.request.url
        if url == BASE + '/assets/member-session.js':
            await route.fulfill(status=200, content_type='application/javascript', body='/* Test only: no account client or member gate. */')
        elif url.startswith(BASE + '/'):
            await route.continue_()
        else:
            await route.abort()

    await context.route('**/*', local_only)
    result = {'width': width, 'height': height, 'checks': checks, 'passed': False, 'scope': 'Local synthetic memory adapter, no production authentication or database requests'}
    try:
        await page.goto(BASE + '/members/app.html', wait_until='load')
        await page.evaluate("""() => {
          document.documentElement.dataset.memberState='demo';
          document.getElementById('memberGate').hidden=true;
        }""")
        await page.wait_for_function('window.WorkstationApp && !window.WorkstationApp.busy && window.WorkstationSchedule')
        await page.add_script_tag(url=BASE + '/assets/workstation/entry-flow.js')
        await page.wait_for_function("document.getElementById('taskSchedulePanel') && window.WorkstationToday")
        await expect(page.locator('#mode')).to_have_text('Synthetic demo · memory only')
        checks.append('synthetic_adapter_no_external_requests')
        await page.locator('#taskText').fill('Schedule acceptance task')
        await page.locator('#taskForm button[type=submit]').click()
        await expect(page.locator('#taskList .connect-item')).to_have_count(2)
        count = await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length')
        row = page.locator('#taskList .connect-item').filter(has_text='Schedule acceptance task')
        await row.get_by_role('button', name='Schedule', exact=True).click()
        panel = page.locator('#taskSchedulePanel')
        await expect(panel).to_be_visible()
        await expect(panel).to_contain_text('Schedule acceptance task')
        await panel.locator('input[type=time]').fill('10:45')
        await panel.get_by_role('button', name='25 min', exact=True).click()
        await expect(panel).to_contain_text('Ends at 11:10')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count
        checks.append('preview_and_cancel_do_not_add_block')
        await row.get_by_role('button', name='Schedule', exact=True).click()
        await panel.locator('input[type=time]').fill('10:45')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        await expect(panel).to_be_hidden()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        assert await page.evaluate("""() => {const r=WorkstationApp.record;const t=r.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task');return r.plan.scheduleBlocks.some(b=>b.taskId===t.id&&b.start==='10:45'&&b.end==='11:10') && !t.done;}""")
        checks.append('add_preserves_task_link_without_completion')
        await page.evaluate("WorkstationToday.go('editor')")
        await expect(page.locator('#todayBlockEditor')).to_have_attribute('open', '')
        await page.locator('#blockTitle').fill('Keep this unsaved editor draft')
        await page.locator('#todayBlockEditor').evaluate('(el) => el.open=false')
        await page.get_by_role('button', name='View timeline', exact=True).click()
        assert not await page.locator('#todayBlockEditor').evaluate('(el) => el.open')
        assert await page.locator('#blockTitle').input_value() == 'Keep this unsaved editor draft'
        checks.append('timeline_navigation_preserves_draft_without_opening_editor')
        await page.evaluate("WorkstationToday.go('editor')")
        await page.locator('#blockForm').get_by_role('button', name='Cancel block edit', exact=True).click()
        await row.get_by_role('button', name='Schedule', exact=True).click()
        await panel.locator('input[type=time]').fill('10:50')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        await expect(panel.locator('[role=status]')).not_to_be_empty()
        checks.append('overlap_rejected_without_new_block')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await page.evaluate("WorkstationToday.go('editor')")
        await page.locator('#protectSleep').check()
        await page.locator('#sleepStart').fill('22:00')
        await page.locator('#sleepEnd').fill('07:00')
        await page.locator('#applySleep').click()
        await row.get_by_role('button', name='Schedule', exact=True).click()
        await panel.locator('input[type=time]').fill('22:30')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        await expect(panel.locator('[role=status]')).not_to_be_empty()
        checks.append('protected_sleep_rejected_without_new_block')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await page.locator('#save').click()
        await expect(page.locator('#saveState')).to_have_text('Saved in demo memory only.')
        await page.locator('#reload').click()
        await page.wait_for_function('!WorkstationApp.busy')
        assert await page.evaluate("""() => {const r=WorkstationApp.record;const t=r.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task');return !!t&&r.plan.scheduleBlocks.some(b=>b.taskId===t.id&&b.start==='10:45'&&b.end==='11:10');}""")
        checks.append('memory_save_reload_preserves_link')
        await page.evaluate("WorkstationToday.go('editor')")
        linked = page.locator('#blockList .connect-item').filter(has_text='Schedule acceptance task')
        await expect(linked.get_by_role('button', name='Start focus', exact=True)).to_be_visible()
        await linked.get_by_role('button', name='Start focus', exact=True).click()
        assert await page.evaluate("WorkstationApp.record.plan.focusTaskId===WorkstationApp.record.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task').id")
        await expect(page.locator('[data-view=focus]')).to_be_visible()
        assert await page.evaluate("!WorkstationApp.record.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task').done")
        checks.append('focus_handoff_does_not_complete_task')
        await page.evaluate("WorkstationToday.go('tasks')")
        await row.get_by_role('button', name='Schedule', exact=True).click()
        await page.evaluate("WorkstationApp.change(r=>{r.plan.workspaceTasks=r.plan.workspaceTasks.filter(t=>t.text!=='Schedule acceptance task')})")
        await panel.locator('input[type=time]').fill('12:00')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        await expect(panel.locator('[role=status]')).to_contain_text('no longer exists')
        checks.append('deleted_task_draft_cannot_create_block')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await page.evaluate("WorkstationApp.change(()=>{}); window.dispatchEvent(new Event('workstation:render'))")
        metrics = await page.evaluate('({viewport:document.documentElement.clientWidth, width:document.documentElement.scrollWidth})')
        assert metrics['width'] <= metrics['viewport'] + 3, metrics
        checks.append('no_horizontal_document_overflow')
        assert not errors, errors
        result['passed'] = True
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        result['page_errors'] = errors
        try:
            await page.screenshot(path=str(OUT / f'planner-{width}.png'), full_page=True)
        except Exception as error:
            result['screenshot_error'] = str(error)
        await context.close()
    return result

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '4176', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = []
    try:
        for _ in range(50):
            try:
                with urlopen(BASE + '/members/app.html', timeout=1):
                    break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError('Local server did not start')
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            for width, height in [(390, 844), (1280, 900)]:
                results.append(await run_case(browser, width, height))
            await browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        report = {'scope': 'Synthetic local browser acceptance only. No real signup, SMTP, production account isolation, deployed-domain or APK acceptance.', 'cases': results}
        (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'cases': len(results), 'passed': sum(result['passed'] for result in results)}))
    return 0 if len(results) == 2 and all(result['passed'] for result in results) else 1

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
