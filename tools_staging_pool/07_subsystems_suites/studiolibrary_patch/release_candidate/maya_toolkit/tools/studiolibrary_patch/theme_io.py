"""Recoverable CSS install/uninstall; backup first and content ownership checks."""
from pathlib import Path
import hashlib,json,os,tempfile,uuid
from .guards import path,read
CSS=Path(__file__).parent/'native/StudioLibrary_ThemePatch/theme_resources/css/default.css'
def digest(blob):return hashlib.sha256(blob).hexdigest()
def target(value):
    root=path(value);p=root/'css/default.css'
    if not p.is_file() or p.is_symlink():raise ValueError('Existing external Studio Library resource/css/default.css required')
    if Path(__file__).parent.resolve() in p.resolve().parents:raise ValueError('Bundled immutable resource cannot be overwritten')
    return p
def atomic(p,blob):
    fd,tmp=tempfile.mkstemp(prefix='.mtb_theme_',dir=str(p.parent))
    try:
        with os.fdopen(fd,'wb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def install(value):
    p=target(value);receipt=p.with_name('default.css.mtb_theme_receipt.json');theme=CSS.read_bytes()
    if receipt.exists():
        row=read(receipt)
        if row.get('owner')!='mtb_studiolibrary_theme' or row.get('target')!=str(p):raise ValueError('Foreign receipt')
        if digest(p.read_bytes())!=row['installed_sha256']:raise ValueError('External CSS changed; refuse overwrite')
        return row
    backup=p.with_name('default.css.mtb_backup_'+uuid.uuid4().hex);original=p.read_bytes()
    with backup.open('xb') as f:f.write(original)
    if backup.read_bytes()!=original:raise IOError('Backup verification failed; CSS unchanged')
    row={'owner':'mtb_studiolibrary_theme','target':str(p),'backup':str(backup),'original_sha256':digest(original),'installed_sha256':digest(theme)}
    with receipt.open('x',encoding='utf8') as f:json.dump(row,f,indent=2)
    try:atomic(p,theme)
    except Exception:
        atomic(p,original);receipt.unlink();raise
    return row
def uninstall(value):
    p=target(value);receipt=p.with_name('default.css.mtb_theme_receipt.json');row=read(receipt)
    if row.get('owner')!='mtb_studiolibrary_theme' or row.get('target')!=str(p):raise ValueError('Foreign theme receipt')
    backup=path(row['backup'])
    if backup.parent!=p.parent or not backup.name.startswith('default.css.mtb_backup_'):raise ValueError('Foreign backup path')
    if digest(p.read_bytes())!=row['installed_sha256'] or digest(backup.read_bytes())!=row['original_sha256']:raise ValueError('CSS or backup modified; restore refused')
    atomic(p,backup.read_bytes());receipt.unlink()
    return {'restored':str(p),'retained_backup':str(backup)}
