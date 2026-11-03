import json,os,tempfile
from pathlib import Path
p=Path('data/social-showcase.json')
data=json.loads(p.read_text(encoding='utf-8'))
profile={'group':'David Sicairos','platform':'linkedin','label':'LinkedIn','handle':'David Sicairos · @sicairosdavid','url':'https://www.linkedin.com/in/sicairosdavid/'}
profiles=data.setdefault('profiles',[])
if not any(x.get('platform')=='linkedin' and x.get('url','').rstrip('/')==profile['url'].rstrip('/') for x in profiles):profiles.append(profile)
selected=[
 {'id':'linkedin-7520804431630712832','title':'What I built after the firing','caption':'Preview: Card 1: What I built after the firing. Fired September 18, 2025. The job ended. The work did not.','url':'https://www.linkedin.com/posts/sicairosdavid_card-1-what-i-built-after-the-firing-fired-activity-7520804431630712832-G7MI'},
 {'id':'linkedin-7497339478471159808','title':'The lawsuit is moving forward','caption':'Preview: The lawsuit is moving forward. But the public-records work does not stop. Every request, response, deadline, and missing document creates a record.','url':'https://www.linkedin.com/posts/sicairosdavid_the-lawsuit-is-moving-forward-but-the-public-records-activity-7497339478471159808--Fzb'},
 {'id':'linkedin-7419868819990405120','title':'This is The 209 Audit','caption':'Preview: This is The 209 Audit. Receipts are the only cure for arrogance.','url':'https://www.linkedin.com/posts/sicairosdavid_this-is-the-209-audit-receipts-are-the-only-activity-7419868819990405120-Z4Gx'},
 {'id':'linkedin-7519416729404530689','title':'The audit lesson','caption':'Preview: I run the 209 audit the same way. Every CPRA request has a bounded scope, a named owner, a deadline. No spillover.','url':'https://www.linkedin.com/posts/sicairosdavid_leadership-systems-orgdesign-activity-7519416729404530689-l06i'}
]
posts=data.setdefault('posts',[]);existing={x.get('url','').rstrip('/') for x in posts}
for post in selected:
 if post['url'].rstrip('/') not in existing:
  posts.append({**post,'platform':'linkedin','kind':'conversation','account':'David Sicairos · LinkedIn','brand':'David Sicairos','published_at':None,'thumbnail':None,'origin':'selected_linkedin','caption_is_excerpt':True})
  existing.add(post['url'].rstrip('/'))
data['linkedin_collection_note']='Selected publicly indexed LinkedIn posts. Dates, full bodies, artwork and native embed URLs were not retrieved. This is not an automatic LinkedIn account feed.'
with tempfile.NamedTemporaryFile('w',dir=p.parent,delete=False,encoding='utf-8') as f:
 json.dump(data,f,ensure_ascii=False,indent=2);name=f.name
os.replace(name,p)
print('LinkedIn showcase selections installed; existing profiles and collections preserved.')
