from pathlib import Path
import json,os,tempfile,uuid
BOOLS={'baseFilter','selectionFilter','sf_getHierarchy','sf_getShadingNetwork','sf_getInputConnections','scriptFilter','searchInvert','showShapes','ignoreHierarchy','expandObjects','updateSelectionFilter'}
STRINGS={'icon','baseFilterType','internalFilter','scriptFunction','scriptModule','scriptArgs','searchString','description','hierarchyBehavior'}
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def config(value):
    if not isinstance(value,dict) or set(value)-{'FILTERS','FILTERORDER','MENUPRESETS'}:raise ValueError('Unknown filter config keys')
    filters=value.get('FILTERS')
    if not isinstance(filters,dict) or not 1<=len(filters)<=512:raise ValueError('1-512 filters required')
    for name,row in filters.items():
        if not isinstance(name,str) or not name or len(name)>256 or not isinstance(row,dict) or set(row)-BOOLS-STRINGS-{'nodeTypes'}:raise ValueError('Invalid filter')
        for k,v in row.items():
            if k in BOOLS and type(v) is not bool:raise ValueError('Strict filter boolean '+k)
            if k in STRINGS and (not isinstance(v,str) or len(v)>4096):raise ValueError('Invalid filter string '+k)
        if 'nodeTypes' in row and (not isinstance(row['nodeTypes'],list) or len(row['nodeTypes'])>512 or any(not isinstance(n,str) or not n or len(n)>256 for n in row['nodeTypes'])):raise ValueError('Invalid nodeTypes')
        if row.get('baseFilterType','internalFilter') not in ('internalFilter','nodeTypes'):raise ValueError('Unknown base filter type')
    order=value.get('FILTERORDER',list(filters))
    if order is None:order=list(filters)
    if not isinstance(order,list) or len(order)!=len(set(order)) or any(n not in filters for n in order):raise ValueError('Invalid filter order')
    presets=value.get('MENUPRESETS',{})
    if not isinstance(presets,dict) or len(presets)>512:raise ValueError('Invalid presets')
    for name,row in presets.items():
        if not isinstance(name,str) or not name or not isinstance(row,dict):raise ValueError('Invalid preset')
        for key,names in row.items():
            if key not in ('defaultFilter_nodeOutlinerA','defaultFilter_nodeOutlinerB','iconMenu','outlinerMenu') or not isinstance(names,list) or any(n not in filters for n in names):raise ValueError('Invalid preset filter references')
    return {'FILTERS':filters,'FILTERORDER':order,'MENUPRESETS':presets}
def read(value):
    p=path(str(value))
    if not p.is_file() or p.stat().st_size>8*1024*1024:raise ValueError('Config absent or exceeds 8MiB')
    def pairs(rows):
        out={}
        for k,v in rows:
            if k in out:raise ValueError('Duplicate config key')
            out[k]=v
        return out
    return config(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def output(value,overwrite=False):
    p=path(str(value))
    if p.suffix.lower()!='.json' or not p.parent.is_dir():raise ValueError('JSON with existing parent required')
    if p.exists() and (not overwrite or not p.is_file()):raise ValueError('Existing file requires explicit overwrite')
    if Path(__file__).parent.resolve() in p.resolve().parents:raise ValueError('Bundled config is immutable')
    return p
def write(value,data,overwrite=False):
    p=output(value,overwrite);data=config(data);blob=(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8');backup=None
    if p.exists():
        backup=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex);original=p.read_bytes()
        with backup.open('xb') as f:f.write(original)
        if backup.read_bytes()!=original:raise IOError('Config backup mismatch')
        fd,tmp=tempfile.mkstemp(prefix='.mtb_outliner_',dir=str(p.parent))
        try:
            with os.fdopen(fd,'wb') as f:f.write(blob)
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    else:
        with p.open('xb') as f:f.write(blob)
    return {'path':str(p),'backup':str(backup) if backup else None}
