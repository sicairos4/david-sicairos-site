import datetime
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

project = 'uwidjnnhdgtrpsymuhwp'
base = 'https://sicairos4.github.io/david-sicairos-site/'
target = base + 'members/app.html'
required = [base + path for path in ['members/workstation.html', 'members/app.html', 'login.html', 'recover.html']]
endpoint = 'https://api.supabase.com/v1/projects/' + project + '/config/auth'
receipt = {'schema_version': 1, 'project': project, 'target_site_url': target, 'source_sha': os.environ.get('GITHUB_SHA'), 'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'not_applied', 'end_to_end_login_verified': False}
output = Path('ops/workstation-auth-config-result.json')
def finish(status, reason, code):
    receipt.update(status=status, reason=reason, observed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(code)

token = os.environ.get('SUPABASE_ACCESS_TOKEN', '').strip()
if not token:
    finish('blocked_missing_secret', 'SUPABASE_ACCESS_TOKEN is unavailable to this workflow. No backend request was made.', 1)
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
def request(method, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(endpoint, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        text = response.read().decode('utf-8')
        return json.loads(text) if text.strip() else {}

try:
    current = request('GET')
    existing = current.get('uri_allow_list')
    if not isinstance(existing, str):
        finish('blocked_config_format', 'Unexpected redirect-list format. No PATCH was sent.', 1)
    allowed = [value.strip() for value in existing.split(',') if value.strip()]
    for value in required:
        if value not in allowed:
            allowed.append(value)
    receipt['previous_site_matched_target'] = current.get('site_url') == target
    receipt['patch_attempted'] = True
    request('PATCH', {'site_url': target, 'uri_allow_list': ','.join(allowed)})
    receipt['patch_acknowledged'] = True
    after = request('GET')
    final_list = after.get('uri_allow_list', '')
    final_allowed = {value.strip() for value in final_list.split(',')} if isinstance(final_list, str) else set()
    receipt['effective_site_matches_target'] = after.get('site_url') == target
    receipt['required_redirects_present'] = {value: value in final_allowed for value in required}
    receipt['existing_redirects_preserved'] = set(value.strip() for value in existing.split(',') if value.strip()).issubset(final_allowed)
    enabled = after.get('external_google_enabled')
    receipt['google_provider_enabled'] = enabled if isinstance(enabled, bool) else None
    if not receipt['effective_site_matches_target'] or not all(receipt['required_redirects_present'].values()) or not receipt['existing_redirects_preserved']:
        finish('readback_mismatch', 'PATCH was acknowledged but the required configuration was not fully confirmed. Do not claim the redirect fixed.', 1)
    finish('applied_and_read_back', 'Production Site URL and required returns match the new Workstation. Provider credentials were not changed. End-to-end login still requires separate confirmation.', 0)
except urllib.error.HTTPError as error:
    receipt['management_http_status'] = error.code
    finish('failed_or_unconfirmed', 'Management API request failed. Private response bodies are not logged. A failed read-back does not prove a preceding PATCH was undone.', 1)
except (urllib.error.URLError, TimeoutError, OSError, ValueError, AttributeError):
    finish('failed_or_unconfirmed', 'Configuration request or read-back did not complete. Do not claim successful application or unchanged backend state.', 1)
