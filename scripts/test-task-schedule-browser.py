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
    errors, checks = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    async def local_only(route):
        url = route.request.url
        if url == BASE + '/assets/member-session.js':
            await route.fulfill(status=200, content_type='application/javascript', body='/* Synthetic test: no production account client. */')
        elif url.startswith(BASE + '/'):
            await route.continue_()
        else:
            await route.abort()
    await context.route('**/*', local_only)
    result = {'width': width, 'height': height, 'checks': checks, 'passed': False, 'scope': 'Local synthetic memory adapter; no production authentication or database requests'}
    try:
        await page.goto(BASE + '/members/app.html', wait_until='load')
        await page.evaluate("""() => {document.documentElement.dataset.memberState='demo';document.getElementById('memberGate').hidden=true;}""")
        await page.wait_for_function('window.WorkstationApp && !window.WorkstationApp.busy && window.WorkstationSchedule')
        await page.add_script_tag(url=BASE + '/assets/workstation/entry-flow.js')
        await page.add_script_tag(url=BASE + '/assets/workstation/day-print.js')
        await page.wait_for_function("document.getElementById('taskSchedulePanel') && document.getElementById('journeyTodayTabs') && document.getElementById('alignedDateNavigation') && window.WorkstationToday?.journeyWrapped")
        await expect(page.locator('#mode')).to_have_text('Synthetic demo · memory only')
        tabs = page.locator('#journeyTodayTabs')
        await expect(tabs.locator('[data-section=morning]')).to_have_attribute('aria-pressed', 'true')
        await expect(page.locator('#todayTasks')).to_be_hidden()
        checks.append('morning_default_and_tasks_initially_hidden')
        async def tasks_view():
            await tabs.locator('[data-section=tasks]').click()
            await expect(page.locator('#todayTasks')).to_be_visible()
        async def schedule_view():
            await tabs.locator('[data-section=schedule]').click()
            await expect(page.locator('#visualDayTimeline')).to_be_visible()
        async def open_editor():
            await schedule_view()
            editor = page.locator('#todayBlockEditor')
            if not await editor.evaluate('(el) => el.open'):
                await editor.locator(':scope > summary').click()
            await expect(page.locator('#blockTitle')).to_be_visible()
        await tasks_view()
        await page.locator('#taskText').fill('Schedule acceptance task')
        await page.locator('#taskForm button[type=submit]').click()
        await expect(page.locator('#taskList .connect-item')).to_have_count(2)
        count = await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length')
        row = page.locator('#taskList .connect-item').filter(has_text='Schedule acceptance task')
        trigger = row.get_by_role('button', name='Schedule', exact=True)
        panel = page.locator('#taskSchedulePanel')
        async def schedule_task():
            await tasks_view()
            await trigger.click()
            await expect(tabs.locator('[data-section=schedule]')).to_have_attribute('aria-pressed', 'true')
            await expect(panel).to_be_visible()
        await schedule_task()
        await expect(panel).to_contain_text('Schedule acceptance task')
        await panel.locator('input[type=time]').fill('10:45')
        await panel.get_by_role('button', name='25 min', exact=True).click()
        await expect(panel).to_contain_text('Ends at 11:10')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await expect(panel).to_be_hidden()
        await expect(tabs.locator('[data-section=tasks]')).to_have_attribute('aria-pressed', 'true')
        await expect(trigger).to_be_visible()
        await expect(trigger).to_be_focused()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count
        checks.append('cancel_returns_to_visible_task_trigger_without_adding_block')
        await schedule_task()
        await panel.locator('input[type=time]').fill('10:45')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        await expect(panel).to_be_hidden()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        assert await page.evaluate("""() => {const r=WorkstationApp.record,t=r.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task');return r.plan.scheduleBlocks.some(b=>b.taskId===t.id&&b.start==='10:45'&&b.end==='11:10')&&!t.done;}""")
        checks.append('add_preserves_task_link_without_completion')
        await open_editor()
        await page.locator('#blockTitle').fill('Keep this unsaved editor draft')
        await page.locator('#todayBlockEditor > summary').click()
        await schedule_view()
        assert not await page.locator('#todayBlockEditor').evaluate('(el) => el.open')
        assert await page.locator('#blockTitle').input_value() == 'Keep this unsaved editor draft'
        checks.append('schedule_tab_preserves_draft_without_opening_editor')
        await open_editor()
        await page.locator('#blockTitle').fill('')
        await schedule_task()
        await panel.locator('input[type=time]').fill('10:50')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        await expect(panel.locator('[role=status]')).not_to_be_empty()
        checks.append('overlap_rejected_without_new_block')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await schedule_view()
        sleep = page.locator('#alignedScheduleSettings')
        if not await sleep.evaluate('(el) => el.open'):
            await sleep.locator(':scope > summary').click()
        await page.locator('#protectSleep').check()
        await page.locator('#sleepStart').fill('22:00')
        await page.locator('#sleepEnd').fill('07:00')
        await page.locator('#applySleep').click()
        await schedule_task()
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
        assert await page.evaluate("""() => {const r=WorkstationApp.record,t=r.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task');return !!t&&r.plan.scheduleBlocks.some(b=>b.taskId===t.id&&b.start==='10:45'&&b.end==='11:10');}""")
        checks.append('memory_save_reload_preserves_link')
        await open_editor()
        linked = page.locator('#blockList .connect-item').filter(has_text='Schedule acceptance task')
        await expect(linked.get_by_role('button', name='Start focus', exact=True)).to_be_visible()
        await linked.get_by_role('button', name='Start focus', exact=True).click()
        assert await page.evaluate("WorkstationApp.record.plan.focusTaskId===WorkstationApp.record.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task').id")
        await expect(page.locator('[data-view=focus]')).to_be_visible()
        assert await page.evaluate("!WorkstationApp.record.plan.workspaceTasks.find(t=>t.text==='Schedule acceptance task').done")
        checks.append('focus_handoff_does_not_complete_task')
        await page.evaluate("WorkstationToday.go('tasks')")
        await schedule_task()
        await page.evaluate("WorkstationApp.change(r=>{r.plan.workspaceTasks=r.plan.workspaceTasks.filter(t=>t.text!=='Schedule acceptance task')})")
        await panel.locator('input[type=time]').fill('12:00')
        await panel.get_by_role('button', name='Add to day', exact=True).click()
        assert await page.evaluate('WorkstationApp.record.plan.scheduleBlocks.length') == count + 1
        await expect(panel.locator('[role=status]')).to_contain_text('no longer exists')
        checks.append('deleted_task_draft_cannot_create_block')
        await panel.get_by_role('button', name='Cancel', exact=True).click()
        await page.evaluate("WorkstationApp.change(()=>{});window.dispatchEvent(new Event('workstation:render'))")
        metrics = await page.evaluate('({viewport:document.documentElement.clientWidth,width:document.documentElement.scrollWidth})')
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
