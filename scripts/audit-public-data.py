import json
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://www.youtube.com/channel/UCDMa9oEWj4i6KFOkjF79qLg'
errors = []
SKIP = {'.git', 'node_modules', 'qa-artifacts', 'output', '.venv', 'venv'}
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
for item in cfg.get('socialPulse', []):
    value = item.get('followers')
    observed = item.get('verified_on') or item.get('measurement_date')
    attested = item.get('verified') is True or item.get('status') == 'API_SNAPSHOT'
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            errors.append('Invalid follower measurement')
        if not (attested and item.get('source') and observed):
            errors.append('Measurement missing verification/source/date')
        else:
            try:
                date.fromisoformat(observed)
            except (ValueError, TypeError):
                errors.append('Invalid measurement date')
    if item.get('followers28dAgo') is not None and not (item.get('baseline_verified') is True and item.get('baseline_source') and item.get('baseline_measured_at')):
        errors.append('Historical baseline lacks independent evidence')
    if item.get('url') in {'https://www.youtube.com/', 'https://www.facebook.com/', 'https://www.linkedin.com/'}:
        errors.append('Generic platform homepage placeholder')
    if item.get('name') == 'YouTube' and (item.get('url') != CANONICAL or item.get('channelId') != 'UCDMa9oEWj4i6KFOkjF79qLg'):
        errors.append('Wrong canonical YouTube identity')
if cfg.get('museStatus', {}).get('state', '').lower() == 'connected':
    errors.append('Unsupported connected claim')
result = {'scope': 'Repository-wide wrong-channel source scan plus targeted media accessibility and data provenance; not live HTTP or visual verification', 'errors': errors}
out = ROOT / 'qa-artifacts/public-data-audit.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result, indent=2))
print(json.dumps(result))
raise SystemExit(bool(errors))
