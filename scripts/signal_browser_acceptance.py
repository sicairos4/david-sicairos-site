import json, os, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
BASE = 'https://209connect.com/'
OUT = Path('browser-audit-results')
OUT.mkdir(exist_ok=True)
report = {'source_revision': os.environ.get('GITHUB_SHA'), 'scope': 'public non-account browser checks', 'checks': [], 'not_exercised': ['signup submission', 'login', 'account saving', 'payments', 'Drive updater', 'original-host worker']}
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1280, 'height': 900}, accept_downloads=True)
    page = context.new_page()
    page.set_default_timeout(15000)
    def check(name, fn):
        try:
            fn()
            report['checks'].append({'name': name, 'state': 'passed'})
        except Exception as error:
            report['checks'].append({'name': name, 'state': 'failed', 'error_type': type(error).__name__})
        try:
            page.screenshot(path=str(OUT / (name + '.png')), full_page=True)
        except Exception:
            pass
    def visit(path):
        response = page.goto(BASE + path, wait_until='domcontentloaded', timeout=45000)
        assert response and response.status == 200
        assert page.url.startswith(BASE), 'Unexpected route origin'
    def revision_files():
        matches = []
        for path in ['assets/signal-reader.js', 'data/newsletters.json']:
            response = context.request.get(BASE + path, timeout=45000)
            assert response.status == 200
            live = response.body()
            expected = Path(path).read_bytes()
            same = live == expected
            matches.append({'path': path, 'matches_checkout': same, 'live_sha256': hashlib.sha256(live).hexdigest()})
        report['deployed_file_comparison'] = matches
        assert all(item['matches_checkout'] for item in matches), 'Deployment does not match audited files'
    check('deployed-files', revision_files)
    def articles():
        visit('signal.html')
        expect(page.locator('.signal-card').first).to_be_visible()
        title = page.locator('.signal-card h2').first.inner_text()
        page.locator('#signalSearch').fill(title)
        expect(page.locator('.signal-card')).to_have_count(1)
        page.locator('.signal-card a').first.click()
        expect(page.locator('#signalArticle')).to_be_visible()
        expect(page.locator('#signalArticle h1')).to_have_text(title)
        assert len(page.locator('#signalArticle').inner_text()) > 300
        images = page.locator('#signalArticle img')
        assert images.count() > 0
        for img in images.all():
            img.scroll_into_view_if_needed()
            expect(img).to_be_visible()
            img.evaluate('(img) => img.decode()')
            assert img.evaluate('(img) => img.naturalWidth > 0')
    check('articles-search-reading-images', articles)
    def desktop_nav():
        visit('signal.html')
        menu = page.locator('.nav-group').first
        menu.locator('button').click()
        expect(menu.locator('.dropdown')).to_be_visible()
        menu.get_by_role('link', name='209 Signal', exact=True).click()
        expect(page.locator('#signalSearch')).to_be_visible()
    check('desktop-navigation', desktop_nav)
    def mobile_nav():
        page.set_viewport_size({'width': 390, 'height': 844})
        visit('signal.html')
        page.locator('.nav-burger').click()
        expect(page.locator('#mobile-menu')).to_be_visible()
        page.get_by_role('button', name='Close menu', exact=True).click()
        expect(page.locator('#mobile-menu')).to_be_hidden()
    check('mobile-navigation', mobile_nav)
    def signup_render():
        visit('signal-subscribe.html')
        expect(page.locator('[data-subscribe-form] iframe').first).to_be_visible(timeout=30000)
    check('signup-embed-render-only', signup_render)
    def guest_download():
        visit('members/guest.html')
        page.locator('#guestPriority').fill('Browser audit synthetic plan')
        page.locator('#guestTaskText').fill('Synthetic audit task')
        page.locator('#guestTaskForm button').click()
        expect(page.locator('#guestTasks')).to_contain_text('Synthetic audit task')
        with page.expect_download() as pending:
            page.locator('#guestDownload').click()
        download = pending.value
        assert download.failure() is None
        data = json.loads(Path(download.path()).read_text())
        assert 'Synthetic audit task' in json.dumps(data)
        report['guest_download'] = 'Synthetic JSON downloaded and task found; no account save attempted'
    check('guest-planning-download', guest_download)
    def catalog():
        visit('store.html')
        page.locator('#wellnessCatalog summary').click()
        expect(page.locator('script[src*="app.ecwid.com/script.js"]')).to_have_count(1, timeout=30000)
        expect(page.locator('#wellness-status')).to_have_text('A catalog view loaded. Review current product details in the hosted store before purchasing.', timeout=45000)
        assert page.locator('#my-store-17851284').inner_text().strip()
    check('store-catalog-loading', catalog)
    context.close()
    browser.close()
report['state'] = 'failed' if any(c['state'] == 'failed' for c in report['checks']) else 'public_checks_passed_not_full_acceptance'
(OUT / 'report.json').write_text(json.dumps(report, indent=2))
summary = os.environ.get('GITHUB_STEP_SUMMARY')
if summary:
    with open(summary, 'a') as stream:
        stream.write('## Public browser audit\n\nRevision: ' + str(report['source_revision']) + '\n\n')
        for item in report['checks']:
            stream.write('- ' + item['name'] + ': ' + item['state'] + '\n')
        stream.write('\nAccount mutations, payments, worker installation and Drive synchronization were not exercised.\n')
raise SystemExit(1 if report['state'] == 'failed' else 0)
