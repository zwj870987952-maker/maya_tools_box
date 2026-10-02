"""Complete native smart assistant with explicit reversible session hooks."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/smart_assistant';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/smart_assistant';NATIVE=PKG/'native'
for src in UNIT.rglob('*'):
    if not src.is_file() or 'release_candidate' in src.relative_to(UNIT).parts or '__pycache__' in src.parts or src.name=='.gitattributes':continue
    target=NATIVE/src.relative_to(UNIT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
put(PKG/'config_io.py',r'''"""Five supplied optionVar keys; literal config and deterministic sequence parsing."""
from pathlib import Path
import json,math,re
KEYS={'workingUnitLinear':str,'workingUnitTime':str,'gridSize':float,'gridSpacing':float,'gridDivisions':int}
FILES={'.ma','.mb','.fbx','.obj','.abc'}
IMAGES={'.png','.jpg','.jpeg','.bmp'}
def prefs(values):
    if not isinstance(values,dict) or set(values)-set(KEYS):raise ValueError('Only original five preference keys accepted')
    result={}
    for key,value in values.items():
        typ=KEYS[key]
        if typ is str:
            if not isinstance(value,str) or not value or len(value)>128:raise ValueError('Unit optionVar must be a nonempty string')
        elif typ is int:
            if type(value) not in (int,float) or not math.isfinite(value) or value!=int(value) or not 1<=value<=10000:raise ValueError('Grid divisions must be a positive integral number (Maya may store float)')
        elif type(value) not in (int,float) or not math.isfinite(value) or value<=0 or value>1000000:raise ValueError('Positive finite grid value required')
        result[key]=value
    return result
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or p.is_symlink():raise ValueError('Absolute non-symlink path required')
    return p
def read_prefs(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>1024*1024:raise ValueError('Config absent or exceeds 1 MiB')
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise ValueError('Duplicate config key')
            d[k]=v
        return d
    return prefs(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def output_path(value):
    p=path(value)
    if not p.parent.is_dir() or p.exists() or p.suffix.lower()!='.json':raise ValueError('New JSON file with existing parent required')
    return p
def write_prefs(value,values):
    p=output_path(value);values=prefs(values)
    with p.open('x',encoding='utf8') as f:json.dump(values,f,ensure_ascii=False,allow_nan=False,indent=2)
    return str(p)
def sequence(folder):
    p=path(folder)
    if not p.is_dir():raise ValueError('Sequence folder absent')
    groups={}
    for child in sorted(p.iterdir()):
        if not child.is_file() or child.suffix.lower() not in IMAGES:continue
        match=re.fullmatch(r'(.*?)(\d+)',child.stem)
        if match:groups.setdefault((match[1],len(match[2]),child.suffix.lower()),[]).append((int(match[2]),child))
    groups={k:sorted(v) for k,v in groups.items() if len(v)>=2}
    if len(groups)!=1:raise ValueError('Exactly one numbered image sequence (at least two frames) required')
    key,values=next(iter(groups.items()));frames=[i for i,p in values]
    if len(frames)>10000 or len(set(frames))!=len(frames) or frames!=list(range(frames[0],frames[-1]+1)):raise ValueError('Sequence must have unique contiguous frames, maximum 10000')
    return {'folder':str(p),'first_image':str(values[0][1]),'first_frame':frames[0],'last_frame':frames[-1],'count':len(frames),'prefix':key[0],'padding':key[1]}
''')
put(PKG/'session.py',r'''"""Explicit typed optionVar changes and reversible Python fileDialog2 patch."""
from pathlib import Path
from . import config_io
patch=None;original=None;preference_snapshot=None
def capture_prefs():
    from maya import cmds
    result={}
    for key in config_io.KEYS:
        if cmds.optionVar(exists=key):result[key]=cmds.optionVar(query=key)
    return config_io.prefs(result)
def apply_prefs(values):
    global preference_snapshot
    from maya import cmds
    values=config_io.prefs(values)
    before={k:{'exists':cmds.optionVar(exists=k),'value':cmds.optionVar(query=k) if cmds.optionVar(exists=k) else None} for k in values}
    # Keep the first pre-session value for every changed key, including keys
    # added by later apply calls. Failure rolls back this call's own full set.
    saved=preference_snapshot or {}
    for key,row in before.items():saved.setdefault(key,row)
    try:
        for key,value in values.items():
            flag='stringValue' if type(value) is str else 'intValue' if type(value) is int else 'floatValue'
            cmds.optionVar(**{flag:(key,value)})
    except Exception:
        _restore(before);raise
    preference_snapshot=saved
    return {'applied':values,'undo':'optionVars require restore_prefs; no scene Undo'}
def _restore(values):
    from maya import cmds
    for key,row in values.items():
        if not row['exists']:
            if cmds.optionVar(exists=key):cmds.optionVar(remove=key)
        else:
            v=row['value'];flag='stringValue' if type(v) is str else 'intValue' if type(v) is int else 'floatValue'
            cmds.optionVar(**{flag:(key,v)})
def restore_prefs():
    global preference_snapshot
    if preference_snapshot:_restore(preference_snapshot)
    preference_snapshot=None
def patch_dialog():
    global patch,original
    from maya import cmds
    if patch is not None:
        if cmds.fileDialog2 is not patch:raise RuntimeError('Another tool changed fileDialog2; refusing to stack hooks')
        return
    original=cmds.fileDialog2
    def wrapper(*args,**kwargs):
        current=cmds.file(query=True,sceneName=True)
        if 'startingDirectory' not in kwargs and 'dir' not in kwargs and current and Path(current).parent.is_dir():kwargs['startingDirectory']=str(Path(current).parent)
        return original(*args,**kwargs)
    patch=wrapper;cmds.fileDialog2=patch
def restore_dialog():
    global patch,original
    from maya import cmds
    if patch is not None:
        if cmds.fileDialog2 is not patch:raise RuntimeError('Foreign fileDialog2 wrapper installed later; restore that wrapper first')
        cmds.fileDialog2=original
    patch=None;original=None
def state():
    from .native.dragdrop import dragdrop_handler
    return {'dialog_patch_owned':patch is not None,'dragdrop_enabled':dragdrop_handler._filter is not None,
            'prefs_restore_available':bool(preference_snapshot)}
''')
put(PKG/'operations.py',r'''"""Whole-input validation before original file/sequence operations."""
import re
from . import config_io
def plan_files(paths,mode,namespace='',confirm_replace_scene=False):
    from maya import cmds
    if mode not in ('open','import','reference'):raise ValueError('Unknown file mode')
    if not isinstance(paths,list) or not paths or len(paths)>64 or any(not isinstance(p,str) for p in paths) or len(set(paths))!=len(paths):raise ValueError('1-64 unique absolute files required')
    resolved=[]
    for value in paths:
        p=config_io.path(value)
        if not p.is_file() or p.suffix.lower() not in config_io.FILES:raise ValueError('Unsupported/absent source: '+value)
        if str(p.resolve()).casefold() in {r.casefold() for r in resolved}:raise ValueError('Duplicate resolved input')
        resolved.append(str(p.resolve()))
    if not isinstance(namespace,str) or namespace and not re.fullmatch(r'[A-Za-z_]\w*(?::[A-Za-z_]\w*)*',namespace):raise ValueError('Namespace must contain valid identifiers')
    if mode=='open':
        if len(resolved)!=1 or not confirm_replace_scene:raise ValueError('Open requires exactly one file and confirm_replace_scene=True')
        if cmds.file(query=True,modified=True):raise ValueError('Save the current dirty scene before opening another file')
    spaces=[]
    if mode=='reference':
        if not namespace:raise ValueError('Explicit reference namespace required')
        for index in range(len(resolved)):
            ns=namespace if len(resolved)==1 else namespace+'_'+str(index+1)
            if cmds.namespace(exists=ns):raise ValueError('Reference namespace already exists: '+ns)
            spaces.append(ns)
    return {'paths':resolved,'mode':mode,'namespaces':spaces,'scene_replace_undo':False,'script_nodes':False}
def execute_files(plan):
    from maya import cmds
    from maya_toolkit.core.context import UndoChunkContext
    if plan['mode']=='open':
        cmds.file(plan['paths'][0],open=True,force=False,executeScriptNodes=False)
        return {'opened':plan['paths'][0],'scene_replace_undo':False}
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo before import/reference')
    created=[]
    with UndoChunkContext('Smart Assistant '+plan['mode']):
        for index,p in enumerate(plan['paths']):
            if plan['mode']=='reference':created.extend(cmds.file(p,reference=True,namespace=plan['namespaces'][index],returnNewNodes=True,executeScriptNodes=False) or [])
            else:created.extend(cmds.file(p,i=True,ignoreVersion=True,renameAll=True,mergeNamespacesOnClash=False,preserveReferences=True,returnNewNodes=True,executeScriptNodes=False) or [])
    return {'created_nodes':created,'paths':plan['paths'],'mode':plan['mode'],'file_reference_undo':'Requires real Maya verification; no file rollback'}
def create_sequence(info,open_view=False):
    from maya import cmds
    from maya_toolkit.core.context import UndoChunkContext
    if open_view and cmds.about(batch=True):raise ValueError('Real Maya GUI needed for camera view')
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
    before=cmds.ls(selection=True,long=True) or []
    with UndoChunkContext('Smart Assistant camera sequence'):
        try:
            camera,shape=cmds.camera(name='MTB_sa_bg_cam')
            plane,plane_shape=cmds.imagePlane(camera=camera,showInAllViews=True,width=10,height=10)
            cmds.setAttr(plane_shape+'.imageName',info['first_image'],type='string')
            cmds.setAttr(plane_shape+'.useFrameExtension',1);cmds.setAttr(plane_shape+'.displayOnlyIfCurrent',1)
            cmds.setAttr(camera+'.visibility',0)
            # Explicit, inspectable frame linkage rather than relying on a UI checkbox.
            connections=cmds.listConnections(plane_shape+'.frameExtension',source=True,destination=False,plugs=True) or []
            if len(connections)>1:raise RuntimeError('Unexpected imagePlane frame linkage')
            driver=connections[0] if connections else cmds.expression(name='MTB_sa_sequenceFrame',string=plane_shape+'.frameExtension = frame;',alwaysEvaluate=True,unitConversion='none')
        finally:cmds.select([n for n in before if cmds.objExists(n)],replace=True)
    view=None
    if open_view:
        from .native.main import camera_view
        view=camera_view(camera)
    return {'camera':camera,'camera_shape':shape,'image_plane':plane,'image_plane_shape':plane_shape,'frame_driver':driver,'view':view,**info}
''')
put(NATIVE/'utils/path_utils.py','''from ...config_io import sequence
def is_image_sequence_folder(path):
    try:sequence(path);return True
    except (ValueError,OSError):return False
''')
put(NATIVE/'config/prefs_manager.py','''from ... import session,config_io
def export_prefs(path=None):
    from maya import cmds
    if path is None:
        chosen=cmds.fileDialog2(fileMode=0,fileFilter='JSON (*.json)',caption='Export to new config file')
        if not chosen:return None
        path=chosen[0]
    return config_io.write_prefs(path,session.capture_prefs())
def apply_prefs(path=None):
    from maya import cmds
    if path is None:
        chosen=cmds.fileDialog2(fileMode=1,fileFilter='JSON (*.json)',caption='Apply saved preference optionVars')
        if not chosen:return None
        path=chosen[0]
    return session.apply_prefs(config_io.read_prefs(path))
''')
put(NATIVE/'file_dialog_patch/patch_file_dialog.py','''from ...session import patch_dialog,restore_dialog
def patch_file_dialog():return patch_dialog()
def restore_file_dialog():return restore_dialog()
''')
put(NATIVE/'dragdrop/camera_imageplane.py','''from ...config_io import sequence
from ...operations import create_sequence
def create_camera_with_sequence(folder_path):return create_sequence(sequence(folder_path),open_view=True)
''')
put(NATIVE/'dragdrop/dragdrop_handler.py',r'''"""Owned QObject filter retained until explicit stop; Qt6/Qt5 supported."""
_filter=None
def _qt():
    try:
        from PySide6 import QtWidgets,QtCore
        from shiboken6 import wrapInstance
    except ImportError:
        from PySide2 import QtWidgets,QtCore
        from shiboken2 import wrapInstance
    return QtWidgets,QtCore,wrapInstance
def start_dragdrop_monitor():
    global _filter
    if _filter is not None:return
    from maya import cmds,OpenMayaUI
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    QtWidgets,QtCore,wrapInstance=_qt();app=QtWidgets.QApplication.instance()
    ptr=OpenMayaUI.MQtUtil.mainWindow()
    if app is None or not ptr:raise RuntimeError('Maya main window unavailable')
    if QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Maya main thread required')
    main=wrapInstance(int(ptr),QtWidgets.QWidget)
    _filter=make_filter(main,app)
    app.installEventFilter(_filter)
def stop_dragdrop_monitor():
    global _filter
    if _filter is None:return
    QtWidgets,_,_=_qt();app=QtWidgets.QApplication.instance()
    if app:app.removeEventFilter(_filter)
    _filter.deleteLater();_filter=None
def supported(paths):
    from pathlib import Path
    from ...config_io import FILES,sequence
    if not paths:return False
    if len(paths)==1 and Path(paths[0]).is_dir():
        try:sequence(paths[0]);return True
        except (ValueError,OSError):return False
    return all(Path(p).is_file() and Path(p).suffix.lower() in FILES for p in paths)
def make_filter(main,parent=None):
    QtWidgets,QtCore,_=_qt()
    class DragDropEventFilter(QtCore.QObject):
        def eventFilter(self,obj,event):
            if not isinstance(obj,QtWidgets.QWidget) or not (obj is main or main.isAncestorOf(obj)):return False
            if event.type() not in (QtCore.QEvent.Drop,QtCore.QEvent.DragEnter,QtCore.QEvent.DragMove):return False
            mime=event.mimeData()
            if not mime.hasUrls():return False
            paths=[url.toLocalFile() for url in mime.urls()]
            if not supported(paths):return False
            if event.type()==QtCore.QEvent.Drop:
                from .file_actions import handle_drop
                try:handle_drop(paths)
                except Exception as e:
                    from maya import cmds
                    cmds.warning(str(e))
            event.acceptProposedAction();return True
    return DragDropEventFilter(parent)
''')
put(NATIVE/'dragdrop/file_actions.py',r'''"""Cancel-preserving dispatch for every supplied supported drop file."""
from pathlib import Path
from ..dialogs import choose_action_dialog,namespace_dialog
from . import camera_imageplane
from ... import operations
def handle_drop(paths):
    from maya import cmds
    if not paths:return None
    if len(paths)==1 and Path(paths[0]).is_dir():return camera_imageplane.create_camera_with_sequence(paths[0])
    action=choose_action_dialog.ask_action()
    if action is None:return None
    namespace=''
    if action=='reference':
        namespace=namespace_dialog.get_namespace()
        if namespace is None:return None
    confirm=False
    if action=='open':
        confirm=cmds.confirmDialog(title='打开替换当前场景',message='打开不能通过 Undo 撤回。先保存当前场景，使用备份文件验收。',button=['打开','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')=='打开'
        if not confirm:return None
    plan=operations.plan_files(paths,action,namespace,confirm)
    return operations.execute_files(plan)
''')
p=NATIVE/'dialogs/namespace_dialog.py';s=p.read_text(encoding='utf8').replace("return ''","return None");put(p,s)
put(NATIVE/'main.py',r'''"""Full preference/drop/dialog feature controls; explicit session activation."""
owned_window=None;views=[]
NAME='MTB_SmartAssistant';TAG='maya_toolkit.smart_assistant'
def _call(fn,*args,**kwargs):
    from maya import cmds
    try:return fn(*args,**kwargs)
    except Exception as e:cmds.warning(str(e))
def launch():
    from ... import SmartAssistantTool
    return SmartAssistantTool().run(action='enable')
def show_main_window():
    global owned_window
    from maya import cmds
    from ... import session
    from .config import prefs_manager
    from .dragdrop import dragdrop_handler
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    if cmds.window(NAME,exists=True):
        if owned_window!=NAME or cmds.window(NAME,query=True,docTag=True)!=TAG:raise RuntimeError('Foreign window name collision')
        cmds.showWindow(NAME);return NAME
    window=cmds.window(NAME,title='Maya Smart Assistant',widthHeight=(330,270),docTag=TAG);owned_window=window
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='原五项 optionVar；启用监听和路径补丁为会话行为')
    cmds.button(label='导出当前首选项（新 JSON）',command=lambda *_:_call(prefs_manager.export_prefs))
    cmds.button(label='加载并应用首选项',command=lambda *_:_call(prefs_manager.apply_prefs))
    cmds.button(label='恢复本会话应用前首选项',command=lambda *_:_call(session.restore_prefs))
    cmds.button(label='开启拖拽监听',command=lambda *_:_call(dragdrop_handler.start_dragdrop_monitor))
    cmds.button(label='停止拖拽监听',command=lambda *_:_call(dragdrop_handler.stop_dragdrop_monitor))
    cmds.button(label='启用 Python 文件对话框当前场景路径',command=lambda *_:_call(session.patch_dialog))
    cmds.button(label='恢复文件对话框',command=lambda *_:_call(session.restore_dialog))
    cmds.button(label='关闭界面',command=lambda *_:close_ui())
    cmds.showWindow(window);return window
def close_ui():
    global owned_window
    from maya import cmds
    if owned_window and cmds.window(owned_window,exists=True):
        if cmds.window(owned_window,query=True,docTag=True)!=TAG:raise RuntimeError('Window ownership changed')
        cmds.deleteUI(owned_window,window=True)
    owned_window=None
def camera_view(camera):
    from maya import cmds
    window=cmds.window(title='Smart Assistant sequence camera')
    pane=cmds.paneLayout(parent=window);panel=cmds.modelPanel(parent=pane,camera=camera)
    cmds.modelEditor(panel,edit=True,allObjects=False,imagePlane=True,grid=False)
    views.append(window);cmds.showWindow(window);return window
''')
put(PKG/'__init__.py',r'''"""Full assistant suite contract, with zero global hooks on import/UI launch."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import config_io,session,operations
class SmartAssistantTool(BaseMayaTool):
    tool_id='smart_assistant';tool_name='Maya Smart Assistant';category='pipeline_io';version='1.0.0'
    description='五项偏好typed保存/应用/恢复，完整文件拖拽与图片序列相机，显式可撤销会话监听/Python文件对话框补丁'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','enable','disable','start_monitor','stop_monitor','patch_dialog','restore_dialog','capture_prefs','save_prefs','read_prefs','apply_prefs','restore_prefs','open_scene','import_file','reference_file','create_sequence_camera'],'default':'inspect'},
        'path':{'type':'string','description':'绝对JSON路径或序列目录'},'paths':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':64,'uniqueItems':True},
        'preferences':{'type':'object','description':'只允许原五项typed optionVar'},'namespace':{'type':'string','default':''},
        'confirm_replace_scene':{'type':'boolean','default':False},'open_view':{'type':'boolean','default':False}},'required':[]}
    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown argument')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Unknown action')
        for key in ('confirm_replace_scene','open_view'):
            if type(kwargs.get(key,False)) is not bool:raise ValueError('Strict boolean required')
        p={'action':action}
        if action=='inspect':return p
        if action in ('read_prefs','apply_prefs'):
            values=config_io.prefs(kwargs['preferences']) if 'preferences' in kwargs else config_io.read_prefs(kwargs.get('path'))
            return {**p,'preferences':values,'scene_undo':False}
        if action=='save_prefs':
            values=config_io.prefs(kwargs['preferences']) if 'preferences' in kwargs else session.capture_prefs()
            return {**p,'preferences':values,'path':str(config_io.output_path(kwargs.get('path')))}
        if action in ('open_scene','import_file','reference_file'):
            mode={'open_scene':'open','import_file':'import','reference_file':'reference'}[action]
            plan=operations.plan_files(kwargs.get('paths'),mode,kwargs.get('namespace',''),kwargs.get('confirm_replace_scene',False))
            if mode!='open':
                from maya import cmds
                if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
            return {**p,**plan}
        if action=='create_sequence_camera':
            p.update(config_io.sequence(kwargs.get('path')));p['open_view']=kwargs.get('open_view',False)
            from maya import cmds
            if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
            if p['open_view'] and cmds.about(batch=True):raise ValueError('Real Maya GUI required for view')
            return p
        if action in ('show_ui','close_ui','enable','disable','start_monitor','stop_monitor','patch_dialog','restore_dialog'):
            from maya import cmds
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required for session hooks')
        return p
    def validate(self,**kwargs):
        try:return ToolResult.ok('Assistant plan',data=self._plan(kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(str(e),errors=[str(e)])
    def execute(self,**kwargs):
        p=self._plan(kwargs);a=p['action']
        if a=='inspect':return ToolResult.ok('Assistant inventory',data={'preference_keys':list(config_io.KEYS),'file_types':sorted(config_io.FILES),'gui_acceptance':'not_run','hooks_automatic':False})
        if a=='read_prefs':return ToolResult.ok('Preference data',data={'preferences':p['preferences']})
        if a=='capture_prefs':return ToolResult.ok('Current preference optionVars',data={'preferences':session.capture_prefs()})
        if a=='save_prefs':return ToolResult.ok('Saved new config',data={'path':config_io.write_prefs(p['path'],p['preferences'])})
        if a=='apply_prefs':return ToolResult.ok('Typed optionVars applied',data=session.apply_prefs(p['preferences']))
        if a=='restore_prefs':session.restore_prefs();return ToolResult.ok('Pre-session optionVars restored')
        if a in ('open_scene','import_file','reference_file'):return ToolResult.ok('File operation completed',data=operations.execute_files(p))
        if a=='create_sequence_camera':return ToolResult.ok('Sequence camera created',data=operations.create_sequence(p,p['open_view']))
        from .native import main
        from .native.dragdrop import dragdrop_handler
        if a=='show_ui':return ToolResult.ok('Assistant controls',data={'window':main.show_main_window()})
        if a=='close_ui':main.close_ui();return ToolResult.ok('Owned controls closed; hooks retain explicit session state')
        if a=='start_monitor':dragdrop_handler.start_dragdrop_monitor()
        if a=='stop_monitor':dragdrop_handler.stop_dragdrop_monitor()
        if a=='patch_dialog':session.patch_dialog()
        if a=='restore_dialog':session.restore_dialog()
        if a=='enable':
            had_patch=session.patch is not None;had_monitor=dragdrop_handler._filter is not None
            session.patch_dialog()
            try:dragdrop_handler.start_dragdrop_monitor();main.show_main_window()
            except Exception:
                if not had_monitor:dragdrop_handler.stop_dragdrop_monitor()
                if not had_patch:session.restore_dialog()
                raise
        if a=='disable':
            dragdrop_handler.stop_dragdrop_monitor();session.restore_dialog();session.restore_prefs();main.close_ui()
        return ToolResult.ok('Explicit session state changed',data=session.state())
    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            r=self.validate(**kwargs)
            if r.success and not dry_run:r=self.execute(**kwargs)
        except Exception as e:r=ToolResult.fail(str(e),errors=[str(e)])
        r.tool_id=self.tool_id;r.dry_run=dry_run;return r
    def show_ui(self,parent=None):return self.run(action='show_ui')
''')
put(RC/'tests/test_smart_assistant.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.smart_assistant import SmartAssistantTool
    tool=SmartAssistantTool()
from maya_toolkit.tools.smart_assistant import config_io
class Checks(unittest.TestCase):
    def test_prefs_no_automatic_hooks_and_file_overwrite(self):
        self.assertTrue(tool.run().success);self.assertNotIn('PySide6',sys.modules)
        self.assertFalse(tool.run(action='inspect',open_view=1).success)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'prefs.json';values={'workingUnitLinear':'cm','gridSize':12.5,'gridDivisions':8}
            self.assertTrue(tool.run(action='save_prefs',path=str(p),preferences=values,dry_run=True).success);self.assertFalse(p.exists())
            self.assertTrue(tool.run(action='save_prefs',path=str(p),preferences=values).success)
            before=p.read_bytes();self.assertEqual(config_io.read_prefs(str(p)),values)
            self.assertFalse(tool.run(action='save_prefs',path=str(p),preferences=values).success);self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(ValueError):config_io.prefs({'gridSize':True})
            with self.assertRaises(ValueError):config_io.prefs({'unexpected':'x'})
    def test_sequence_is_unambiguous_and_numerically_ordered(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for n in (8,9,10):(p/f'img.{n:04d}.png').write_bytes(b'fixture')
            s=config_io.sequence(td);self.assertEqual(s['first_frame'],8);self.assertEqual(s['last_frame'],10)
            (p/'img.0012.png').write_bytes(b'gap')
            with self.assertRaises(ValueError):config_io.sequence(td)
            (p/'img.0012.png').unlink();(p/'other.0001.png').write_bytes(b'x');(p/'other.0002.png').write_bytes(b'x')
            with self.assertRaises(ValueError):config_io.sequence(td)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_smart_assistant_maya.py',r'''import base64,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.smart_assistant import session
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True);session.restore_prefs()
    def test_optionvar_types_restore_and_dry(self):
        captured=tool.run(action='capture_prefs');self.assertTrue(captured.success,captured.message)
        old={'exists':cmds.optionVar(exists='gridDivisions'),'value':cmds.optionVar(query='gridDivisions')}
        before=set(cmds.ls());cmds.optionVar(intValue=('gridDivisions',7))
        self.assertTrue(tool.run(action='apply_prefs',preferences={'gridDivisions':9},dry_run=True).success);self.assertEqual(cmds.optionVar(query='gridDivisions'),7)
        self.assertTrue(tool.run(action='apply_prefs',preferences={'gridDivisions':9}).success);self.assertIsInstance(cmds.optionVar(query='gridDivisions'),int)
        self.assertEqual(cmds.optionVar(query='gridDivisions'),9)
        self.assertTrue(tool.run(action='restore_prefs').success);self.assertEqual(cmds.optionVar(query='gridDivisions'),7)
        self.assertEqual(set(cmds.ls()),before)
        if old['exists']:cmds.optionVar(intValue=('gridDivisions',old['value']))
        else:cmds.optionVar(remove='gridDivisions')
        self.assertFalse(tool.run(action='enable',dry_run=True).success)
    def test_camera_image_sequence_whole_undo(self):
        cube=cmds.polyCube()[0];cmds.select(cube);before=set(cmds.ls());selection=cmds.ls(selection=True,long=True)
        png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jFWUAAAAASUVORK5CYII=')
        with tempfile.TemporaryDirectory() as td:
            for i in (1,2):(Path(td)/f'seq.{i:04d}.png').write_bytes(png)
            dry=tool.run(action='create_sequence_camera',path=td,dry_run=True);self.assertTrue(dry.success,dry.message);self.assertEqual(set(cmds.ls()),before)
            result=tool.run(action='create_sequence_camera',path=td);self.assertTrue(result.success,result.message)
            shape=result.data['image_plane_shape'];self.assertEqual(cmds.getAttr(shape+'.useFrameExtension'),1)
            self.assertEqual(cmds.ls(selection=True,long=True),selection)
            cmds.undo();self.assertEqual(set(cmds.ls()),before);cmds.redo()
            cmds.currentTime(2);self.assertEqual(cmds.getAttr(shape+'.frameExtension'),2)
    def test_file_batch_preflight_and_open_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/'source.ma';cube=cmds.polyCube(name='fixtureCube')[0];cmds.file(rename=str(src));cmds.file(save=True,type='mayaAscii',force=True)
            cmds.file(new=True,force=True);caller=cmds.createNode('transform',name='caller');before=set(cmds.ls())
            result=tool.run(action='import_file',paths=[str(src),str(Path(td)/'missing.ma')]);self.assertFalse(result.success);self.assertEqual(set(cmds.ls()),before)
            self.assertFalse(tool.run(action='open_scene',paths=[str(src)],confirm_replace_scene=True).success);self.assertTrue(cmds.objExists(caller))
            result=tool.run(action='import_file',paths=[str(src)]);self.assertTrue(result.success,result.message);self.assertTrue(cmds.objExists(caller))
            meshes=cmds.ls(type='mesh');self.assertEqual(len(meshes),1);self.assertEqual(cmds.polyEvaluate(meshes[0],face=True),6)
            parent=(cmds.listRelatives(meshes[0],parent=True,fullPath=True) or [None])[0];self.assertIn(parent,result.data['created_nodes'])
            cmds.file(new=True,force=True);result=tool.run(action='open_scene',paths=[str(src)],confirm_replace_scene=True);self.assertTrue(result.success,result.message)
            self.assertTrue(cmds.objExists('fixtureCube'))
    def test_python_dialog_wrapper_restores_and_respects_explicit_path(self):
        native=cmds.fileDialog2
        with tempfile.TemporaryDirectory() as td:
            cmds.file(rename=str(Path(td)/'caller.ma'));records=[]
            def fake(*args,**kwargs):records.append((args,kwargs));return ['unchanged result']
            cmds.fileDialog2=fake
            try:
                session.patch_dialog();owned=cmds.fileDialog2;session.patch_dialog();self.assertIs(cmds.fileDialog2,owned)
                self.assertEqual(cmds.fileDialog2('sentinel'),['unchanged result']);self.assertEqual(records[-1][0],('sentinel',));self.assertEqual(records[-1][1]['startingDirectory'],td)
                self.assertEqual(cmds.fileDialog2(startingDirectory='explicit'),['unchanged result']);self.assertEqual(records[-1][1]['startingDirectory'],'explicit')
                def foreign(*args,**kwargs):return owned(*args,**kwargs)
                cmds.fileDialog2=foreign
                with self.assertRaises(RuntimeError):session.restore_dialog()
                self.assertIs(cmds.fileDialog2,foreign)
                cmds.fileDialog2=owned;session.restore_dialog();self.assertIs(cmds.fileDialog2,fake)
            finally:cmds.fileDialog2=native;session.patch=None;session.original=None
if __name__=='__main__':
    result=unittest.main(exit=False).result;session.restore_prefs();maya.standalone.uninitialize();sys.exit(0 if result.wasSuccessful() else 1)
''')
put(RC/'tests/test_smart_assistant_qt.py',r'''"""Real QObject/QDropEvent fixture; no Maya initialization or actual file drop."""
import importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sa',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtGui,QtWidgets
from maya_toolkit.tools.smart_assistant.native.dragdrop import dragdrop_handler,file_actions
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
class QtChecks(unittest.TestCase):
    def test_drop_filter_owned_subtree_supported_and_stop(self):
        main=QtWidgets.QWidget();child=QtWidgets.QWidget(main);foreign=QtWidgets.QWidget();records=[];native=file_actions.handle_drop
        def event(p):
            mime=QtCore.QMimeData();mime.setUrls([QtCore.QUrl.fromLocalFile(str(p))])
            drop=QtGui.QDropEvent(QtCore.QPointF(1,1),QtCore.Qt.CopyAction,mime,QtCore.Qt.LeftButton,QtCore.Qt.NoModifier)
            return mime,drop
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'test.ma';source.write_bytes(b'// fixture');unsupported=Path(td)/'script.py';unsupported.write_bytes(b'# fixture')
            hook=dragdrop_handler.make_filter(main,app);dragdrop_handler._filter=hook;app.installEventFilter(hook)
            file_actions.handle_drop=lambda paths:records.append(paths)
            try:
                mime,drop=event(source);self.assertTrue(hook.eventFilter(child,drop));self.assertTrue(drop.isAccepted());self.assertEqual([[Path(p) for p in values] for values in records],[[source]])
                mime,drop=event(source);self.assertFalse(hook.eventFilter(foreign,drop));self.assertEqual(len(records),1)
                mime,drop=event(unsupported);self.assertFalse(hook.eventFilter(child,drop));self.assertEqual(len(records),1)
                dragdrop_handler.stop_dragdrop_monitor();self.assertIsNone(dragdrop_handler._filter)
                dragdrop_handler.stop_dragdrop_monitor()
            finally:file_actions.handle_drop=native;dragdrop_handler.stop_dragdrop_monitor()
        main.deleteLater();foreign.deleteLater();app.sendPostedEvents(None,QtCore.QEvent.DeferredDelete);app.processEvents()
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/smart_assistant.md','''# Maya Smart Assistant 完整待验候选

用户17原文件精确SHA归档；完整偏好JSON保存/应用、拖拽ma/mb/fbx/obj/abc打开/导入/引用选择、图片序列相机+独立modelPanel、Python fileDialog2当前场景目录功能与控制UI全部准备。原path_utils空文件缺is_image_sequence_folder、QtWidgets.QObject错误/弱生命周期、Qt6导入缺失、namespace取消变root引用、optionVar全部用stringValue、launch默默覆盖偏好/全局命令等确定问题已改。native模块路径完整，默认inspect/show_ui不注册监听或patch，不生成config、不写package路径；需要明确enable或UI按钮，关闭控件后仍可用disable显式撤所有自有hooks+恢复本会话optionVars。没有启动安装/userSetup自动写入。

API遵循Base/Schema/ToolResult，actions原三feature及capture/read/save/apply/restore prefs、open/import/reference、sequence、monitor/patch独立启停。GUI/mainwindow/QApplication/主线程检查；Qt6/Qt5真实filter使用QtCore.QObject、application强引用、仅Maya窗口子树支持文件Drop/DragEnter/Move，未支持后缀和其他窗口不拦截；stop只移除自有filter。fileDialog2只补caller未明确startingDirectory/dir时的当前scene目录，保存原函数且不重复叠加；foreign后装wrapper时拒绝覆盖，先恢复foreign wrapper再disable。原MEL global proc fileDialog2不能保持内建签名/返回值，不继续破坏内建MEL命令；MEL直调保持原生行为，Python调用默认路径功能完整。

```python
from maya_toolkit.tools.smart_assistant import SmartAssistantTool
t=SmartAssistantTool()
t.show_ui() # controls; hooks opt in
t.run(action='enable')
t.run(action='save_prefs',path=r'C:/temp/new_prefs.json')
t.run(action='apply_prefs',preferences={'gridDivisions':8},dry_run=True)
t.run(action='apply_prefs',preferences={'gridDivisions':8})
t.run(action='restore_prefs')
t.run(action='import_file',paths=[r'C:/temp/source.ma'],dry_run=True)
t.run(action='create_sequence_camera',path=r'C:/temp/sequence',open_view=True)
t.run(action='disable')
```

偏好只原五key：workingUnitLinear/Time string，gridSize/Spacing正有限数，gridDivisions正整数数值且保留原float/int存储（实际Maya2025为float），未知key/strict bool/类型错误/重复JSON key/超过1MiB拒绝。保存已有parent的新绝对JSON，不覆盖/不mkdir；read/dry只查文件/scene。apply全部数据先检，typed optionVar；记录每key第一次状态，后续apply不同key也保留，失败恢复本次，restore准确恢复不存在key或原类型。不主动SavePreferences，不假称改scene currentUnit/grid生效：原设计存optionVar，需用户选项UI刷新后实际核验。

file操作全1–64paths先检存在/后缀/绝对/重复，坏最后文件不前项import；reference明确namespace、不碰撞，多文件suffix分配，namespace取消不运行。import/reference existing新scene对象UndoChunk，但真实reference/file插件Undo支持须验收；open一次1file/confirm_replace_scene=True/dirty scene须先保存，force=False，不自动丢未存场景；open整体不能Undo。MA执行scriptNodes=False，FBX/OBJ/Alembic插件按真实Maya运行方式，不声称此参数封闭所有插件或reference副作用。

序列要求唯一同prefix/padding/扩展名、至少2连续数字帧，最大10000；避免原不明确目录多组和字符串顺序。预检纯查文件，不建nodes/view；执行完整camera+imagePlane/正确shape attrs/隐藏camera/只当前相机显示/可选modelPanel，复用本次新imagePlane的原生frameExtension驱动，只有未连接才创建frame expression并返回frame_driver，不覆盖外来连接。scene单Undo并保持原selection，view属非sceneUI只由用户关闭，Undo不撤viewport窗口/外部图片；timeline按源图片帧号（如0008-0010需时间8-10），不自动修改playback或当前时间。图片不复制，folder/first_image属于用户外部输入路径，不是遗漏候选素材；Maya低于原兼容target/缺图片时实记，不能用UI打开就推定显示/帧序列正常。

隔离检查为typed optionVar/dry/restore、真正camera/imagePlane/选择/一次UndoRedo/frameExtension、坏最后file/dirty open拒绝/真实MA import与open的临时fixture、Python wrapper尊重caller dir/传参返回/重复不叠加/foreign拒绝/restore；单独Qt离屏QObject/QDropEvent测试只自有子树受支持文件/其他对象与后缀不吞/停止强引用filter。真实用户文件Drop/filter重复长期生命周期、实际Python对话框与MEL原生、UI/sequence显示/插件/production reference/跨版本均not_run。全部code/UI/资源/测试/文档及注册promotion预制，用户真实Maya满意前留待整理池；不改正式core/registry。
''')
put(RC/'acceptance.md','''# Smart Assistant 真实Maya验收 not_run

1. show_ui仅controls不修改prefs/注册hooks；enable/disable重复启停，Qt5/6 QObject强引用filter单实例，拖拽支持文件/序列、其他后缀/其他窗口不吞事件；整批多files不忽略第二项。场景dirty open要求先保存，namespace取消不建ref，已有namespace拒绝，open仅1file默认取消且不可Undo。FBX/OBJ/ABC插件与引用复杂源使用备份场景。
2. export/read/apply/restore原5optionVars实际类型、坏最后key不先改首项、重复key拒绝、新绝对JSON不覆盖不mkdir，多个apply恢复所有初始值/不存在key。仅optionVar不是scene currentUnit切换，确认真实偏好UI刷新语义；没有自动SavePreferences/重写config/userSetup。
3. Python fileDialog2 caller未提供dir用当前scene目录、明确dir尊重、args/kwargs与返回完整、不重复嵌套、restore还原原callable；foreign后来wrapper需先恢复它，候选不强覆盖；原MEL命令参数/返回保持原生，未假称MEL路径已劫持。
4. 同prefix/padding连续数字图片至少2frame、gap/multiple groups拒绝，sequence camera+正确imagePlane shape+frame expression/frameExtension/独立viewport实际显示、原selection保持/单UndoRedo。open_view=False可纯scene调用；窗口不可由scene Undo撤回，图片为外部用户输入，不写素材。
5. fullGUI关闭/重开/会话hooks独立管理、disable恢复；并行其他工具的global patch/Drop过滤器交互与Maya跨版本实记。candidate_sha256/maya_version/accepted_by/date/passed=true后执行promotion；此前不迁正式。
''')
review=[{'path':p.relative_to(NATIVE).as_posix(),'symbols':[n.name for n in ast.parse(p.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]} for p in sorted(NATIVE.rglob('*.py'))]
put(PKG/'source_review.json',json.dumps(review,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/smart_assistant','--class-name','SmartAssistantTool',
                '--summary','Complete preference/drop/sequence/dialog assistant with typed optionVars, explicit reversible session hooks, whole-file preflight and guarded JSON',
                '--dependencies','Maya cmds/MEL and native import plugins','PySide6/PySide2 for actual dragdrop session',
                '--limitations','Real Maya GUI/drop lifecycle/Python dialog/sequence viewport/plugins/reference/cross-version acceptance not_run; MEL native dialog remains original'],check=True)
