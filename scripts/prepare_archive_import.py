#!/usr/bin/env python3
"""Prepare owner-bound private metadata SQL. No network or database execution."""
import argparse, hashlib, json, os, pathlib, re, uuid
EXPECTED_BYTES=44102

def clean(value):
    if isinstance(value,str) and '\x00' in value:
        raise ValueError('NUL characters cannot be imported')
    if isinstance(value,dict):
        for k,v in value.items():
            clean(k); clean(v)
    elif isinstance(value,list):
        for v in value:
            clean(v)

def literal(value):
    if '\x00' in value:
        raise ValueError('NUL characters cannot be imported')
    return "'"+value.replace("'","''")+"'"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',required=True,type=pathlib.Path)
    p.add_argument('--owner',required=True,type=uuid.UUID)
    p.add_argument('--output',required=True,type=pathlib.Path)
    p.add_argument('--commit',action='store_true',help='Generate apply SQL; never execute it')
    a=p.parse_args(); os.umask(0o077)
    expected=os.environ.get('ARCHIVE_DATASET_SHA256','').strip().lower()
    if not re.fullmatch(r'[0-9a-f]{64}',expected):
        raise ValueError('Configure ARCHIVE_DATASET_SHA256 from the trusted source receipt')
    if a.owner.int==0:
        raise ValueError('Actual Supabase Auth owner UUID required')
    receipt=a.output.with_suffix(a.output.suffix+'.receipt.json')
    if a.output.exists() or receipt.exists():
        raise ValueError('Choose a new private output filename')
    raw=a.dataset.read_bytes()
    if len(raw)!=EXPECTED_BYTES or hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError('Source size/hash mismatch; do not substitute the PDF index or package')
    data=json.loads(raw.decode('utf-8-sig')); clean(data)
    if not isinstance(data,dict) or not isinstance(data.get('files'),list) or not isinstance(data.get('missing'),list):
        raise ValueError('Original files/missing arrays required; no inferred conversion')
    if len(data['files'])!=88 or len(data['missing'])!=17:
        raise ValueError('Exactly 88 retrieved records and 17 historical missing entries required')
    rows=[]; identities=set()
    for index,r in enumerate(data['files'],1):
        if not isinstance(r,dict) or not all(isinstance(r.get(k),str) and r[k].strip() for k in ('folder','file')):
            raise ValueError(f'Record {index}: explicit folder/file identity required')
        folder,filename=r['folder'],r['file']
        if len(filename)>500:
            raise ValueError(f'Record {index}: filename exceeds archive title limit')
        identity=json.dumps([folder,filename],ensure_ascii=False,separators=(',',':'))
        external='archive-20261024:'+hashlib.sha256(identity.encode()).hexdigest()
        if external in identities:
            raise ValueError('Duplicate source identity requires reconciliation')
        identities.add(external)
        rows.append(dict(external_id=external,title=filename,original_filename=filename,entity_labels=[folder],intake_metadata={'archive_import':{'source_sha256':expected,'source_filename':a.dataset.name,'historical_missing_count':17,'original_record':r,'basis':'metadata-only; no byte retrieval, Drive mapping, release approval or matter completion inferred'}}))
    template=pathlib.Path(__file__).with_name('archive_import_template.psql').read_text(encoding='utf-8')
    rendered=[]
    for line in template.splitlines():
        if line.startswith('\\set '):
            continue
        line=line.replace(":'owner_uuid'",literal(str(a.owner))).replace(":'source_sha256'",literal(expected))
        line=line.replace(":'records_json'",literal(json.dumps(rows,ensure_ascii=False,separators=(',',':'))))
        if line=='ROLLBACK;' and a.commit:
            line='COMMIT;'
        rendered.append(line)
    sql='\n'.join(rendered)+'\n'
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:
        f.write(sql)
    fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:
        json.dump(dict(source_sha256=expected,source_bytes=len(raw),owner=str(a.owner),records=88,missing=17,sql_sha256=hashlib.sha256(sql.encode()).hexdigest(),generated_mode='apply' if a.commit else 'rollback',executed=False,tests_run=False,original_hashes_inferred=False,drive_ids_inferred=False),f,indent=2)
    print(json.dumps({'sql':str(a.output),'receipt':str(receipt),'records':88,'executed':False}))

if __name__=='__main__':
    try:
        main()
    except (ValueError,OSError) as e:
        raise SystemExit(str(e))
