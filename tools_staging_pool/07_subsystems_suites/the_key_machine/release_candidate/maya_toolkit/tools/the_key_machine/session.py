"""Scoped file IO, exact backups, owned jobs/UI/commands and main-thread timers."""
from pathlib import Path
import ast,builtins,functools,hashlib,importlib,json,math,os,shutil,sys,types,uuid
ROOT=Path(__file__).parent;NATIVE=ROOT/'native';data_root=None;language='zh_CN';timers=[];jobs=set();uis=set();ui_handles={};widgets=[];nodes=set();commands={};errors=[];toolbar_module=None;authorized_files=set();active_depth=0
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Absolute non-symlink path required')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def root_path(value):
    p=path(value)
    if not p.is_dir():raise ValueError('Existing data root required')
    if ROOT.resolve() in (p.resolve(),*p.resolve().parents):raise ValueError('Data root must be outside immutable candidate')
    return p
def finite(value):
    if isinstance(value,float) and (not math.isfinite(value) or abs(value)>1e12):raise ValueError('Nonfinite/out-of-range number')
    if isinstance(value,(list,tuple)):
        if len(value)>1000000:raise ValueError('Array limit')
        for v in value:finite(v)
    elif isinstance(value,dict):
        if len(value)>100000:raise ValueError('Object limit')
        for k,v in value.items():
            if not isinstance(k,str):raise ValueError('JSON string keys required')
            finite(v)
def scope(value):
    p=path(str(value))
    if data_root is None:raise RuntimeError('Explicit data_root session not configured')
    if not (data_root==p or data_root in p.parents or p in authorized_files):raise ValueError('Write outside owned data directory or explicit save-dialog path')
    return p
def backup(p):
    p=scope(p)
    if not p.exists():return None
    if not p.is_file():raise ValueError('Expected existing file')
    folder=data_root/'MTB_TheKeyMachine_user_data/.mtb_backups';folder.mkdir(parents=True,exist_ok=True)
    dest=folder/(p.name+'.'+uuid.uuid4().hex);blob=p.read_bytes()
    with dest.open('xb') as f:f.write(blob)
    if dest.read_bytes()!=blob:raise IOError('Backup mismatch')
    receipt={'source':str(p),'backup':str(dest),'sha256':hashlib.sha256(blob).hexdigest()}
    with dest.with_name(dest.name+'.json').open('x',encoding='utf8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
    return dest
def guarded_open(value,mode='r',*args,**kw):
    if isinstance(value,int):raise ValueError('Raw descriptor access unsupported')
    p=path(str(value))
    if any(c in mode for c in 'wax+'):
        scope(p)
        if p.exists() and 'x' not in mode:backup(p)
    elif p.exists() and p.stat().st_size>64*1024*1024:raise ValueError('Input exceeds 64MiB')
    return builtins.open(p,mode,*args,**kw)
def discard(value,*args,**kw):
    p=scope(value)
    if p==data_root or p.name=='MTB_TheKeyMachine_user_data':raise ValueError('Root deletion refused')
    if not p.exists():return
    for child in p.rglob('*') if p.is_dir() else []:
        if child.is_symlink():raise ValueError('Symlink in deletion tree')
    folder=data_root/'MTB_TheKeyMachine_user_data/.mtb_deleted';folder.mkdir(parents=True,exist_ok=True)
    dst=folder/(p.name+'.'+uuid.uuid4().hex);shutil.move(str(p),str(dst));return str(dst)
class OSProxy:
    def __getattr__(self,name):
        if name in ('remove','unlink','rmdir'):return discard
        if name in ('mkdir','makedirs'):
            def make(value,*args,**kw):return getattr(os,name)(scope(value),*args,**kw)
            return make
        if name in ('rename','replace'):
            def move(src,dst,*args,**kw):scope(src);p=scope(dst);backup(p) if p.exists() else None;return getattr(os,name)(src,dst,*args,**kw)
            return move
        return getattr(os,name)
os_proxy=OSProxy()
class ShutilProxy:
    def __getattr__(self,name):
        if name=='rmtree':return discard
        if name in ('copy','copy2','copyfile','move','copytree'):
            def copy(src,dst,*args,**kw):
                p=scope(dst)
                if p.is_dir() and name!='copytree':p=p/Path(src).name
                if p.exists() and p.is_file():backup(p)
                if name=='move':scope(src)
                return getattr(shutil,name)(src,dst,*args,**kw)
            return copy
        return getattr(shutil,name)
shutil_proxy=ShutilProxy()
class JSONProxy:
    def __getattr__(self,name):
        if name=='load':
            def load(stream,**kw):
                blob=stream.read(64*1024*1024+1)
                if len(blob)>64*1024*1024:raise ValueError('JSON too large')
                def pairs(rows):
                    result={}
                    for k,v in rows:
                        if k in result:raise ValueError('Duplicate JSON key')
                        result[k]=v
                    return result
                result=json.loads(blob,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')));finite(result);return result
            return load
        if name in ('dump','dumps'):
            def dump(value,*args,**kw):finite(value);kw['allow_nan']=False;return getattr(json,name)(value,*args,**kw)
            return dump
        return getattr(json,name)
json_proxy=JSONProxy()
def load_config():
    if data_root is None:raise RuntimeError('Configure explicit data_root before importing native modules')
    return {'STUDIO_INSTALL':True,'INSTALL_PATH':str(NATIVE),'USER_FOLDER_PATH':str(data_root),'LICENSE_FOLDER':str(data_root/'MTB_TheKeyMachine_user_data/license'),'LICENSE_FILE_NAME':'user','UPDATER':False,'BUG_REPORT':False,'CUSTOM_TOOLS_MENU':True,'CUSTOM_TOOLS_EDITABLE_BY_USER':True,'CUSTOM_SCRIPTS_MENU':True,'CUSTOM_SCRIPTS_EDITABLE_BY_USER':True}
def literal_module(file,name):
    p=path(str(file));tree=ast.parse(p.read_bytes());module=types.ModuleType(name);module.__file__=str(p)
    for n in tree.body:
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
        if not isinstance(n,ast.Assign) or len(n.targets)!=1 or not isinstance(n.targets[0],ast.Name):raise ValueError('Preferences/custom menu configuration must be literal assignments; no import/exec on activation')
        value=ast.literal_eval(n.value);finite(value);setattr(module,n.targets[0].id,value)
    return module
def initialize_user_data():
    folder=data_root/'MTB_TheKeyMachine_user_data'
    for rel,source in [('preferences/user_preferences.py',None),('connect/tools/tools.py',NATIVE/'TheKeyMachine/connect/tools/tools.py'),('connect/scripts/scripts.py',NATIVE/'TheKeyMachine/connect/scripts/scripts.py')]:
        p=folder/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            content=source.read_text(encoding='utf8') if source else 'show_tooltips=True\ntoolbar_icon_w=28\ntoolbar_icon_h=28\ntoolbar_size=1580\n'
            with p.open('x',encoding='utf8') as f:f.write(content)
    preferences=literal_module(folder/'preferences/user_preferences.py','MTB_TheKeyMachine_user_preferences')
    for key in ('toolbar_icon_w','toolbar_icon_h','toolbar_size'):
        if type(getattr(preferences,key,None)) is not int or not 1<=getattr(preferences,key)<=10000:raise ValueError('Invalid preference '+key)
    if type(getattr(preferences,'show_tooltips',None)) is not bool:raise ValueError('Invalid tooltip preference')
    tools=literal_module(folder/'connect/tools/tools.py','MTB_TheKeyMachine_tools');scripts=literal_module(folder/'connect/scripts/scripts.py','MTB_TheKeyMachine_scripts')
    return preferences,tools,scripts
def translate(value):
    if language!='zh_CN' or not isinstance(value,str):return value
    module=importlib.import_module('TheKeyMachine.styleMod_cn');return getattr(module,'chinese_translation',{}).get(value,value)
def selected(nodes_arg=None,write=False):
    from maya import cmds
    values=nodes_arg if nodes_arg is not None else (cmds.ls(sl=True,long=True) or [])
    if not isinstance(values,list) or len(values)>4096:raise ValueError('At most 4096 explicit nodes')
    out=[]
    for value in values:
        if not isinstance(value,str) or any(c in value for c in '*?[]'):raise ValueError('Exact object names required')
        matches=cmds.ls(value,long=True) or []
        if len(matches)!=1 or matches[0] in out:raise ValueError('Missing, ambiguous or duplicate node')
        node=matches[0]
        if write:
            if cmds.referenceQuery(node,isNodeReferenced=True):raise ValueError('Referenced destination rejected')
            for attr in cmds.listAttr(node,keyable=True) or []:
                plug=node+'.'+attr
                if cmds.getAttr(plug,lock=True):raise ValueError('Locked destination '+plug)
                if any(not cmds.nodeType(n).startswith('animCurve') for n in (cmds.listConnections(plug,s=True,d=False) or [])):raise ValueError('Driven destination '+plug)
        out.append(node)
    return out
def node_uuid(value):
    from maya import cmds
    return (cmds.ls(str(value).split('.')[0],uuid=True) or [None])[0]
def ui_handle(value):
    from maya import OpenMayaUI
    api=OpenMayaUI.MQtUtil
    return int(api.findControl(value) or api.findLayout(value) or api.findMenuItem(value) or 0)
class CmdProxy:
    def __getattr__(self,name):
        from maya import cmds
        fn=getattr(cmds,name)
        def call(*args,**kw):
            try:
                finite(args);finite(kw)
                query=kw.get('q',kw.get('query',False));edit=kw.get('e',kw.get('edit',False))
                if not query and not edit and args and isinstance(args[0],str) and name in ('window','workspaceControl','iconTextButton','button','columnLayout','rowLayout','formLayout','menuItem'):
                    target=args[0]
                    if target not in uis and (cmds.control(target,exists=True) or cmds.window(target,exists=True) or cmds.menuItem(target,exists=True)):raise ValueError('Foreign UI name collision: '+target)
                if name=='deleteUI' and args:
                    target=str(args[0])
                    if target not in uis and not any(target.startswith(u+'|') for u in uis):raise ValueError('Foreign UI deletion refused: '+target)
                    if target in ui_handles and ui_handle(target)!=ui_handles[target]:raise ValueError('Owned UI name replaced by foreign widget')
                if name=='scriptJob' and ('kill' in kw or 'k' in kw):
                    job=kw.get('kill',kw.get('k'))
                    if job not in jobs:raise ValueError('Foreign job kill refused')
                if name=='delete':
                    targets=[]
                    def flatten(value):
                        if isinstance(value,(list,tuple)):
                            for v in value:flatten(v)
                        elif value is not None:targets.append(value)
                    flatten(args)
                    allowed=set(nodes)
                    for obj in cmds.ls(sl=True,long=True) or []:
                        allowed.add(node_uuid(obj))
                        for child in cmds.listRelatives(obj,allDescendents=True,fullPath=True) or []:allowed.add(node_uuid(child))
                    if not targets or any(node_uuid(n) is None or node_uuid(n) not in allowed for n in targets):raise ValueError('Delete requires selected hierarchy or nodes created by this session')
                if name=='runTimeCommand' and args:
                    args=('MTB_TKM_'+str(args[0]),)+args[1:]
                    if not query and cmds.runTimeCommand(args[0],q=True,exists=True) and args[0] not in commands:raise ValueError('Foreign runtime command collision')
                for key in ('label','l','annotation','ann','title','message'):
                    if key in kw:kw[key]=translate(kw[key])
                result=fn(*args,**kw)
                if name=='fileDialog2' and kw.get('fileMode',kw.get('fm'))==0 and result:
                    for value in result:authorized_files.add(path(value))
                if name=='scriptJob' and not query and type(result) is int:jobs.add(result)
                if name=='runTimeCommand' and not query and not kw.get('delete'):commands[args[0]]=cmds.runTimeCommand(args[0],q=True,command=True)
                if not query and not edit and name in ('window','workspaceControl','columnLayout','rowLayout','formLayout','rowColumnLayout','iconTextButton','iconTextCheckBox','button','text','textField','textFieldButtonGrp','intField','floatField','floatSlider','floatSliderGrp','popupMenu','menuItem','separator','optionMenu','checkBox','frameLayout','scrollLayout') and isinstance(result,str):
                    uis.add(result);ui_handles[result]=ui_handle(result)
                if not query and name in ('createNode','group','spaceLocator','camera','duplicate','curve','expression','cluster','parentConstraint','pointConstraint','orientConstraint','sets'):
                    for value in result if isinstance(result,(list,tuple)) else [result]:
                        if isinstance(value,str) and cmds.objExists(value):nodes.add(node_uuid(value))
                return result
            except Exception as e:
                errors.append(str(e));raise
        return call
cmdshim=CmdProxy()
class MainThreadWorker:
    def __init__(self,target=None,args=(),kwargs=None,**unused):self.target=target;self.args=args;self.kwargs=kwargs or {}
    def start(self):return self.target(*self.args,**self.kwargs)
def repeat(seconds,callback,predicate=lambda:True):
    try:from PySide6 import QtCore
    except ImportError:from PySide2 import QtCore
    app=QtCore.QCoreApplication.instance()
    if app is None or QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Main Qt thread required')
    timer=QtCore.QTimer(app);timers.append(timer)
    def tick():
        if not predicate():timer.stop();return
        try:
            callback()
            if not predicate():timer.stop()
        except Exception as e:timer.stop();errors.append(str(e))
    timer.timeout.connect(tick);timer.start(max(1,int(float(seconds)*1000)));return timer
def owned_timer(*args,**kw):
    try:from PySide6 import QtCore
    except ImportError:from PySide2 import QtCore
    timer=QtCore.QTimer(*args,**kw);timers.append(timer);return timer
def single_shot(milliseconds,callback):
    timer=owned_timer();timer.setSingleShot(True);timer.timeout.connect(callback);timer.start(milliseconds);return timer
owned_timer.singleShot=single_shot
def tracked_widget(*args,**kw):
    try:from PySide6 import QtWidgets
    except ImportError:from PySide2 import QtWidgets
    try:from PySide6 import QtCore
    except ImportError:from PySide2 import QtCore
    widget=QtWidgets.QWidget(*args,**kw);widgets.append(widget)
    class TranslationFilter(QtCore.QObject):
        def eventFilter(self,obj,event):
            if event.type()==QtCore.QEvent.Show:owned_timer.singleShot(0,lambda:translate_widget(widget))
            return False
    widget._mtb_translation_filter=TranslationFilter(widget);widget.installEventFilter(widget._mtb_translation_filter)
    return widget
def translate_widget(widget):
    try:from PySide6 import QtWidgets
    except ImportError:from PySide2 import QtWidgets
    try:
        objects=[widget]+widget.findChildren(QtWidgets.QWidget)
        for obj in objects:
            if isinstance(obj,(QtWidgets.QLabel,QtWidgets.QPushButton,QtWidgets.QCheckBox)) and hasattr(obj,'text'):obj.setText(translate(obj.text()))
            if obj.toolTip():obj.setToolTip(translate(obj.toolTip()))
            if obj.windowTitle():obj.setWindowTitle(translate(obj.windowTitle()))
    except RuntimeError:pass # deleted owned widget, no global traversal
def native_preflight(name):
    selected(write=True)
    if 'copy_worldspace' in name:
        from maya import cmds
        start=cmds.playbackOptions(q=True,minTime=True);end=cmds.playbackOptions(q=True,maxTime=True)
        if end<start or end-start>10000:raise ValueError('World capture range exceeds 10000 frames')
def configure(value):
    global data_root
    p=root_path(value)
    if data_root is not None and p!=data_root:raise RuntimeError('Native config is fixed for this Maya session; use a fresh session for another data_root')
    for name in ('TheKeyMachine','MTB_TheKeyMachine_user_data'):
        module=sys.modules.get(name)
        if module is not None and not (ROOT.resolve() in Path(getattr(module,'__file__','')).resolve().parents):raise RuntimeError('Foreign '+name+' module loaded; use fresh session')
    data_root=p
    if str(NATIVE) not in sys.path:sys.path.insert(0,str(NATIVE))
    return p
def native_module(name):
    if data_root is None:raise RuntimeError('Explicit data_root required')
    return importlib.import_module(name)
def show(value):
    global toolbar_module
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    configure(value);toolbar_module=native_module('TheKeyMachine.core.toolbar')
    toolbar_module.user_preferences,toolbar_module.connectToolBox,toolbar_module.cbScripts=initialize_user_data()
    if toolbar_module.tb is None:toolbar_module.tb=toolbar_module.toolbar()
    toolbar_module.tb.startUI();return {'workspace':'MTB_TKM_k','data_root':str(data_root)}
def close(*unused):
    from maya import cmds
    for timer in timers:timer.stop();timer.deleteLater()
    timers.clear()
    if toolbar_module and toolbar_module.tb:
        tb=toolbar_module.tb
        for flag in ('run_centerToolbar','anim_offset_run_timer','micro_move_run_timer'):setattr(tb,flag,False)
        for flag in ('toggleAnimOffsetButtonState','micro_move_button_state'):
            if getattr(tb,flag,False):cmds.undoInfo(closeChunk=True);setattr(tb,flag,False)
        toolbar_module.tb=None
    for module_name,function in [('TheKeyMachine.mods.barMod','remove_micro_move_callbacks'),('TheKeyMachine.mods.keyToolsMod','remove_link_obj_callbacks')]:
        module=sys.modules.get(module_name)
        if module and hasattr(module,function):getattr(module,function)()
    for job in list(jobs):
        if cmds.scriptJob(exists=job):cmds.scriptJob(kill=job,force=True)
    jobs.clear()
    # Only tracked UI; query each host type before deletion.
    for name in sorted(uis,key=lambda n:n.count('|'),reverse=True):
        try:
            if cmds.control(name,exists=True) or cmds.window(name,exists=True) or cmds.menuItem(name,exists=True):
                if ui_handle(name)!=ui_handles.get(name):raise RuntimeError('Foreign widget replaced owned UI name; preserve '+name)
                cmds.deleteUI(name)
        except RuntimeError:pass
    uis.clear();ui_handles.clear()
    for widget in widgets:
        try:widget.close();widget.deleteLater()
        except RuntimeError:pass
    widgets.clear()
    for name in list(commands):
        if cmds.runTimeCommand(name,q=True,exists=True):
            if cmds.runTimeCommand(name,q=True,command=True)!=commands[name]:raise RuntimeError('Foreign later command replacement; preserve '+name)
            cmds.runTimeCommand(name,e=True,delete=True)
    commands.clear()
    return {'closed':True,'data_preserved':True,'helper_nodes_preserved':True}
def reload_ui(*args):
    close();return show(str(data_root))
def operations():return json.loads((ROOT/'operations.json').read_text(encoding='utf8'))
def operation(value,arguments=None,objects=None):
    rows={r['id']:r for r in operations()}
    if value not in rows:raise ValueError('Unknown source operation')
    row=rows[value];arguments=arguments or {}
    if not isinstance(arguments,dict):raise ValueError('Operation arguments must be object')
    finite(arguments);params={p['name']:p for p in row['parameters']}
    if not row['varkw'] and set(arguments)-set(params):raise ValueError('Unknown native parameter')
    if any(p['required'] and p['name'] not in arguments for p in row['parameters']):raise ValueError('Missing required native parameter')
    for key,p in params.items():
        if key in arguments and 'default' in p and p['default'] is not None:
            default=p['default'];value=arguments[key]
            if type(default) is bool and type(value) is not bool:raise ValueError('Strict native boolean '+key)
            if isinstance(default,str) and not isinstance(value,str):raise ValueError('Native string '+key)
    if objects is not None:selected(objects,bool(row['scene_writes']))
    return row,arguments
def invoke(value,arguments=None,objects=None):
    row,args=operation(value,arguments,objects);module=native_module(row['module']);fn=getattr(module,row['function'])
    from maya import cmds
    from maya_toolkit.core.context import UndoChunkContext
    before=cmds.ls(sl=True,long=True) or [];time=cmds.currentTime(q=True);errors.clear()
    with UndoChunkContext(chunk_name='MTB TheKeyMachine '+row['function']):
        try:
            if objects is not None:cmds.select(selected(objects,bool(row['scene_writes'])),r=True)
            result=fn(**args)
            if errors:raise RuntimeError('Native operation incomplete: '+'; '.join(errors))
            return result
        finally:
            cmds.currentTime(time,edit=True)
            if not row['function'].lower().startswith(('select','isolate')):cmds.select(before,r=True) if before else cmds.select(clear=True)
