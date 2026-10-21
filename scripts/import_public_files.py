"""Validate/import catalog JSON. Dry-run default; never publishes or overwrites."""
import argparse, datetime, json, os, re, urllib.parse, urllib.request
FIELDS=('source_url','public_document_url','sha256','retrieved_at','title','description','agency','document_type','document_date','keywords')
def https(value):
    p=urllib.parse.urlsplit(value if isinstance(value,str) else '')
    return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password
def validate(data):
    if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(data.get('documents'),list): raise ValueError('Expected schema_version 1 and documents array')
    if len(data['documents'])>5000: raise ValueError('Batch exceeds 5000 documents')
    rows=[]; seen=set()
    for i,item in enumerate(data['documents']):
        if not isinstance(item,dict): raise ValueError('Document object required')
        for key in ('title','agency','document_type','description'):
            if not isinstance(item.get(key),str) or not item[key].strip() or len(item[key])>5000: raise ValueError(f'Row {i}: invalid {key}')
        digest=item.get('sha256','')
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest): raise ValueError('Invalid SHA256')
        if digest in seen: raise ValueError('Duplicate SHA256 in manifest')
        seen.add(digest)
        for key in ('source_url','public_document_url'):
            if not https(item.get(key)): raise ValueError(f'Public HTTPS {key} required')
        stamp=item.get('retrieved_at')
        if not isinstance(stamp,str): raise ValueError('retrieved_at required')
        dt=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))
        if dt.tzinfo is None: raise ValueError('Timezone required')
        if item.get('document_date') is not None: datetime.date.fromisoformat(item['document_date'])
        tags=item.get('keywords',[])
        if not isinstance(tags,list) or len(tags)>100 or any(not isinstance(x,str) or len(x)>200 for x in tags): raise ValueError('Invalid keywords')
        row={k:item[k] for k in FIELDS if k in item}; row.update(review_status='draft',redaction_reviewed=False); rows.append(row)
    return rows
def request(base,key,path,method='GET',body=None):
    req=urllib.request.Request(base+'/rest/v1/'+path,data=None if body is None else json.dumps(body).encode(),method=method,headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=minimal'})
    with urllib.request.urlopen(req,timeout=45) as response:
        raw=response.read(); return json.loads(raw) if raw else None
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('manifest'); p.add_argument('--apply',action='store_true'); args=p.parse_args()
    with open(args.manifest,encoding='utf-8') as f: rows=validate(json.load(f))
    if not args.apply:
        print(json.dumps({'validated':len(rows),'writes':0,'mode':'dry-run','publication':'always draft'})); return
    base=os.environ.get('SUPABASE_URL','').rstrip('/'); key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
    if not https(base) or not key: raise SystemExit('Set HTTPS SUPABASE_URL and server-only SUPABASE_SERVICE_ROLE_KEY')
    inserted=skipped=0
    for row in rows:
        if request(base,key,'pf_documents?select=id&sha256=eq.'+row['sha256']): skipped+=1; continue
        request(base,key,'pf_documents','POST',row); inserted+=1
    print(json.dumps({'inserted_drafts':inserted,'existing_skipped':skipped,'published':0}))
if __name__=='__main__': main()
