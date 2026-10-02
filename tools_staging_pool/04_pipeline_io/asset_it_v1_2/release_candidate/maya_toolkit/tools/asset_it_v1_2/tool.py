"""Separate integration adapter for pristine licensed AssetIt 1.2 suite."""
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
from maya_toolkit.framework import BaseMayaTool,ToolResult

PKG=Path(__file__).resolve().parent
BUNDLE=PKG/'bundle'
LIBRARY=BUNDLE/'AssetIt/AssetIt_LIBRARY'


def bounded_json(path):
    if not path.is_file() or path.stat().st_size>8*1024*1024: raise ValueError('Missing/oversized JSON: '+str(path))
    return json.loads(path.read_text(encoding='utf8'))


def normalize(values):
    p=dict(action='inventory',library=None,asset=None,namespace=None,scale=1.,target_dir=None)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inventory','metadata','import_asset','install','launch_native'): raise ValueError('Invalid action')
    for key in ('library','target_dir'):
        if p[key] is not None and (not isinstance(p[key],str) or not Path(p[key]).is_absolute()): raise ValueError('Absolute directory required')
    if p['asset'] is not None and (not isinstance(p['asset'],str) or not p['asset'] or Path(p['asset']).is_absolute() or any(x in p['asset'].replace('\\','/').split('/') for x in ('','.','..')) or any(c in p['asset'] for c in '\x00\n\r')): raise ValueError('Safe relative asset .ma path required')
    if p['namespace'] is not None and (not isinstance(p['namespace'],str) or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',p['namespace'])): raise ValueError('Simple new namespace identifier required')
    if not isinstance(p['scale'],(int,float)) or isinstance(p['scale'],bool) or not math.isfinite(p['scale']) or not 0<p['scale']<=1e6: raise ValueError('Positive finite scale required')
    if p['action'] in ('metadata','import_asset') and p['asset'] is None: raise ValueError('Asset required')
    if p['action']=='import_asset' and p['namespace'] is None: raise ValueError('Explicit unique import namespace required')
    if p['action']!='import_asset' and any(k in values for k in ('namespace','scale')): raise ValueError('Import-only parameters')
    if p['action'] not in ('metadata','import_asset') and p['asset'] is not None: raise ValueError('Asset-only action required')
    if p['action'] not in ('install','launch_native') and p['target_dir'] is not None: raise ValueError('Target only applies to install/native UI')
    return p


def library(p):
    root=Path(p['library']).resolve() if p['library'] is not None else LIBRARY.resolve()
    if not root.is_dir(): raise ValueError('Library missing')
    return root


def asset_path(p):
    root=library(p); relative=Path(p['asset']); source=root/relative
    if source.is_symlink(): raise ValueError('Symlink asset unsupported')
    asset=source.resolve()
    if not asset.is_relative_to(root) or asset==root or asset.suffix.lower()!='.ma' or not asset.is_file(): raise ValueError('Asset must be existing .ma strictly inside declared library')
    if asset.is_symlink(): raise ValueError('Symlink asset unsupported')
    metadata=asset.with_suffix('.json'); thumbnail=asset.with_suffix('.png')
    return {'asset':str(asset),'relative':asset.relative_to(root).as_posix(),'metadata':bounded_json(metadata) if metadata.exists() else None,'thumbnail':str(thumbnail) if thumbnail.is_file() else None}


def inventory(p):
    root=library(p); assets=[]
    for file in sorted(root.rglob('*.ma')):
        resolved=file.resolve()
        if not resolved.is_relative_to(root): raise ValueError('Asset escapes declared library')
        assets.append({'relative':file.relative_to(root).as_posix(),'bytes':file.stat().st_size,'thumbnail':file.with_suffix('.png').is_file(),'metadata':file.with_suffix('.json').is_file()})
    return {'library':str(root),'assets':assets,'count':len(assets),'license_path':str(BUNDLE/'AssetIt_License.txt'),'native_code_modified':False}


def installed_target(p):
    from maya import cmds
    expected=(Path(cmds.internalVar(userAppDir=True))/str(cmds.about(version=True))/'scripts/AssetIt').resolve()
    target=Path(p['target_dir']).resolve() if p['target_dir'] is not None else expected
    if target.name!='AssetIt' or target==BUNDLE/'AssetIt' or target.is_relative_to(PKG): raise ValueError('Install only to separate directory named AssetIt')
    return target,expected


def install_plan(p):
    target,expected=installed_target(p)
    if target.exists() or target.is_symlink() or not target.parent.is_dir(): raise ValueError('Fresh target required; create scripts parent explicitly; existing installs never replaced')
    if 'AssetIt' in sys.modules: raise ValueError('AssetIt already imported; restart before fresh installation')
    user_library=library(p) if p['library'] is not None else target/'AssetIt_LIBRARY'
    if p['library'] is not None and user_library.is_relative_to(PKG): raise ValueError('Native runtime library must be a separate user copy, never packaged assets')
    return {'target':str(target),'original_expected':str(expected),'native_ui_path_matches':target==expected,'library':str(user_library),'bytes':sum(f.stat().st_size for f in (BUNDLE/'AssetIt').rglob('*') if f.is_file()),'file_undo':False}


def native_plan(p):
    from maya import cmds
    target,expected=installed_target(p)
    if cmds.about(batch=True): raise ValueError('Native UI requires interactive Maya; no standalone QApplication is created')
    if target!=expected or not target.is_dir(): raise ValueError('Original suite requires versioned Maya scripts/AssetIt install path')
    missing=[]
    for name in ('PySide2','shiboken2','pymel','mtoa'):
        try: spec=importlib.util.find_spec(name)
        except (ImportError,ValueError): spec=None
        if spec is None: missing.append(name)
    if missing: raise ValueError('Original native UI dependencies missing: '+', '.join(missing))
    rows=bounded_json(PKG/'catalog.json')['files']
    for row in rows:
        if row['path'].startswith('AssetIt/') and row['path'].endswith('.py'):
            code=target/Path(row['path']).relative_to('AssetIt')
            if not code.is_file() or hashlib.sha256(code.read_bytes()).hexdigest()!=row['sha256']: raise ValueError('Installed native code differs from bundled source: '+str(code))
    preference=bounded_json(target/'Preferences/UserLibPath.json')
    if not Path(preference.get('USER_LIB_PATH','')).is_dir(): raise ValueError('Installed UserLibPath points to missing library')
    collisions=cmds.ls('AssetIt_Thumb_*','AssetI_ThumbScene_*',long=True) or []
    if collisions: raise ValueError('Native fixed-name thumbnail cleanup would collide with existing scene nodes; use fresh backup test scene')
    existing=sys.modules.get('AssetIt')
    if existing is not None and Path(existing.__file__).resolve().parent!=target: raise ValueError('Another AssetIt package already loaded; restart Maya')
    return {'target':str(target),'library':preference['USER_LIB_PATH'],'native_effects':'Full original UI retains scene/file/preferences/render/tool and recursive-delete effects; those callbacks are not adapter transactions','legacy_gui_acceptance':False}


def identities():
    from maya import cmds
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or []}


def execute_import(p):
    from maya import cmds
    path=Path(__file__).with_name('asset_import_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbAssetItImport' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path: raise ValueError('Import command owned by another package; restart before using this candidate')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    result=cmds.mtbAssetItImport(json.dumps(p))
    if isinstance(result,list) and len(result)==1: result=result[0]
    return json.loads(result)


def import_native(p):
    from maya import cmds
    data=asset_path(p); selected=cmds.ls(selection=True,long=True) or []; current=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
    before=identities(); namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True)
    try:
        if auto: cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        created=cmds.file(data['asset'],i=True,namespace=p['namespace'],mergeNamespacesOnClash=False,returnNewNodes=True,executeScriptNodes=False,removeDuplicateNetworks=False)
        roots=[n for n in (cmds.ls(created,long=True,type='transform') or []) if not cmds.listRelatives(n,parent=True,fullPath=True)]
        if not roots: raise RuntimeError('Asset contains no root transform')
        group=cmds.group(empty=True,name=p['namespace']+':AssetIt_Ctrl')
        cmds.parent(roots,group); cmds.setAttr(group+'.scale',p['scale'],p['scale'],p['scale'])
        data.update(namespace=p['namespace'],group=cmds.ls(group,long=True)[0],created=cmds.ls(created,long=True) or [],created_uuids=sorted(identities()-before),scale=p['scale'])
        return data
    except Exception:
        created=identities()-before; nodes=[n for identity in created for n in cmds.ls(identity,long=True) or []]
        if nodes: cmds.delete(nodes)
        if cmds.namespace(exists=p['namespace']): cmds.namespace(removeNamespace=p['namespace'])
        raise
    finally:
        cmds.namespace(setNamespace=namespace)
        if cmds.currentTime(query=True)!=current: cmds.currentTime(current)
        if (cmds.ls(selection=True,long=True) or [])!=selected: cmds.select(selected,replace=True) if selected else cmds.select(clear=True)
        if cmds.autoKeyframe(query=True,state=True)!=auto: cmds.autoKeyframe(state=auto)


class AssetItTool(BaseMayaTool):
    tool_id='asset_it_v1_2'; tool_name='AssetIt 1.2 资源套件'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Preserved licensed AssetIt complete native suite and resource library with separate bounded inventory/metadata/import/fresh-install integration.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inventory','metadata','import_asset','install','launch_native'],'default':'inventory'},
        'library':{'type':'string','description':'Absolute library directory; default bundled library'},
        'asset':{'type':'string','description':'Relative .ma strictly under library'},'namespace':{'type':'string','pattern':'^[A-Za-z_][A-Za-z0-9_]*$'},
        'scale':{'type':'number','exclusiveMinimum':0,'maximum':1e6,'default':1},
        'target_dir':{'type':'string','description':'Fresh standalone AssetIt copy; native UI requires original versioned user scripts path'}}}

    def validate(self,**values):
        try:
            p=normalize(values)
            if p['action']=='inventory': data=inventory(p)
            elif p['action'] in ('metadata','import_asset'):
                data=asset_path(p)
                if p['action']=='import_asset':
                    from maya import cmds
                    if cmds.namespace(exists=':'+p['namespace']): raise ValueError('Import namespace already exists')
                    if not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Maya Undo before importing')
                    data.update(namespace=p['namespace'],scale=p['scale'])
            elif p['action']=='install': data=install_plan(p)
            else: data=native_plan(p)
            return ToolResult.ok(message='AssetIt preflight passed',data=data)
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**values):
        p=normalize(values)
        if p['action']=='inventory': return ToolResult.ok(message='Library inventoried without importing native suite',data=inventory(p))
        if p['action']=='metadata': return ToolResult.ok(message='Asset metadata read',data=asset_path(p))
        if p['action']=='install':
            plan=install_plan(p); target=Path(plan['target'])
            shutil.copytree(BUNDLE/'AssetIt',target,copy_function=shutil.copyfile)
            # Runtime user configuration, original bundled code/preferences remain byte-identical.
            with (target/'Preferences/UserLibPath.json').open('w',encoding='utf8') as stream: json.dump({'USER_LIB_PATH':plan['library']},stream)
            return ToolResult.ok(message='Fresh copy installed; no existing install/shelf replaced, external files not Undoable',data=plan)
        from maya import cmds
        if p['action']=='launch_native':
            plan=native_plan(p); parent=str(Path(plan['target']).parent)
            if parent not in sys.path: sys.path.insert(0,parent)
            native=importlib.import_module('AssetIt.AssetIt_UI'); native.showUI()
            return ToolResult.ok(message='Original full native suite launched; deferred legacy callbacks retain original effects',data=plan)
        return ToolResult.ok(message='Asset imported with owned node Undo/Redo; script nodes disabled',data=execute_import(p))

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        title='mtbAssetItAdapter'
        if cmds.window(title,exists=True): cmds.deleteUI(title)
        cmds.window(title,title='AssetIt 原套件适配',widthHeight=(540,220)); cmds.columnLayout(adjustableColumn=True)
        data=self.run(action='inventory'); count=data.data.get('count',0)
        cmds.text(label='完整原版225函数 / '+str(count)+'模型；原代码保持字节完整',height=30)
        cmds.text(label='原窗口需要原版本scripts安装目录、PySide2、PyMel和Arnold。')
        cmds.text(label='原界面包含文件删除/重命名、渲染和偏好写入；使用备份库验收。',height=30)
        def call(action):
            result=self.run(action=action); print(result.to_dict())
            if not result.success: cmds.warning(result.message)
        cmds.button(label='只读资源清单',command=lambda unused:call('inventory'))
        cmds.button(label='预检原版启动条件',command=lambda unused:print(self.run(action='launch_native',dry_run=True).to_dict()))
        cmds.button(label='复制到新的原版安装目录（已有目录拒绝）',command=lambda unused:call('install'))
        cmds.button(label='打开完整原版界面',command=lambda unused:call('launch_native'))
        cmds.showWindow(title); return title
