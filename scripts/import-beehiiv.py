import os,json,time,re,html,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode,urljoin,urlsplit
from html.parser import HTMLParser
from datetime import datetime,timezone
KEY=os.environ.get('BEEHIIV_API_KEY','')
PUB=os.environ.get('BEEHIIV_PUBLICATION_ID','pub_16f23338-bd23-443e-9a22-fad5e136629b')
if not KEY: raise SystemExit('BEEHIIV_API_KEY is missing. Existing public archive left unchanged.')
ALLOWED=set('p div span article section h1 h2 h3 h4 h5 h6 strong b em i u s blockquote ul ol li a img br hr table thead tbody tr th td pre code figure figcaption'.split())
VOID={'img','br','hr'}
DROP={'script','style','head','form','iframe','object','embed','svg','button','noscript'}
def url(value,base):
    value=urljoin(base,value or '')
    p=urlsplit(value)
    return value if p.scheme=='https' and not p.username and not p.password else ''
class Clean(HTMLParser):
    def __init__(self,base): super().__init__(convert_charrefs=True); self.base=base; self.out=[]; self.block=0
    def handle_starttag(self,tag,attrs):
        if tag in DROP: self.block+=1; return
        if self.block or tag not in ALLOWED:return
        attrs=dict(attrs); kept=[]
        for k in ('href','src','alt','title','colspan','rowspan'):
            if k not in attrs:continue
            if k=='href' and tag!='a':continue
            if k=='src' and tag!='img':continue
            v=attrs[k] or ''
            if k in ('href','src'):
                v=url(v,self.base)
                if not v:continue
            kept.append(k+'="'+html.escape(v,quote=True)+'"')
        if tag=='a':kept.append('rel="noopener noreferrer"')
        if tag=='img':kept.append('loading="lazy"')
        self.out.append('<'+tag+(' '+' '.join(kept) if kept else '')+'>')
    def handle_endtag(self,tag):
        if tag in DROP:
            self.block=max(0,self.block-1);return
        if not self.block and tag in ALLOWED and tag not in VOID:self.out.append('</'+tag+'>')
    def handle_data(self,data):
        if not self.block:self.out.append(html.escape(data))
def fetch(page):
    query=urlencode({'status':'confirmed','audience':'free','hidden_from_feed':'false','limit':100,'page':page,'order_by':'publish_date','direction':'desc','expand[]':'free_web_content'})
    req=Request('https://api.beehiiv.com/v2/publications/'+PUB+'/posts?'+query,headers={'Authorization':'Bearer '+KEY,'Accept':'application/json'})
    for attempt in range(6):
        try:
            with urlopen(req,timeout=60) as r:
                if r.status==202:
                    time.sleep(min(60,float(r.headers.get('Retry-After','10'))));continue
                data=json.load(r)
                if not isinstance(data.get('data'),list):raise RuntimeError('Invalid post response; archive unchanged')
                return data
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==5:raise RuntimeError('Beehiiv post request failed: HTTP '+str(e.code)) from None
            time.sleep(min(60,2**attempt*3))
    raise RuntimeError('Content still processing; archive unchanged')
posts=[];page=1
while True:
    data=fetch(page);posts.extend(data['data'])
    if page>=int(data.get('total_pages',1)):break
    page+=1
    if page>1000:raise RuntimeError('Pagination limit; archive unchanged')
articles=[]
for p in posts:
    if p.get('platform') not in ('web','both') or p.get('audience')!='free' or p.get('hidden_from_feed'):continue
    stamp=p.get('publish_date')
    if not isinstance(stamp,(int,float)) or stamp>time.time():continue
    slug=p.get('slug','')
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',slug):continue
    content=p.get('content',{});free=content.get('free',{}) if isinstance(content,dict) else {}
    body=free.get('web','') if isinstance(free,dict) else ''
    if not body:raise RuntimeError('Missing public body for '+slug+'; archive unchanged')
    source=p.get('web_url') or 'https://209connect.beehiiv.com/p/'+slug
    clean=Clean(source);clean.feed(body);clean.close()
    authors=p.get('authors') or ['David Sicairos']
    tags=p.get('content_tags') or []
    articles.append({'id':p['id'],'slug':slug,'title':p.get('title','Untitled'),'subtitle':p.get('subtitle',''),'date':datetime.fromtimestamp(stamp,timezone.utc).date().isoformat(),'author':', '.join(a if isinstance(a,str) else a.get('name','') for a in authors),'thumbnail':url(p.get('thumbnail_url',''),source) if p.get('thumbnail_url') else '', 'tags':[t if isinstance(t,str) else t.get('display','') for t in tags],'source_url':source,'html':''.join(clean.out)})
if not articles:raise RuntimeError('No eligible public web articles returned; archive unchanged')
# Localize links between imported editions without altering historical article wording.
for article in articles:
    for target in articles:
        old=html.escape('https://209connect.beehiiv.com/p/'+target['slug'],quote=True)
        article['html']=article['html'].replace('href="'+old+'"','href="signal.html?issue='+target['slug']+'"')
path=Path('data/newsletters.json');path.parent.mkdir(exist_ok=True)
output={'imported_at':datetime.now(timezone.utc).isoformat(),'articles':articles}
with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:
    json.dump(output,f,ensure_ascii=False);temp=f.name
os.replace(temp,path)
print('Imported public web articles:',len(articles))
