import json,os,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
from xml.etree import ElementTree as ET
from datetime import datetime,timezone
HANDLE='davidsicairos.bsky.social'
CHANNEL='UCDMa9oEWj4i6KFOkjF79qLg'
PATH=Path('data/social-showcase.json')
def request(url):
 req=Request(url,headers={'User-Agent':'209Connect-PublicShowcase/1.0','Accept':'application/json,application/atom+xml,application/xml'})
 with urlopen(req,timeout=30) as r:return r.read()
def https(value):
 if not isinstance(value,str):return None
 try:
  p=urlsplit(value);return value if p.scheme=='https' and not p.username and not p.password else None
 except ValueError:return None
def bluesky():
 raw=json.loads(request('https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?'+urlencode({'actor':HANDLE,'limit':30})))
 if not isinstance(raw.get('feed'),list):raise ValueError('Invalid public feed')
 rows=[]
 for item in raw['feed']:
  p=item.get('post') or {};author=p.get('author') or {};record=p.get('record') or {}
  if str(author.get('handle','')).lower()!=HANDLE or item.get('reason') or record.get('reply'):continue
  uri=p.get('uri','');parts=uri.split('/')
  if len(parts)!=5 or not uri.startswith('at://did:') or parts[3]!='app.bsky.feed.post':continue
  key=parts[-1]
  if not key or not all(c.isalnum() or c in '._~-' for c in key):continue
  text=str(record.get('text') or '').strip()
  if not text:continue
  embed=p.get('embed') or {};images=embed.get('images') or [];thumbnail=None;kind='conversation'
  if images and isinstance(images[0],dict):thumbnail=https(images[0].get('thumb'));kind='photo'
  external=embed.get('external') or {}
  if not thumbnail and isinstance(external,dict):thumbnail=https(external.get('thumb'))
  if embed.get('$type')=='app.bsky.embed.video#view':thumbnail=https(embed.get('thumbnail'));kind='video'
  rows.append({'id':uri,'platform':'bluesky','kind':kind,'title':text.splitlines()[0][:120],'caption':text,'account':'@'+HANDLE,'brand':'David Sicairos','published_at':record.get('createdAt'),'url':'https://bsky.app/profile/'+HANDLE+'/post/'+key,'thumbnail':thumbnail,'origin':'public_bluesky'})
  if len(rows)>=12:break
 return rows
def youtube():
 root=ET.fromstring(request('https://www.youtube.com/feeds/videos.xml?'+urlencode({'channel_id':CHANNEL})))
 ns={'a':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015','m':'http://search.yahoo.com/mrss/'}
 if root.tag!='{http://www.w3.org/2005/Atom}feed':raise ValueError('Invalid video feed')
 rows=[]
 for entry in root.findall('a:entry',ns):
  ident=entry.findtext('yt:videoId','',ns)
  if len(ident)!=11 or not all(c.isalnum() or c in '_-' for c in ident):continue
  thumbnail=entry.find('m:group/m:thumbnail',ns)
  rows.append({'id':'youtube-'+ident,'platform':'youtube','kind':'video','title':entry.findtext('a:title','YouTube video',ns),'caption':entry.findtext('m:group/m:description','',ns)[:10000],'account':'David Sicairos · YouTube','brand':'David Sicairos','published_at':entry.findtext('a:published',None,ns),'url':'https://www.youtube.com/watch?v='+ident,'thumbnail':https(thumbnail.get('url')) if thumbnail is not None else None,'origin':'public_youtube'})
 return rows
if not PATH.exists():raise SystemExit('Showcase configuration missing; no file overwritten')
config=json.loads(PATH.read_text(encoding='utf-8'))
existing=config.get('posts',[])
if not isinstance(existing,list):raise SystemExit('Unexpected configuration; no file overwritten')
statuses=dict(config.get('collection_status') or {});success=0
for name,origin,collect in [('bluesky','public_bluesky',bluesky),('youtube','public_youtube',youtube)]:
 try:
  new=collect();existing=[p for p in existing if p.get('origin')!=origin]+new
  statuses[name]={'state':'collected','collected_at':datetime.now(timezone.utc).isoformat(),'count':len(new)};success+=1
 except Exception:
  statuses[name]={'state':'collection_unavailable','last_attempt_at':datetime.now(timezone.utc).isoformat(),'retained_previous_collection':True}
  print(name+': collection unavailable; previous entries retained')
if not success:raise SystemExit('All sources unavailable; showcase configuration unchanged')
seen=set();posts=[]
for p in existing:
 link=p.get('url')
 if not https(link) or link in seen:continue
 seen.add(link);posts.append(p)
config['posts']=posts;config['collection_status']=statuses
config['collection_note']='Recent public source items, not a complete account archive. No posting credentials used.'
with tempfile.NamedTemporaryFile('w',dir=PATH.parent,delete=False,encoding='utf-8') as f:
 json.dump(config,f,ensure_ascii=False,indent=2);name=f.name
os.replace(name,PATH)
print('Updated showcase from public sources; source collections completed:',success)
