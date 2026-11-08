import base64, datetime as dt, html, json, os, re, tempfile, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NOW=dt.datetime.now(dt.timezone.utc).isoformat()
PATH=ROOT/'data/media-catalog.json'
try: old=json.loads(PATH.read_text())
except FileNotFoundError: old={'items':[],'sources':{}}
items={i['id']:i for i in old.get('items',[])}
sources=dict(old.get('sources',{}))
def read(url,headers=None,data=None):
    if urllib.parse.urlparse(url).scheme!='https': raise ValueError('https_required')
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'209-Catalog/1.0',**(headers or {})})
    with urllib.request.urlopen(req,timeout=25) as r:
        b=r.read(5000001)
        if len(b)>5000000: raise ValueError('response_too_large')
        return b

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n'); name=f.name
    os.replace(name,path)
def row(platform,key,title,date,url,description=''):
    p=urllib.parse.urlparse(url or '')
    if p.scheme!='https' or not p.hostname or p.username or p.password: raise ValueError('invalid_public_url')
    return {'id':platform+':'+key,'platform':platform,'title':title,'published_at':date,'url':url,'description':description[:5000],'observed_at':NOW,'state':'public_source_observed'}
def collect(name,fn):
    try:
        rows,meta=fn()
        for i in rows: items[i['id']]=i
        sources[name]={'status':'ok','last_attempt_at':NOW,'last_success_at':NOW,'returned_count':len(rows),**meta}
    except Exception as e:
        sources[name]={**sources.get(name,{}),'status':'blocked' if isinstance(e,RuntimeError) else 'error','last_attempt_at':NOW,'error_type':type(e).__name__}
def youtube():
    root=ET.fromstring(read('https://www.youtube.com/feeds/videos.xml?channel_id=UCDMa9oEWj4i6KFOkjF79qLg'))
    ns={'a':'http://www.w3.org/2005/Atom','y':'http://www.youtube.com/xml/schemas/2015'}
    rows=[]
    for e in root.findall('a:entry',ns):
        k=e.findtext('y:videoId',namespaces=ns)
        if k: rows.append(row('youtube',k,e.findtext('a:title',default='',namespaces=ns),e.findtext('a:published',namespaces=ns),'https://www.youtube.com/watch?v='+k))
    if not rows: raise RuntimeError('empty_feed')
    return rows,{'coverage':'recent_feed_window_not_full_archive'}
def beehiiv():
    home='https://209connect.beehiiv.com/'
    url=os.environ.get('BEEHIIV_PUBLIC_RSS_URL','')
    if not url:
        page=read(home).decode('utf-8',errors='replace')
        for tag in re.findall(r'<link\b[^>]*>',page,re.I):
            attrs=dict(re.findall(r'''([\w:-]+)\s*=\s*['"]([^'"]*)['"]''',tag))
            if attrs.get('type','').lower() in ('application/rss+xml','application/atom+xml'):
                url=urllib.parse.urljoin(home,html.unescape(attrs.get('href',''))); break
    if not url: raise RuntimeError('outgoing_rss_not_configured_or_advertised')
    host=urllib.parse.urlparse(url).hostname or ''
    if not (host=='beehiiv.com' or host.endswith('.beehiiv.com')): raise RuntimeError('unapproved_feed_host')
    root=ET.fromstring(read(url)); rows=[]
    for e in root.findall('./channel/item'):
        link=e.findtext('link',''); key=e.findtext('guid') or link
        if link: rows.append(row('beehiiv',key,e.findtext('title',''),e.findtext('pubDate'),link,re.sub('<[^>]+>',' ',html.unescape(e.findtext('description','')))))
    ns={'a':'http://www.w3.org/2005/Atom'}
    for e in root.findall('a:entry',ns):
        link=next((x.get('href','') for x in e.findall('a:link',ns) if x.get('rel','alternate')=='alternate'),'')
        if link: rows.append(row('beehiiv',e.findtext('a:id',default=link,namespaces=ns),e.findtext('a:title',default='',namespaces=ns),e.findtext('a:published',namespaces=ns),link))
    if not rows: raise RuntimeError('empty_feed')
    return rows,{'coverage':'public_feed_window','feed_url':url}
def spotify():
    c=os.environ.get('SPOTIFY_CLIENT_ID'); s=os.environ.get('SPOTIFY_CLIENT_SECRET')
    if not c or not s: raise RuntimeError('spotify_actions_secrets_missing')
    h={'Authorization':'Basic '+base64.b64encode((c+':'+s).encode()).decode(),'Content-Type':'application/x-www-form-urlencoded'}
    token=json.loads(read('https://accounts.spotify.com/api/token',h,b'grant_type=client_credentials'))['access_token']
    url='https://api.spotify.com/v1/shows/75EZyW6vctDYLMvKgt5Uuf/episodes?market=US&limit=50'; rows=[]
    for _ in range(40):
        page=json.loads(read(url,{'Authorization':'Bearer '+token}))
        for e in page.get('items',[]):
            if e: rows.append(row('spotify',e['id'],e['name'],e.get('release_date'),e.get('external_urls',{}).get('spotify',''),e.get('description','')))
        url=page.get('next')
        if not url: break
        if not url.startswith('https://api.spotify.com/v1/shows/'): raise ValueError('unexpected_pagination_url')
    else: raise RuntimeError('pagination_limit')
    return rows,{'coverage':'public_show_episodes_US_market','owner_reported_uploads':8,'discrepancy':len(rows)!=8}
for name,fn in [('youtube',youtube),('beehiiv',beehiiv),('spotify',spotify)]: collect(name,fn)
ordered=sorted(items.values(),key=lambda i:i.get('published_at') or '',reverse=True)
save(PATH,{'version':1,'generated_at':NOW,'items':ordered,'sources':sources})
briefs=[{'source_id':i['id'],'source_url':i['url'],'title':i['title'],'state':'draft_requires_review','instruction':'Prepare platform-specific social copy or an audio/video script from this source; review claims, freshness, rights and prior publication before approval.'} for i in ordered[:40]]
save(ROOT/'data/media-draft-briefs.json',{'generated_at':NOW,'publishing_enabled':False,'briefs':briefs})
if any(s.get('status')!='ok' for s in sources.values()): raise SystemExit(2)
