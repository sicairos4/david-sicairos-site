"""Scheduled restricted-Drive manifest import. Never changes sharing or publishes."""
import json, os, re, sys
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from import_public_files import validate, request, https

def main():
    folder=os.environ.get('PUBLIC_FILES_DRIVE_FOLDER_ID','')
    raw=os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON','')
    base=os.environ.get('SUPABASE_URL','').rstrip('/')
    key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
    if not re.fullmatch('[A-Za-z0-9_-]{10,200}',folder) or not raw or not https(base) or not key:
        raise ValueError('Required private sync configuration is missing')
    credentials=service_account.Credentials.from_service_account_info(json.loads(raw),scopes=['https://www.googleapis.com/auth/drive.readonly'])
    session=AuthorizedSession(credentials)
    params={'q':"'"+folder+"' in parents and trashed = false and name = 'public-files-manifest.json'",'fields':'nextPageToken,files(id,mimeType,size)','pageSize':100,'supportsAllDrives':'true','includeItemsFromAllDrives':'true'}
    response=session.get('https://www.googleapis.com/drive/v3/files',params=params,timeout=45)
    response.raise_for_status(); listing=response.json(); matches=listing.get('files',[])
    if listing.get('nextPageToken') or len(matches)>1: raise ValueError('Multiple manifests found; keep exactly one canonical manifest')
    if not matches:
        print(json.dumps({'status':'waiting_for_manifest','inserted_drafts':0,'published':0})); return
    file=matches[0]
    if int(file.get('size','0'))>10000000: raise ValueError('Manifest exceeds 10 MB')
    download=session.get('https://www.googleapis.com/drive/v3/files/'+file['id'],params={'alt':'media','supportsAllDrives':'true'},timeout=45,stream=True)
    download.raise_for_status(); chunks=[]; length=0
    for chunk in download.iter_content(65536):
        length+=len(chunk)
        if length>10000000: raise ValueError('Manifest exceeds 10 MB')
        chunks.append(chunk)
    rows=validate(json.loads(b''.join(chunks).decode('utf-8-sig')))
    inserted=skipped=0
    for row in rows:
        if request(base,key,'pf_documents?select=id&sha256=eq.'+row['sha256']):
            skipped+=1; continue
        request(base,key,'pf_documents','POST',row); inserted+=1
    print(json.dumps({'status':'complete','inserted_drafts':inserted,'existing_skipped':skipped,'published':0}))
if __name__=='__main__':
    try: main()
    except Exception as error:
        print('Public Files sync failed ('+type(error).__name__+'). No publication performed. Check credentials, manifest and folder access; rerun resumes by original checksum.',file=sys.stderr)
        sys.exit(1)
