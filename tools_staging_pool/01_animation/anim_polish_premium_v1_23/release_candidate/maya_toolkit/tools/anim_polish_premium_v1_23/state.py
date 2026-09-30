"""Non-executable per-user settings and attribute clipboard, outside immutable code."""
import importlib
import json
import os
from pathlib import Path
import tempfile
import uuid
from .file_guards import external_directory

PACKAGE = Path(__file__).resolve().parent
CATALOG = json.loads((PACKAGE/'catalog.json').read_text(encoding='utf-8'))
SCALAR_TYPES = {'bool','byte','short','long','enum','float','double','doubleAngle','doubleLinear'}
VECTOR_TYPES = {'double2','double3','float2','float3','long2','long3','short2','short3'}


def data_directory(path=''):
    if path:
        return external_directory(path)
    import maya.cmds as cmds
    return external_directory((Path(cmds.internalVar(userAppDir=True))/'maya_toolkit_data/anim_polish').as_posix())


def _write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    text = json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+'\n'
    # Only the named private settings/clipboard is replaced; no arbitrary code/cache overwrite.
    descriptor,temporary = tempfile.mkstemp(prefix='anim_polish_',suffix='.json',dir=str(path.parent))
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as output:
            output.write(text)
        os.replace(temporary,path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def save_settings():
    import maya.cmds as cmds
    rows = []
    for typ,name,flag in CATALOG['settings_fields']:
        rows.append(dict(type=typ,name=name,flag=flag,value=getattr(cmds,typ)(name,query=True,**{flag:True})))
    path = data_directory()/'settings.json'
    _write(path,dict(version=1,fields=rows))
    return dict(path=path.as_posix(),saved=len(rows),scene_undo=False)


def load_settings():
    import maya.cmds as cmds
    path = data_directory()/'settings.json'
    if not path.is_file():
        importlib.import_module(__package__+'.vendor.animPolish.user_settings_default').run()
        return dict(defaults=True)
    data = json.loads(path.read_text(encoding='utf-8'))
    allowed = {tuple(row) for row in CATALOG['settings_fields']}
    if data.get('version')!=1 or not isinstance(data.get('fields'),list):
        raise ValueError('Unsupported settings JSON')
    for row in data['fields']:
        if (row.get('type'),row.get('name'),row.get('flag')) not in allowed:
            raise ValueError('Unknown settings field')
    for row in data['fields']:
        getattr(cmds,row['type'])(row['name'],edit=True,**{row['flag']:row['value']})
    return dict(path=path.as_posix(),loaded=len(data['fields']))


def default_settings():
    path = data_directory()/'settings.json'
    if path.exists():
        path.unlink()
    return load_settings()


def copy_attrs(path='',keyable=0):
    import maya.cmds as cmds
    selection = cmds.ls(selection=True,long=True) or []
    if len(selection)!=1:
        raise ValueError('Select one object to copy attributes')
    if keyable not in (0,1):
        raise ValueError('keyable must be 0/1')
    rows,skipped = [],[]
    names = cmds.listAttr(selection[0],keyable=True) if keyable else cmds.listAttr(selection[0])
    for name in names or []:
        plug = selection[0]+'.'+name
        try:
            kind = cmds.getAttr(plug,type=True)
            if kind not in SCALAR_TYPES|VECTOR_TYPES|{'string','matrix'}:
                skipped.append(name)
                continue
            value = cmds.getAttr(plug)
            json.dumps(value,allow_nan=False)
            rows.append(dict(name=name,type=kind,value=value))
        except Exception:
            skipped.append(name)
    destination = data_directory(path)/'attributes.json'
    _write(destination,dict(version=1,source=selection[0],attributes=rows))
    return dict(path=destination.as_posix(),copied=len(rows),skipped=skipped,scene_undo=False)


def paste_attrs(path=''):
    import maya.cmds as cmds
    selection = cmds.ls(selection=True,long=True) or []
    if not selection:
        raise ValueError('Select objects to paste attributes')
    source = data_directory(path)/'attributes.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    if data.get('version')!=1 or not isinstance(data.get('attributes'),list):
        raise ValueError('Unsupported attribute clipboard JSON')
    changed,skipped = [],[]
    for node in selection:
        for row in data['attributes']:
            name,kind,value = row['name'],row['type'],row['value']
            plug = node+'.'+name
            try:
                if not cmds.objExists(plug) or not cmds.getAttr(plug,settable=True) or cmds.getAttr(plug,type=True)!=kind:
                    skipped.append(plug)
                    continue
                if kind in SCALAR_TYPES:
                    cmds.setAttr(plug,value)
                elif kind=='string':
                    cmds.setAttr(plug,value or '',type='string')
                elif kind in VECTOR_TYPES:
                    values = value[0] if len(value)==1 and isinstance(value[0],list) else value
                    cmds.setAttr(plug,*values,type=kind)
                elif kind=='matrix':
                    cmds.setAttr(plug,*value,type='matrix')
                else:
                    raise ValueError('Unsupported attribute type')
                changed.append(plug)
            except Exception:
                skipped.append(plug)
    return dict(path=source.as_posix(),changed=changed,skipped=skipped)


def create_subdue_cache():
    import maya.mel as mel
    directory = data_directory()/'subdue_cache'/uuid.uuid4().hex
    directory.mkdir(parents=True,exist_ok=False)
    # Maya2025 doCreateGeometryCache documented args[5] is the directory.
    args = ['2','1','10','OneFile','1',directory.as_posix(),'0','','0','add','0','1','1','0','1','mcx','0']
    command = 'doCreateGeometryCache 6 {'+','.join(json.dumps(v,ensure_ascii=False) for v in args)+'};'
    return mel.eval(command)


def defer_sort(function):
    import maya.cmds as cmds
    selected = cmds.ls(selection=True,long=True) or []
    ids = [cmds.ls(n,uuid=True)[0] for n in selected]
    def sort_after_chunk():
        resolved = [found[0] for ident in ids for found in [cmds.ls(ident,long=True) or []] if found]
        if not resolved:
            return
        current = cmds.ls(selection=True,long=True) or []
        try:
            cmds.select(resolved,replace=True)
            function()
        finally:
            current = [n for n in current if cmds.objExists(n)]
            cmds.select(current,replace=True) if current else cmds.select(clear=True)
    cmds.evalDeferred(sort_after_chunk,lowPriority=True)
    return dict(deferred=True,selection_uuids=ids,reason='Original deleteAttr/Undo sort runs after framework chunk closes')
