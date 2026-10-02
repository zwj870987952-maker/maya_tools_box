"""Owned native UI/filter nodes; real Maya and explicit desktop preview separate."""
from pathlib import Path
import importlib,json,sys
from . import config_io
ROOT=Path(__file__).parent;NATIVE=ROOT/'native';config_path=None;window=None;preview=False;allow_custom_scripts=False;owned_filters={};owned_editors={};owned_workspace=None;option_snapshot={};option_installed={};closing=False
def configure(value,desktop=False,allow_custom=False):
    global config_path,preview,allow_custom_scripts
    p=config_io.path(value)
    if config_path is not None and p!=config_path:raise RuntimeError('Configuration fixed for this Qt/Maya session; use fresh process for another file')
    if p.exists():config_io.read(p)
    else:
        config_io.output(str(p));config_io.write(str(p),config_io.read(NATIVE/'ks_nodeOutliner/ksNodeOutliner_filterData.json'))
    old=sys.modules.get('ks_nodeOutliner')
    if old is not None and ROOT.resolve() not in Path(getattr(old,'__file__','')).resolve().parents:raise RuntimeError('Foreign ks_nodeOutliner already loaded; use fresh Maya session')
    if str(NATIVE) not in sys.path:sys.path.insert(0,str(NATIVE))
    config_path=p;preview=desktop;allow_custom_scripts=allow_custom
    package=importlib.import_module('ks_nodeOutliner');package._CONFIG_USER_=str(p)
    return package
def native_lib():return importlib.import_module('ks_nodeOutliner.lib.libDesktop' if preview else 'ks_nodeOutliner.lib.libMaya')
def native_outliner():return importlib.import_module('ks_nodeOutliner.lib.outlinerDesktop' if preview else 'ks_nodeOutliner.lib.outlinerMaya')
def option_get(key):
    from maya import cmds
    key='MTB_'+key
    return cmds.optionVar(q=key) if cmds.optionVar(exists=key) else None
def option_set(key,value):
    from maya import cmds
    key='MTB_'+key
    if key not in option_snapshot:option_snapshot[key]=(cmds.optionVar(exists=key),cmds.optionVar(q=key) if cmds.optionVar(exists=key) else None)
    if value is None:value=''
    if not isinstance(value,str):raise ValueError('Native UI settings must be strings')
    cmds.optionVar(sv=(key,value));option_installed[key]=value
def restore_options():
    from maya import cmds
    for key,(exists,value) in option_snapshot.items():
        if cmds.optionVar(exists=key) and cmds.optionVar(q=key)!=option_installed.get(key):raise RuntimeError('Foreign optionVar edit; preserve '+key)
        if not exists:
            if cmds.optionVar(exists=key):cmds.optionVar(remove=key)
        else:
            flag='sv' if isinstance(value,str) else 'iv' if type(value) is int else 'fv';cmds.optionVar(**{flag:(key,value)})
    option_snapshot.clear();option_installed.clear()
class MayaCmds:
    def __getattr__(self,name):
        from maya import cmds
        fn=getattr(cmds,name)
        def call(*args,**kw):
            if name=='outlinerEditor' and args and args[0] in ('nodeOutlinerA','nodeOutlinerB'):args=('MTB_KS_'+args[0],)+args[1:]
            if name=='delete':
                values=list(args[0]) if args and isinstance(args[0],(list,tuple)) else list(args)
                if not values:raise ValueError('Empty filter deletion refused')
                for value in values:
                    actual=(cmds.ls(value,uuid=True) or [None])[0]
                    if value not in owned_filters or actual!=owned_filters[value]:raise ValueError('Foreign itemFilter deletion refused')
            if name=='deleteUI':
                if args and args[0] in ('nodeOutlinerA','nodeOutlinerB'):args=('MTB_KS_'+args[0],)+args[1:]
                if not args or args[0] not in owned_editors:raise ValueError('Foreign Outliner/UI deletion refused')
                from maya import OpenMayaUI
                if int(OpenMayaUI.MQtUtil.findControl(args[0]) or 0)!=owned_editors[args[0]]:raise ValueError('Foreign Outliner replacement refused')
            if name=='outlinerEditor' and not any(kw.get(k,False) for k in ('ex','exists','q','query','e','edit')):
                if not args or cmds.outlinerEditor(args[0],exists=True):raise ValueError('Existing Outliner name preserved')
            result=fn(*args,**kw)
            if name=='outlinerEditor' and not any(kw.get(k,False) for k in ('ex','exists','q','query','e','edit')):
                from maya import OpenMayaUI
                owned_editors[result]=int(OpenMayaUI.MQtUtil.findControl(result) or 0)
            if name=='deleteUI':owned_editors.pop(args[0],None)
            if name=='itemFilter' and not kw.get('query',kw.get('q',False)) and isinstance(result,str):owned_filters[result]=(cmds.ls(result,uuid=True) or [None])[0]
            if name=='delete':
                for value in values:owned_filters.pop(value,None)
            return result
        return call
cmdshim=MayaCmds()
def script_module(value,reload=False):
    if value.startswith('.'):value='ks_nodeOutliner.SCRIPTFILTERS'+value
    bundled=value=='ks_nodeOutliner.SCRIPTFILTERS.ksMiscFilters'
    if not bundled and not allow_custom_scripts:raise ValueError('Custom script imports require explicit allow_custom_scripts=True')
    module=importlib.import_module(value)
    if reload:
        if not bundled and not allow_custom_scripts:raise ValueError('Custom script reload not authorized')
        module=importlib.reload(module)
    return module
def show(value,parent=None,allow_custom=False):
    global window,owned_workspace
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    from .qt_compat import QtWidgets,QtCore
    app=QtWidgets.QApplication.instance()
    if app is None or QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Existing Maya Qt main thread required')
    configure(value,False,allow_custom);close()
    if cmds.workspaceControl('MTB_KS_NodeOutlinerWorkspaceControl',exists=True):raise RuntimeError('Existing workspace control preserved; close/remove your old candidate dock explicitly')
    from ks_nodeOutliner.ksNodeOutliner import maya_dockableGUI
    try:
        window=maya_dockableGUI(parent=parent);window.setObjectName('MTB_KS_NodeOutliner');window.show(dockable=True,loadImmediately=True)
        from maya import OpenMayaUI
        name='MTB_KS_NodeOutlinerWorkspaceControl';owned_workspace=(name,int(OpenMayaUI.MQtUtil.findControl(name) or 0))
    except Exception:
        close();raise
    return window
def close():
    global window,closing,owned_workspace
    if closing:return
    closing=True
    try:
        owned=window;window=None
        if owned:
            try:owned.close();owned.deleteLater()
            except RuntimeError:pass
        from maya import cmds
        if owned_workspace:
            from maya import OpenMayaUI
            name,pointer=owned_workspace
            if cmds.workspaceControl(name,exists=True):
                if not pointer or int(OpenMayaUI.MQtUtil.findControl(name) or 0)!=pointer:raise RuntimeError('Foreign workspace replacement preserved')
                cmds.deleteUI(name)
            owned_workspace=None
        for name,identity in list(owned_filters.items()):
            if cmds.objExists(name):
                if (cmds.ls(name,uuid=True) or [None])[0]!=identity:raise RuntimeError('Foreign replacement of filter name; preserve '+name)
                cmds.delete(name)
        owned_filters.clear();owned_editors.clear()
        module=sys.modules.get('ks_nodeOutliner.lib.outlinerMaya')
        if module:module._OUTLINERS_.clear()
    finally:closing=False
def native_save(value,data):
    overwrite=config_path is not None and config_io.path(value)==config_path
    return config_io.write(value,data,overwrite)
def nodes(values):
    from maya import cmds
    if not isinstance(values,list) or len(values)>100000:raise ValueError('Explicit node list required')
    result=[]
    for value in values:
        if not isinstance(value,str) or any(c in value for c in '*?[]'):raise ValueError('Exact node names required')
        found=cmds.ls(value,long=True) or []
        if len(found)!=1:raise ValueError('Missing or ambiguous node '+value)
        if found[0] not in result:result.append(found[0])
    return result
def query(types=None,objects=None,search='*',hierarchy=False):
    from maya import cmds
    import fnmatch
    if objects is not None:values=nodes(objects)
    else:values=cmds.ls(long=True) or []
    if hierarchy:
        for obj in list(values):values.extend(cmds.listRelatives(obj,allDescendents=True,fullPath=True) or [])
    if types:values=[n for n in values if cmds.nodeType(n) in types]
    return sorted(set(n for n in values if fnmatch.fnmatchcase(n,search) or fnmatch.fnmatchcase(n.rsplit('|',1)[-1],search)))
