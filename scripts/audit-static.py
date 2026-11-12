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
    manifests_checked = 0
    def add(page, severity, kind, target):
        issues.append({'page': str(page.relative_to(root)), 'severity': severity, 'kind': kind, 'target': target})
    def check(page, ref):
        try:
            u = urlsplit(ref)
        except ValueError:
            add(page, 'error', 'invalid_reference', ref)
            return
        if u.scheme or u.netloc:
            return
        path = unquote(u.path)
        if path.startswith('/david-sicairos-site/'):
            target = root / path[len('/david-sicairos-site/'):]
        elif path.startswith('/'):
            target = root / path.lstrip('/')
        else:
            target = page.parent / path if path else page
        target = target.resolve()
        if not target.is_relative_to(root):
            add(page, 'error', 'outside_site_root', ref)
            return
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            add(page, 'error', 'missing_local_target', ref)
            return
        if u.fragment and target.suffix.lower() == '.html':
            fragment = unquote(u.fragment)
            if fragment.startswith(('/', '!')):
                return
            dest = docs.get(target)
            if dest and fragment not in dest.ids:
                add(page, 'warning', 'anchor_not_in_static_html', ref)
    for page, doc in docs.items():
        if not doc.lang:
            add(page, 'warning', 'missing_lang', '')
        if not doc.viewport:
            add(page, 'warning', 'missing_viewport', '')
        for tag, ref in doc.refs:
            check(page, ref)
    for path in sorted(root.rglob('course-kit-manifest.json')):
        if any(x in SKIP for x in path.relative_to(root).parts):
            continue
        manifests_checked += 1
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            add(path, 'error', 'invalid_course_manifest', '')
            continue
        if not isinstance(data, dict) or not isinstance(data.get('kits'), list):
            add(path, 'error', 'invalid_course_manifest_shape', '')
            continue
        for field in ('entry_page', 'blank_template_download'):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                add(path, 'error', 'missing_manifest_reference', field)
            else:
                check(path, value)
        seen = set()
        for kit in data['kits']:
            if not isinstance(kit, dict):
                add(path, 'error', 'invalid_kit', '')
                continue
            ident = kit.get('id')
            if not isinstance(ident, str) or not ident.strip():
                add(path, 'error', 'missing_kit_id', '')
            elif ident in seen:
                add(path, 'error', 'duplicate_kit_id', ident)
            else:
                seen.add(ident)
            resources = kit.get('existing_resources')
            if not isinstance(resources, list):
                add(path, 'error', 'invalid_kit_resources', str(ident))
            else:
                for value in resources:
                    if not isinstance(value, str) or not value.strip():
                        add(path, 'error', 'invalid_kit_resource', str(ident))
                    else:
                        check(path, value)
            if 'optional_tool' in kit:
                value = kit['optional_tool']
                if not isinstance(value, str) or not value.strip():
                    add(path, 'error', 'invalid_optional_tool', str(ident))
                else:
                    check(path, value)
    return {'scope': 'Static HTML and course-kit manifest references only; no live URL checks, CSS rendering, generated routes, database access or content-quality certification', 'pages_checked': len(pages), 'course_manifests_checked': manifests_checked, 'errors': sum(x['severity'] == 'error' for x in issues), 'warnings': sum(x['severity'] == 'warning' for x in issues), 'issues': issues}

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
