from pathlib import Path
import shutil,uuid,hashlib
def save_scene(value):
    from maya import cmds
    p=Path(value)
    if not p.is_absolute() or not p.parent.is_dir() or p.suffix.lower() not in ('.ma','.mb') or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Existing independent Maya output parent required')
    if p.exists():
        if not p.is_file():raise ValueError('Non-file output refused')
        backup=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
        with p.open('rb') as original,backup.open('xb') as target:shutil.copyfileobj(original,target)
        def sha(path):
            h=hashlib.sha256()
            with path.open('rb') as f:
                for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
            return h.digest()
        if sha(p)!=sha(backup):raise IOError('Scene backup mismatch')
    cmds.file(rename=str(p));return cmds.file(save=True,force=True,type='mayaAscii' if p.suffix.lower()=='.ma' else 'mayaBinary')
