"""Preserve complete licensed Maya Tabs source, isolate state and guard file changes."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/08_utilities_system/maya_tabs_v1_3a';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/maya_tabs_v1_3a'
shutil.copytree(UNIT/'plug-ins/Maya-Tabs_Files',PKG/'resources',dirs_exist_ok=True)
shutil.copyfile(UNIT/'How to Install - Maya Tabs.jpg',PKG/'original_install.jpg')
qt=ROOT/'tools_staging_pool/08_utilities_system/ks_node_outliner_v2_2/release_candidate/maya_toolkit/tools/ks_node_outliner_v2_2/qt_compat.py'
put(PKG/'qt_compat.py',qt.read_text().replace('Signal=QtCore.Signal;wrapInstance','isValid=shiboken.isValid\nSignal=QtCore.Signal;wrapInstance'))
put(PKG/'storage.py',r'''from pathlib import Path
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
''')
put(PKG/'session.py',r'''from pathlib import Path
import builtins,copy,importlib,io,json,sys,types
from . import storage
ROOT=Path(__file__).parent;data_root=None;native=None;window=None;preview=False;closing=False;callbacks=[];generation=0;ui_windows={};dialog_outputs=set();errors=[]
class Versions:
    def current(self):
        from maya import cmds
        return str(cmds.about(version=True))
versions=Versions()
def load(value,desktop_preview=False):
    global data_root,native,preview
    p=storage.root(value)
    if data_root is not None and p!=data_root:raise RuntimeError('Use one state root or fresh session')
    if (p/'Maya-Tabs.ini').exists():storage.read(str(p/'Maya-Tabs.ini'))
    data_root=p;preview=desktop_preview
    if native is None:
        native=importlib.import_module('maya_toolkit.tools.maya_tabs_v1_3a.native')
        native.mayaTabsSettingsFile=str(p/'Maya-Tabs.ini');native.__.settings_fname=native.mayaTabsSettingsFile
        native.mayaTabsSerialFile=str(p/'serial.cfg');native.mayaTabsSerialConfigFile=str(p/'mayatabs_51x56.config')
        native.m2mSettingsFile=native.mayaTabsSettingsFile;native.m2mSerialFile=native.mayaTabsSerialFile
        native.mainWindowName=native.mayaTabsMainWindowName
        native.__.settings['lastSaveDir']=str(p)
        native.srl=None
        if Path(native.mayaTabsSerialFile).is_file():
            lines=Path(native.mayaTabsSerialFile).read_text(encoding='utf8').splitlines()
            native.srl=next((line.split('=',1)[1] for line in lines if line.startswith('Serial=')),None)
    return native
def save_settings():
    count=len(native.__.settings['tabs']);native.__.settings['currentTabIndex']=min(max(0,native.__.settings.get('currentTabIndex',0)),max(0,count-1))
    return storage.write(str(data_root/'Maya-Tabs.ini'),native.__.settings,overwrite=True)
def read_settings():
    p=data_root/'Maya-Tabs.ini'
    if p.exists():native.__.settings=copy.deepcopy(storage.read(str(p)))
    else:save_settings()
def later(milliseconds,callback):
    from .qt_compat import QtCore,isValid
    owned=window or (native.MayaTabs.instance if native else None)
    if owned is None:return
    token=generation;timer=QtCore.QTimer(owned);timer.setSingleShot(True)
    def invoke():
        if token==generation and isValid(owned):callback()
        timer.deleteLater()
    timer.timeout.connect(invoke);timer.start(milliseconds);return timer
def install_callbacks():
    if preview:return
    if callbacks:return
    from maya.api import OpenMaya
    token=generation
    for event,name in ((OpenMaya.MSceneMessage.kAfterNew,'on_new'),(OpenMaya.MSceneMessage.kAfterOpen,'on_open'),(OpenMaya.MSceneMessage.kAfterSave,'on_save')):
        def callback(*args,method=name):
            if token!=generation or window is None:return
            def invoke():
                if token!=generation or window is None:return
                if method=='on_new':window.on_new()
                else:
                    from maya import cmds
                    getattr(window,method)(cmds.file(q=True,sceneName=True))
            later(0,invoke)
        callbacks.append(OpenMaya.MSceneMessage.addCallback(event,callback))
def close():
    global window,closing,generation
    if closing:return
    closing=True;generation+=1
    try:
        if callbacks:
            from maya.api import OpenMaya
            for value in callbacks:OpenMaya.MMessage.removeCallback(value)
            callbacks.clear()
        owned=window;window=None
        if owned:
            from .qt_compat import QtCore,isValid
            if isValid(owned):
                for timer in owned.findChildren(QtCore.QTimer):timer.stop()
                owned._tooltip_anim.stop();owned._tooltip.hide()
                parent=owned.parentWidget()
                if parent and hasattr(parent,'removeToolBar'):parent.removeToolBar(owned)
                owned.close();owned.deleteLater()
        for name,pointer in list(ui_windows.items()):
            from maya import cmds,OpenMayaUI
            if cmds.window(name,exists=True):
                if int(OpenMayaUI.MQtUtil.findWindow(name) or 0)!=pointer:raise RuntimeError('Foreign window replacement preserved')
                cmds.deleteUI(name)
            ui_windows.pop(name,None)
        if native:native.MayaTabs.instance=None
    finally:closing=False
def install_toolbar():
    global window
    close();window=native.MayaTabs();window.setObjectName('MTB_MayaTabs_Toolbar')
    if not preview:
        from .qt_compat import QtWidgets,QtCore,wrapInstance
        from maya import OpenMayaUI
        pointer=OpenMayaUI.MQtUtil.mainWindow()
        if not pointer:raise RuntimeError('Maya main window absent')
        parent=wrapInstance(int(pointer),QtWidgets.QMainWindow);parent.addToolBar(QtCore.Qt.BottomToolBarArea,window)
    window.show();return window
def show(value):
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    from .qt_compat import QtWidgets,QtCore
    app=QtWidgets.QApplication.instance()
    if app is None or QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Maya Qt main thread required')
    module=load(value);close();module.install()
    if window is None:raise RuntimeError('Original version/license gate did not create toolbar; complete vendor activation in its owned dialog')
    return window
class Dialogs:
    @staticmethod
    def getSaveFileName(*args,**kwargs):
        from .qt_compat import QtWidgets
        result=QtWidgets.QFileDialog.getSaveFileName(*args,**kwargs)
        if result[0]:dialog_outputs.add(str(storage.path(result[0])))
        return result
    @staticmethod
    def getOpenFileName(*args,**kwargs):
        from .qt_compat import QtWidgets
        return QtWidgets.QFileDialog.getOpenFileName(*args,**kwargs)
def native_open(value,mode='r',*args,**kwargs):
    p=storage.path(str(value));writing=any(c in mode for c in 'wax+')
    if not writing:
        if p.suffix in ('.tabs-session','.mttheme') or p.name=='Maya-Tabs.ini':return io.StringIO(json.dumps(storage.read(str(p))))
        if p.name not in ('serial.cfg','mayatabs_51x56.config') or p.stat().st_size>16384:raise ValueError('Unknown/oversized native read')
        return builtins.open(p,mode,encoding='utf8')
    own=data_root and p.parent.resolve()==data_root.resolve() and p.name in ('Maya-Tabs.ini','serial.cfg','mayatabs_51x56.config')
    if not own and str(p) not in dialog_outputs:raise ValueError('Write requires own state or explicit Save dialog path')
    class Writer(io.StringIO):
        def __exit__(self,typ,error,tb):
            if typ is None:
                if p.name in ('serial.cfg','mayatabs_51x56.config'):
                    content=self.getvalue()
                    if len(content)>16384 or not content.startswith('Serial='):raise ValueError('Invalid native license record')
                    if p.exists():storage.backup(p)
                    p.write_text(content,encoding='utf8')
                else:storage.write(str(p),json.loads(self.getvalue()),overwrite=True)
            self.close();return False
    return Writer()
class Commands:
    def __getattr__(self,name):
        def call(*args,**kw):
            if preview:
                if name=='file' and kw.get('query',kw.get('q',False)):return False if kw.get('modified') else ''
                raise RuntimeError('Desktop preview cannot execute Maya commands')
            from maya import cmds,OpenMayaUI
            fn=getattr(cmds,name)
            query=kw.get('query',kw.get('q',False));edit=kw.get('edit',kw.get('e',False))
            if name=='file' and not query:
                if kw.get('rename'):
                    p=storage.path(kw['rename'])
                    if p.suffix.lower() not in ('.ma','.mb') or not p.parent.is_dir():raise ValueError('Existing parent Maya file required')
                if kw.get('save'):
                    target=storage.path(cmds.file(q=True,sn=True))
                    if target.suffix.lower() not in ('.ma','.mb'):raise ValueError('Only explicit Maya scene paths writable')
                    kw['type']='mayaAscii' if target.suffix.lower()=='.ma' else 'mayaBinary'
                    if target.exists():storage.backup(target)
                if kw.get('open') or kw.get('new'):
                    if kw.get('open'):
                        p=storage.path(args[0])
                        if not p.is_file() or p.suffix.lower() not in ('.ma','.mb'):raise ValueError('Existing Maya scene required')
                    if cmds.file(q=True,modified=True):
                        answer=cmds.confirmDialog(title='Maya Tabs',message='当前场景有未保存修改。切换前保存、放弃或取消。',button=['Save','Discard','Cancel'],defaultButton='Save',cancelButton='Cancel',dismissString='Cancel')
                        if answer=='Cancel':raise RuntimeError('Scene switch cancelled')
                        if answer=='Save':
                            if not window or not window._save():raise RuntimeError('Save cancelled; scene preserved')
            if name=='deleteUI':
                if not args or args[0] not in ui_windows:raise ValueError('Foreign native UI deletion refused')
                if int(OpenMayaUI.MQtUtil.findWindow(args[0]) or 0)!=ui_windows[args[0]]:raise ValueError('Foreign native UI replacement preserved')
            if name=='window' and not query and not edit and not kw.get('exists',kw.get('ex',False)):
                if args and cmds.window(args[0],exists=True):raise ValueError('Existing native window preserved')
            result=fn(*args,**kw)
            if name=='window' and not query and not edit and not kw.get('exists',kw.get('ex',False)):ui_windows[result]=int(OpenMayaUI.MQtUtil.findWindow(result) or 0)
            if name=='deleteUI':ui_windows.pop(args[0],None)
            return result
        return call
cmds=Commands()
''')
source=(UNIT/'plug-ins/Maya-Tabs.py').read_text(encoding='utf-8-sig');tree=ast.parse(source)
# ast.unparse preserves every statement/algorithm while dropping upstream line
# comments/obfuscated spacing; exact original remains SHA archive.
s=ast.unparse(tree)+'\n'
s=s.replace('from PySide2 import QtCore, QtWidgets, QtGui','from maya_toolkit.tools.maya_tabs_v1_3a.qt_compat import QtCore,QtWidgets,QtGui').replace('from shiboken2 import wrapInstance, isValid','from maya_toolkit.tools.maya_tabs_v1_3a.qt_compat import wrapInstance,isValid').replace('from maya import cmds','from maya_toolkit.tools.maya_tabs_v1_3a.session import cmds').replace('from pymel import versions','from maya_toolkit.tools.maya_tabs_v1_3a.session import versions')
s=s.replace("scriptPath = os.path.expanduser('~/maya/plug-ins/Maya-Tabs_Files')","from pathlib import Path\nscriptPath = str(Path(__file__).parent/'resources')").replace("if os.path.exists(scriptPath23):\n    scriptPath = scriptPath23",'')
s=s.replace("mayaTabsSerialWindowName = 'mayaTabsSerial'","mayaTabsSerialWindowName = 'MTB_mayaTabsSerial'").replace("mayaTabsMainWindowName = 'mayaTabsMain'","mayaTabsMainWindowName = 'MTB_mayaTabsMain'")
for name in ('menuTabsWidth','menuTabsHeight','txtFieldCode'):s=s.replace(repr(name),repr('MTB_'+name))
s=s.replace('.exec_(','.exec(').replace('QtWidgets.QAction','QtGui.QAction').replace('QtCore.QTimer.singleShot(', '_owned_single_shot(')
# Correct QMessageBox/size/Python3 image pointer conversion and slot lifetime.
s=s.replace('O0O00OO00000O0O0O.width() * OO00000000O0O0O0O','int(round(O0O00OO00000O0O0O.width() * OO00000000O0O0O0O))')
s=s.replace('ctypes.c_ubyte * O00O00O000O0000OO[0] * O00O00O000O0000OO[1]','ctypes.c_ubyte * (O00O00O000O0000OO[0] * O00O00O000O0000OO[1] * 4)')
s=s.replace('    def on_new_tab(', '    def closeEvent(self,event):\n        from maya_toolkit.tools.maya_tabs_v1_3a import session\n        if session.window is self:session.close()\n        super().closeEvent(event)\n\n    def on_new_tab(',1)
# Guard private QFileDialogs and file streams locally, with no global patch.
s+='\nfrom maya_toolkit.tools.maya_tabs_v1_3a.session import native_open as open, later as _owned_single_shot, Dialogs\nimport types as _types\nQtWidgets=_types.SimpleNamespace(**vars(QtWidgets));QtWidgets.QFileDialog=Dialogs\n'
replacements={'_OOO00OO0O00000OO0':'def _OOO00OO0O00000OO0():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import save_settings\n    return save_settings()', '_OO0O000O0OO0O000O':'def _OO0O000O0OO0O000O():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import read_settings\n    return read_settings()', 'install_toolbar':'def install_toolbar():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import install_toolbar\n    return install_toolbar()', 'uninstall_toolbar':'def uninstall_toolbar():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import close\n    return close()', 'install_callbacks':'def install_callbacks():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import install_callbacks\n    return install_callbacks()', 'uninstall_callbacks':'def uninstall_callbacks():\n    from maya_toolkit.tools.maya_tabs_v1_3a.session import close\n    return close()', 'addToClipBoard':'def addToClipBoard(value):\n    QtWidgets.QApplication.clipboard().setText(value.strip())'}
tree=ast.parse(s);lines=s.splitlines();edits=[]
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name in replacements:edits.append((n.lineno-1,n.end_lineno,replacements[n.name]))
    # Defer defective m2m serial reads until explicitly configured; original
    # license verification and activation/version gate algorithms are retained.
    if isinstance(n,ast.Try) and any(isinstance(x,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='srl' for v in x.targets) for x in n.body):edits.append((n.lineno-1,n.end_lineno,'# serial read only by explicit session.load'))
for a,b,t in sorted(edits,reverse=True):lines[a:b]=t.splitlines()
s='\n'.join(lines)+'\n'
# Remove duplicate unmanaged settings overwrite in original save_settings.
tree=ast.parse(s);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MayaTabs');method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='save_settings');lines=s.splitlines()
for n in reversed(method.body):
    if isinstance(n,ast.With):lines[n.lineno-1:n.end_lineno]=[]
s='\n'.join(lines)+'\n';put(PKG/'native.py',s)
put(PKG/'__init__.py',r'''from pathlib import Path
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import storage
class MayaTabsTool(BaseMayaTool):
    tool_id='maya_tabs_v1_3a';tool_name='Maya Tabs 多场景标签';category='scene_hygiene';version='1.0.0'
    description='Complete licensed original tab toolbar, thumbnails, autosave-on-switch, sessions and theme editor with independent backed-up state'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','read_settings','write_settings','read_session','write_session','read_theme','write_theme','open_theme_editor'],'default':'inspect'},'data_root':{'type':'string'},'path':{'type':'string'},'data':{},'overwrite':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            if type(kw.get('overwrite',False)) is not bool:raise ValueError('Strict overwrite boolean')
            if action in ('show_ui','read_settings','write_settings'):storage.root(kw.get('data_root'))
            if action.startswith('read_') or action.startswith('write_'):
                p=storage.root(kw['data_root'])/'Maya-Tabs.ini' if action.endswith('settings') else storage.path(kw.get('path'))
                if action.startswith('read_'):storage.read(str(p))
                else:
                    storage.payload(p,kw.get('data'))
                    if not p.parent.is_dir() or p.exists() and not kw.get('overwrite'):raise ValueError('Existing output requires explicit overwrite')
            return ToolResult.ok(message='无Qt/授权读取/回调/scene/file写入的预检')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'themes':len(list((Path(__file__).parent/'resources/Themes').glob('*.mttheme'))),'license_gate':'retained','original_version_gate':'2014-2023 allowlist retained; newer GUI acceptance pending','gui_acceptance':'not_run'})
        if action.startswith('read_') or action.startswith('write_'):
            p=storage.root(kw['data_root'])/'Maya-Tabs.ini' if action.endswith('settings') else storage.path(kw['path'])
            return ToolResult.ok(data={'value':storage.read(str(p))}) if action.startswith('read_') else ToolResult.ok(data=storage.write(str(p),kw['data'],kw.get('overwrite',False)))
        from . import session
        if action=='show_ui':session.show(kw['data_root']);return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if session.window is None:raise RuntimeError('Open licensed owned toolbar first')
        session.native.guiMayaTabs();return ToolResult.ok()
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        values=cmds.fileDialog2(fileMode=3,caption='Maya Tabs：选择独立配置/授权状态目录')
        if not values:return None
        from .session import show
        return show(values[0])
''')
put(RC/'tests/test_maya_tabs_v1_3a.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.maya_tabs_v1_3a import MayaTabsTool
    tool=MayaTabsTool()
from maya_toolkit.tools.maya_tabs_v1_3a import storage
class Checks(unittest.TestCase):
    def test_typed_complete_themes_and_transactional_session(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.maya_tabs_v1_3a.native',sys.modules)
        themes=list((Path(storage.__file__).parent/'resources/Themes').glob('*.mttheme'));self.assertGreaterEqual(len(themes),19)
        for theme in themes:storage.read(str(theme))
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'session.tabs-session';data=[{'name':'Empty','fname':'','autosave':False,'active':False,'thumbnail':''}];storage.write(str(p),data);before=p.read_bytes();row=storage.write(str(p),data,True);self.assertEqual(Path(row['backup']).read_bytes(),before)
            with self.assertRaises(ValueError):storage.write(str(p),data+[{'name':'Bad','fname':'','autosave':1}],True)
            self.assertEqual(p.read_bytes(),before)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_maya_tabs_v1_3a_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Qt only; Maya not initialized')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets,QtGui,QtCore
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.maya_tabs_v1_3a import session,storage
class QtChecks(unittest.TestCase):
    def test_complete_toolbar_and_thumbnail_without_maya_or_license_bypass(self):
        with tempfile.TemporaryDirectory() as td:
            module=session.load(td,True);win=session.install_toolbar();self.assertEqual(len(win._slots),8);self.assertEqual(session.callbacks,[])
            win.on_new_tab();self.assertEqual(len(win._slots),9);data=storage.read(str(Path(td)/'Maya-Tabs.ini'));self.assertEqual(len(data['tabs']),9)
            pix=QtGui.QPixmap(32,16);pix.fill(QtCore.Qt.red);encoded=win._serialise_thumnail(pix);self.assertTrue(encoded);module.__.settings['tabs'][0]['thumbnail']=encoded;session.save_settings()
            called=[];timer=session.later(0,lambda:called.append(True));self.assertTrue(timer.isActive());session.close();app.processEvents();self.assertEqual(called,[]);self.assertIsNone(module.MayaTabs.instance)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_maya_tabs_v1_3a_maya.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tabs',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.maya_tabs_v1_3a import session
class MayaChecks(unittest.TestCase):
    def test_unbound_modified_scene_cancel_and_exact_save_backup(self):
        cmds.file(new=True,force=True);cube=cmds.polyCube(name='keepCube')[0]
        with patch.object(cmds,'confirmDialog',return_value='Cancel'):
            with self.assertRaises(RuntimeError):session.cmds.file(new=True,force=True)
        self.assertTrue(cmds.objExists(cube));self.assertEqual(session.callbacks,[])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'temp.ma';cmds.file(rename=str(p));cmds.file(save=True,type='mayaAscii',force=True);before=p.read_bytes();cmds.setAttr(cube+'.tx',5);session.cmds.file(save=True,force=True)
            backups=list(Path(td).glob('temp.ma.mtb_backup_*'));self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),before);self.assertNotEqual(p.read_bytes(),before)
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/maya_tabs_v1_3a.md','''# Maya Tabs 1.3a 完整候选

27原文件精确SHA归档，完整混淆源算法（AST排版，未拆掉业务分支）/Tab/Toolbar/tooltip动画/active选项/autosave-on-switch/clear/delete/open-folder/session JSON/PNG viewport thumbnails/完整cmds主题编辑器与19主题/icon/logo/安装图/原INI样例。原PyMel versions唯一用途改cmds.about版本查询；Qt5/6 facade/shiboken/QAction/python3 imagebuffer/size兼容。Base/Schema/API/read-write settings/session/theme/主题UI与未来注册面板预制，默认inspect/validate无native/Qt、授权读取或scene/file写入。

保留原chkSrl/guiSerial/install授权逻辑和2014-2023版本allowlist，无序列号生成/跳过授权/把新Maya版本视为原授权兼容。显式独立state目录可放用户已有合法serial.cfg/mayatabs_51x56.config；修复原undefined m2mSerialFile等别名，仅显式启动读取，原许可判定仍由原函数处理。缺授权或不在原版本列表时show明确未创建toolbar，保留vendor activation UI而不能登记成功。独立Qt preview只构造无scene demo，不执行install/license gate，不属于有授权生产可用证据。

原HOME固定路径改自包含resources、独立state中的Maya-Tabs.ini；新目录创建8个空tab，不自动导入原INI用户场景/缩略图。JSON32MiB/256tabs/strictbool/完整style/hexRGB/size/base64PNG/引用索引/duplicatekey全量预检后写；scene fname仅绝对ma/mb。每次已有设置/会话/主题覆盖先精确backup再atomic，包内资源只读，原重复settings overwrite移除。native open和QtFileDialog私有代理仅明确Save路径/自有配置写入，不全球patch；原授权文件只用户原激活成功才写自己的state且先backup。剪贴板改Qt clipboard，不shell拼echo。

原slot打开/clear强制file新建可能在当前slot缺失时丢未保存scene，cmds私有proxy补全modified确认Save/Discard/Cancel；取消不open/new，所有现存scene保存前精确磁盘backup，后续save/scene切换不可Maya Undo。原autosave指切换前保存该slot，不是定时autosave。clear/delete/session/theme只真实用户按钮执行，原SceneOpened/Saved/New回调用owned IDs和generation保护Qt deferred，close停止own timer/tooltip/toolbar与native窗口，foreign同名/指针变拒绝删，不注册startup/loadPlugin或改Maya.env。生产API干净模块不依赖旧staging路径。

原API2 viewport pointer路径需跨版本真实验收；修复buffer原少4通道尺寸并保留像素copy。完整offline19themes/session备份/坏末项不覆盖、独立Qt8→9tab/PNG/close后deferred不执行/future布局；真实Maya授权/版本/UI主题编辑/场景SaveDiscardCancel/viewport/真实callbacks not_run，prepared_unverified。生产scene切换只临时备份scene验收，静态依赖不证明组合已通过。
''')
put(RC/'acceptance.md','''# Maya Tabs 真实Maya验收 not_run

1. 原支持2014-2023列表内合法已授权新Maya会话，独立state放已有vendor许可，启动完整底栏/所有资源/8空tab；无许可原activation、新版本原gate拒绝不能记通过。本候选未生成或绕过序列号。
2. 备份场景下点击tab、新建/clear/删除/slot未绑定但scene modified、autosave切换、Save/Discard/Cancel各分支；取消保留scene，已有ma/mb保存磁盘先exact backup，Undo不能恢复打开新scene/文件写。
3. 完整session/19theme编辑/import/export/尺寸颜色/缩略图捕获、无效最后tab/图像/JSON拒绝，settings/session/theme覆盖先backup且resources/原用户配置不变。新目录不加载原INI示例中的用户项目场景。
4. close/remove只owntoolbar/timer/deferred/callback/native窗口，foreign同名保留，重开不叠加；真实viewport API指针/像素/跨版本实测。accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/maya_tabs_v1_3a','--class-name','MayaTabsTool','--summary','Complete original licensed Maya Tabs toolbar, session thumbnails and theme editor with independent state and backed-up file writes','--dependencies','Real licensed original-supported Maya GUI/Qt/shiboken','Original vendor activation/version gate retained','--limitations','Real Maya license/version gate/full scene switch/viewport/theme/callback/cross-version GUI acceptance not_run'],check=True)
