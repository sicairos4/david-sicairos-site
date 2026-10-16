import asyncio
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa-artifacts' / 'responsive'
PAGES = ['index.html', 'warchest.html', 'donations.html', 'store.html', 'sovereign-university/pathways.html', 'multimedia/index.html']
SIZES = [(360, 800), (390, 844), (768, 1024), (1440, 1000)]
THEMES = ['valley-light', 'midnight-ledger']

async def main():
    from playwright.async_api import async_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '4173', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for attempt in range(50):
            try:
                with urlopen('http://127.0.0.1:4173/index.html', timeout=1):
                    break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError('Local preview server did not start')
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            for width, height in SIZES:
                for theme in THEMES:
                    context = await browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce', color_scheme='dark' if theme == 'midnight-ledger' else 'light')
                    async def local_only(route):
                        u = urlsplit(route.request.url)
                        if u.scheme == 'data' or (u.hostname == '127.0.0.1' and u.port == 4173):
                            await route.continue_()
                        else:
                            await route.abort()
                    await context.route('**/*', local_only)
                    for path in PAGES:
                        page = await context.new_page()
                        errors = []
                        page.on('pageerror', lambda error, bucket=errors: bucket.append(str(error)))
                        record = {'page': path, 'width': width, 'height': height, 'theme': theme, 'issues': []}
                        try:
                            await page.goto('http://127.0.0.1:4173/' + path, wait_until='domcontentloaded', timeout=30000)
                            await page.evaluate('(theme) => { document.documentElement.dataset.theme = theme; }', theme)
                            await page.wait_for_timeout(400)
                            metrics = await page.evaluate('''() => {
                              const visible = el => { const r=el.getBoundingClientRect(); return r.width>0 && r.height>0; };
                              const buttons=Array.from(document.querySelectorAll('main .btn, main .cta')).filter(visible);
                              const overlaps=[];
                              for(let i=0;i<buttons.length;i++)for(let j=i+1;j<buttons.length;j++){
                                const a=buttons[i],b=buttons[j];if(a.contains(b)||b.contains(a))continue;
                                const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();
                                if(Math.min(x.right,y.right)-Math.max(x.left,y.left)>3 && Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>3)overlaps.push([a.textContent.trim(),b.textContent.trim()]);
                              }
                              return {viewport:document.documentElement.clientWidth,bodyWidth:document.body.scrollWidth,documentWidth:document.documentElement.scrollWidth,overlaps};
                            }''')
                            record['metrics'] = metrics
                            if max(metrics['bodyWidth'], metrics['documentWidth']) > metrics['viewport'] + 3:
                                record['issues'].append('Document-level horizontal overflow')
                            if metrics['overlaps']:
                                record['issues'].append('Overlapping visible content buttons')
                            if path == 'warchest.html' and await page.locator('.hero .links > a.btn').count() != 2:
                                record['issues'].append('Warchest hero does not have exactly two content buttons')
                            if path == 'donations.html' and width >= 768:
                                buttons = await page.locator('.payment-card .payment-actions > a.btn').all()
                                boxes = [await b.bounding_box() for b in buttons]
                                if len(boxes) != 2 or any(b is None for b in boxes):
                                    record['issues'].append('Payment action pair missing')
                                elif abs(boxes[0]['y'] - boxes[1]['y']) > 4:
                                    record['issues'].append('Payment button top edges are not aligned')
                            name = path.replace('/', '-').replace('.html', '') + '-' + str(width) + '-' + theme
                            await page.screenshot(path=str(OUT / (name + '.png')), full_page=True)
                            record['screenshot'] = name + '.png'
                            if path == 'index.html' and width < 768:
                                burger = page.locator('.nav-burger')
                                if await burger.count() and await burger.is_visible():
                                    await burger.click()
                                    await page.screenshot(path=str(OUT / (name + '-menu.png')), full_page=True)
                                    await page.keyboard.press('Escape')
                                    if await burger.get_attribute('aria-expanded') != 'false':
                                        record['issues'].append('Mobile menu did not close with Escape')
                            if errors:
                                record['javascript_errors'] = errors
                                record['issues'].append('Uncaught page JavaScript error')
                        except Exception as error:
                            record['issues'].append(type(error).__name__ + ': ' + str(error))
                        records.append(record)
                        await page.close()
                    await context.close()
            await browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        report = {'scope': 'Local Chromium preview; all remote requests blocked. No deployed-site, authenticated, payment, Ecwid, YouTube playback or live API acceptance test.', 'records': records, 'cases': len(records), 'cases_with_issues': sum(bool(r['issues']) for r in records)}
        (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'cases': report['cases'], 'cases_with_issues': report['cases_with_issues']}))
    return 1 if report['cases_with_issues'] or report['cases'] != len(PAGES) * len(SIZES) * len(THEMES) else 0

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
