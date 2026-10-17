import json
import math
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://www.youtube.com/channel/UCDMa9oEWj4i6KFOkjF79qLg'
errors = []
SKIP = {'.git', 'node_modules', 'qa-artifacts', 'output', '.venv', 'venv'}
def has_source(value):
    return isinstance(value, str) and bool(value.strip())
def valid_count(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0
def utc_day(value):
    if not isinstance(value, str):
        return None
    try:
        if len(value) == 10:
            return date.fromisoformat(value)
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc).date() if parsed.tzinfo else None
    except ValueError:
        return None
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.ids = [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a)
        if tag == 'img':
            self.images.append(a)
for page in ROOT.rglob('*.html'):
    if SKIP.intersection(page.relative_to(ROOT).parts):
        continue
    name = page.relative_to(ROOT).as_posix()
    p = Parser()
    p.feed(page.read_text(encoding='utf-8', errors='replace'))
    for a in p.links:
        u = urlsplit(a.get('href', ''))
        if u.hostname in {'youtube.com', 'www.youtube.com', 'm.youtube.com'} and u.path.rstrip('/').lower() == '/@davidsicairos':
            errors.append(name + ': wrong YouTube channel handle')
    if name in {'library.html', 'intelligence/index.html'}:
        if len(p.ids) != len(set(p.ids)):
            errors.append(name + ': duplicate IDs')
        for a in p.links:
            if a.get('target') == '_blank' and 'noopener' not in a.get('rel', '').split():
                errors.append(name + ': unsafe external target')
        for image in p.images:
            if not image.get('alt') or not image.get('width') or not image.get('height'):
                errors.append(name + ': image missing accessibility or dimensions')
cfg = json.loads((ROOT / 'data/site-config.json').read_text())
items = cfg.get('socialPulse', [])
if not isinstance(items, list):
    errors.append('Invalid socialPulse list')
    items = []
for item in items:
    if not isinstance(item, dict):
        errors.append('Invalid socialPulse entry')
        continue
    value = item.get('followers')
    observed = utc_day(item.get('verified_on') or item.get('measurement_date'))
    attested = item.get('verified') is True or item.get('status') == 'API_SNAPSHOT'
    if value is not None:
        if not valid_count(value):
            errors.append('Invalid follower measurement')
        if not (attested and has_source(item.get('source')) and observed):
            errors.append('Measurement missing verification/nonblank source/valid date')
    baseline = item.get('followers28dAgo')
    if baseline is not None:
        baseline_day = utc_day(item.get('baseline_measured_at'))
        if not (valid_count(baseline) and item.get('baseline_verified') is True and has_source(item.get('baseline_source')) and observed and baseline_day and (observed - baseline_day).days == 28):
            errors.append('Historical baseline requires verified source, nonnegative finite count, and matching 28-day UTC date')
    if item.get('url') in {'https://www.youtube.com/', 'https://www.facebook.com/', 'https://www.linkedin.com/'}:
        errors.append('Generic platform homepage placeholder')
    if item.get('name') == 'YouTube' and (item.get('url') != CANONICAL or item.get('channelId') != 'UCDMa9oEWj4i6KFOkjF79qLg'):
        errors.append('Wrong canonical YouTube identity')
state = cfg.get('museStatus', {}).get('state', '')
if isinstance(state, str) and state.strip().lower() == 'connected':
    errors.append('Unsupported connected claim')
result = {'scope': 'Repository-wide wrong-channel source scan plus targeted media accessibility and data provenance; not live HTTP or visual verification', 'errors': errors}
out = ROOT / 'qa-artifacts/public-data-audit.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result, indent=2))
print(json.dumps(result))
raise SystemExit(bool(errors))
