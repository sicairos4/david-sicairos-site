import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa-artifacts' / 'ui-responsive'
BASE = 'http://127.0.0.1:4178'
PAGES = ['index.html', 'dbeastco.html', 'studio.html', 'store.html', 'public-files.html', 'login.html', 'recover.html', 'members/guest.html', 'members/app.html', 'intelligence/index.html']

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '4178', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cases = []
    try:
        for _ in range(50):
            try:
                with urlopen(BASE + '/index.html', timeout=1):
                    break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError('Local preview failed to start')
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            for width in [320, 390, 768, 1280]:
                context = await browser.new_context(viewport={'width': width, 'height': 844}, reduced_motion='reduce')
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
                        response = await page.goto(BASE + '/' + path, wait_until='load', timeout=20000)
                        if not response or response.status != 200:
                            raise RuntimeError('Local page not served successfully')
                        await page.wait_for_timeout(250)
                        header = page.locator('header.site-toolbar')
                        if await header.count():
                            await expect(header).to_be_visible()
                            box = await header.bounding_box()
                            if width <= 768 and box and box['height'] > 80:
                                issues.append('Toolbar exceeds compact mobile height')
                            if width <= 768:
                                burger = header.get_by_role('button', name='Open navigation', exact=True)
                                await expect(burger).to_be_visible()
                                await burger.click()
                                menu = page.locator('#mobile-menu')
                                await expect(menu).to_be_visible()
                                menu_box = await menu.bounding_box()
                                if box and menu_box and abs(menu_box['y'] - (box['y'] + box['height'])) > 3:
                                    issues.append('Menu not aligned below actual toolbar')
                                await page.keyboard.press('Escape')
                                await expect(menu).to_be_hidden()
                                await expect(burger).to_be_focused()
                            image = header.locator('.brand img')
                            if await image.count():
                                image_box = await image.bounding_box()
                                if image_box and abs(image_box['width'] - image_box['height']) > 1:
                                    issues.append('Brand image not square')
                        metrics = await page.evaluate('({viewport:document.documentElement.clientWidth,width:document.documentElement.scrollWidth})')
                        if metrics['width'] > metrics['viewport'] + 3:
                            issues.append('Horizontal document overflow')
                        controls = await page.locator('main .btn:visible, main button[type=submit]:visible').evaluate_all('(els)=>els.map(el=>({text:el.textContent.trim().slice(0,60),height:el.getBoundingClientRect().height}))')
                        for control in controls:
                            if control['height'] < 43:
                                issues.append('Short action target: ' + control['text'])
                        await page.screenshot(path=str(OUT / (path.replace('/', '-') + '-' + str(width) + '.png')), full_page=True)
                        cases.append({'page': path, 'width': width, 'issues': issues, 'metrics': metrics})
                    except Exception as error:
                        cases.append({'page': path, 'width': width, 'issues': [type(error).__name__ + ': ' + str(error)]})
                    finally:
                        await page.close()
                await context.close()
            await browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        report = {'scope': 'Local unauthenticated preview, external requests blocked. Not whole-site coverage, production login, live data, APK or visual approval.', 'cases': cases}
        (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    failed = sum(bool(case['issues']) for case in cases)
    print(json.dumps({'cases': len(cases), 'cases_with_issues': failed}))
    return 1 if failed or len(cases) != len(PAGES) * 4 else 0

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
