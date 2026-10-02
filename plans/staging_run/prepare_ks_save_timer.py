"""Complete bilingual KS SaveTimer native suite with explicit host and owned state."""
import ast,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/08_utilities_system/ks_save_timer_v1_3_0';SOURCE=UNIT/'KS_SaveTimer-1.3.0';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/ks_save_timer_v1_3_0'
for locale,label in [('en','【原版】'),('zh','【汉化版】')]:shutil.copytree(SOURCE/label/'ks_saveTimer',PKG/'native'/locale/'ks_saveTimer',dirs_exist_ok=True)
shutil.copytree(SOURCE/'docs',PKG/'original_docs',dirs_exist_ok=True)
other=ROOT/'tools_staging_pool/08_utilities_system/ks_node_outliner_v2_2/release_candidate/maya_toolkit/tools/ks_node_outliner_v2_2'
shutil.copyfile(other/'compat_six.py',PKG/'compat_six.py')
put(PKG/'qt_compat.py',(other/'qt_compat.py').read_text().replace('Signal=QtCore.Signal;wrapInstance','Signal=QtCore.Signal;Property=QtCore.Property;wrapInstance'))
put(PKG/'storage.py',r'''"""Bounded typed history/config, own paths and byte-exact backups before replace."""
from pathlib import Path
import configparser,io,json,math,os,re,tempfile,uuid
NUMBERS={'timer_a_starttime','timer_b_starttime','timer_c_starttime','timer_flash_a_starttime','timer_flash_starttime','timer_flash_b_starttime','timer_flash_freq'}
COLORS={f'timer_{group}_{color}color' for group in ('a','b','c','flash_a','flash_b','pause','default') for color in ('bg','text')}
FLAGS={'timer_automute','timer_autopause'}
def root(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Explicit state directory required')
    p=Path(value)
    if not p.is_absolute() or not p.is_dir() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Existing absolute non-symlink directory required')
    if Path(__file__).parent.resolve() in (p.resolve(),*p.resolve().parents):raise ValueError('Candidate bundle is immutable')
    return p
def history(data):
    if not isinstance(data,dict) or set(data)-{'maya','nuke','desktop'}:raise ValueError('Invalid history hosts')
    for host,files in data.items():
        if not isinstance(files,dict) or len(files)>10000:raise ValueError('History file bound')
        for name,row in files.items():
            if not isinstance(name,str) or not name or len(name)>4096 or not isinstance(row,dict) or set(row)-{'totalTime','lastSave','dirPath','history'}:raise ValueError('Invalid history row')
            for key in ('totalTime',):
                if type(row.get(key)) is not int or not 0<=row[key]<=1000000000:raise ValueError('Nonnegative integer minutes required')
            if not isinstance(row.get('history'),dict) or len(row['history'])>10000:raise ValueError('Invalid version history')
            for key in ('lastSave','dirPath'):
                if row.get(key) is not None and (not isinstance(row[key],str) or len(row[key])>4096):raise ValueError('Invalid history text')
            for version,item in row['history'].items():
                if not isinstance(version,str) or not version.isdigit() or len(version)>12 or not isinstance(item,dict) or set(item)-{'time','date','fileName'}:raise ValueError('Invalid version record')
                if type(item.get('time')) is not int or not 0<=item['time']<=1000000000:raise ValueError('Invalid version minutes')
                for key in ('date','fileName'):
                    if not isinstance(item.get(key),str) or len(item[key])>4096:raise ValueError('Invalid version strings')
    return data
def read_history(path):
    p=Path(path)
    if not p.exists():return {}
    if not p.is_file() or p.is_symlink() or p.stat().st_size>32*1024*1024:raise ValueError('Invalid or oversized history')
    def pairs(rows):
        out={}
        for k,v in rows:
            if k in out:raise ValueError('Duplicate history key')
            out[k]=v
        return out
    return history(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def config_value(section,key,value):
    if section=='general' and key in FLAGS:
        if type(value) is bool:return str(value)
        if value in ('True','False','true','false'):return str(value).title()
        raise ValueError('Strict boolean required')
    if section=='timerOptions' and key in NUMBERS:
        if isinstance(value,str) and value.isdigit():value=int(value)
        if type(value) is not int or not (50 if key=='timer_flash_freq' else 0)<=value<=1000000:raise ValueError('Bounded timer integer required')
        return str(value)
    if section=='timerOptions' and key in COLORS:
        if hasattr(value,'getRgb'):value='rgba'+str(value.getRgb())
        if not isinstance(value,str) or not re.fullmatch(r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',value) or any(int(n)>255 for n in re.findall(r'\d+',value)):raise ValueError('RGBA channels 0-255 required')
        return value
    raise ValueError('Unknown configuration option')
def ini(text):
    if not isinstance(text,str) or len(text)>1024*1024:raise ValueError('Config exceeds 1MiB')
    parser=configparser.ConfigParser(interpolation=None,strict=True);parser.read_string(text)
    if parser.defaults():raise ValueError('INI defaults not allowed')
    for section in parser.sections():
        if section not in ('timerOptions','general'):raise ValueError('Unknown INI section')
        for key,value in parser.items(section):config_value(section,key,value)
    return parser
def read_config(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>1024*1024:raise ValueError('Invalid or oversized INI')
    return ini(p.read_text(encoding='utf8'))
def atomic(path,blob):
    from . import session
    p=Path(path)
    if session.data_root is None or p.parent.resolve()!=session.data_root.resolve() or p.name not in ('ksSaveTimer_config.ini','KSSaveTimer_timeTrackHistory.json') or p.is_symlink():raise ValueError('Only own configured state files writable')
    if p.suffix=='.json':history(json.loads(blob.decode('utf8')))
    else:ini(blob.decode('utf8'))
    backup=None
    if p.exists():
        if not p.is_file():raise ValueError('Existing non-file refused')
        old=p.read_bytes();backup=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
        with backup.open('xb') as f:f.write(old)
        if backup.read_bytes()!=old:raise IOError('Backup mismatch')
        fd,tmp=tempfile.mkstemp(prefix='.mtb_save_timer_',dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:f.write(blob)
            os.replace(tmp,p)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    else:
        with p.open('xb') as f:f.write(blob)
    return {'path':str(p),'backup':str(backup) if backup else None}
def write_history(path,data):return atomic(path,(json.dumps(history(data),ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8'))
def write_config(path,parser):
    stream=io.StringIO();parser.write(stream);return atomic(path,stream.getvalue().encode('utf8'))
''')
put(PKG/'session.py',r'''"""Native singletons owned by one explicit host/state/locale session; no auto startup."""
from pathlib import Path
import importlib,sys
from . import storage
data_root=None;host=None;locale=None;window=None;closing=False;callback_ids=[];nuke_callbacks=[];embedded=None;watched_file=None
ROOT=Path(__file__).parent
def configure(value,language='zh',runtime='maya',watch_file=None):
    global data_root,host,locale,watched_file
    p=storage.root(value)
    if language not in ('zh','en') or runtime not in ('maya','nuke','desktop'):raise ValueError('Unknown language/host')
    if data_root is not None and (p!=data_root or language!=locale or runtime!=host):raise RuntimeError('Native singletons require same state/host/language or a fresh process')
    old=sys.modules.get('ks_saveTimer')
    if old is not None and ROOT.resolve() not in Path(getattr(old,'__file__','')).resolve().parents:raise RuntimeError('Foreign KS SaveTimer loaded; use fresh session')
    if (p/'ksSaveTimer_config.ini').exists():storage.read_config(p/'ksSaveTimer_config.ini')
    storage.read_history(p/'KSSaveTimer_timeTrackHistory.json')
    if watch_file is not None:
        q=Path(watch_file)
        if not q.is_absolute() or not q.is_file() or q.is_symlink():raise ValueError('Existing explicit watch file required')
        if q.resolve() in (p.resolve(),*p.resolve().parents) or p.resolve() in q.resolve().parents:raise ValueError('State directory must not be watched recursively')
        watched_file=str(q)
    data_root=p;host=runtime;locale=language
    source=ROOT/'native'/language
    if str(source) not in sys.path:sys.path.insert(0,str(source))
    return importlib.import_module('ks_saveTimer')
def current_file():
    if host=='maya':
        from maya import cmds
        return cmds.file(q=True,sn=True) or None
    if host=='nuke':
        import nuke
        value=nuke.root().knob('name').value();return None if value in ('','Root') else value
    return watched_file
def singleton(module,name,*args,**kwargs):
    cls=getattr(module,'_'+name);instance=getattr(module,'_INSTANCE',None)
    if instance is None:
        instance=cls(*args,**kwargs);module._INSTANCE=instance
    return instance
def init_callbacks(obj):
    if host=='maya':
        from maya import OpenMaya
        for event,signal in ((OpenMaya.MSceneMessage.kAfterOpen,obj.fileOpened),(OpenMaya.MSceneMessage.kAfterNew,obj.fileOpened),(OpenMaya.MSceneMessage.kAfterSave,obj.fileSaved)):
            callback_ids.append(OpenMaya.MSceneMessage.addCallback(event,lambda *args,s=signal:s.emit()))
    elif host=='nuke':
        import nuke
        for kind,signal in (('ScriptLoad',obj.fileOpened),('ScriptClose',obj.fileOpened),('ScriptSave',obj.fileSaved)):
            callback=lambda *args,s=signal:s.emit();getattr(nuke,'addOn'+kind)(callback);nuke_callbacks.append((kind,callback))
def start_callbacks():
    module=importlib.import_module('ks_saveTimer.libApp.getLibApp').__LIB_APP__;obj=module.appCallbacks()
    if host=='desktop':
        if watched_file:obj.setWatchFile(watched_file)
    elif not callback_ids and not nuke_callbacks:init_callbacks(obj)
def show(value,language='zh',runtime='maya',embed=False,watch_file=None,parent=None):
    global window
    configure(value,language,runtime,watch_file)
    from .qt_compat import QtWidgets,QtCore
    app=QtWidgets.QApplication.instance()
    if app is None or QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Existing host Qt main thread required')
    if runtime=='maya':
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    elif runtime=='nuke':
        import nuke
        if not nuke.env.get('gui'):raise RuntimeError('Real Nuke GUI required')
    close();start_callbacks()
    module=importlib.import_module('ks_saveTimer.lib.GUI_saveTimer')
    try:
        window=module.GUI_SaveTimer(parent);window.setObjectName('MTB_KS_SaveTimer_Widget');window.setWindowTitle('KS Save Timer')
        window.setFixedHeight(24);window.setMinimumWidth(65)
        if embed and runtime=='maya':importlib.import_module('ks_saveTimer.libApp.libMaya').QT_embedUItoInterface('MTB_KS_SaveTimer',window)
        elif embed and runtime=='nuke':
            bars=[w for w in QtWidgets.QApplication.allWidgets() if isinstance(w,QtWidgets.QStatusBar)]
            if len(bars)!=1:raise RuntimeError('Unique Nuke status bar required')
            bars[0].insertPermanentWidget(0,window)
        window.show();return window
    except Exception:close();raise
def close():
    global window,closing,embedded
    if closing:return
    closing=True
    try:
        tm=sys.modules.get('ks_saveTimer.lib.timer');timer=getattr(tm,'_INSTANCE',None)
        if timer:timer.stop();timer.blockSignals(True)
        owned=window;window=None
        if owned:
            for name in ('ANIM_FLASH','ANIM_SAVE','ANIM_RESET'):getattr(owned,name).stop()
            try:owned.close();owned.deleteLater()
            except RuntimeError:pass
        if callback_ids:
            from maya import OpenMaya
            for callback in callback_ids:OpenMaya.MMessage.removeCallback(callback)
            callback_ids.clear()
        if nuke_callbacks:
            import nuke
            for kind,callback in nuke_callbacks:getattr(nuke,'removeOn'+kind)(callback)
            nuke_callbacks.clear()
        desktop=sys.modules.get('ks_saveTimer.libApp.libDesktop');obj=getattr(desktop,'_INSTANCE',None)
        if obj:
            obj.blockSignals(True)
            obj.systemWatcher.removePaths(obj.systemWatcher.files()+obj.systemWatcher.directories())
        if embedded:
            from maya import cmds,OpenMayaUI
            name,pointer=embedded
            if cmds.layout(name,exists=True):
                if not pointer or int(OpenMayaUI.MQtUtil.findLayout(name) or 0)!=pointer:raise RuntimeError('Foreign layout replacement preserved')
                cmds.deleteUI(name)
            embedded=None
        # Disconnect widget-owned closures before reopening; tracker/callback signals
        # otherwise retain dead wrappers. Dispose and recreate native instances.
        for name in ('ks_saveTimer.lib.tracker','ks_saveTimer.lib.timer','ks_saveTimer.lib.config','ks_saveTimer.libApp.libDesktop','ks_saveTimer.libApp.libMaya','ks_saveTimer.libApp.libNuke'):
            module=sys.modules.get(name);obj=getattr(module,'_INSTANCE',None)
            if obj:
                try:obj.deleteLater()
                except RuntimeError:pass
                module._INSTANCE=None
    finally:closing=False
def embed_maya(widget):
    global embedded
    from maya import cmds,mel,OpenMayaUI
    from .qt_compat import QtWidgets,wrapInstance
    name='MTB_KS_SaveTimer_rootLayout'
    if cmds.layout(name,exists=True):raise RuntimeError('Existing status-line layout preserved')
    button=mel.eval('$tmpVar=$gLayerEditorButton');parent=cmds.formLayout(cmds.iconTextCheckBox(button,q=True,p=True),q=True,p=True)
    children=cmds.formLayout(parent,q=True,childArray=True) or []
    if not children:raise RuntimeError('No Maya status-line attachment target')
    current=cmds.setParent(q=True)
    try:
        cmds.setParent(parent);row=cmds.rowLayout(name);pointer=int(OpenMayaUI.MQtUtil.findLayout(row) or 0);embedded=(row,pointer)
        cmds.formLayout(parent,e=True,attachControl=[(row,'right',10,children[-1])],attachNone=[(row,'left')])
        if not pointer:raise RuntimeError('Native layout Qt pointer absent')
        wrapper=wrapInstance(pointer,QtWidgets.QWidget);layouts=wrapper.findChildren(QtWidgets.QHBoxLayout)
        if not layouts:raise RuntimeError('Native status-line Qt layout absent')
        layouts[0].addWidget(widget)
    finally:cmds.setParent(current)
''')
# Keep both complete source trees. Replace only scoped compatibility/persistence
# and lifecycle operations; never execute an original entrypoint while preparing.
for p in sorted((PKG/'native').rglob('*.py')):
    s=p.read_text(encoding='utf-8-sig');tree=ast.parse(s);lines=s.splitlines();edits=[]
    for n in tree.body:
        if isinstance(n,ast.Try) and any('PySide' in ast.get_source_segment(s,child) for child in n.body):
            edits.append((n.lineno-1,n.end_lineno,'from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance\n_PYSIDE_VERSION_ = 2'))
    for a,b,t in sorted(edits,reverse=True):lines[a:b]=t.splitlines()
    s='\n'.join(lines)+'\n';s=s.replace('import six','from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six').replace('from six.moves import range','').replace('from six.moves.configparser import ConfigParser','from configparser import ConfigParser').replace('omui.MQtUtil_findLayout','omui.MQtUtil.findLayout').replace("filePath is ''","filePath == ''").replace('.exec_(','.exec(').replace('def exec_(self):','def exec(self):').replace('.setWeight(120)','.setWeight(QtGui.QFont.Bold)').replace('.setWeight(75)','.setWeight(QtGui.QFont.Bold)').replace('.setWeight(87)','.setWeight(QtGui.QFont.Black)').replace('timer_autoMute','timer_automute').replace('timer_autoPause','timer_autopause')
    for literal in ('0','1','2','3','4',"'background'","'text'"):s=s.replace(' is '+literal+':',' == '+literal+':')
    # Every native QObject singleton becomes a plain QObject with explicit factory.
    for name in ('configuration','timerObject','timeTracker','appCallbacks'):
        marker='@six.add_metaclass(Singleton.QtSingletonMetaclass)\nclass '+name+'(QtCore.QObject):'
        desktop='class appCallbacks(six.with_metaclass(Singleton.QtSingletonMetaclass, QtCore.QObject)):'
        if marker in s or name=='appCallbacks' and desktop in s:
            s=s.replace(marker,'class _'+name+'(QtCore.QObject):').replace(desktop,'class _appCallbacks(QtCore.QObject):').replace('super('+name+',','super(_'+name+',')
            s+='\n_INSTANCE=None\ndef '+name+'(*args,**kwargs):\n    import sys\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton\n    return singleton(sys.modules[__name__],"'+name+'",*args,**kwargs)\n'
    replacements={}
    if p.name=='getLibApp.py':
        s=s.replace('__HOST_APP__ = getHostApp()','from maya_toolkit.tools.ks_save_timer_v1_3_0 import session\n__HOST_APP__ = session.host\nif __HOST_APP__ is None:raise RuntimeError("Configure explicit host first")')
    if p.name=='config.py':
        s=s.replace('self.parser = ConfigParser()','self.parser = ConfigParser(interpolation=None)')
        s=s.replace('            self.parser.read([self._config_path])','            from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import read_config\n            self.readDefaultConfig()\n            self.parser.read_dict({k:dict(v) for k,v in read_config(self._config_path).items() if k!="DEFAULT"})')
        s=s.replace('self._DICT_[section][key] = bool(data)',"self._DICT_[section][key] = data.lower() == 'true'")
        s=s.replace("    def set(self, section, key, value=''):","    def set(self, section, key, value=''):\n        from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import config_value\n        config_value(section,key,value)")
        replacements={'getConfigPath':'def getConfigPath(self):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import data_root\n    if data_root is None:raise RuntimeError("Configure state directory first")\n    return str(data_root/"ksSaveTimer_config.ini")','writeConfig':'def writeConfig(self):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import write_config\n    return write_config(self._config_path,self.parser)'}
    if p.name=='tracker.py':
        replacements={'getHistoryPath':'def getHistoryPath(self):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import data_root\n    return str(data_root/"KSSaveTimer_timeTrackHistory.json")','readFromJson':'def readFromJson(filePath):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import read_history\n    return read_history(filePath)','writeToJson':'def writeToJson(localData,filePath):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import write_history\n    return write_history(filePath,localData)'}
        s=s.replace('        filePath = __LIB_APP__.get_filePath()','        filePath = __LIB_APP__.get_filePath()\n        if not filePath:return')
        s=s.replace('    def addHistory(self, fileName, minutes):','    def addHistory(self, fileName, minutes):\n        if not isinstance(fileName,str) or not os.path.isabs(fileName) or type(minutes) is not int or not 0<=minutes<=1000000:raise ValueError("Absolute filename/nonnegative integer minutes required")')
        s=s.replace('        for fileName in topNodes:','        for fileName in topNodes or []:').replace('six.iteritems(versionNodes)','six.iteritems(versionNodes or {})')
    if p.name=='timer.py':
        s=s.replace('self.counter -= self.idleTarget','self.counter = max(0,self.counter-self.idleTarget)').replace('self.counterTotal -= self.idleTarget','self.counterTotal = max(0,self.counterTotal-self.idleTarget)')
        s=s.replace('    def setTime(self, value):','    def setTime(self, value):\n        if type(value) is not int or not 0<=value<=1000000:raise ValueError("Bounded nonnegative timer minutes")')
    if p.name=='libMaya.py':
        replacements={'QT_embedUItoInterface':'def QT_embedUItoInterface(uiName,widget,target="statusLine"):\n    if target!="statusLine":raise ValueError("Only statusLine supported")\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import embed_maya\n    return embed_maya(widget)','deleteLayoutFromUI':'def deleteLayoutFromUI(uiName):\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import close\n    return close()'}
        # Replace callback constructor body, not QObject signals/type.
        tree=ast.parse(s);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_appCallbacks');n=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['    def __init__(self,parent=None):','        super().__init__(parent)','        from maya_toolkit.tools.ks_save_timer_v1_3_0.session import init_callbacks','        init_callbacks(self)'];s='\n'.join(lines)+'\n'
    if p.name=='libNuke.py':
        tree=ast.parse(s);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_appCallbacks');n=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__');lines=s.splitlines();lines[n.lineno-1:n.end_lineno]=['    def __init__(self,parent=None):','        super().__init__(parent)','        from maya_toolkit.tools.ks_save_timer_v1_3_0.session import init_callbacks','        init_callbacks(self)'];s='\n'.join(lines)+'\n'
    if p.name=='libDesktop.py':
        s=s.replace('cls.systemWatcher = QtCore.QFileSystemWatcher()','cls.systemWatcher = QtCore.QFileSystemWatcher(cls)').replace('def emitSaveSignal(cls):','def emitSaveSignal(cls,*args):').replace('def checkNewFiles(cls):','def checkNewFiles(cls,*args):').replace('fileExt = os.path.splitext(path)','fileExt = os.path.splitext(path)[1]')
        s+='\ndef get_filePath():\n    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import current_file\n    return current_file()\n'
        s=s.replace('    def emitSaveSignal(cls,*args):','    def emitSaveSignal(cls,*args):\n        from maya_toolkit.tools.ks_save_timer_v1_3_0 import session\n        if args and isinstance(args[0],str) and os.path.isfile(args[0]):session.watched_file=args[0]')
        s=s.replace("                print('newFile:', file)","                from maya_toolkit.tools.ks_save_timer_v1_3_0 import session\n                session.watched_file=os.path.normpath(os.path.join(cls.currentWatchFolder,file))\n                print('newFile:', file)")
    if p.name in ('GUI_config.py','GUI_tracker.py'):
        replacements['center']='def center(self):\n    screen=QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos()) or QtGui.QGuiApplication.primaryScreen()\n    frame=self.frameGeometry();frame.moveCenter(screen.availableGeometry().center());self.move(frame.topLeft())'
    if p.name=='GUI_saveTimer.py':
        s=s.replace('    def openConfig(self):','    def closeEvent(self,event):\n        from maya_toolkit.tools.ks_save_timer_v1_3_0 import session\n        if session.window is self:session.close()\n        super().closeEvent(event)\n\n    def openConfig(self):',1)
        s=s.replace('    def formatTimeToString(self, minutes):','    def formatTimeToString(self, minutes):\n        minutes=int(round(minutes))')
    if replacements:
        tree=ast.parse(s);lines=s.splitlines();edits=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.FunctionDef) and n.name in replacements:
                indent=' '*n.col_offset;edits.append((n.lineno-1,n.end_lineno,'\n'.join(indent+line for line in replacements[n.name].splitlines())))
        for a,b,t in sorted(edits,reverse=True):lines[a:b]=t.splitlines()
        s='\n'.join(lines)+'\n'
    put(p,s)
put(PKG/'__init__.py',r'''from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import storage
class KSSaveTimerTool(BaseMayaTool):
    tool_id='ks_save_timer_v1_3_0';tool_name='KS Save Timer 保存提醒与工时';category='scene_hygiene';version='1.0.0'
    description='Complete bilingual native timer, idle detection, color flashing, configuration and file-version history; never autosaves scenes'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','start','pause','reset','set_time','read_history','set_option'],'default':'inspect'},'data_root':{'type':'string'},'language':{'type':'string','enum':['zh','en'],'default':'zh'},'host':{'type':'string','enum':['maya','nuke','desktop'],'default':'maya'},'embed':{'type':'boolean','default':False},'watch_file':{'type':'string'},'minutes':{'type':'integer','minimum':0,'maximum':1000000},'section':{'type':'string','enum':['general','timerOptions']},'key':{'type':'string'},'value':{},'persist':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for key in ('embed','persist'):
                if key in kw and type(kw[key]) is not bool:raise ValueError('Strict boolean '+key)
            if kw.get('host','maya') not in ('maya','nuke','desktop') or kw.get('language','zh') not in ('zh','en'):raise ValueError('Unknown host/language')
            if action in ('show_ui','read_history'):storage.root(kw.get('data_root'))
            if action=='set_time' and (type(kw.get('minutes')) is not int or not 0<=kw['minutes']<=1000000):raise ValueError('Bounded integer minutes required')
            if action=='set_option':storage.config_value(kw.get('section'),kw.get('key'),kw.get('value'))
            if 'watch_file' in kw:
                from pathlib import Path
                p=Path(kw['watch_file'])
                if not p.is_absolute() or not p.is_file() or p.is_symlink():raise ValueError('Existing watch file required')
            return ToolResult.ok(message='无Qt/回调/计时/文件写入的预检')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'languages':['zh','en'],'hosts':['maya','nuke','desktop'],'autosave':False,'gui_acceptance':'not_run'})
        if action=='read_history':return ToolResult.ok(data={'history':storage.read_history(storage.root(kw['data_root'])/'KSSaveTimer_timeTrackHistory.json')})
        from . import session
        if action=='show_ui':session.show(kw['data_root'],kw.get('language','zh'),kw.get('host','maya'),kw.get('embed',False),kw.get('watch_file'));return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if session.window is None:raise RuntimeError('Open owned timer UI first')
        timer=session.window.TIMER
        if action=='start':session.window.setPauseToggle(False)
        elif action=='pause':session.window.setPauseToggle(True)
        elif action=='reset':timer.reset()
        elif action=='set_time':timer.setTime(kw['minutes'])
        elif action=='set_option':
            config=session.window._CONFIG_;config.set(kw['section'],kw['key'],kw['value'])
            if kw.get('persist'):config.writeConfig()
        return ToolResult.ok(data={'counter':timer.counter,'active':timer.isActive()})
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=3,caption='KS Save Timer：选择独立计时配置与历史目录')
        if not values:return None
        from .session import show
        return show(values[0],parent=parent)
''')
put(RC/'tests/test_ks_save_timer_v1_3_0.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.ks_save_timer_v1_3_0 import KSSaveTimerTool
    tool=KSSaveTimerTool()
from maya_toolkit.tools.ks_save_timer_v1_3_0 import storage,session
class Checks(unittest.TestCase):
    def test_pure_preflight_typed_config_history_and_backups(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('ks_saveTimer',sys.modules)
        self.assertEqual(storage.config_value('general','timer_autopause','False'),'False')
        with tempfile.TemporaryDirectory() as td:
            session.data_root=Path(td);p=Path(td)/'KSSaveTimer_timeTrackHistory.json';storage.write_history(p,{'desktop':{}});original=p.read_bytes();row=storage.write_history(p,{'desktop':{}});self.assertEqual(Path(row['backup']).read_bytes(),original)
            with self.assertRaises(ValueError):storage.write_history(p,{'desktop':{'bad':{'totalTime':-1,'history':{}}}})
            self.assertEqual(p.read_bytes(),original)
            with self.assertRaises(ValueError):storage.ini('[general]\ntimer_autopause=malformed\n')
            with self.assertRaises(ValueError):storage.atomic(Path(td)/'foreign.json',b'{}')
            self.assertFalse((Path(td)/'foreign.json').exists());session.data_root=None
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_ks_save_timer_v1_3_0_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.ks_save_timer_v1_3_0 import session,storage
class QtChecks(unittest.TestCase):
    def test_complete_timer_history_config_and_owned_close(self):
        with tempfile.TemporaryDirectory() as td:
            watch=Path(td)/'asset_v001_work.ma';watch.write_text('unmodified');state=Path(td)/'state';state.mkdir()
            win=session.show(str(state),language=os.environ.get('KS_TEST_LOCALE','zh'),runtime='desktop',watch_file=str(watch))
            timer=win.TIMER;self.assertTrue(timer.isActive());self.assertGreaterEqual(len(win.contextMenu.actions()),6)
            timer.setTime(12);self.assertEqual(timer.counter,12)
            win._CONFIG_.set('general','timer_autopause','False');self.assertFalse(win._CONFIG_.get('general','timer_autopause'));win._CONFIG_.writeConfig()
            timer.CALLBACKS.fileSaved.emit();self.assertEqual(timer.counter,0);self.assertEqual(timer.saveCount,1)
            saved=storage.read_history(state/'KSSaveTimer_timeTrackHistory.json');self.assertEqual(next(iter(saved['desktop'].values()))['totalTime'],12)
            from ks_saveTimer.lib.GUI_config import saveTimer_config_GUI
            from ks_saveTimer.lib.GUI_tracker import GUI_timeTracker
            from ks_saveTimer.lib.GUI_saveTimer import aboutDialog_ksSaveTimer
            config=saveTimer_config_GUI(win);history=GUI_timeTracker(win);about=aboutDialog_ksSaveTimer(win)
            callbacks=timer.CALLBACKS;self.assertIn(str(watch),callbacks.systemWatcher.files())
            session.close();self.assertFalse(timer.isActive());self.assertEqual(callbacks.systemWatcher.files(),[]);self.assertEqual(callbacks.systemWatcher.directories(),[]);self.assertEqual(watch.read_text(),'unmodified')
            again=session.show(str(state),language=os.environ.get('KS_TEST_LOCALE','zh'),runtime='desktop',watch_file=str(watch));self.assertIsNot(again.TIMER,timer);session.close()
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_ks_save_timer_v1_3_0_maya.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_timer',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.ks_save_timer_v1_3_0 import session
class MayaChecks(unittest.TestCase):
    def test_current_filename_query_and_dry_run_no_callbacks(self):
        cmds.file(new=True,force=True);session.host='maya';self.assertIsNone(session.current_file())
        with tempfile.TemporaryDirectory() as td:
            cmds.file(rename=str(Path(td)/'scene.ma'));result=tool.run(action='show_ui',data_root=td,dry_run=True);self.assertTrue(result.success,result.errors);self.assertEqual(Path(session.current_file()).name,'scene.ma');self.assertEqual(session.callback_ids,[]);self.assertIsNone(session.window);self.assertEqual(list(Path(td).iterdir()),[])
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/ks_save_timer_v1_3_0.md','''# KS SaveTimer 1.3 完整中英文候选

39原始文件SHA归档，完整中英文timerWidget/GUI/config/tracker/history/stat/about、Maya/Nuke/Desktop lib与runApp、README/EULA PDF保留。六兼容源自固定官方MIT六模块自包含，Qt5/6 facade/Signal/Property/shiboken、Python3/配置bool(False)与idle扣减不负数、Qt6旧QDesktopWidget/font enum确定兼容修复；旧six多metaclass QObject单例改显式单实例factory，功能与共享signal保留。Base/Schema/ToolResult默认inspect/validate纯，无Qt/回调/定时/配置写入；API show/close/start/pause/reset/set_time/read_history/set_option完整，未来layout/注册挂面板预制。

实际用途是保存间隔提醒/计时/idle detection/阈值颜色/flash/reset/save动画/选项/文件版本工时历史，不自动保存scene。一次host(maya/nuke/desktop)+language(zh/en)+data_root固定，不能热切或混foreign旧模块；独立现有目录中仅ksSaveTimer_config.ini和KSSaveTimer_timeTrackHistory.json写入，不用HOME、包内默认、旧KS_TIMETRACKER环境变量。既有数据严格全量校验；INI无插值/重复未知项/限定bool/颜色/时间；JSON32MiB/host/计时/version结构严格校验。覆盖和删除历史通过native保存都先exact backup再atomic；失败传播，外部写不可Maya Undo。旧版本按basename归档，跨项目相同basename可能归在同项，原行为保留且在直验中重点核对，不声称自动去冲突。

实际Maya宿主用自有MSceneMessage kAfterNew/Open/Save IDs；Nuke保留addOnScriptLoad/Close/Save并精确记录同callable用于remove；desktop只有明确watch_file才QFileSystemWatcher，不监听自有state目录，修复splitext原tuple不能endswith与signal参数。关闭只移本会话listener/timer/animations/dialog/widget；reopen重建单例避免旧widget信号closure，不杀foreign scriptJob或覆盖全局hook。Maya嵌入statusLine用独立MTB rootLayout，创建时MQt pointer记录/foreign同名替代保护，恢复setParent；Nuke statusbar唯一时可嵌入，自有widget移除不改原statusbar。完整旧runApp源作为兼容参考保留，框架session入口负责生命周期，主线程/真实host Qt要求不静默退desktop。

Maya scene是读取当前文件名和保存后通知，预检不创建回调/写scene，不需要scene Undo。本工具可与保存/版本管理工具手动衔接，不证明静态import即组合成功。离线typed数据/精确备份/foreign写拒绝、隔离Maya文件名与dry无Qt/listener、独立Qt中英文完整timer/options/history/about/保存signal计时持久化/关闭watcher/reopen；实际Maya GUI statusLine/真实save callback及Nuke GUI/原复杂历史/跨版本not_run。
''')
put(RC/'acceptance.md','''# KS SaveTimer 真实GUI验收 not_run

1. 新Maya会话选独立state目录，中英文各新会话，完整浮动/嵌statusLine计时、pause/mute/reset/idle/颜色阈值/flash/保存动画/Options/History/About。它只提醒保存，不能记成自动保存功能。
2. 保存临时scene触发自有kAfterSave，打开/新建归零，分钟/idle扣减不负，unsaved不写history。同目录v001/v002文件与不同项目同basename核对原历史汇总行为，不满意时在candidate修复后再验收。
3. 配置/历史只写独立state两个文件；已有每次先精确backup，坏末项不覆盖；旧HOME/KS_TIMETRACKER/原包与测试scene不变。native历史删除确认后备份，数据保存不可Maya Undo。
4. close/X/remove只停止own timer/animation/MSceneMessage/QFileSystemWatcher；reopen不叠监听，foreign scriptJob/callback/statusLine保留。真实Maya save events/Qt嵌入、Nuke唯一statusBar/save callbacks、desktop指定watch_file的新版本/原file替换需实测。中英文/跨版本每项记录accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/ks_save_timer_v1_3_0','--class-name','KSSaveTimerTool','--summary','Complete bilingual original save timer/idle/color/history/config for explicit Maya, Nuke or desktop host with scoped state backups and callback cleanup','--dependencies','Real Maya/Nuke Qt GUI or desktop QApplication','Bundled six MIT notice; original EULA/manual retained','--limitations','Real Maya/Nuke GUI embedding/save callback/idle focus/complex version history/cross-version acceptance not_run; original basename-based history may combine same basename across projects'],check=True)
