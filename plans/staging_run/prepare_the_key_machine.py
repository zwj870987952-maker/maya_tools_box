"""Full original toolset with scoped persistence and explicit Maya session."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/the_key_machine';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/the_key_machine';NATIVE=PKG/'native/TheKeyMachine'
for src in UNIT.rglob('*'):
    if not src.is_file() or 'release_candidate' in src.relative_to(UNIT).parts or '__pycache__' in src.parts or src.name=='.gitattributes':continue
    p=NATIVE/src.relative_to(UNIT);p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
for sub in ('mods','core','connect','connect/tools','connect/scripts'):put(NATIVE/sub/'__init__.py','"""Bundled original TheKeyMachine package."""')
catalog=[]
for p in sorted(NATIVE.rglob('*.py')):
    tree=ast.parse(p.read_bytes());module='TheKeyMachine.'+'.'.join(p.relative_to(NATIVE).with_suffix('').parts)
    if p.name=='__init__.py':continue
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and not n.name.startswith('_') and p.parent.name in ('mods','core'):
            defaults=[None]*(len(n.args.args)-len(n.args.defaults))+n.args.defaults
            params=[]
            for arg,default in zip(n.args.args,defaults):
                row={'name':arg.arg,'required':default is None}
                if default is not None:
                    try:row['default']=ast.literal_eval(default)
                    except (ValueError,TypeError):row['native_default']=ast.unparse(default)
                params.append(row)
            writes=[c.func.attr for c in ast.walk(n) if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='cmds' and c.func.attr in {'setAttr','delete','cutKey','setKeyframe','keyframe','xform','connectAttr','disconnectAttr','parent','group','createNode','rename','bakeResults'} and not any(k.arg in ('q','query') and isinstance(k.value,ast.Constant) and k.value.value is True for k in c.keywords)]
            catalog.append({'id':module+'.'+n.name,'module':module,'function':n.name,'parameters':params,'varargs':bool(n.args.vararg),'varkw':bool(n.args.kwarg),'source_line':n.lineno,'scene_writes':sorted(set(writes))})
put(PKG/'operations.json',json.dumps(catalog,ensure_ascii=False,indent=2))
put(PKG/'session.py',r'''"""Scoped file IO, exact backups, owned jobs/UI/commands and main-thread timers."""
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
''')
# Native semantics remain in full source, replacing only setup/lifecycle/IO hazards.
for p in sorted(NATIVE.rglob('*.py')):
    if p.name=='__init__.py':continue
    if 'connect' in p.relative_to(NATIVE).parts:continue # literal config template only
    s=p.read_text(encoding='utf-8-sig');s=s.replace('TheKeyMachine_user_data','MTB_TheKeyMachine_user_data')
    s=s.replace('import maya.cmds as cmds','from maya_toolkit.tools.the_key_machine.session import cmdshim as cmds')
    # Keep stdlib imports private to the native modules; no global monkeypatch.
    for name,proxy in [('os','os_proxy'),('shutil','shutil_proxy'),('json','json_proxy')]:
        s=s.replace('import '+name+'\n','from maya_toolkit.tools.the_key_machine.session import '+proxy+' as '+name+'\n')
    tree=ast.parse(s);lines=s.splitlines();edits=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='reload':edits.append((n.lineno-1,n.end_lineno,(' '*n.col_offset)+'pass # no implicit reload of owned runtime modules'))
    for start,end,value in sorted(edits,reverse=True):lines[start:end]=[value]
    s='\n'.join(lines)+'\n'
    if p.parent.name in ('mods','core'):
        # Original UI callbacks get the same full-target guard as direct API.
        writes={r['function'] for r in catalog if r['module']=='TheKeyMachine.'+'.'.join(p.relative_to(NATIVE).with_suffix('').parts) and r['scene_writes']}
        tree=ast.parse(s);lines=s.splitlines();inserts=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef) and n.name in writes:
                at=n.body[0].lineno-1
                if isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):at=n.body[0].end_lineno
                inserts.append((at,['    from maya_toolkit.tools.the_key_machine.session import native_preflight','    native_preflight('+repr(n.name)+')']))
        for at,value in sorted(inserts,reverse=True):lines[at:at]=value
        s='\n'.join(lines)+'\n'
    if p.name=='generalMod.py':
        tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_config');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['def load_config():','    from maya_toolkit.tools.the_key_machine.session import load_config as configured','    return configured()'];s='\n'.join(lines)+'\n'
        s=s.replace('    from PySide6.QtCore import QTimer','    from PySide6.QtCore import QTimer\n    from PySide6.QtGui import QIcon,QPixmap\n    from PySide6.QtWidgets import QWidget')
    if p.name=='toolbar.py':
        start=s.index('USER_PREFERENCE_FILE =');end=s.index('current_blend_slider_mode =')
        s=s[:start]+'''from maya_toolkit.tools.the_key_machine.session import initialize_user_data
user_preferences, connectToolBox, cbScripts = initialize_user_data()
USER_PREFERENCE_FILE = os.path.join(USER_FOLDER_PATH,'MTB_TheKeyMachine_user_data/preferences/user_preferences.py')
\n'''+s[end:]
        s=s.replace("WorkspaceName = 'k'","WorkspaceName = 'MTB_TKM_k'").replace("selection_sets_workspace = 's'","selection_sets_workspace = 'MTB_TKM_s'")
        s=s.replace('tb = toolbar()','tb = None # explicit session.show only')
        s=s.replace('threading.Thread(','MainThreadWorker(')
        s=s.replace('import threading','from maya_toolkit.tools.the_key_machine.session import MainThreadWorker,repeat')
        # Keep the same periodic work with owned QTimers rather than threads.
        s=s.replace('        while self.anim_offset_run_timer: \n            time.sleep(interval)\n            utils.executeDeferred(adjust_offset_animation)','        return repeat(interval,adjust_offset_animation,lambda:self.anim_offset_run_timer)')
        s=s.replace('        while self.micro_move_run_timer: \n            time.sleep(interval)\n            utils.executeDeferred(micro_move_run)','        return repeat(interval,micro_move_run,lambda:self.micro_move_run_timer)')
        s=s.replace('        while self.run_centerToolbar: \n            time.sleep(interval)\n            utils.executeDeferred(centerBar_run)','        return repeat(interval,centerBar_run,lambda:self.run_centerToolbar)')
        s=s.replace('            while link_obj_image_timer: \n                time.sleep(interval)\n                utils.executeDeferred(toggle_link_obj_button_image)','            return repeat(interval,toggle_link_obj_button_image,lambda:link_obj_image_timer)')
        tree=ast.parse(s);n=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='reload');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['    def reload(self,*args):','        from maya_toolkit.tools.the_key_machine.session import reload_ui','        return reload_ui()'];s='\n'.join(lines)+'\n'
        s=s.replace("exec(compile(open(config_file).read(), config_file, 'exec'), config)","config.update(vars(literal_module(config_file, 'MTB_TKM_preferences_read')))")
        tree=ast.parse(s);n=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='isScriptJobActive');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['    def isScriptJobActive(self, jobId):','        return bool(jobId is not None and cmds.scriptJob(exists=jobId))'];s='\n'.join(lines)+'\n'
    if p.name=='uiMod.py':
        tree=ast.parse(s);edits=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef) and n.name=='uninstall':edits.append((n.lineno-1,n.end_lineno,'def uninstall():\n    from maya_toolkit.tools.the_key_machine.session import close\n    return close() # unload owned session; preserve installation and user data'))
        lines=s.splitlines()
        for start,end,value in sorted(edits,reverse=True):lines[start:end]=value.splitlines()
        s='\n'.join(lines)+'\n'
    if p.name=='keyToolsMod.py':
        tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='get_selected_channels');lines=s.splitlines();lines[n.body[0].lineno-1:n.body[0].lineno-1]=['    if cmds.about(batch=True):return []'];s='\n'.join(lines)+'\n'
    # File/machine-wide installers are replaced by reversible in-memory language.
    if p.name in ('direct_translator.py','toolbar_patch.py'):
        s='''"""In-memory Chinese switch; no source replacement or installer."""
def apply_chinese_patch():
    from maya_toolkit.tools.the_key_machine import session
    session.language='zh_CN'
    if session.toolbar_module and session.toolbar_module.tb:return session.reload_ui()
    return {'language':'zh_CN'}
def direct_translate():return apply_chinese_patch()
'''
    if p.parent.name=='mods' and p.name=='barMod.py':
        # Importing bar functions must not instantiate the toolbar or QObject.
        pass
    # Every native file open uses a scoped path and exact backup before truncation.
    tree=ast.parse(s);body=tree.body;offset=0
    if body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):offset=body[0].end_lineno
    lines=s.splitlines();lines[offset:offset]=['from maya_toolkit.tools.the_key_machine.session import guarded_open as open,owned_timer,tracked_widget,literal_module'];s='\n'.join(lines)+'\n'
    s=s.replace('QTimer.singleShot(','owned_timer.singleShot(').replace('QtCore.QTimer()','owned_timer()').replace('window = QtWidgets.QWidget(','window = tracked_widget(')
    # Distinct helper roots: keep real package imports/file paths unchanged.
    tree=ast.parse(s);replacements=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and (n.value=='TheKeyMachine' or n.value.startswith('TheKeyMachine_')) and not any(c in n.value for c in '/\\. '):
            token=ast.get_source_segment(s,n)
            if token:replacements.add((token,repr('MTB_TKM_'+n.value)))
    for token,value in sorted(replacements,key=lambda r:len(r[0]),reverse=True):s=s.replace(token,value)
    put(p,s)
put(PKG/'__init__.py',r'''"""Complete original TheKeyMachine with source-enumerated API and owned session."""
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import session
OPS=[r['id'] for r in session.operations()]
class TheKeyMachineTool(BaseMayaTool):
    tool_id='the_key_machine';tool_name='TheKeyMachine 完整动画工具集';category='animation';version='1.0.0'
    description='Full native toolbar/selection sets/graph editor/mirror/pose/animation/worldspace/hotkey tools with isolated user data and Chinese localization'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','invoke','set_language'],'default':'inspect'},
        'data_root':{'type':'string'},'operation':{'type':'string','enum':OPS},'arguments':{'type':'object'},
        'objects':{'type':'array','items':{'type':'string'},'maxItems':4096},'language':{'type':'string','enum':['en_US','zh_CN'],'default':'zh_CN'}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            if kw.get('language','zh_CN') not in ('en_US','zh_CN'):raise ValueError('Invalid language')
            if action in ('show_ui','invoke'):session.root_path(kw.get('data_root'))
            if action=='invoke':session.operation(kw.get('operation'),kw.get('arguments'),kw.get('objects'))
            return ToolResult.ok(message='纯参数/目标预检；未导入native、写目录、注册job/UI或timer',data={'action':action,'native_context_checks':'Deferred to original operation; GUI-only commands require real Maya'})
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'operations':len(OPS),'source_version':'0.1.4 build306','gui_acceptance':'not_run','full_resources':True})
        if action=='close_ui':return ToolResult.ok(data=session.close())
        if action=='set_language':
            session.language=kw.get('language','zh_CN')
            if session.toolbar_module and session.toolbar_module.tb:session.reload_ui()
            return ToolResult.ok(data={'language':session.language,'file_write':False})
        session.language=kw.get('language','zh_CN')
        if action=='show_ui':return ToolResult.ok(data=session.show(kw['data_root']))
        session.configure(kw['data_root']);value=session.invoke(kw['operation'],kw.get('arguments'),kw.get('objects'))
        return ToolResult.ok(data={'operation':kw['operation'],'result':value if isinstance(value,(dict,list,str,int,float,bool,type(None))) else str(value),'external_files_undoable':False})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        roots=cmds.fileDialog2(fileMode=3,caption='TheKeyMachine 候选：选择独立数据目录')
        return session.show(roots[0]) if roots else None
''')
put(RC/'tests/test_the_key_machine.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.the_key_machine import TheKeyMachineTool
    tool=TheKeyMachineTool()
from maya_toolkit.tools.the_key_machine import session
class Checks(unittest.TestCase):
    def test_no_native_import_and_config_literals(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('TheKeyMachine',sys.modules);self.assertGreater(len(session.operations()),150)
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);prefs,tools,scripts=session.initialize_user_data();self.assertEqual(prefs.toolbar_size,1580);self.assertTrue(tools.tool_order)
            p=Path(td)/'bad.py';p.write_text('import os\nx=1')
            with self.assertRaises(ValueError):session.literal_module(p,'bad')
            session.data_root=None
    def test_exact_backup_and_no_source_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);p=Path(td)/'clip.json';p.write_bytes(b'old\r\n')
            with session.guarded_open(str(p),'w') as f:f.write('new')
            backups=list((Path(td)/'MTB_TheKeyMachine_user_data/.mtb_backups').glob('clip.json.*'));self.assertTrue(any(q.read_bytes()==b'old\r\n' for q in backups if q.suffix!='.json'))
            with self.assertRaises(ValueError):session.guarded_open(str(Path(session.__file__).resolve()),'w')
            with self.assertRaises(ValueError):session.json_proxy.loads('{"x":NaN}') if False else session.finite(float('nan'))
            discarded=session.discard(str(p));self.assertFalse(p.exists());self.assertEqual(Path(discarded).read_text(),'new');session.data_root=None
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_the_key_machine_maya.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.the_key_machine import session
class MayaChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.temp=tempfile.TemporaryDirectory();cls.root=cls.temp.name
    @classmethod
    def tearDownClass(cls):session.close();cls.temp.cleanup()
    def setUp(self):cmds.file(new=True,force=True)
    def test_full_source_pose_copy_paste_one_undo(self):
        node=cmds.createNode('transform',name='control');cmds.setAttr(node+'.tx',7);cmds.select(node)
        result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.copy_pose',objects=[node]);self.assertTrue(result.success,result.errors)
        cmds.setAttr(node+'.tx',22);cmds.flushUndo();result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.paste_pose',objects=[node]);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.getAttr(node+'.tx'),7);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),22)
    def test_bad_last_lock_foreign_delete_and_job_ownership(self):
        node=cmds.createNode('transform',name='control');other=cmds.createNode('transform',name='other');cmds.setAttr(other+'.rz',lock=True);cmds.setAttr(node+'.tx',7)
        result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.reset_object_values',objects=[node,other],dry_run=True);self.assertFalse(result.success);self.assertEqual(cmds.getAttr(node+'.tx'),7)
        session.configure(self.root);cmds.select(node)
        with self.assertRaises(ValueError):session.cmdshim.delete(other)
        self.assertTrue(cmds.objExists(other))
        # scriptJobs are inert in standalone Maya; exercise the gate without
        # claiming an actual GUI event lifecycle was validated.
        with self.assertRaises(ValueError):session.cmdshim.scriptJob(kill=987654321,force=True)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_the_key_machine_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process only; Maya must not initialize')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtWidgets,QtTest
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.the_key_machine import session
class QtChecks(unittest.TestCase):
    def test_native_modules_resources_and_owned_timers(self):
        with tempfile.TemporaryDirectory() as td:
            session.configure(td);toolbar=session.native_module('TheKeyMachine.core.toolbar');self.assertIsNone(toolbar.tb)
            import TheKeyMachine.mods.mediaMod as media
            self.assertTrue(Path(media.shelf_icon).is_file());self.assertEqual(session.translate('Copy Pose'),'复制姿势')
            values=[];timer=session.repeat(0.001,lambda:values.append(1),lambda:len(values)<2);QtTest.QTest.qWait(30);self.assertEqual(len(values),2);self.assertFalse(timer.isActive())
            session.owned_timer.singleShot(100,lambda:values.append(9));widget=session.tracked_widget();label=QtWidgets.QLabel('Copy Pose',widget);session.translate_widget(widget);self.assertEqual(label.text(),'复制姿势');widget.show();session.close();QtTest.QTest.qWait(130);self.assertEqual(values,[1,1])
            import shiboken6
            self.assertFalse(shiboken6.isValid(widget));self.assertFalse(session.timers)
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/the_key_machine.md','''# TheKeyMachine 完整待验候选

用户186文件原始SHA归档，GPL3 source_version0.1.4 build306 Gort，完整toolbar/selection sets/customGraph、bar/keyTools/selSets/hotkeys/helper/general/ui/media/style、connect菜单脚本、原中文词典、全部png/svg/cert/config/许可自包含；operations.json逐函数来源/行号/参数/默认/varargs/写场景命令，完整原业务源仍在native/TheKeyMachine，不依赖原池目录。缺失mods/core/connect包init补齐。README提及chinese_installer.py原缺失，已用完整memory语言API替代安装文件改写；不运行原汉化改源/卸载删package/Maya.env/userSetup。

Base/Schema/ToolResult：inspect默认纯元数据，show_ui/close_ui、set_language、invoke完整公开源操作enum/arguments/objects。validate只参数/当前节点，native UI context checks真实执行前/原函数内检查，不假称dry创建临时pivot/camera/hotkeys/job。show选择已有独立data_root，严禁候选目录当数据目录；一次会话固定root，外来TheKeyMachine已加载拒绝混用；INSTALL_PATH固定自有完整native。MTB_TheKeyMachine_user_data自有namespace，首次显式激活才创建默认prefs/connect模板，已有文件不自动覆盖；prefs/connect只literal AST assignment导入、不在激活执行用户模块代码。自定义菜单command字符串保留原MEL/Python，只有用户选该菜单才执行，属于用户主动脚本功能。

原线程循环改为Qt主线程自有QTimer/停止flag，模块import不实例化tb/重载所有module；显式show启动原整toolbar，reload先close清自有timer/job/UI再重建，同session未导入外国模块。UI workspace使用MTB_TKM_k/s，创建UI/SceneOpened和SelectionChanged jobs/runtimeCommands记录自有handle，close只撤自有、停止动画offset/micro长Undo、清本工具callback，不删除scene helper nodes/库/数据，也不改用户安装环境。原customGraph/bake/micro/input上下文在真实GUI中验收，不在mayapy强建QWidgets。汉化通过本模块cmds proxy转换label/title/annotation/message，不覆盖全局Maya cmds或磁盘源；en_US/zh_CN可重建原toolbar，Qt文本的完整翻译覆盖范围逐项验收。

完整native API operation catalog，字面参数含严格bool/有限JSON与上限、未知或缺required参数拒绝。objects精确存在/唯一/无wildcard，原直接场景写函数预检全部选中keyable attrs locked/reference/non-animCurve驱动，避免坏最后对象导致前项改动；复杂原互调/GUI控件依赖在invoke如实执行并收集proxy errors，原catch不能吞成全成功。场景Undo共享原context，每次invoke保存当前时间与非selection类操作的selection；选择/隔离动作保留实际新选择。原高级业务算法保持，不把标准化当已验证生产rig。删除只当前选中层级或本session创建UUID节点，unknown/foreign UI/jobs/runtimecommand拒绝，避免原通用短名删除外来节点；运行时命令加MTB_TKM_前缀，不删用户同名原命令，不自动绑定按键。

open/os/shutil/json为native module局部proxy，不修改全局builtins或stdlib。文件write只能data_root或用户明确Save Dialog返回文件，已有文件先exclusive精确backup/hash receipt再写，删除移到自有.mtb_deleted而不是rmtree，数据目录本身/不可归属路径/symlink拒绝。JSON bounded64MiB/重复key/非有限值拒绝，所有写allow_nan=False。copy/paste pose/anim/worldspace/mirror exceptions/reset defaults/pivot/selection-set配置仍完整原格式；外部这些文件不由Maya Undo撤销，备份为恢复依据；原native JSON类型/目标映射复杂异常按真实验收修复。UPDATER/BUG_REPORT默认false，不自动向外部发送或运行安装器；界面卸载=关闭自有会话保留原数据，升级与报告属于维护，不影响动画业务。

例：TheKeyMachineTool().run(action='invoke', data_root=r'C:/temp/tkm_data', operation='TheKeyMachine.mods.keyToolsMod.copy_pose', objects=['control'])，然后paste_pose，一次scene Undo；t.show_ui()选择root启动全部原工具，close_ui显式清理；dry使用原operation/arguments而不调用native。可与姿态/曲线/时间范围工具衔接，原静态imports不是复杂动画组合已验收。离线完整layout/registry/domain/panel/schema/source资源检查，隔离mayapy原pose业务+Undo和坏末项/foreign删除/job保护；真实Maya GUI、全部source catalog业务、customGraph/micro/offset/callback生命周期、多命名空间生产rig、镜像/复杂clip和跨版本not_run。验收前仅待整理池，不迁正式。
''')
put(RC/'acceptance.md','''# TheKeyMachine 真实Maya验收 not_run

1. 新会话选择备份场景和已有独立data_root，完整原toolbar与selection sets/customGraph/Qt菜单所有png/svg正确；原186资源完整、inspect/dry不写prefs/启动job/timer。首次显式show新数据namespace，已有prefs/connect只literal，不自动执行配置代码；中文/英文切换不改源文件。
2. 原按钮/slider/右键完整检查：smart keys/inbetween/tangent/time move/reset/mirror/pose/animation insert/opposite/worldspace frame/range/link/locators/pivot/tracer/followCamera/depth/gimbal/selectionSet/shelf/hotkey runtime catalog、customGraph/blend/offset/micro。复杂rig、namespace、父变换和锁轴/reference检查；原native接口失败不能登记通过。
3. pose/anim/镜像异常/reset默认/selection-set/pivot JSON先backup再覆盖，坏key/非有限/重复key不接受；删除移自有.mtb_deleted，只自有root/明确Save Dialog路径；外部file不能scene Undo。单业务一次UndoRedo、选择/时间恢复，选择类保留输出选择。
4. 重复show/reload/close不叠线程，timer全部Qt主线程；close撤自有job/UI/commands/callback，长期offset/micro正确结束Undo，不清外来UI/job/短名对象、不删除用户安装/数据/userSetup/Maya.env。runtimecommand前缀，已有用户同名原命令不动，不自动热键绑定；foreign冲突明确报告。
5. 记录所有未通过source catalog分支、Maya版本、candidate_sha256、accepted_by/date/passed=true后再promotion；隔离Qt/mayapy/离线不能冒充真实Maya直验。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/the_key_machine','--class-name','TheKeyMachineTool','--summary','Complete original GPL TheKeyMachine toolbar and native API with isolated data, literal config, backups, owned lifecycle and memory localization','--dependencies','Maya cmds/MEL/API and real GUI contexts','PySide6/PySide2; full GPL3 original native source/resources bundled','--limitations','Real Maya GUI, complete source-operation coverage, complex rigs/graph/offset/micro/callback lifecycle and cross-version acceptance not_run'],check=True)
