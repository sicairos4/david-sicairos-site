import argparse, asyncio, contextlib, fcntl, hashlib, ipaddress, json, os, re, socket, sys, uuid
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit

os.umask(0o077)
ROOT = Path(os.environ.get('BROWSER_STATE_DIR', str(Path.home()/'.local/share/209-browser'))).expanduser()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def config(account):
    if not re.fullmatch(r'[a-z0-9_-]{1,64}', account):
        raise ValueError('invalid_account_key')
    accounts = json.loads(Path(os.environ.get('BROWSER_ACCOUNTS_FILE', 'accounts.json')).read_text())
    c = accounts[account]
    if not c.get('enabled'):
        raise ValueError('account_not_enabled')
    return c

def allowed_url(url, hosts):
    u = urlsplit(url)
    if u.scheme != 'https' or u.username or u.password or u.port not in (None,443) or u.hostname not in hosts:
        raise ValueError('url_not_allowed')
    addresses = socket.getaddrinfo(u.hostname,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
        raise ValueError('non_public_address')
    return u

def validate(job, c):
    if not isinstance(job,dict) or set(job) != {'steps'} or not isinstance(job['steps'],list) or not 1 <= len(job['steps']) <= 20:
        raise ValueError('invalid_steps')
    fields={'goto':{'action','url'},'fill':{'action','selector','text'},'click':{'action','selector'},'observe':{'action','selector','expected_text'}}
    for step in job['steps']:
        if not isinstance(step,dict): raise ValueError('invalid_step')
        kind=step.get('action')
        if not isinstance(kind,str) or kind not in fields or set(step)!=fields[kind] or any(not isinstance(v,str) or len(v)>10000 for v in step.values()):
            raise ValueError('unsupported_step')
        if kind=='goto': allowed_url(step['url'],c['allowed_hosts'])
        if kind in ('fill','click') and (not c.get('identity_selector') or not c.get('identity_text') or 'REPLACE_' in c['identity_selector']+c['identity_text']):
            raise ValueError('identity_check_not_configured')

@contextlib.contextmanager
def profile_lock(account):
    ROOT.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (ROOT/(account+'.lock')).open('a') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield ROOT/account

async def browse(account, payload=None):
    from playwright.async_api import async_playwright
    c=config(account)
    if payload is not None: validate(payload,c)
    with profile_lock(account) as profile:
        async with async_playwright() as p:
            ctx=await p.chromium.launch_persistent_context(str(profile),headless=payload is not None,chromium_sandbox=True,accept_downloads=False,service_workers='block')
            try:
                async def guard(route):
                    try:
                        hosts=c['allowed_hosts'] if route.request.is_navigation_request() else c.get('resource_hosts',c['allowed_hosts'])
                        await asyncio.to_thread(allowed_url,route.request.url,hosts)
                    except Exception:
                        await route.abort()
                        return
                    await route.continue_()
                await ctx.route('**/*',guard)
                page=await ctx.new_page()
                page.set_default_timeout(15000)
                if payload is None:
                    allowed_url(c['start_url'],c['allowed_hosts'])
                    await page.goto(c['start_url'],wait_until='domcontentloaded',timeout=30000)
                    await asyncio.to_thread(input,'Sign in yourself and confirm the account. Press Enter to close and retain this private profile: ')
                    return {'state':'profile_saved','login_validity_verified':False}
                for step in payload['steps']:
                    action=step['action']
                    if action=='goto':
                        await page.goto(step['url'],wait_until='domcontentloaded',timeout=30000)
                    else:
                        allowed_url(page.url,c['allowed_hosts'])
                        if action in ('click','fill'):
                            identity=page.locator(c['identity_selector'])
                            if await identity.count()!=1 or not await identity.is_visible() or (await identity.inner_text()).strip()!=c['identity_text']:
                                raise ValueError('account_identity_not_confirmed')
                        target=page.locator(step['selector'])
                        if await target.count()!=1 or not await target.is_visible():
                            raise ValueError('target_not_unique_or_visible')
                        if action=='fill': await target.fill(step['text'])
                        elif action=='click': await target.click()
                        elif (await target.inner_text()).strip()!=step['expected_text']:
                            raise ValueError('observation_mismatch')
                return {'state':'executed_unverified','steps_executed':len(payload['steps']),'platform_acceptance_verified':False,'public_visibility_verified':False}
            finally:
                await ctx.close()

def connection():
    import psycopg
    from psycopg.rows import dict_row
    url=os.environ.get('BROWSER_DATABASE_URL')
    if not url: raise ValueError('BROWSER_DATABASE_URL_required')
    return psycopg.connect(url,row_factory=dict_row,connect_timeout=10)

def run_once():
    with connection() as db:
        with db.transaction():
            row=db.execute("SELECT * FROM browser_209.jobs WHERE state='approved' AND due_at<=now() AND expires_at>now() ORDER BY due_at,id FOR UPDATE SKIP LOCKED LIMIT 1").fetchone()
            if not row: return {'state':'no_due_job'}
            db.execute("UPDATE browser_209.jobs SET state='running',started_at=now() WHERE id=%s",(row['id'],))
        result={'state':'uncertain','automatic_retry_allowed':False}
        try:
            if digest(row['payload'])!=row['payload_sha256']: raise ValueError('payload_digest_mismatch')
            remaining=(row['expires_at']-datetime.now(timezone.utc)).total_seconds()
            if remaining<=0: raise ValueError('authorization_expired')
            result=asyncio.run(asyncio.wait_for(browse(row['account_key'],row['payload']),timeout=min(180,remaining)))
        except Exception:
            pass
        db.execute("UPDATE browser_209.jobs SET state=%s,result=%s::jsonb,finished_at=now() WHERE id=%s AND state='running'",(result['state'],canonical(result),row['id']))
        return {'job_id':str(row['id']),**result}

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='command',required=True)
    login=sub.add_parser('login');login.add_argument('account')
    prop=sub.add_parser('propose');prop.add_argument('account');prop.add_argument('payload_file');prop.add_argument('idempotency_key');prop.add_argument('--due',required=True);prop.add_argument('--expires',required=True)
    approval=sub.add_parser('approve');approval.add_argument('job_id')
    sub.add_parser('run-once')
    args=parser.parse_args()
    if args.command=='login': return asyncio.run(browse(args.account))
    if args.command=='run-once': return run_once()
    with connection() as db:
        if args.command=='propose':
            payload=json.loads(Path(args.payload_file).read_text())
            validate(payload,config(args.account))
            jid=uuid.uuid4()
            db.execute("INSERT INTO browser_209.jobs(id,idempotency_key,account_key,payload,payload_sha256,due_at,expires_at) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s)",(jid,args.idempotency_key,args.account,canonical(payload),digest(payload),args.due,args.expires))
            return {'job_id':str(jid),'state':'proposed','payload_sha256':digest(payload)}
        row=db.execute('SELECT account_key,payload,payload_sha256,due_at,expires_at,state FROM browser_209.jobs WHERE id=%s',(args.job_id,)).fetchone()
        if not row or row['state']!='proposed': raise ValueError('proposal_not_found')
        print(json.dumps(row,default=str,indent=2))
        if input('Type APPROVE '+row['payload_sha256']+': ')!='APPROVE '+row['payload_sha256']:
            return {'state':'not_approved'}
        result=db.execute("UPDATE browser_209.jobs SET state='approved',approved_at=now() WHERE id=%s AND state='proposed' AND expires_at>now() RETURNING id",(args.job_id,)).fetchone()
        return {'state':'approved' if result else 'not_approved'}

if __name__=='__main__':
    try: print(json.dumps(main()))
    except Exception: print(json.dumps({'error':'operation_failed','detail':'Inspect private configuration; no secret values are logged.'}));sys.exit(1)
