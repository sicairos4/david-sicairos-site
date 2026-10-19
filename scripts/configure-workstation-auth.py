import json
import os
import sys
import urllib.error
import urllib.request

token = os.environ.get('SUPABASE_ACCESS_TOKEN', '').strip()
if not token:
    sys.exit('::error::SUPABASE_ACCESS_TOKEN repository secret is missing. No backend setting was changed. Add a scoped Supabase Management API token with auth-config read/write access in GitHub Actions secrets; never commit or paste it into source.')
endpoint = 'https://api.supabase.com/v1/projects/uwidjnnhdgtrpsymuhwp/config/auth'
base = 'https://sicairos4.github.io/david-sicairos-site/'
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
def request(method, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(endpoint, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit('::error::Supabase Auth configuration request failed with HTTP ' + str(error.code) + '. Response bodies are not logged because they may contain private configuration.')
    except urllib.error.URLError:
        sys.exit('::error::Supabase Auth configuration service could not be reached. No successful change is claimed.')
current = request('GET')
existing = current.get('uri_allow_list', '')
if not isinstance(existing, str):
    sys.exit('::error::Unexpected allow-list format. Refusing to replace existing redirects.')
allowed = [value.strip() for value in existing.split(',') if value.strip()]
for path in ['members/workstation.html', 'members/app.html', 'login.html', 'recover.html']:
    value = base + path
    if value not in allowed:
        allowed.append(value)
request('PATCH', {'site_url': base + 'members/workstation.html', 'uri_allow_list': ','.join(allowed)})
