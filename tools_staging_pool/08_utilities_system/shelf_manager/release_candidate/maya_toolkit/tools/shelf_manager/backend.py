from pathlib import Path
import hashlib,json,os,re,shutil,uuid
DEFAULTS={'Animation','Arnold','Bifrost','Cexport','CurvesSurfaces','Custom','FX','FXCaching','MASH','MotionGraphics','MSPlugin','Polygons','Rendering','Rigging','Sculpting','TURTLE','XGen','Brushes','Display','Dynamics','General','Help','Modeling','Paint Effects','Stereo','Subdivision','Surfaces','UV'}
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Valid absolute path required')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def roots(values):
    if not isinstance(values,list) or not 1<=len(values)<=32:raise ValueError('1-32 explicit roots required')
    result=[]
    for value in values:
        p=path(value)
        if not p.is_dir():raise ValueError('Existing Maya preference root required')
        if p.resolve() not in result:result.append(p.resolve())
    return result
def detect():
    values=[Path.home()/'Documents/maya',Path.home()/'maya'];env=os.environ.get('MAYA_APP_DIR')
    if env:values.append(Path(env))
    return [str(p) for p in values if p.is_dir() and not any(q.is_symlink() for q in (p,*p.parents))]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def scan(values,include_defaults=False):
    base=roots(values);rows=[]
    for root in base:
        for version in range(2018,2027):
            for lang,sub in (('zh','zh_CN/prefs/shelves'),('en','prefs/shelves')):
                folder=root/str(version)/sub
                if not folder.is_dir():continue
                if any(q.is_symlink() for q in (folder,*folder.parents)):continue
                for p in sorted(folder.glob('shelf_*.mel')):
                    if not p.is_file() or p.is_symlink() or not p.stem[6:] or p.stat().st_size>16*1024*1024:continue
                    name=p.stem[6:]
                    if not include_defaults and name in DEFAULTS:continue
                    rows.append({'root':str(root),'version':str(version),'language':lang,'name':name,'path':str(p.resolve()),'icon':str(p.with_suffix('.png')) if p.with_suffix('.png').is_file() and not p.with_suffix('.png').is_symlink() else None,'sha256':sha(p)})
                    if len(rows)>10000:raise ValueError('Shelf scan exceeds 10000 files')
    return rows
def selected(values,files,icons=True):
    base=roots(values)
    if not isinstance(files,list) or not 1<=len(files)<=1000 or len(set(files))!=len(files):raise ValueError('1-1000 unique explicit shelf paths required')
    catalog={r['path']:r for r in scan(values,True)};rows=[]
    for value in files:
        p=path(value).resolve();row=catalog.get(str(p))
        if row is None:raise ValueError('File is not a scanned shelf in an explicit root: '+str(p))
        rows.append({'source':p,'root':Path(row['root']),'sha256':row['sha256']})
        if icons and row['icon']:
            icon=path(row['icon']);rows.append({'source':icon,'root':Path(row['root']),'sha256':sha(icon)})
    return rows
def migration(values,files,target,icons=True,overwrite=False):
    destination=path(target)
    if not destination.is_dir():raise ValueError('Existing migration directory required')
    if Path(__file__).parent.resolve() in (destination.resolve(),*destination.resolve().parents):raise ValueError('Candidate bundle is immutable')
    rows=selected(values,files,icons);seen=set()
    for row in rows:
        output=destination/row['source'].name
        if os.path.normcase(str(output)) in seen:raise ValueError('Two selected sources collide at destination')
        seen.add(os.path.normcase(str(output)));path(str(output))
        if output.resolve()==row['source'].resolve():raise ValueError('Source/destination identical')
        if output.exists() and (not output.is_file() or not overwrite):raise ValueError('Existing migration target requires explicit overwrite')
        row['target']=output
    return rows
def migrate(rows):
    receipts=[]
    for row in rows:
        source=row['source'];target=row['target']
        if sha(source)!=row['sha256']:raise RuntimeError('Source changed after preflight; previous completed copies preserved')
        backup=None
        if target.exists():
            backup=target.with_name(target.name+'.mtb_backup_'+uuid.uuid4().hex)
            with target.open('rb') as f,backup.open('xb') as out:shutil.copyfileobj(f,out)
            if sha(target)!=sha(backup):raise IOError('Backup mismatch')
        temporary=target.with_name('.mtb_copy_'+uuid.uuid4().hex)
        try:
            with source.open('rb') as f,temporary.open('xb') as out:shutil.copyfileobj(f,out)
            if sha(temporary)!=row['sha256'] or sha(source)!=row['sha256']:raise IOError('Copy/source hash mismatch')
            if not backup:
                # Exclusive final creation preserves a concurrent new destination.
                with temporary.open('rb') as f,target.open('xb') as out:shutil.copyfileobj(f,out)
            else:
                if sha(target)!=sha(backup):raise RuntimeError('Destination changed after backup; preserve foreign edit')
                os.replace(temporary,target)
            receipts.append({'source':str(source),'target':str(target),'backup':str(backup) if backup else None,'sha256':row['sha256']})
        finally:
            if temporary.exists():temporary.unlink()
    return receipts
def quarantine(rows):
    receipts=[];folders={}
    for row in rows:
        source=row['source'];root=row['root'].resolve()
        if root not in source.resolve().parents or sha(source)!=row['sha256']:raise RuntimeError('Source scope/hash changed; previous quarantined files recoverable')
        if root not in folders:
            folder=root/('.mtb_shelf_trash_'+uuid.uuid4().hex);folder.mkdir();folders[root]=folder
        folder=folders[root];target=folder/(uuid.uuid4().hex+'_'+source.name)
        if root not in target.resolve().parents or target.exists():raise ValueError('Invalid quarantine destination')
        source.rename(target);receipts.append({'source':str(source),'quarantine':str(target),'sha256':row['sha256']})
        (folder/'receipt.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return receipts
