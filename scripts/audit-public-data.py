import json
import pathlib
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT = pathlib.Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.ids = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a)
        if tag == 'img':
            self.images.append(a)
errors = []
for name in ['library.html', 'intelligence/index.html']:
    p = Parser()
    p.feed((ROOT / name).read_text())
    if len(p.ids) != len(set(p.ids)):
        errors.append(name + ': duplicate IDs')
    for a in p.links:
        u = urlparse(a.get('href', ''))
        if u.hostname in ['youtube.com', 'www.youtube.com'] and u.path.lower() == '/@davidsicairos':
            errors.append(name + ': wrong YouTube channel handle')
        if a.get('target') == '_blank' and 'noopener' not in a.get('rel', '').split():
            errors.append(name + ': unsafe external target')
    for image in p.images:
        if not image.get('alt') or not image.get('width') or not image.get('height'):
            errors.append(name + ': image missing accessibility or dimensions')
cfg = json.loads((ROOT / 'data/site-config.json').read_text())
for item in cfg.get('socialPulse', []):
    if item.get('followers') is not None and not (item.get('source') and item.get('verified_on')):
        errors.append('Measurement missing source/date')
    if item.get('name') == 'YouTube' and item.get('channelId') != 'UCDMa9oEWj4i6KFOkjF79qLg':
        errors.append('Wrong canonical channel ID')
    if item.get('followers28dAgo') is not None:
        errors.append('Historical baseline must have independent evidence before enabling growth')
if cfg.get('museStatus', {}).get('state', '').lower() == 'connected':
    errors.append('Unsupported connected claim')
result = {'scope': 'targeted source regression; not a live HTTP or visual pass', 'errors': errors}
(ROOT / 'qa-artifacts').mkdir(exist_ok=True)
(ROOT / 'qa-artifacts/public-data-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result))
raise SystemExit(bool(errors))
