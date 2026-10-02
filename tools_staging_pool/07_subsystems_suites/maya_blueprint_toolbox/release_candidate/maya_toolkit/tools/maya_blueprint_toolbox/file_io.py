"""Bounded literal JSON reads, exclusive writes and explicit overwrite backups."""
from pathlib import Path
import hashlib,json,shutil,uuid
MAX=8*1024*1024
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or p.is_symlink():raise ValueError('Absolute non-symlink path required')
    return p
def output_path(value,overwrite=False):
    if type(overwrite) is not bool:raise ValueError('overwrite_existing must be boolean')
    p=path(value)
    if not p.parent.is_dir():raise ValueError('Parent must already exist')
    if p.exists() and (not overwrite or not p.is_file()):raise ValueError('Existing output preserved; explicitly choose overwrite_existing with backup')
    return p
def backup_file(p):
    if p.stat().st_size>128*1024*1024:raise ValueError('Backup limit 128 MiB')
    dst=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open('rb') as source,dst.open('xb') as target:shutil.copyfileobj(source,target)
    if hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError('Backup verification failed')
    return {'path':str(dst),'sha256':digest}
def write_json(value,data,overwrite=False):
    p=output_path(value,overwrite);raw=json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2).encode('utf8')
    if len(raw)>MAX:raise ValueError('JSON exceeds 8 MiB')
    if p.exists():backup_file(p)
    if overwrite:
        temp=p.with_name(p.name+'.mtb_write_'+uuid.uuid4().hex)
        try:
            with temp.open('xb') as f:f.write(raw)
            temp.replace(p)
        finally:
            if temp.exists():temp.unlink()
    else:
        with p.open('xb') as f:f.write(raw)
    return str(p)
def read_json(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>MAX:raise ValueError('JSON absent or exceeds 8 MiB')
    def pairs(rows):
        result={}
        for key,item in rows:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=item
        return result
    def bad(value):raise ValueError('Non-finite JSON constant')
    return json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=bad)
