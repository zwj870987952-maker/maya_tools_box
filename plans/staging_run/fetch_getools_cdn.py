"""Pinned GitHub repository bytes through jsDelivr when direct GitHub routes fail."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'tools_staging_pool/07_subsystems_suites/getools_overlappy/release_candidate/dependency_source'
SHA='45c4e17504fded01262941843ed186e9ac73c477'
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'maya-staging-source-review'})
    with urllib.request.urlopen(req,timeout=30) as response:data=response.read(4*1024*1024+1)
    if len(data)>4*1024*1024:raise ValueError('File exceeds bound')
    return data
tree=json.loads(fetch('https://data.jsdelivr.com/v1/package/gh/GenEugene/GETools@'+SHA))
items=[]
def walk(nodes,prefix=''):
    for node in nodes:
        path=prefix+node['name']
        if node['type']=='directory':walk(node['files'],path+'/')
        elif path.startswith('GETOOLS_SOURCE/') or path in ('LICENSE','README.md','changelog.txt'):
            items.append(dict(node,path=path))
walk(tree['files'])
assert len(items)<10000 and sum(r['size'] for r in items)<100*1024*1024
print(json.dumps({'commit':SHA,'files':len(items)}),flush=True)
def download(row):
    path=row['path'];target=(DEST/path).resolve()
    if not target.is_relative_to(DEST.resolve()):raise ValueError('Unsafe repository path')
    value=target.read_bytes() if target.exists() else fetch('https://cdn.jsdelivr.net/gh/GenEugene/GETools@'+SHA+'/'+urllib.parse.quote(path,safe='/'))
    digest=hashlib.sha256(value).digest()
    if len(value)!=row['size'] or base64.b64encode(digest).decode()!=row['hash']:raise ValueError('Pinned tree SHA256 mismatch: '+path)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(value)
    return {'path':path,'sha256':digest.hex(),'size':len(value)}
rows=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    for future in as_completed([pool.submit(download,row) for row in items]):
        rows.append(future.result())
        if len(rows)%40==0:print(json.dumps({'downloaded':len(rows)}),flush=True)
license_data=(DEST/'LICENSE').read_text(encoding='utf-8')
assert 'MIT License' in license_data
info={'repository':'https://github.com/GenEugene/GETools','commit':SHA,
      'method':'Fixed GitHub commit via jsDelivr; every downloaded file matches pinned tree SHA256/size',
      'note':'GitHub archive, Git and raw routes timed out. jsDelivr serves original pinned public MIT source. Supplied localized modules overlay separately; no installer executed.',
      'files':sorted(rows,key=lambda r:r['path'])}
(DEST.parent/'dependency_provenance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':True,'files':len(rows),'commit':SHA}),flush=True)
