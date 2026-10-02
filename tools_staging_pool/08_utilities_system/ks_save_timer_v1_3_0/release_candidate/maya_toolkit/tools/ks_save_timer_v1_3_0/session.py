"""Native singletons owned by one explicit host/state/locale session; no auto startup."""
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
