"""Native output checks and exact-byte backups, independent of Maya."""
from pathlib import Path
import hashlib
import shutil
import uuid
backups=[]

def checked_path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid file path')
    path=Path(value)
    if not path.is_absolute():raise ValueError('Absolute file path required')
    if path.is_symlink():raise ValueError('Symlink destination refused')
    if not path.parent.is_dir():raise ValueError('Output parent must already exist')
    return path

def require_new(value):
    path=checked_path(value)
    if path.exists():raise FileExistsError('Existing output is preserved: '+str(path))
    return str(path)

def backup_existing(value):
    path=checked_path(value)
    if not path.exists():return None
    if not path.is_file():raise ValueError('Only file backup supported')
    if path.stat().st_size>128*1024*1024:raise ValueError('Backup file exceeds 128 MiB')
    dst=path.with_name(path.name+'.mtb_backup_'+uuid.uuid4().hex)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open('rb') as source,dst.open('xb') as target:shutil.copyfileobj(source,target)
    if hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError('Backup verification failed; original untouched')
    row={'source':str(path),'backup':str(dst),'sha256':digest};backups.append(row)
    return row
