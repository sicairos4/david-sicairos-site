#!/usr/bin/env python3
"""Private OCR-first segmentation with parent/child receipts; no DB or upload."""
import argparse
from datetime import datetime,timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,type=Path)
    ap.add_argument('--parent-external-id',required=True)
    ap.add_argument('--output-root',type=Path,default=Path.home()/'209-private/priority-runs')
    ap.add_argument('--memory-mb',type=int,default=1536)
    ap.add_argument('--expected-pages',type=int)
    ap.add_argument('--expected-children',type=int)
    a=ap.parse_args()
    if not sys.platform.startswith('linux') or a.memory_mb<256: ap.error('Linux and memory-mb >=256 required')
    source=a.input.expanduser().resolve(strict=True)
    tools=Path(__file__).resolve().parent
    splitter=tools/'split_bundles.py'
    validator=tools/'validate_bundle_manifest.py'
    if not source.is_file() or not splitter.is_file() or not validator.is_file() or not a.parent_external_id.strip():
        ap.error('Missing original source, splitter, validator or parent ID')
    if not shutil.which('ocrmypdf') or not shutil.which('tesseract'):
        ap.error('Install OCRmyPDF and Tesseract first')
    original_hash=digest(source)
    if a.parent_external_id=='CPRA_MERCED_067':
        if original_hash!='d6c0a59d5a200f975c7efadce86f66b7df43a76952f72305acf1a2cde83fdd8c':
            ap.error('PHA original differs from previously inspected digest; inspect before processing')
        a.expected_pages=a.expected_pages or 50
        a.expected_children=a.expected_children or 10
    os.umask(0o077)
    root=a.output_root.expanduser()
    root.mkdir(mode=0o700,parents=True,exist_ok=True)
    run=root/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])
    run.mkdir(mode=0o700)
    derivative=run/'ocr_derivative.pdf'
    segments=run/'segments'
    state={'status':'started','original_sha256':original_hash,'original_bytes':source.stat().st_size,
           'splitter_sha256':digest(splitter),'validator_sha256':digest(validator),
           'versions':{'python':sys.version,'pypdf':version('pypdf'),'ocrmypdf':version('ocrmypdf')},
           'database_writes':False,'uploads':False,'publication':False,'stages':[]}
    def inspect(path):
        job={'input':str(path),'operation':'inspect','memory_mb':a.memory_mb,'timeout':180}
        result=subprocess.run([sys.executable,str(splitter),'--_worker'],input=json.dumps(job),text=True,
                              capture_output=True,timeout=180,check=False)
        if result.returncode: raise RuntimeError('inspect failed: '+result.stderr[-500:])
        return json.loads(result.stdout)['pages']
    def execute(command,name,timeout,limit=False):
        import resource
        def cap():
            max_bytes=a.memory_mb*1024*1024
            resource.setrlimit(resource.RLIMIT_AS,(max_bytes,max_bytes))
            resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        with (run/(name+'.stdout.log')).open('w') as stdout,(run/(name+'.stderr.log')).open('w') as stderr:
            result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=timeout,check=False,
                                  preexec_fn=cap if limit else None,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
        state['stages'].append({'name':name,'exit_code':result.returncode})
        if result.returncode: raise RuntimeError(name+' failed; inspect '+str(run/(name+'.stderr.log')))
    try:
        pages=inspect(source)
        if a.expected_pages is not None and pages!=a.expected_pages: raise ValueError('unexpected original page count')
        state['original_page_count']=pages
        execute(['ocrmypdf','--jobs','1','--skip-text','--output-type','pdf','--optimize','0',
                 '--tesseract-timeout','180',str(source),str(derivative)],'ocr',max(600,pages*180+120),True)
        if inspect(derivative)!=pages: raise ValueError('OCR changed physical page count')
        execute([sys.executable,str(splitter),'--input',str(derivative),'--parent-external-id',a.parent_external_id,
                 '--output',str(segments),'--memory-mb',str(a.memory_mb),'--scan-batch','8'],
                'split',max(600,pages*240+600))
        manifest_path=segments/'manifest.json'
        m=json.loads(manifest_path.read_text())
        m['source_provenance']={'original_source_filename':source.name,
                                'original_source_sha256':original_hash,
                                'original_source_size_bytes':source.stat().st_size,
                                'ocr_derivative_filename':derivative.name,
                                'ocr_derivative_sha256':digest(derivative),
                                'page_counts_equal':True,
                                'note':'Children are rewritten OCR derivatives; no signature validity is asserted.'}
        manifest_path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
        cmd=[sys.executable,str(validator),str(manifest_path),'--children-dir',str(segments),
             '--processing-parent',str(derivative),'--original-parent',str(source)]
        if a.expected_children: cmd+=['--expected-children',str(a.expected_children)]
        execute(cmd,'validate',max(180,pages*5))
        for child in m['children']:
            if inspect(segments/child['child_file_name'])!=child['page_count']:
                raise ValueError('child physical PDF page count mismatch')
        if digest(source)!=original_hash: raise ValueError('original changed during processing')
        state.update(status='candidate_segmentation_complete',child_page_counts_checked=True,
                     child_count=m['child_count'],validator_result=json.loads((run/'validate.stdout.log').read_text()))
    except Exception as exc:
        state.update(status='failed',error=str(exc))
        raise
    finally:
        (run/'run_receipt.json').write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps({'status':state['status'],'run':str(run)}))

if __name__=='__main__': main()
