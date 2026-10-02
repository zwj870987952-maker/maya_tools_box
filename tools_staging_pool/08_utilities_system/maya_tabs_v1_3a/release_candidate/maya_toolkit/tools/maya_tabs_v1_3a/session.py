from pathlib import Path
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
