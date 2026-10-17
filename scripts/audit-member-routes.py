import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SKIP = {'.git', 'node_modules', '.venv', 'output', 'qa-artifacts'}
SUFFIXES = {'.html', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.toml'}

def audit(root):
    root = Path(root).resolve()
    findings, count = [], 0
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix not in SUFFIXES or any(x in SKIP for x in path.relative_to(root).parts):
            continue
        count += 1
        for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if 'lovable' in line.lower():
                hosts = []
                for value in re.findall(r'https?://[^\s\x22\x27<>]+', line):
                    host = urlsplit(value).hostname
                    if host and 'lovable' in host.lower():
                        hosts.append(host)
                findings.append({'file': str(path.relative_to(root)), 'line': number, 'kind': 'lovable_url_reference' if hosts else 'lovable_text_reference', 'hosts': sorted(set(hosts)), 'note': 'Source reference only; inspect whether this is an executed redirect, dependency or text.'})
            if 'auth-callback' in line and ('location.origin' in line or "navigate('/dashboard'" in line or 'navigate("/dashboard"' in line):
                findings.append({'file': str(path.relative_to(root)), 'line': number, 'kind': 'root_based_auth_route_review', 'note': 'Check project-base path and deployed auth configuration.'})
    return {'files_scanned': count, 'scope': 'Local checked-in source only. Does not read hosted Supabase auth settings, DNS, browser caches or another repository.', 'findings': findings}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--output', default='qa-artifacts/member-redirects.json')
    args = parser.parse_args()
    result = audit(args.root)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'files_scanned': result['files_scanned'], 'findings': len(result['findings']), 'runtime_redirect_proved': False}))
