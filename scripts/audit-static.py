import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP = {'.git', 'node_modules', '.venv', 'venv', 'output', 'qa-artifacts'}
class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs = set(), []
        self.lang = self.viewport = False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = bool(a.get('lang'))
        if tag == 'meta' and a.get('name', '').lower() == 'viewport':
            self.viewport = True
        field = 'src' if tag in {'script', 'img', 'iframe', 'source', 'video', 'audio'} else 'href' if tag in {'a', 'link'} else None
        if field and a.get(field):
            self.refs.append((tag, a[field]))

def audit(root):
    root = Path(root).resolve()
    pages = sorted(p for p in root.rglob('*.html') if not any(x in SKIP for x in p.relative_to(root).parts))
    docs = {p: Document(p.read_text(encoding='utf-8', errors='replace')) for p in pages}
    issues = []
    def add(page, severity, kind, target):
        issues.append({'page': str(page.relative_to(root)), 'severity': severity, 'kind': kind, 'target': target})
    for page, doc in docs.items():
        if not doc.lang:
            add(page, 'warning', 'missing_lang', '')
        if not doc.viewport:
            add(page, 'warning', 'missing_viewport', '')
        for tag, ref in doc.refs:
            u = urlsplit(ref)
            if u.scheme or u.netloc:
                continue
            path = unquote(u.path)
            if path.startswith('/david-sicairos-site/'):
                path = path[len('/david-sicairos-site/'):]
                target = root / path
            elif path.startswith('/'):
                target = root / path.lstrip('/')
            else:
                target = page.parent / path if path else page
            target = target.resolve()
            if not target.is_relative_to(root):
                add(page, 'error', 'outside_site_root', ref)
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.exists():
                add(page, 'error', 'missing_local_target', ref)
                continue
            if u.fragment and target.suffix.lower() == '.html':
                fragment = unquote(u.fragment)
                if fragment.startswith(('/', '!')):
                    continue
                dest = docs.get(target)
                if dest and fragment not in dest.ids:
                    add(page, 'warning', 'anchor_not_in_static_html', ref)
    return {'scope': 'Static HTML references only; no live URL checks, CSS rendering or generated routes', 'pages_checked': len(pages), 'errors': sum(x['severity'] == 'error' for x in issues), 'warnings': sum(x['severity'] == 'warning' for x in issues), 'issues': issues}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--output', default='qa-artifacts/static-audit.json')
    args = parser.parse_args()
    result = audit(args.root)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'issues'}))
    raise SystemExit(1 if result['errors'] else 0)
