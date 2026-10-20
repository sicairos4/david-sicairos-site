import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa-artifacts' / 'styled-workstation'
BASE = 'http://127.0.0.1:4174'
SIZES = [(320, 720), (360, 800), (390, 844), (600, 900), (768, 1024), (1280, 900)]
PAGES = ['members/app.html', 'public-files.html']

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '4174', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cases = []
    try:
        for _ in range(50):
            try:
                with urlopen(BASE + '/public-files.html', timeout=1):
                    break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError('Local preview did not start')
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            for width, height in SIZES:
                context = await browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
                async def local_only(route):
                    if route.request.url.startswith(BASE + '/'):
                        await route.continue_()
                    else:
                        await route.abort()
                await context.route('**/*', local_only)
                for path in PAGES:
                    page = await context.new_page()
                    issues = []
                    try:
                        await page.goto(BASE + '/' + path, wait_until='domcontentloaded', timeout=30000)
                        await page.wait_for_timeout(200)
                        stylesheet = 'responsive-panels.css' if path.startswith('members/') else 'public-files-panels.css'
                        links = await page.evaluate('''() => Array.from(document.styleSheets).map(sheet => sheet.href || '').concat(Array.from(document.querySelectorAll('link[rel=stylesheet]')).map(link => link.href))''')
                        if not any(stylesheet in href for href in links) and path.startswith('members/'):
                            imports = await page.evaluate('''() => {const sheet=Array.from(document.styleSheets).find(s=>s.href?.endsWith('/assets/workstation/morning.css'));try{return Array.from(sheet?.cssRules||[]).map(rule=>rule.href||'')}catch{return []}}''')
                            if not any(stylesheet in href for href in imports):
                                issues.append('Workstation responsive stylesheet not imported')
                        elif not any(stylesheet in href for href in links):
                            issues.append('Public Files responsive stylesheet not linked')
                        width_info = await page.evaluate('''() => ({viewport:document.documentElement.clientWidth, body:document.body.scrollWidth, document:document.documentElement.scrollWidth})''')
                        if max(width_info['body'], width_info['document']) > width_info['viewport'] + 3:
                            issues.append('Horizontal document overflow')
                        if path == 'members/app.html':
                            await page.evaluate('''() => {document.documentElement.dataset.memberState='demo'; document.getElementById('memberGate').hidden=true;}''')
                            button = await page.locator('#workstationMonthNavigation button').first.count()
                            if button:
                                box = await page.locator('#workstationMonthNavigation button').first.bounding_box()
                                if box and box['height'] < 44:
                                    issues.append('Month day target below 44 CSS pixels')
                        name = path.replace('/', '-') + '-' + str(width)
                        await page.screenshot(path=str(OUT / (name + '.png')), full_page=True)
                        cases.append({'page': path, 'width': width, 'stylesheet': stylesheet, 'metrics': width_info, 'issues': issues, 'screenshot': name + '.png', 'scope': 'local unauthenticated/offline preview'})
                    except Exception as error:
                        cases.append({'page': path, 'width': width, 'issues': [type(error).__name__ + ': ' + str(error)]})
                    finally:
                        await page.close()
                await context.close()
            await browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        report = {'scope': 'Local offline Chromium preview; remote auth and Supabase requests blocked. Does not prove signed-in planner, hosted deployment, APK imagery or live records.', 'cases': cases, 'cases_with_issues': sum(bool(case['issues']) for case in cases)}
        (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'cases': len(cases), 'cases_with_issues': report['cases_with_issues']}))
    return 1 if report['cases_with_issues'] else 0

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
