from pathlib import Path
import base64,copy,json,os,re,tempfile,uuid
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Explicit valid absolute path required')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def root(value):
    p=path(value)
    if not p.is_dir() or Path(__file__).parent.resolve() in (p.resolve(),*p.resolve().parents):raise ValueError('Independent existing state directory required')
    return p
def tabs(rows):
    if not isinstance(rows,list) or len(rows)>256:raise ValueError('0-256 tabs required')
    for row in rows:
        if not isinstance(row,dict) or set(row)-{'name','fname','autosave','active','thumbnail'}:raise ValueError('Unknown tab fields')
        if not isinstance(row.get('name'),str) or not row['name'] or len(row['name'])>256:raise ValueError('Invalid tab name')
        if not isinstance(row.get('fname'),str):raise ValueError('Invalid filename')
        if row['fname'] and (not path(row['fname']).suffix.lower() in ('.ma','.mb')):raise ValueError('Only Maya scene files in tabs')
        for k in ('autosave','active'):
            if k in row and type(row[k]) is not bool:raise ValueError('Strict tab boolean')
        if 'autosave' not in row:raise ValueError('autosave boolean required')
        thumb=row.get('thumbnail','')
        if not isinstance(thumb,str) or len(thumb)>4*1024*1024:raise ValueError('Thumbnail bound')
        if thumb:
            blob=base64.b64decode(thumb,validate=True)
            if not blob.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG thumbnail required')
    return rows
def style(row):
    if not isinstance(row,dict) or set(row)!={'width','height','tabColor','tabColorActive','tabColorHasFile'}:raise ValueError('Complete style required')
    for key in ('width','height'):
        if not isinstance(row[key],str) or not row[key].isdigit() or not 1<=int(row[key])<=2000:raise ValueError('Bounded style size')
    for key in ('tabColor','tabColorActive','tabColorHasFile'):
        if not isinstance(row[key],str) or not re.fullmatch('#[0-9a-fA-F]{6}',row[key]):raise ValueError('Hex RGB color required')
    return row
def theme(row):
    if not isinstance(row,dict) or set(row)!={'size','style'} or not isinstance(row['size'],dict) or set(row['size'])!={'width','height'} or not isinstance(row['style'],dict) or set(row['style'])!={'active','inactive','empty'}:raise ValueError('Invalid theme')
    style({'width':row['size']['width'],'height':row['size']['height'],'tabColor':row['style']['inactive'],'tabColorActive':row['style']['active'],'tabColorHasFile':row['style']['empty']});return row
def settings(row):
    if not isinstance(row,dict) or set(row)-{'version','animated','tooltipDelay','tabs','currentTabIndex','lastSaveDir','style'}:raise ValueError('Unknown settings fields')
    tabs(row.get('tabs'));style(row.get('style'))
    if type(row.get('animated')) is not bool or type(row.get('tooltipDelay')) is not int or not 0<=row['tooltipDelay']<=60000:raise ValueError('Invalid animation options')
    if type(row.get('currentTabIndex')) is not int or not 0<=row['currentTabIndex']<max(1,len(row['tabs'])):raise ValueError('Invalid tab index')
    if not isinstance(row.get('version'),str) or len(row['version'])>64:raise ValueError('Invalid version')
    path(row.get('lastSaveDir'));return row
def payload(p,row):
    if p.suffix=='.tabs-session':return tabs(row)
    if p.suffix=='.mttheme':return theme(row)
    if p.name=='Maya-Tabs.ini':return settings(row)
    raise ValueError('Unknown JSON file format')
def read(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>32*1024*1024:raise ValueError('Missing/oversized JSON')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate JSON key')
            result[k]=v
        return result
    return payload(p,json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def backup(value):
    p=path(str(value))
    if not p.is_file():raise ValueError('Existing regular file required')
    q=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
    with p.open('rb') as source,q.open('xb') as target:
        import shutil
        shutil.copyfileobj(source,target,1024*1024)
    import hashlib
    def sha(file):
        h=hashlib.sha256()
        with file.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()
    if sha(p)!=sha(q):raise IOError('Backup mismatch')
    return q
def write(value,row,overwrite=False):
    p=path(value);payload(p,row)
    if not p.parent.is_dir() or Path(__file__).parent.resolve() in (p.resolve(),*p.resolve().parents):raise ValueError('Independent existing parent required')
    blob=(json.dumps(row,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8')
    if len(blob)>32*1024*1024:raise ValueError('JSON bound')
    backed=None
    if p.exists():
        if not overwrite:raise ValueError('Existing file requires explicit overwrite')
        backed=backup(p);fd,tmp=tempfile.mkstemp(prefix='.mtb_tabs_',dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(blob)
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    else:
        with p.open('xb') as f:f.write(blob)
    return {'path':str(p),'backup':str(backed) if backed else None}
