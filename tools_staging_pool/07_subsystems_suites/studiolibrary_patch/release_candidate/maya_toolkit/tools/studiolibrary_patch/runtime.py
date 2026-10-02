"""Owned full Studio Library runtime, transactional reversible integration hooks."""
from pathlib import Path
import importlib,sys,types,shutil,uuid
from . import guards,history_safety
ROOT=Path(__file__).parent;VENDOR=ROOT/'vendor/src';NATIVE=ROOT/'native'
active=False;snapshot=[];installed=[];fields_before=None;window=None;paths=[];history_ready=False;registered={}
def ensure_paths():
    for prefix in ('studiovendor','studioqt','studiolibrary','studiolibrarymaya','mutils','studiolibrary_wanimation'):
        module=sys.modules.get(prefix)
        if module is not None:
            source=getattr(module,'__file__',None)
            if not source or not (ROOT.resolve() in Path(source).resolve().parents):raise RuntimeError('Foreign '+prefix+' already loaded; use a fresh Maya session with this bundled version')
    for p in (VENDOR,NATIVE):
        value=str(p)
        if value not in sys.path:sys.path.insert(0,value);paths.append(value)
def core():
    ensure_paths()
    from studiolibrary_wanimation import worldpose,worldanimation
    return worldpose,worldanimation
def activate():
    global active,snapshot,installed,fields_before,history_ready,registered
    ensure_paths()
    if active:return {'active':True}
    from studiolibrary_wanimation import integration as i,history
    if not history_ready:history_safety.install(history);history_ready=True
    specs=[(i.studiolibrary.libraryitem.LibraryItem,['safeSave']),(i.studiolibrary.library.Library,['createItems']),
           (i.studiolibrary.widgets.formwidget.FormWidget,['setSchema']),(i.studiolibrary.widgets.menubarwidget.MenuBarWidget,['findAction','findToolButton']),
           (i.studioqt.menu.Menu,['findAction']),(i.studiolibrary.widgets.sortbymenu.SortByMenu,['populateMenu']),
           (i.studiolibrary.librarywindow.LibraryWindow,['__init__','createSettingsMenu','createNewItemMenu','createItemContextMenu','setPreviewWidget'])]
    snapshot=[(cls,name,getattr(cls,name)) for cls,names in specs for name in names];fields_before=list(i.studiolibrary.library.Library.Fields)
    try:
        i.install()
        from studiolibrary_wanimation import WAnimationItem,WPoseItem
        import studiolibrary.utils as utils
        registered={cls.__name__:(utils._itemClasses.get(cls.__name__),cls) for cls in (WAnimationItem,WPoseItem)}
        for old,cls in registered.values():i.studiolibrary.registerItem(cls)
        installed=[getattr(cls,name) for cls,name,old in snapshot];active=True
    except Exception:
        for cls,name,old in snapshot:setattr(cls,name,old)
        i.studiolibrary.library.Library.Fields[:]=fields_before;i._installed=False;raise
    return {'active':True,'classes':['WPoseItem','WAnimationItem']}
def deactivate():
    global active,window
    if not active:return {'active':False}
    for (cls,name,old),own in zip(snapshot,installed):
        if getattr(cls,name) is not own:raise RuntimeError('Foreign later hook detected: '+name+'; restore that hook first')
    from studiolibrary_wanimation import integration as i
    import studiolibrary.utils as utils
    for name,(old,own) in registered.items():
        if utils._itemClasses.get(name) is not own:raise RuntimeError('Foreign item registry change')
    if window:window.close();window=None
    for cls,name,old in snapshot:setattr(cls,name,old)
    added=[row for row in i.studiolibrary.library.Library.Fields if row not in fields_before]
    for row in added:
        if row.get('name')=='modified':i.studiolibrary.library.Library.Fields.remove(row)
    for name,(old,own) in registered.items():
        if old is None:utils._itemClasses.pop(name,None)
        else:utils._itemClasses[name]=old
    i._installed=False;active=False
    return {'active':False}
def apply_theme():
    if window is None:raise RuntimeError('Open this candidate library first')
    import studiolibrary.widgets,studioqt
    from .theme_io import CSS
    theme=studiolibrary.widgets.Theme();theme.setName('ModernDark');theme.setAccentColor('rgb(108, 92, 231)');theme.setBackgroundColor('rgb(24, 25, 32)')
    def css(self):return studioqt.StyleSheet.fromPath(str(CSS),options=self.options(),dpi=self.dpi()).data()
    theme.styleSheet=types.MethodType(css,theme);window.setTheme(theme)
    return {'theme':'ModernDark','file_write':False}
def show(root,parent=None):
    global window
    root=guards.path(root)
    if not root.is_dir():raise ValueError('Existing library root required')
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required; mayapy cannot create this window')
    activate()
    from studiolibrarymaya.mayalibrarywindow import MayaLibraryWindow
    import studiolibrary
    studiolibrary.registerItems()
    window=MayaLibraryWindow.instance(name='MTB_StudioLibraryPlusPatch',path=str(root),show=False)
    window.setCheckForUpdateEnabled(False);apply_theme();window.show();return window
def repair():
    if window is None:raise RuntimeError('Open owned library first')
    from studiolibrary_wanimation.startup import repair_library_cache
    library=window.library();database=guards.path(library.databasePath());root=guards.path(library.path())
    if root not in database.parents:raise ValueError('Cache must be inside chosen library root')
    backup=None
    if database.exists():
        backup=database.with_name(database.name+'.mtb_backup_'+uuid.uuid4().hex)
        with backup.open('xb') as f:f.write(database.read_bytes())
        if backup.read_bytes()!=database.read_bytes():raise IOError('Cache backup mismatch')
    count=repair_library_cache(library)
    return {'repaired':count,'cache':str(database),'backup':str(backup) if backup else None}
