#!/usr/bin/env python3
"""Read-only structural and byte-level checks for 209.bundle-segmentation.v1."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

def fail(msg):
    raise ValueError(msg)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def check_file(path, record):
    path = Path(path)
    if not path.is_file() or path.is_symlink(): fail('missing or symlinked file: ' + str(path))
    if path.stat().st_size != record['file_size_bytes'] or digest(path) != record['sha256']:
        fail('byte receipt mismatch: ' + str(path))

def validate(m, children_dir=None, processing_parent=None, original_parent=None, expected_children=None):
    required = ('schema_version','parent_external_id','parent_file_name','parent_sha256',
                'parent_file_size_bytes','parent_page_count','child_count','children','detection',
                'resource_controls','limitations','publication_status')
    for key in required:
        if key not in m: fail('missing ' + key)
    if m['schema_version'] != '209.bundle-segmentation.v1' or m['publication_status'] != 'private_unreviewed':
        fail('unsupported manifest version or publication status')
    for key in ('parent_page_count','parent_file_size_bytes','child_count'):
        if type(m[key]) is not int or m[key] < 1: fail('invalid ' + key)
    if not isinstance(m['children'], list) or len(m['children']) != m['child_count']:
        fail('child count mismatch')
    if not re.fullmatch('[0-9a-f]{64}',m['parent_sha256']): fail('parent hash invalid')
    if not m['parent_external_id'] or not m['parent_file_name']: fail('missing parent identity')
    audit = m['detection']['page_audit']
    if [entry['page'] for entry in audit] != list(range(1,m['parent_page_count']+1)):
        fail('page audit incomplete')
    names=set()
    next_page=1
    for child in m['children']:
        name=child['child_file_name']
        if name in names or name != Path(name).name or not name.lower().endswith('.pdf') or '/' in name or chr(92) in name:
            fail('duplicate or unsafe child filename')
        names.add(name)
        if child['parent_external_id'] != m['parent_external_id'] or child['page_start'] != next_page or child['page_end'] < next_page:
            fail('parent identity, page gap, overlap or reversed range')
        if child['page_count'] != child['page_end']-child['page_start']+1:
            fail('child page arithmetic mismatch')
        if not re.fullmatch('[0-9a-f]{64}',child['sha256']) or type(child['file_size_bytes']) is not int or child['file_size_bytes'] < 1:
            fail('invalid child byte receipt')
        if child['boundary_status'] != 'heuristic_candidate_needs_review': fail('boundary overclaim')
        next_page=child['page_end']+1
        if children_dir is not None: check_file(Path(children_dir)/name,child)
    if next_page != m['parent_page_count']+1: fail('parent coverage incomplete')
    provenance=m.get('source_provenance')
    if processing_parent is not None: check_file(processing_parent,{'sha256':m['parent_sha256'],'file_size_bytes':m['parent_file_size_bytes']})
    if provenance:
        if provenance['ocr_derivative_sha256'] != m['parent_sha256'] or provenance['ocr_derivative_filename'] != m['parent_file_name']:
            fail('processing parent and OCR derivative disagree')
        if not provenance['page_counts_equal']: fail('OCR page count not equal')
    if original_parent is not None:
        if not provenance: fail('original provenance required')
        check_file(original_parent,{'sha256':provenance['original_source_sha256'],
                                    'file_size_bytes':provenance['original_source_size_bytes']})
    return {'valid':True,'child_count':m['child_count'],'parent_pages':m['parent_page_count'],
            'child_bytes_verified':children_dir is not None,'processing_parent_bytes_verified':processing_parent is not None,
            'original_bytes_verified':original_parent is not None,
            'expected_child_count_match':None if expected_children is None else expected_children==m['child_count'],
            'boundary_identity_certified':False,'database_modified':False}

def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result: fail('duplicate JSON key: '+key)
        result[key]=value
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--children-dir',type=Path)
    parser.add_argument('--processing-parent',type=Path)
    parser.add_argument('--original-parent',type=Path)
    parser.add_argument('--expected-children',type=int)
    args=parser.parse_args()
    try:
        data=json.loads(args.manifest.read_text(),object_pairs_hook=unique,
                        parse_constant=lambda x:fail('nonstandard number: '+x))
        print(json.dumps(validate(data,args.children_dir,args.processing_parent,
                                  args.original_parent,args.expected_children),indent=2))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(str(error),file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__': main()
