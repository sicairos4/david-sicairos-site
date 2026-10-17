import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://www.youtube.com/channel/UCDMa9oEWj4i6KFOkjF79qLg'
issues = []
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        u = urlsplit(href)
        if tag == 'a' and u.hostname in {'youtube.com', 'www.youtube.com', 'm.youtube.com'}:
            if u.path.rstrip('/').lower() == '/@davidsicairos':
                issues.append({'page': str(self.page.relative_to(ROOT)), 'issue': 'Wrong YouTube handle', 'href': href})
for page in ROOT.rglob('*.html'):
    if any(x in {'.git', 'node_modules', 'qa-artifacts', 'output', '.venv', 'venv'} for x in page.relative_to(ROOT).parts):
        continue
    parser = Links()
    parser.page = page
    parser.feed(page.read_text(encoding='utf-8', errors='replace'))
cfg = json.loads((ROOT / 'data/site-config.json').read_text())
for p in cfg.get('socialPulse', []):
    value = p.get('followers')
    if value is not None and (p.get('verified') is not True or not p.get('source') or not p.get('measurement_date')):
        issues.append({'issue': 'Follower number lacks provenance', 'platform': p.get('name')})
    if p.get('followers28dAgo') is not None and (p.get('baseline_verified') is not True or not p.get('baseline_measured_at')):
        issues.append({'issue': 'Growth baseline lacks provenance', 'platform': p.get('name')})
    if p.get('url') in {'https://www.youtube.com/', 'https://www.facebook.com/', 'https://www.linkedin.com/'}:
        issues.append({'issue': 'Generic platform homepage placeholder', 'platform': p.get('name')})
    if p.get('name') == 'YouTube' and p.get('url') != CANONICAL:
        issues.append({'issue': 'YouTube channel identity mismatch'})
if cfg.get('museStatus', {}).get('state') == 'Connected':
    issues.append({'issue': 'Unverified connected-state claim'})
out = ROOT / 'qa-artifacts/public-data-audit.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'scope': 'Source links and public-data provenance, not live HTTP or API ingestion', 'issues': issues}, indent=2))
print(json.dumps({'public_data_issues': len(issues)}))
raise SystemExit(bool(issues))
