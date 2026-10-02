"""Fetch pinned MIT dependency source only; never run an installer or downloaded code."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'tools_staging_pool/07_subsystems_suites/getools_overlappy/release_candidate/dependency_source'

def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'maya-tools-staging-source-review'})
    with urllib.request.urlopen(request,timeout=40) as response:
        data=response.read(40*1024*1024+1)
    if len(data)>40*1024*1024:raise ValueError('Archive exceeds size bound')
    return data

meta=json.loads(fetch('https://api.github.com/repos/GenEugene/GETools/commits/master'))
sha=meta['sha']
assert len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
url='https://codeload.github.com/GenEugene/GETools/zip/'+sha
data=fetch(url)
archive=zipfile.ZipFile(io.BytesIO(data))
entries=archive.infolist()
if len(entries)>10000 or sum(x.file_size for x in entries)>100*1024*1024:raise ValueError('Archive too large')
rows=[]
for entry in entries:
    parts=Path(entry.filename).parts[1:]
    if not parts or entry.is_dir():continue
    if any(p in ('..','.') for p in parts) or ((entry.external_attr>>16)&0o170000)==0o120000:raise ValueError('Unsafe archive entry')
    target=(DEST/Path(*parts)).resolve()
    if not target.is_relative_to(DEST.resolve()):raise ValueError('Outside dependency directory')
    value=archive.read(entry)
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=value:raise ValueError('Refuse changing existing dependency snapshot')
    target.write_bytes(value)
    rows.append({'path':target.relative_to(DEST).as_posix(),'sha256':hashlib.sha256(value).hexdigest()})
info={'repository':'https://github.com/GenEugene/GETools','commit':sha,'url':url,'archive_sha256':hashlib.sha256(data).hexdigest(),
      'note':'Only missing dependency source and resources; supplied localized modules preserved separately and overlay in candidate. No downloaded code executed.', 'files':rows}
(DEST.parent/'dependency_provenance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'commit':sha,'files':len(rows),'archive_sha256':info['archive_sha256']}))
