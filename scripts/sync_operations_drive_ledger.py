#!/usr/bin/env python3
"""Manual-first original-ledger updater. No schedule or credential provisioning."""
import base64, fcntl, hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class Blocked(Exception):
    pass

def required(name):
    value = os.environ.get(name, '')
    if not value:
        raise Blocked('missing_configuration:' + name)
    return value

def main():
    config = json.loads(Path('ops/drive-ledger-sync.json').read_text())
    mode = os.environ.get('OPS_SYNC_MODE', 'stage')
    if mode not in ('stage', 'apply'):
        raise Blocked('invalid_mode')
    state = Path(required('OPS_SYNC_STATE_DIR'))
    if state.is_symlink():
        raise Blocked('unsafe_state_path')
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    lock = open(state / 'single-writer.lock', 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise Blocked('another_local_updater_running')
    def save(name, data):
        target = state / name
        temporary = state / (name + '.tmp')
        temporary.write_bytes(data)
        temporary.chmod(0o600)
        temporary.replace(target)
    def http(method, url, headers, **kwargs):
        response = requests.request(method, url, headers=headers, timeout=30, allow_redirects=False, **kwargs)
        if not 200 <= response.status_code < 300:
            raise Blocked('request_rejected_' + str(response.status_code))
        return response
    bearer = required('OPS_LEDGER_BEARER')
    try:
        claims = json.loads(base64.urlsafe_b64decode(bearer.split('.')[1] + '==='))
    except Exception:
        raise Blocked('scoped_backend_jwt_required')
    if claims.get('role') != config['backend_role'] or claims.get('exp', 0) <= datetime.now(timezone.utc).timestamp():
        raise Blocked('dedicated_backend_role_or_expiry_invalid')
    bh = {'apikey': required('OPS_LEDGER_API_KEY'), 'Authorization': 'Bearer ' + bearer, 'Accept-Profile': config['schema'], 'Content-Profile': config['schema']}
    rest = config['supabase_url'] + '/rest/v1/'
    ledger = http('GET', rest + 'operations_ledger', bh, params={'ledger_key': 'eq.' + config['ledger_key'], 'select': 'ledger_key,coordination_id,source_file_id,updated_at'}).json()
    if len(ledger) != 1 or ledger[0]['source_file_id'] != config['drive_file_id'] or ledger[0]['coordination_id'] != config['coordination_id']:
        raise Blocked('ledger_identity_mismatch')
    fields = ['task_key', 'priority', 'title', 'owner_label', 'status', 'updated_at']
    rows = http('GET', rest + 'operations_backlog', bh, params={'coordination_id': 'eq.' + config['coordination_id'], 'select': ','.join(fields), 'order': 'priority.asc,task_key.asc'}).json()
    if not isinstance(rows, list) or not rows or len(rows) > 250:
        raise Blocked('unexpected_backlog_shape')
    credentials = Credentials.from_authorized_user_info(json.loads(required('GDRIVE_LEDGER_OAUTH_JSON')))
    if not credentials.valid:
        credentials.refresh(Request())
    gh = {'Authorization': 'Bearer ' + credentials.token}
    drive = 'https://www.googleapis.com/drive/v3/files/' + config['drive_file_id']
    metadata = http('GET', drive, gh, params={'fields': 'id,mimeType,trashed,modifiedTime'}).json()
    if metadata.get('trashed') or metadata.get('mimeType') not in ('text/plain', 'text/markdown'):
        raise Blocked('original_text_ledger_required')
    permissions = http('GET', drive + '/permissions', gh, params={'fields': 'permissions(role,type,emailAddress)'}).json().get('permissions', [])
    if len(permissions) != 1 or permissions[0].get('role') != 'owner' or permissions[0].get('emailAddress') != config['expected_owner']:
        raise Blocked('owner_only_permission_check_failed')
    original = http('GET', drive, gh, params={'alt': 'media'})
    before = original.content
    text = before.decode('utf-8')
    start, end = '<!-- BEGIN 209 MANAGED BACKLOG -->', '<!-- END 209 MANAGED BACKLOG -->'
    if text.count(start) != text.count(end) or text.count(start) > 1:
        raise Blocked('managed_markers_invalid')
    if start in text and text.index(start) > text.index(end):
        raise Blocked('managed_markers_reversed')
    def clean(value):
        result = str(value if value is not None else 'unknown').replace('\n', ' ').replace('\r', ' ').replace('|', '/')
        if len(result) > 500 or re.search(r'Bearer\s|eyJ[A-Za-z0-9_-]{16}|(?i:password|secret|access_token)\s*[:=]|[?&](?:token|key|code)=', result):
            raise Blocked('unsafe_export_field')
        return result
    lines = [start, '## Backend managed backlog', 'Coordination: ' + config['coordination_id'], '| Task | Priority | Title | Owner | State | Updated UTC |', '|---|---|---|---|---|---|']
    lines += ['| ' + ' | '.join(clean(row.get(field)) for field in fields) + ' |' for row in rows]
    block = '\n'.join(lines + [end])
    rendered = text.split(start)[0] + block + text.split(end)[1] if start in text else text.rstrip() + '\n\n' + block + '\n'
    body = rendered.encode()
    receipt = {'file_id': config['drive_file_id'], 'coordination_id': config['coordination_id'], 'mode': mode, 'rows': len(rows), 'before_sha256': hashlib.sha256(before).hexdigest(), 'proposed_sha256': hashlib.sha256(body).hexdigest(), 'state': 'staged_only', 'external_write': False}
    save('original.txt', before)
    save('proposed.txt', body)
    def record():
        save('receipt.json', json.dumps(receipt, indent=2).encode())
    record()
    if mode == 'stage':
        print(json.dumps(receipt))
        return
    proof = json.loads(required('OPS_DRIVE_CONDITIONAL_WRITE_PROOF'))
    if proof.get('file_id') != config['drive_file_id'] or proof.get('if_match_enforcement_verified') is not True or not proof.get('evidence_reference') or not proof.get('approval_reference'):
        raise Blocked('conditional_write_proof_and_approval_required')
    etag = original.headers.get('ETag', '')
    if not etag.startswith('"') or etag.startswith('W/'):
        raise Blocked('strong_http_etag_unavailable')
    if body == before:
        receipt['state'] = 'unchanged_no_write'
        record()
        print(json.dumps(receipt))
        return
    receipt['state'] = 'write_intent'
    record()
    http('PATCH', 'https://www.googleapis.com/upload/drive/v3/files/' + config['drive_file_id'], {**gh, 'If-Match': etag, 'Content-Type': metadata['mimeType']}, params={'uploadType': 'media'}, data=body)
    receipt.update(state='drive_accepted_readback_pending', external_write=True)
    record()
    readback = http('GET', drive, gh, params={'alt': 'media'}).content
    if readback != body:
        raise Blocked('readback_mismatch_reconcile_before_retry')
    now = datetime.now(timezone.utc).isoformat()
    receipt.update(state='drive_verified_backend_pending', drive_written_at_utc=now)
    record()
    updated = http('PATCH', rest + 'operations_ledger', {**bh, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}, params={'ledger_key': 'eq.' + config['ledger_key'], 'updated_at': 'eq.' + ledger[0]['updated_at']}, json={'last_drive_sync_at': now, 'updated_at': now}).json()
    if len(updated) != 1:
        raise Blocked('backend_changed_after_drive_write_reconcile')
    receipt['state'] = 'drive_and_backend_sync_verified'
    record()
    print(json.dumps(receipt))

if __name__ == '__main__':
    try:
        main()
    except Blocked as error:
        print(json.dumps({'state': 'blocked', 'reason': str(error)}))
        sys.exit(2)
    except Exception:
        print(json.dumps({'state': 'unverified_or_uncertain', 'reason': 'redacted_error_no_blind_retry'}))
        sys.exit(3)
