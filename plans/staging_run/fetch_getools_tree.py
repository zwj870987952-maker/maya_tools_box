"""GitHub API/raw fallback; pinned source bytes only, bounded downloads."""
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'tools_staging_pool/07_subsystems_suites/getools_overlappy/release_candidate/dependency_source'
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'maya-tool-source-review'})
    with urllib.request.urlopen(req,timeout=15) as response:data=response.read(4*1024*1024+1)
    if len(data)>4*1024*1024:raise ValueError('File too large')
    return data

sha=json.loads(fetch('https://api.github.com/repos/GenEugene/GETools/commits/master'))['sha']
tree=json.loads(fetch('https://api.github.com/repos/GenEugene/GETools/git/trees/'+sha+'?recursive=1'))
assert not tree.get('truncated') and len(tree['tree'])<10000
items=[r for r in tree['tree'] if r['type']=='blob' and (r['path'].startswith('GETOOLS_SOURCE/') or r['path'] in ('LICENSE','README.md','changelog.txt'))]
print(json.dumps({'commit':sha,'files':len(items)}),flush=True)
# Probe raw routing before making many requests.
sample=next(r for r in items if r['path']=='LICENSE')
raw_url='https://raw.githubusercontent.com/GenEugene/GETools/'+sha+'/'
license_data=fetch(raw_url+'LICENSE')
if b'MIT' not in license_data:raise ValueError('Expected MIT LICENSE')

def download(row):
    path=row['path'];target=(DEST/path).resolve()
    if not target.is_relative_to(DEST.resolve()) or row['mode']=='120000':raise ValueError('Unsafe path')
    if target.exists():value=target.read_bytes()
    else:value=license_data if path=='LICENSE' else fetch(raw_url+urllib.request.quote(path,safe='/'))
    git_sha=hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()
    if git_sha!=row['sha']:raise ValueError('Pinned Git object hash mismatch: '+path)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(value)
    return {'path':path,'sha256':hashlib.sha256(value).hexdigest(),'git_blob':row['sha']}

rows=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    futures=[pool.submit(download,row) for row in items]
    for f in as_completed(futures):rows.append(f.result())
info={'repository':'https://github.com/GenEugene/GETools','commit':sha,'method':'GitHub tree plus raw, every byte verified against pinned Git blob hash',
      'note':'Missing dependencies/resources only, supplied localized modules overlaid separately; installer not executed','files':sorted(rows,key=lambda r:r['path'])}
(DEST.parent/'dependency_provenance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':True,'files':len(rows),'commit':sha}),flush=True)
