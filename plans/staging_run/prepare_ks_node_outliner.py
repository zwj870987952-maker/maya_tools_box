"""Complete original double Outliner and filter manager, isolated persistence."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/08_utilities_system/ks_node_outliner_v2_2';SOURCE=UNIT/'KS_NodeOutliner-2.2.0';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/ks_node_outliner_v2_2';NATIVE=PKG/'native/ks_nodeOutliner'
shutil.copytree(SOURCE/'ks_nodeOutliner',NATIVE,dirs_exist_ok=True)
shutil.copyfile(SOURCE/'EULA-KS_NodeOutliner.pdf',PKG/'EULA-KS_NodeOutliner.pdf');shutil.copyfile(SOURCE/'README.md',PKG/'original_README.md')
six=ROOT/'tools_staging_pool/07_subsystems_suites/studiolibrary_patch/release_candidate/maya_toolkit/tools/studiolibrary_patch/vendor/src/studiovendor/six.py';shutil.copyfile(six,PKG/'compat_six.py')
put(PKG/'qt_compat.py',r'''"""Private Qt5/6 facade; never monkeypatch global QtWidgets."""
import types
try:
    from PySide6 import QtCore,QtGui,QtWidgets as _widgets
    import shiboken6 as shiboken
except ImportError:
    from PySide2 import QtCore,QtGui,QtWidgets as _widgets
    import shiboken2 as shiboken
QtWidgets=types.SimpleNamespace(**vars(_widgets))
for name in ('QAction','QShortcut','QUndoCommand','QUndoStack'):
    if not hasattr(QtWidgets,name) and hasattr(QtGui,name):setattr(QtWidgets,name,getattr(QtGui,name))
Signal=QtCore.Signal;wrapInstance=shiboken.wrapInstance
''')
put(PKG/'config_io.py',r'''from pathlib import Path
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
''')
put(PKG/'session.py',r'''"""Owned native UI/filter nodes; real Maya and explicit desktop preview separate."""
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
''')
# Full original code/resources remain native; private imports and known fixes only.
for p in sorted(NATIVE.rglob('*.py')):
    s=p.read_text(encoding='utf-8-sig');s=s.replace('from PySide2 import QtCore, QtGui, QtWidgets','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore,QtGui,QtWidgets').replace('from PySide2 import QtCore','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore').replace('from PySide2.QtCore import Signal','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import Signal').replace('from PySide2 import QtWidgets','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtWidgets')
    s=s.replace('from PySide2.QtWidgets import','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import')
    s=s.replace('from six.moves.configparser import ConfigParser','from configparser import ConfigParser').replace('from six.moves import range','').replace('import six','from maya_toolkit.tools.ks_node_outliner_v2_2 import compat_six as six')
    s=s.replace('from shiboken2 import wrapInstance','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import wrapInstance').replace('import shiboken2','from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import shiboken').replace('shiboken2.','shiboken.').replace('long(','int(').replace('.exec_(','.exec(').replace('QtGui.QPalette.Foreground','QtGui.QPalette.WindowText').replace('omui.MQtUtil_findControl(','omui.MQtUtil.findControl(')
    s=s.replace('from maya import cmds','from maya_toolkit.tools.ks_node_outliner_v2_2.session import cmdshim as cmds').replace('import maya.cmds as cmds','from maya_toolkit.tools.ks_node_outliner_v2_2.session import cmdshim as cmds')
    if p.name=='__init__.py' and p.parent==NATIVE:
        s=s.replace("_SF_ROOTPACKAGE_ = 'ks_nodeOutliner.scriptFilters'","_SF_ROOTPACKAGE_ = 'ks_nodeOutliner.SCRIPTFILTERS'")
    if p.name in ('GUI_NodeOutliner.py','GUI_FilterManager.py'):
        start=s.index('try:\n    from ks_nodeOutliner.lib import libMaya');end=s.index('\n\n',start)
        s=s[:start]+'from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_lib\nlibMaya=native_lib()'+s[end:]
    if p.name=='GUI_NodeOutliner.py':
        s=s.replace('    def buildUI(self):','    def closeEvent(self,event):\n        from maya_toolkit.tools.ks_node_outliner_v2_2 import session\n        if session.window is self:session.close()\n        super().closeEvent(event)\n\n    def buildUI(self):',1)
    if p.name=='GUI_OutlinerContainer.py':
        start=s.index('try:\n    from ks_nodeOutliner.lib import libMaya');end=s.index('\n\n',start)
        s=s[:start]+'from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_lib,native_outliner\nlibMaya=native_lib();outlinerWidget=native_outliner()'+s[end:]
    if p.name=='libMaya.py':
        tree=ast.parse(s);lines=s.splitlines();edits=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef) and n.name in ('getOptionVar','setOptionVar'):
                target='option_get' if n.name=='getOptionVar' else 'option_set';signature='key' if n.name=='getOptionVar' else 'key,value'
                edits.append((n.lineno-1,n.end_lineno,f'def {n.name}({signature}):\n    from maya_toolkit.tools.ks_node_outliner_v2_2.session import {target}\n    return {target}({signature})'))
        for start,end,value in sorted(edits,reverse=True):lines[start:end]=value.splitlines()
        s='\n'.join(lines)+'\n';s=s.replace('    hierarchyNodes = rootSelection','    hierarchyNodes = list(rootSelection)').replace('cmds.ls(relatedNodes, long=False)','cmds.ls(relatedNodes, long=True)')
    if p.name=='libCommon.py':
        tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='getModule');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['def getModule(moduleName,reloadModule=False):','    from maya_toolkit.tools.ks_node_outliner_v2_2.session import script_module','    return script_module(moduleName,reloadModule)'];s='\n'.join(lines)+'\n';s=s.replace('QtGui.QIcon(processIconPath(iconPath))',"QtGui.QIcon(processIconPath(iconPath) or '')")
    if p.name=='config.py':
        # Shiboken6 QObject construction deadlocks with the inherited six/metaclass
        # singleton. Preserve its public callable with one explicit QObject instance.
        s=s.replace('@six.add_metaclass(QtSingletonMetaclass)\nclass configuration(QtCore.QObject):','class _Configuration(QtCore.QObject):').replace('super(configuration, self).__init__()','super(_Configuration, self).__init__()')
        s+='\n_CONFIGURATION_INSTANCE = None\ndef configuration():\n    global _CONFIGURATION_INSTANCE\n    if _CONFIGURATION_INSTANCE is None:_CONFIGURATION_INSTANCE = _Configuration()\n    return _CONFIGURATION_INSTANCE\n'
        tree=ast.parse(s);lines=s.splitlines();edits=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef) and n.name=='readFromJson':edits.append((n.lineno-1,n.end_lineno,'def readFromJson(filePath):\n    from maya_toolkit.tools.ks_node_outliner_v2_2.config_io import read\n    return read(filePath)'))
            if isinstance(n,ast.FunctionDef) and n.name=='writeToJson':edits.append((n.lineno-1,n.end_lineno,'def writeToJson(localData,filePath):\n    from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_save\n    return native_save(filePath,localData)'))
        for start,end,value in sorted(edits,reverse=True):lines[start:end]=value.splitlines()
        s='\n'.join(lines)+'\n'
        s=s.replace('        self._filterNodes_snapshot = copy.deepcopy(self._filterNodes)','        self._filterOrder_snapshot = list(self._filterOrder)\n        self._filterNodes_snapshot = copy.deepcopy(self._filterNodes)').replace('        self._filterNodes = copy.deepcopy(self._filterNodes_snapshot)','        self._filterOrder = list(self._filterOrder_snapshot)\n        self._filterNodes = copy.deepcopy(self._filterNodes_snapshot)')
        s=s.replace('        self._filterNodes[filterName] = node\n        return node','        self._filterNodes[filterName] = node\n        self._filterOrder.append(filterName)\n        return node').replace('        node = self._filterNodes.pop(filterName)','        node = self._filterNodes.pop(filterName)\n        self._filterOrder = [n for n in self._filterOrder if n != filterName]').replace('        node.setFilterName(newName)','        node.setFilterName(newName)\n        self._filterOrder = [newName if n == oldName else n for n in self._filterOrder]')
    if p.name=='outlinerMaya.py':
        s=s.replace('def scriptFilter_makeItemFilter(outlinerName):','def scriptFilter_makeItemFilter(outlinerName):\n    import re\n    if not isinstance(outlinerName,str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",outlinerName):raise ValueError("Invalid Outliner callback identifier")')
        s=s.replace('ks_getOutlinerCustomOutput_','mtb_ks_getOutlinerCustomOutput_').replace('outliner = _OUTLINERS_[outlinerName]','outliner = _OUTLINERS_.get(outlinerName)\n    if outliner is None:return []')
        s=s.replace('for itemFilter in self.itemFilter_trashbin:','for itemFilter in list(self.itemFilter_trashbin):')
    if p.name=='outlinerDesktop.py':
        s=s.replace('def assignFilter(self, filterNode, attributes):','def assignFilter(self, filterNode, attributes=None):').replace('        self.deleteFilterGarbage()','        self.filterGarbage.clear()').replace('        self.activeAttributes = attributes','        self.activeAttributes = attributes or {}').replace("baseFilterAttr = filterNode.getData('baseFilter')","baseFilterAttr = filterNode.getData('baseFilterType')").replace("self.activeScriptCode = filterNode.getData(\"scriptCode\")","self.activeScriptCode = filterNode.getData(\"scriptFunction\")")
    if p.name=='ksNodeOutliner.py':
        s=s.replace("__WORKSPACE_NAME__ = 'ks_nodeOutliner'","__WORKSPACE_NAME__ = 'MTB_KS_NodeOutliner'")
        tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='OpenNodeOutliner');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['def OpenNodeOutliner():','    from maya_toolkit.tools.ks_node_outliner_v2_2 import session','    if session.config_path is None:raise RuntimeError("Select independent config via candidate show_ui first")','    return session.show(str(session.config_path))'];s='\n'.join(lines)+'\n'
    if p.name=='ksMiscFilters.py':
        tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='ks_geometryWithNGons');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]='''def ks_geometryWithNGons(*args):
    from maya.api import OpenMaya
    result=[]
    for node in args[0]:
        candidates=[node] if cmds.nodeType(node)=='mesh' else cmds.listRelatives(node,shapes=True,fullPath=True,type='mesh') or []
        for mesh in candidates:
            selection=OpenMaya.MSelectionList();selection.add(mesh);fn=OpenMaya.MFnMesh(selection.getDagPath(0))
            counts,vertices=fn.getVertices()
            if any(n>4 for n in counts):result.append(node);break
    return list(dict.fromkeys(result))'''.splitlines();s='\n'.join(lines)+'\n'
    put(p,s)
put(PKG/'__init__.py',r'''from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import config_io
from pathlib import Path
class KSNodeOutlinerTool(BaseMayaTool):
    tool_id='ks_node_outliner_v2_2';tool_name='KS Node Outliner 双大纲';category='scene_hygiene';version='1.0.0'
    description='Complete native double Outliner, filter manager/presets/custom output and script filters with owned UI/filter cleanup'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','query_nodes','show_ui','close_ui','set_custom_output','read_config','write_config','restore_ui_settings'],'default':'inspect'},
        'config_path':{'type':'string'},'config_data':{'type':'object'},'overwrite':{'type':'boolean','default':False},
        'objects':{'type':'array','items':{'type':'string'},'maxItems':100000},'node_types':{'type':'array','items':{'type':'string'},'maxItems':512},'search':{'type':'string','default':'*'},
        'include_hierarchy':{'type':'boolean','default':False},'ignore_hierarchy':{'type':'boolean','default':False},'allow_custom_scripts':{'type':'boolean','default':False},'outliner_index':{'type':'integer','enum':[0,1],'default':0}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for k in ('overwrite','include_hierarchy','ignore_hierarchy','allow_custom_scripts'):
                if k in kw and type(kw[k]) is not bool:raise ValueError('Strict boolean '+k)
            if type(kw.get('outliner_index',0)) is not int or kw.get('outliner_index',0) not in (0,1):raise ValueError('Outliner index 0/1')
            if 'search' in kw and (not isinstance(kw['search'],str) or len(kw['search'])>1024):raise ValueError('Invalid search pattern')
            if 'node_types' in kw and (not isinstance(kw['node_types'],list) or len(kw['node_types'])>512 or any(not isinstance(n,str) or not n or len(n)>256 for n in kw['node_types'])):raise ValueError('Invalid node types')
            if action in ('read_config','write_config','show_ui'):
                p=config_io.path(kw.get('config_path'))
                if action=='read_config' or p.exists() and action=='show_ui':config_io.read(str(p))
                else:config_io.output(str(p),kw.get('overwrite',False))
            if action=='write_config':config_io.config(kw.get('config_data'))
            if 'objects' in kw:
                from .session import nodes
                nodes(kw['objects'])
            if action=='set_custom_output' and 'objects' not in kw:raise ValueError('Explicit objects required')
            return ToolResult.ok(message='无副作用预检；未导入Qt/native配置或创建过滤器/窗口')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'default_filters':list(config_io.read(Path(__file__).parent/'native/ks_nodeOutliner/ksNodeOutliner_filterData.json')['FILTERS']),'gui_acceptance':'not_run','complete_original':True})
        if action=='read_config':return ToolResult.ok(data={'config':config_io.read(kw['config_path'])})
        if action=='write_config':return ToolResult.ok(data=config_io.write(kw['config_path'],kw['config_data'],kw.get('overwrite',False)))
        from . import session
        if action=='show_ui':session.show(kw['config_path'],allow_custom=kw.get('allow_custom_scripts',False));return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if action=='restore_ui_settings':session.restore_options();return ToolResult.ok()
        if action=='query_nodes':return ToolResult.ok(data={'nodes':session.query(kw.get('node_types'),kw.get('objects'),kw.get('search','*'),kw.get('include_hierarchy',False))})
        if session.window is None:raise RuntimeError('Open owned Outliner first')
        session.window.allOutliners[kw.get('outliner_index',0)].setFilter_customOutput(session.nodes(kw['objects']),kw.get('ignore_hierarchy',False));return ToolResult.ok(data={'objects':kw['objects']})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=0,caption='KS Outliner：选择独立过滤器配置JSON',fileFilter='JSON (*.json)')
        if not values:return None
        from .session import show
        return show(values[0],parent)
''')
put(RC/'tests/test_ks_node_outliner_v2_2.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.ks_node_outliner_v2_2 import KSNodeOutlinerTool
    tool=KSNodeOutlinerTool()
from maya_toolkit.tools.ks_node_outliner_v2_2 import config_io
class Checks(unittest.TestCase):
    def test_complete_config_pure_preflight_and_exact_backup(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('ks_nodeOutliner',sys.modules)
        defaults=config_io.read(Path(config_io.__file__).parent/'native/ks_nodeOutliner/ksNodeOutliner_filterData.json');self.assertGreaterEqual(len(defaults['FILTERS']),16)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,defaults);original=Path(p).read_bytes()
            with self.assertRaises(ValueError):config_io.write(p,defaults)
            row=config_io.write(p,defaults,True);self.assertEqual(Path(row['backup']).read_bytes(),original)
            bad={'FILTERS':{'x':{'baseFilter':1}}}
            with self.assertRaises(ValueError):config_io.write(str(Path(td)/'bad.json'),bad)
            self.assertFalse((Path(td)/'bad.json').exists())
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_ks_node_outliner_v2_2_maya.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.ks_node_outliner_v2_2 import session
class MayaChecks(unittest.TestCase):
    def test_queries_pure_ngon_and_foreign_filter_guard(self):
        cmds.file(new=True,force=True);parent=cmds.createNode('transform',name='parent');cube=cmds.polyCube(name='cube')[0];cmds.parent(cube,parent);ngon=cmds.polyCreateFacet(p=[(0,0,0),(2,0,0),(3,1,0),(1,3,0),(-1,1,0)],name='ngon')[0];cmds.select(parent);before=cmds.ls(sl=True,long=True);time=cmds.currentTime(q=True)
        result=tool.run(action='query_nodes',objects=[parent],include_hierarchy=True,node_types=['mesh']);self.assertTrue(result.success,result.errors);self.assertEqual(len(result.data['nodes']),1);self.assertEqual(cmds.ls(sl=True,long=True),before)
        with tempfile.TemporaryDirectory() as td:
            session.configure(str(Path(td)/'filters.json'));module=session.script_module('.ksMiscFilters');constraint=cmds.polySelectConstraint(q=True,stateString=True);output=module.ks_geometryWithNGons([cube,ngon]);self.assertEqual(output,[ngon]);self.assertEqual(cmds.ls(sl=True,long=True),before);self.assertEqual(cmds.polySelectConstraint(q=True,stateString=True),constraint);self.assertEqual(cmds.currentTime(q=True),time)
            own=session.cmdshim.itemFilter(byType='mesh',classification='user');foreign=cmds.itemFilter(byType='camera',classification='user')
            with self.assertRaises(ValueError):session.cmdshim.delete(foreign)
            self.assertTrue(cmds.objExists(foreign));session.close();self.assertFalse(cmds.objExists(own));self.assertTrue(cmds.objExists(foreign));cmds.delete(foreign)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_ks_node_outliner_v2_2_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
import faulthandler
faulthandler.dump_traceback_later(20)
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_no',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.ks_node_outliner_v2_2 import session
class QtChecks(unittest.TestCase):
    def test_explicit_desktop_preview_full_qt_manager(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(str(Path(td)/'filters.json'),True);print('config loaded',flush=True)
            from ks_nodeOutliner.lib.GUI_NodeOutliner import GUI_NodeOutliner
            from ks_nodeOutliner.lib.GUI_FilterManager import GUI_FilterManager
            print('native imports done',flush=True)
            win=GUI_NodeOutliner();print('double Outliner constructed',flush=True);self.assertEqual(len(win.allOutliners),2);self.assertEqual(len(win.CONFIG.getFilterNames()),16)
            manager=GUI_FilterManager(win);print('manager constructed',flush=True);self.assertIs(manager.CONFIG,win.CONFIG)
            win.CONFIG.snapshotData();win.CONFIG.filter_rename('Cameras','RenamedCamera');win.CONFIG.filter_delete('Joints');win.CONFIG.saveData();session.config_io.read(str(Path(td)/'filters.json'));win.CONFIG.restoreData();win.CONFIG.saveData()
            manager.close();win.close();manager.deleteLater();win.deleteLater();faulthandler.cancel_dump_traceback_later()
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/ks_node_outliner_v2_2.md','''# KS Node Outliner 2.2 完整候选

18原文件SHA归档，完整双Maya Outliner/FilterManager/菜单与默认preset/搜索/选择过滤器/层级与输入材质相关节点/scriptFilters/customOutput/desktop demo源、配置/license.txt/EULA原封不动保留。不是开源授权推定，只有所给许可原资料；未发布。补私有Qt5/6 facade（QAction/QShortcut迁QtGui，不猴补全局QtWidgets）、Python3 long/裸reload/脚本目录大小写、缺optionVar查询和字符串保存None等确定问题；六兼容库自包含，MIT notice取已核验官方StudioLibrary固定commit的six.py，future运行不依赖另一个staging候选。

Base/Schema/ToolResult/default inspect/validate无Qt/native/窗口/itemFilter/配置写入；query_nodes读scene精确objects/node_types/search/include_hierarchy，返回长路径；show/close_ui、read/write_config、set_custom_output/outliner_index0/1/ignore_hierarchy、restore_ui_settings。真实UI保持完整标准Outliner/所有菜单与管理器；Qt离线preview用原desktop demo只验控件，不假装Maya scene Outliner正常。实时Maya不再try/except任意错误后静默显示demo。Maya主线程/已有Qt/native混用来源检查；一次session固定自有外部config_path，用户选择新JSON显式复制原默认，有效既有JSON直接读；不覆盖包内资源、不能在candidate路径写配置。

FILTERS/FILTERORDER/MENUPRESETS严格类型/引用/512上限/8MiB/重复key/unknown字段/strict bool；全部配置先校验再更改。用户明确Config保存原本selected配置可overwrite并先exclusive精确backup再atomic换文件；导出到已有其他路径拒绝，API overwrite=True明确允许同样备份。config/UI settings写入不可Maya Undo，QtSingleton保存原接口，过滤器编辑/导入/导出/临时snapshot-restore/menu preset完整。原大纲key名nodeOutlinerA/B在preset保持，实际Maya editor与workspace加MTB_KS_命名；删除只自有itemFilter名字+UUID，close清自有filters和map，不删foreign/builtin filters或Outliner。

脚本MEL回调专用mtb_ks前缀，关闭getter空list，不改外来proc；原ScriptFilter模块/函数/逗号args行为保留， bundled.ksMiscFilters默认允许，外部自定义module必须明确allow_custom_scripts=True才导入/reload，GUI/脚本选择可运行用户代码，不声称预检能证明任意自定义函数只读。原NGon脚本改变selection/polySelectConstraint的确定副作用改为MFnMesh.getVertices只读拓扑，返回原输入中有NGon的对象；不改selection、约束状态、时间，完整过滤结果用于原界面。原ks_vertexCount本来就是passthrough占位，保留并明确未声称它做实际阈值统计。libMaya.getRelatedNodes拷贝输入list不原地扩展，返回长名保留重名区分；原完整UI原有短名显示限制仍需真实重名场景验收。

UI optionVars使用MTB_前缀、读不存在None；仅点击Set as Default UI持久写，首状态记录，restore_ui_settings恢复不存在/原值；外来后来改同key拒绝恢复而保留它，不改旧ks偏好。不自动注册startup/安装插件/userSetup。标准scene清理/查询可衔接其他工具，静态import不证明生产组合。离线配置/精确备份/未来注册/domain/panel，隔离Maya只读层级查询/NGon真实拓扑/selection约束时间不变/self filter清理与foreign保护，独立Qt全双desktop preview及FilterManager构造；真实Maya嵌入Outliner/过滤器UI/preset/custom scripts/恢复dock/复杂重名与跨版本not_run，验收前留池。
''')
with (RC/'docs/tools/ks_node_outliner_v2_2.md').open('a',encoding='utf8') as f:f.write('\n离线实测修复：原JSON合法的description/hierarchyBehavior/updateSelectionFilter历史字段按string/bool保留；Qt6 QObject与six多重metaclass原singleton构造卡死，改为显式单一QObject实例的同名configuration()工厂，保持共享signal/config接口；原desktop demo过期assignFilter签名更新，仅用于预览。增删改名及snapshot恢复同步FILTERORDER，保存后严格校验通过。workspaceControl和Outliner editor按创建时MQt指针记录，外来同名替代拒绝删除；原公开OpenNodeOutliner走同一自有session入口，关闭X同样清自有过滤器/回调；完整真实dock生命周期仍需直验。\n')
put(RC/'acceptance.md','''# KS Node Outliner Maya直验 not_run

1. 新Maya选择独立有效或新JSON，完整双真实Outliner/Qt过滤器管理/搜索/层级/selection filter/local-global/材质与输入/预设菜单/customOutput，Maya资源图标与快捷F实际正确。Qt desktop demo只验证控件，不能作为Maya pass。foreign旧ks模块需要新会话，native错误不静默退demo。
2. 默认过滤/NGon只读拓扑，选择/时间/polySelectConstraint不变；原ks_vertexCount本来passthrough不登记阈值统计成功。长名query/重名scene/生产引用/自定义scripts返回节点都核验；外部脚本明确allow_custom_scripts才import/reload，不在无人值守整理时跑未知用户module。
3. FILTERS/FILTERORDER/presets完整编辑/import/export/snapshot/restore，坏最后项不更新；当前config保存先backup后atomic，包内资源不可写，其他已有导出名拒绝，API显式overwrite精确备份。UI optionVar仅自有前缀，默认设置保存和restore/foreign后来修改保护；外部JSON不能scene Undo。
4. close/reopen只清自有UUID itemFilter/editor/map、MEL回调空输出，无foreign/builtin node/filter删除；workspace恢复dock/关闭FilterManager生命周期与跨Maya版本实际验收。记录candidate_sha256/accepted_by/date/maya_version/passed=true后再promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/ks_node_outliner_v2_2','--class-name','KSNodeOutlinerTool','--summary','Complete original double Outliner/filter manager with scoped config backups, Qt5/6 facade and owned filter cleanup','--dependencies','Maya real Outliner/Qt widgets and cmds/API','Bundled six MIT notice; original license/EULA retained','--limitations','Real Maya GUI embedding/dock/full presets/custom scripts/ambiguous short-name display/cross-version acceptance not_run; original vertex-count function is passthrough placeholder'],check=True)
