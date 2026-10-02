"""Pinned LGPL upstream dependency, complete source/assets, no installer execution."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import base64,hashlib,json,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'tools_staging_pool/07_subsystems_suites/studiolibrary_patch/release_candidate/dependency_source'
META=DEST.parent/'dependency_provenance.json'
REPO='krathjen/studiolibrary'
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'maya-staging-source-review'})
    with urllib.request.urlopen(request,timeout=25) as response:raw=response.read(8*1024*1024+1)
    if len(raw)>8*1024*1024:raise ValueError('Per-file 8MiB limit')
    return raw
if META.exists():SHA=json.loads(META.read_text(encoding='utf8'))['commit']
else:
    metadata=json.loads(fetch('https://api.github.com/repos/'+REPO+'/commits/main'));SHA=metadata['sha']
    META.parent.mkdir(parents=True,exist_ok=True)
    META.write_text(json.dumps({'repository':'https://github.com/'+REPO,'commit':SHA,'state':'downloading','files':[]},indent=2),encoding='utf8')
TREE=META.with_name('dependency_tree.json')
tree=json.loads(TREE.read_text(encoding='utf8')) if TREE.exists() else json.loads(fetch('https://data.jsdelivr.com/v1/package/gh/'+REPO+'@'+SHA))
TREE.write_text(json.dumps(tree,ensure_ascii=False,indent=2),encoding='utf8')
items=[]
def walk(nodes,prefix=''):
    for node in nodes:
        path=prefix+node['name']
        if node['type']=='directory':walk(node['files'],path+'/')
        elif path.startswith(('src/','config/')) or path in ('LICENSE.md','README.md','DOCS.md'):items.append(dict(node,path=path))
walk(tree['files'])
if len(items)>10000 or sum(r['size'] for r in items)>200*1024*1024:raise ValueError('Repository limit exceeded')
print(json.dumps({'commit':SHA,'files':len(items),'bytes':sum(r['size'] for r in items)}),flush=True)
def download(row):
    name=row['path'];target=(DEST/name).resolve()
    if not target.is_relative_to(DEST.resolve()):raise ValueError('Unsafe source path')
    archived=target.with_suffix('.py.original') if target.suffix=='.py' else target
    if target.exists():raw=target.read_bytes()
    elif archived.exists():raw=archived.read_bytes();target=archived
    else:
        failure=None
        for host in ('cdn.jsdelivr.net','fastly.jsdelivr.net','gcore.jsdelivr.net'):
            try:
                raw=fetch('https://'+host+'/gh/'+REPO+'@'+SHA+'/'+urllib.parse.quote(name,safe='/'));failure=None;break
            except Exception as error:failure=error
        if failure is not None:raise failure
    digest=hashlib.sha256(raw).digest()
    if len(raw)!=row['size'] or base64.b64encode(digest).decode()!=row['hash']:raise ValueError('Pinned SHA256 mismatch: '+name)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return {'path':name,'size':len(raw),'sha256':digest.hex()}
rows=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    for future in as_completed([pool.submit(download,row) for row in items]):
        rows.append(future.result())
        if len(rows)%50==0:print(json.dumps({'downloaded':len(rows)}),flush=True)
license_data=(DEST/'LICENSE.md').read_text(encoding='utf8')
if 'LESSER GENERAL PUBLIC LICENSE' not in license_data.upper():raise ValueError('Expected LGPL notice absent')
META.write_text(json.dumps({'repository':'https://github.com/'+REPO,'commit':SHA,'state':'complete',
    'method':'Official GitHub fixed commit; jsDelivr byte-for-byte SHA256/size verification, all src/config/resources/license preserved; no installer executed',
    'files':sorted(rows,key=lambda r:r['path'])},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'complete':True,'commit':SHA,'files':len(rows)}),flush=True)
