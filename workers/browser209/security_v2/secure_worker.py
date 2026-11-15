"""Opt-in worker: no legacy queue, timer or environment changes."""
import asyncio
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, parse_qs


def connection_url(value):
    u=urlsplit(value); q=parse_qs(u.query,keep_blank_values=True)
    if u.scheme not in ('postgres','postgresql') or not u.hostname or q.get('sslmode')!=['verify-full'] or 'options' in q or 'service' in q:
        raise ValueError('scoped_tls_connection_required')
    return value


def rpc(op,p):
    import psycopg
    from psycopg.types.json import Jsonb
    with psycopg.connect(connection_url(os.environ.get('BROWSER_V2_DATABASE_URL','')),connect_timeout=5,options='-c statement_timeout=5000 -c lock_timeout=2000') as db:
        return db.execute('SELECT browser_209_v2.api(%s,%s)',(op,Jsonb(p))).fetchone()[0]


def payload(j):
    t=j['payload_text']
    if not isinstance(t,str) or len(t.encode())>262144 or not hmac.compare_digest(hashlib.sha256(t.encode('utf-8')).hexdigest(),j['payload_sha256']):
        raise ValueError('payload_integrity')
    p=json.loads(t)
    if p!=j['payload']: raise ValueError('payload_mismatch')
    return p


def legacy():
    spec=importlib.util.spec_from_file_location('browser209_legacy',Path(__file__).resolve().parents[1]/'browser_worker.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


async def browse(j,beat):
    from playwright.async_api import async_playwright
    base=legacy();p=payload(j);c=base.config(j['account_key']);base.validate(p,c)
    with base.profile_lock(j['account_key']) as profile:
        async with async_playwright() as pw:
            ctx=await pw.chromium.launch_persistent_context(str(profile),headless=True,chromium_sandbox=True,accept_downloads=False,service_workers='block')
            try:
                async def guard(route):
                    try:
                        hosts=c['allowed_hosts'] if route.request.is_navigation_request() else c.get('resource_hosts',c['allowed_hosts'])
                        await asyncio.to_thread(base.allowed_url,route.request.url,hosts)
                    except Exception:
                        await route.abort();return
                    await route.continue_()
                await ctx.route('**/*',guard)
                page=await ctx.new_page();page.set_default_timeout(5000)
                for s in p['steps']:
                    await beat()
                    if s['action']=='goto':
                        await page.goto(s['url'],wait_until='domcontentloaded',timeout=5000);continue
                    await asyncio.to_thread(base.allowed_url,page.url,c['allowed_hosts'])
                    if s['action'] in ('fill','click'):
                        identity=page.locator(c['identity_selector'])
                        if await identity.count()!=1 or not await identity.is_visible() or (await identity.inner_text()).strip()!=c['identity_text']:
                            raise ValueError('identity_not_confirmed')
                    target=page.locator(s['selector'])
                    if await target.count()!=1 or not await target.is_visible(): raise ValueError('ambiguous_target')
                    await beat()
                    if s['action']=='click': await target.click()
                    elif s['action']=='fill': await target.fill(s['text'])
                    elif (await target.inner_text()).strip()!=s['expected_text']: raise ValueError('observation_mismatch')
            finally: await ctx.close()


async def run(j,call=rpc,executor=browse):
    args={k:j[k] for k in ('claim_token','claim_generation')};args['job_id']=j['id']
    async def beat(): await asyncio.to_thread(call,'heartbeat',args)
    async def pulse():
        while True:
            await beat();await asyncio.sleep(5)
    tasks=[];outcome='uncertain'
    try:
        payload(j);await beat()
        work=asyncio.create_task(executor(j,beat));heart=asyncio.create_task(pulse());tasks=[work,heart]
        done,_=await asyncio.wait(tasks,timeout=180,return_when=asyncio.FIRST_COMPLETED)
        if work in done:
            work.result()
            if heart.done(): heart.result()
            outcome='executed_unverified'
    except Exception: pass
    finally:
        for t in tasks:t.cancel()
        await asyncio.gather(*tasks,return_exceptions=True)
    try:
        await asyncio.to_thread(call,'complete',dict(args,outcome=outcome))
        return {'job_id':j['id'],'state':outcome,'platform_acceptance_verified':False,'public_visibility_verified':False}
    except Exception:return {'job_id':j['id'],'state':'completion_unrecorded','automatic_retry_allowed':False}


def main():
    if os.environ.get('BROWSER_V2_EXECUTION_ENABLED')!='1':return {'state':'disabled'}
    j=rpc('claim',{})
    return asyncio.run(run(j)) if j else {'state':'no_due_job'}


if __name__=='__main__':
    try: print(json.dumps(main()))
    except Exception:
        print(json.dumps({'state':'failed_closed','automatic_retry_allowed':False}));raise SystemExit(1)
