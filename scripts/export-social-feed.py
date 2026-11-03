import os,json,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
from datetime import datetime,timezone
BASE=os.environ.get('SUPABASE_URL','').rstrip('/')
KEY=os.environ.get('SUPABASE_SERVICE_KEY','')
if not BASE or not KEY:raise SystemExit('Missing Supabase configuration; existing social feed preserved.')
HOSTS={'facebook':{'facebook.com','www.facebook.com','m.facebook.com','fb.watch'},'instagram':{'instagram.com','www.instagram.com'},'threads':{'threads.net','www.threads.net','threads.com','www.threads.com'},'linkedin':{'linkedin.com','www.linkedin.com'},'bluesky':{'bsky.app','www.bsky.app'},'tiktok':{'tiktok.com','www.tiktok.com','vm.tiktok.com','vt.tiktok.com'},'youtube':{'youtube.com','www.youtube.com','m.youtube.com','youtu.be'}}
def safe(value,platform=None):
    if not isinstance(value,str):return None
    try:
        u=urlsplit(value)
        if u.scheme!='https' or u.username or u.password:return None
        if platform and u.hostname not in HOSTS.get(platform,set()):return None
        return value
    except ValueError:return None
rows=[]
for offset in range(0,20000,200):
    params={'select':'id,platform,caption,published_at,platform_url,thumbnail_url:metadata->>thumbnail_url,content_items!inner(brand,headline,status,approval_status,risk_level)','status':'eq.published','platform_url':'not.is.null','published_at':'not.is.null','content_items.status':'eq.published','content_items.approval_status':'in.(approved,not_required)','content_items.risk_level':'eq.low','order':'published_at.desc,id.asc','limit':'200','offset':str(offset)}
    req=Request(BASE+'/rest/v1/content_variants?'+urlencode(params),headers={'apikey':KEY,'Authorization':'Bearer '+KEY,'Accept':'application/json'})
    with urlopen(req,timeout=45) as r:data=json.load(r)
    if not isinstance(data,list):raise RuntimeError('Unexpected ledger response; existing feed preserved')
    rows.extend(data)
    if len(data)<200:break
else:raise RuntimeError('Export limit reached; existing feed preserved')
posts=[];seen=set();counts={p:0 for p in HOSTS}
for r in rows:
    platform=r.get('platform');link=safe(r.get('platform_url'),platform)
    if platform not in HOSTS or not link or link in seen or counts[platform]>=30:continue
    item=r.get('content_items') or {}
    if not isinstance(item,dict):continue
    if item.get('status')!='published' or item.get('approval_status') not in ('approved','not_required') or item.get('risk_level')!='low':continue
    stamp=r.get('published_at','')
    try:
        when=datetime.fromisoformat(stamp.replace('Z','+00:00'))
        if when.tzinfo is None or when>datetime.now(timezone.utc):continue
    except (ValueError,TypeError):continue
    seen.add(link);counts[platform]+=1
    posts.append({'id':r['id'],'platform':platform,'title':(item.get('headline') or platform.title()+' post')[:500],'caption':(r.get('caption') or '')[:10000],'brand':(item.get('brand') or '')[:200],'url':link,'thumbnail':safe(r.get('thumbnail_url')),'published_at':stamp,'origin':'published_ledger'})
path=Path('data/social-feed.json')
old=json.loads(path.read_text()) if path.exists() else {'posts':[]}
for p in old.get('posts',[]):
    if p.get('origin')=='existing_site_selection' and p.get('platform')=='youtube' and safe(p.get('url'),'youtube') and p['url'] not in seen:posts.append(p)
output={'updated_at':datetime.now(timezone.utc).isoformat(),'source':'Eligible published ledger records; not a complete platform mirror','counts':counts,'posts':posts}
path.parent.mkdir(exist_ok=True)
with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:
    json.dump(output,f,ensure_ascii=False);name=f.name
os.replace(name,path)
print('Exported published ledger social posts:',sum(counts.values()))
