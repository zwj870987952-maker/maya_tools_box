"""Full pinned Studio Library and PlusPatch; explicit activation and guarded IO."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/studiolibrary_patch';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/studiolibrary_patch';NATIVE=PKG/'native';VENDOR=PKG/'vendor'
provenance=json.loads((RC/'dependency_provenance.json').read_text(encoding='utf8'))
assert provenance['state']=='complete'
for src in (RC/'dependency_source').rglob('*'):
    if src.is_file() and '__pycache__' not in src.parts:
        rel=src.relative_to(RC/'dependency_source');dst=VENDOR/rel
        if dst.name.endswith('.py.original'):dst=dst.with_suffix('')
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
shutil.copyfile(RC/'dependency_provenance.json',VENDOR/'dependency_provenance.json')
for src in UNIT.rglob('*'):
    if not src.is_file() or 'release_candidate' in src.relative_to(UNIT).parts or '__pycache__' in src.parts or src.name=='.gitattributes':continue
    dst=NATIVE/src.relative_to(UNIT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
EXT=NATIVE/'studiolibrary_wanimation'
put(EXT/'__init__.py','''"""Explicit activation only: importing this package never hooks or repairs caches."""
__version__='2.2.2-mtb'
__all__=['WAnimationItem','WPoseItem']
def __getattr__(name):
    if name=='WAnimationItem':
        from .wanimationitem import WAnimationItem
        return WAnimationItem
    if name=='WPoseItem':
        from .wposeitem import WPoseItem
        return WPoseItem
    raise AttributeError(name)
''')
put(PKG/'guards.py',r'''"""Pure preflight plus Maya transform validation; no eager vendor imports."""
from pathlib import Path
import json,math,os,tempfile
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def finite(value):
    if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>1e9:raise ValueError('Finite bounded number required')
    return float(value)
def frames(start,end,step=1):
    start,end,step=map(finite,(start,end,step))
    if step<=0 or end<start or (end-start)/step>9998:raise ValueError('Ordered range, positive step and at most 10000 samples required')
    values=[round(start+i*step,6) for i in range(int((end-start)/step+0.0001)+1)]
    if values[-1]<end-step*0.0001:values.append(end)
    if len(set(values))!=len(values):raise ValueError('Sample step is below supported precision')
    return values
def read(value):
    p=path(str(value))
    if not p.is_file() or p.stat().st_size>64*1024*1024:raise ValueError('JSON missing or exceeds 64 MiB')
    def pairs(rows):
        d={}
        for k,v in rows:
            if k in d:raise ValueError('Duplicate JSON key')
            d[k]=v
        return d
    return json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def data(value,animation=False):
    if not isinstance(value,dict) or value.get('schemaVersion')!=1:raise ValueError('World schemaVersion 1 required')
    objects=value.get('objects')
    if not isinstance(objects,dict) or not 1<=len(objects)<=4096:raise ValueError('1-4096 world objects required')
    count=0
    if animation:frames(value.get('startFrame'),value.get('endFrame'),value.get('sampleBy',1))
    for name,item in objects.items():
        if not isinstance(name,str) or not name or not isinstance(item,dict):raise ValueError('Invalid world object')
        samples=item.get('frames') if animation else [item]
        if not isinstance(samples,list) or not samples or len(samples)>10000:raise ValueError('Invalid world samples')
        times=[]
        for sample in samples:
            if not isinstance(sample,dict):raise ValueError('Invalid sample')
            if animation:
                time=finite(sample.get('time'));times.append(time)
                if not value['startFrame']-0.0001<=time<=value['endFrame']+0.0001:raise ValueError('Sample outside source range')
            for field,size in (('position',3),('rotation',3))+( () if animation else (('matrix',16),)):
                vector=sample.get(field)
                if not isinstance(vector,list) or len(vector)!=size:raise ValueError('Invalid '+field)
                for n in vector:finite(n)
            count+=1
            if count>1000000:raise ValueError('Total sample limit exceeded')
        if animation and times!=sorted(set(times)):raise ValueError('Sample times must be sorted and unique')
    return value
def save_json(value,payload):
    p=path(str(value));blob=(json.dumps(payload,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf8')
    if not p.parent.is_dir():raise ValueError('Existing parent required')
    # Existing world metadata may only be changed through asset/history save.
    if p.exists():raise FileExistsError('World metadata overwrite refused')
    with p.open('xb') as f:f.write(blob)
def targets(objects,writable=False,attributes=None):
    from maya import cmds
    if not isinstance(objects,(list,tuple)) or not 1<=len(objects)<=4096:raise ValueError('Explicit transform objects required')
    result=[]
    for name in objects:
        if not isinstance(name,str) or not name or any(c in name for c in '*?[]'):raise ValueError('Exact transform name required')
        found=cmds.ls(name,long=True) or []
        if len(found)!=1 or not cmds.objectType(found[0],isAType='transform'):raise ValueError('Missing, ambiguous or non-transform: '+name)
        node=found[0]
        if node in result:raise ValueError('Duplicate transform')
        if writable:
            for attr in attributes or ('translateX','translateY','translateZ','rotateX','rotateY','rotateZ'):
                plug=node+'.'+attr
                if cmds.getAttr(plug,lock=True):raise ValueError('Locked destination: '+plug)
                incoming=cmds.listConnections(plug,s=True,d=False) or []
                if any(not cmds.nodeType(n).startswith('animCurve') for n in incoming):raise ValueError('Driven destination: '+plug)
        result.append(node)
    return result
def matches(rows,attributes=None):
    if not rows:raise ValueError('No matched targets')
    return targets([dst for src,dst in rows],True,attributes)
def asset(value,animation=False,new=False):
    p=path(value);suffix='.wanim' if animation else '.wpose'
    if p.suffix.lower()!=suffix:raise ValueError('Expected '+suffix+' asset directory')
    if new:
        if p.exists() or not p.parent.is_dir():raise ValueError('New asset directory and existing parent required')
    else:
        if not p.is_dir():raise ValueError('Asset directory missing')
        filename='world_transform.json' if animation else 'world_pose.json';data(read(p/filename),animation)
        pose=read(p/'pose.json')
        if not isinstance(pose,dict):raise ValueError('Standard pose metadata absent')
    return p
''')
# Native world algorithms retained; guard their original UI and API paths too.
for file,animation in [('worldpose.py',False),('worldanimation.py',True)]:
    p=EXT/file;s=p.read_text(encoding='utf-8-sig');s=s.replace('import mutils\n','import mutils\nfrom maya_toolkit.tools.studiolibrary_patch import guards as _guards\n',1)
    tree=ast.parse(s);edits=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef) and n.name=='save' and isinstance(n.args.args[0],ast.arg) and n.args.args[0].arg=='self':
            edits.append((n.lineno-1,n.end_lineno,'    def save(self, path):\n        _guards.data(self.data, '+repr(animation)+')\n        _guards.save_json(path, self.data)'))
        if isinstance(n,ast.FunctionDef) and n.name=='from_path':
            start=n.body[0].lineno-1
            edits.append((start,n.end_lineno,'        return cls(_guards.data(_guards.read(path), '+repr(animation)+'))'))
        if isinstance(n,ast.FunctionDef) and n.name=='_frame_values':edits.append((n.lineno-1,n.end_lineno,'def _frame_values(start, end, sample_by=1.0):\n    return _guards.frames(start, end, sample_by)'))
        if isinstance(n,ast.FunctionDef) and n.name=='_long_names':edits.append((n.lineno-1,n.end_lineno,'def _long_names(objects):\n    return _guards.targets(objects)'))
    lines=s.splitlines()
    for start,end,value in sorted(edits,reverse=True):lines[start:end]=value.splitlines()
    s='\n'.join(lines)+'\n'
    if not animation:
        s=s.replace('        cache_key = (','        _guards.data(self.data)\n        _guards.finite(blend)\n        _guards.matches(matches)\n        cache_key = (',1)
        s=s.replace('    if mirror and not mirrorTable:','    _guards.data(world_pose.data)\n    _guards.matches(_matches(world_pose, objects, namespaces, searchAndReplace))\n    _guards.finite(blend)\n    if mirror and not mirrorTable:',1)
    else:
        s=s.replace('        try:\n            for frame in collector.expected_frames:', '        maya.cmds.undoInfo(openChunk=True, chunkName="MTB World Capture")\n        try:\n            for frame in collector.expected_frames:',1)
        s=s.replace('            maya.cmds.select(selection, replace=True) if selection else maya.cmds.select(clear=True)\n\n        return collector.world_animation()', '            try:\n                maya.cmds.select(selection, replace=True) if selection else maya.cmds.select(clear=True)\n            finally:\n                maya.cmds.undoInfo(closeChunk=True)\n\n        return collector.world_animation()',1)
        s=s.replace('    source_start = world_animation.start_frame','    _guards.data(world_animation.data, True)\n    if option not in ("replace", "merge", "insert"):raise ValueError("Invalid paste option")\n    source_start = world_animation.start_frame',1)
        s=s.replace('    start_frame = float(start_frame)','    start_frame = _guards.finite(start_frame)',1)
        s=s.replace('    _edit_destination_keys(matches,','    _guards.matches(matches, attributes)\n    _edit_destination_keys(matches,',1)
        s=s.replace('    animation = mutils.Animation.fromPath(path)','    _guards.matches(_match_world_objects(world_animation, objects, namespaces))\n    animation = mutils.Animation.fromPath(path)',1)
    put(p,s)
# Candidate prefs distinct from the original extension.
p=EXT/'localization.py';put(p,p.read_text(encoding='utf8').replace('StudioLibraryPlusPatch','MTB_StudioLibraryPlusPatch'))
# Cache repair only explicit and restricted to the chosen library root.
p=EXT/'startup.py';s=p.read_text(encoding='utf8');s=s.replace('if path.lower().endswith(extension) and os.path.isdir(path)','if path.lower().endswith(extension) and os.path.isdir(path) and\n            os.path.commonpath([os.path.realpath(path),os.path.realpath(library.path())]) == os.path.realpath(library.path())');put(p,s)
put(PKG/'theme_io.py',r'''"""Recoverable CSS install/uninstall; backup first and content ownership checks."""
from pathlib import Path
import hashlib,json,os,tempfile,uuid
from .guards import path,read
CSS=Path(__file__).parent/'native/StudioLibrary_ThemePatch/theme_resources/css/default.css'
def digest(blob):return hashlib.sha256(blob).hexdigest()
def target(value):
    root=path(value);p=root/'css/default.css'
    if not p.is_file() or p.is_symlink():raise ValueError('Existing external Studio Library resource/css/default.css required')
    if Path(__file__).parent.resolve() in p.resolve().parents:raise ValueError('Bundled immutable resource cannot be overwritten')
    return p
def atomic(p,blob):
    fd,tmp=tempfile.mkstemp(prefix='.mtb_theme_',dir=str(p.parent))
    try:
        with os.fdopen(fd,'wb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def install(value):
    p=target(value);receipt=p.with_name('default.css.mtb_theme_receipt.json');theme=CSS.read_bytes()
    if receipt.exists():
        row=read(receipt)
        if row.get('owner')!='mtb_studiolibrary_theme' or row.get('target')!=str(p):raise ValueError('Foreign receipt')
        if digest(p.read_bytes())!=row['installed_sha256']:raise ValueError('External CSS changed; refuse overwrite')
        return row
    backup=p.with_name('default.css.mtb_backup_'+uuid.uuid4().hex);original=p.read_bytes()
    with backup.open('xb') as f:f.write(original)
    if backup.read_bytes()!=original:raise IOError('Backup verification failed; CSS unchanged')
    row={'owner':'mtb_studiolibrary_theme','target':str(p),'backup':str(backup),'original_sha256':digest(original),'installed_sha256':digest(theme)}
    with receipt.open('x',encoding='utf8') as f:json.dump(row,f,indent=2)
    try:atomic(p,theme)
    except Exception:
        atomic(p,original);receipt.unlink();raise
    return row
def uninstall(value):
    p=target(value);receipt=p.with_name('default.css.mtb_theme_receipt.json');row=read(receipt)
    if row.get('owner')!='mtb_studiolibrary_theme' or row.get('target')!=str(p):raise ValueError('Foreign theme receipt')
    backup=path(row['backup'])
    if backup.parent!=p.parent or not backup.name.startswith('default.css.mtb_backup_'):raise ValueError('Foreign backup path')
    if digest(p.read_bytes())!=row['installed_sha256'] or digest(backup.read_bytes())!=row['original_sha256']:raise ValueError('CSS or backup modified; restore refused')
    atomic(p,backup.read_bytes());receipt.unlink()
    return {'restored':str(p),'retained_backup':str(backup)}
''')
put(PKG/'history_safety.py',r'''"""Owned stage recovery; preserve payload and old versions without collisions."""
from pathlib import Path
import shutil,uuid
from .guards import path
owned={}
def tree(p):
    p=path(str(p))
    if p.is_dir():
        for child in p.rglob('*'):
            if child.is_symlink():raise ValueError('Symlink in asset/history tree')
    return p
def install(module):
    original_stage=module.stage_existing_asset;original_commit=module.commit_stage
    def stage(asset,item):
        tree(asset);row=original_stage(asset,item)
        if row:owned[row['stage']]=dict(row)
        return row
    def checked(row):
        expected=owned.get(row.get('stage'))
        if expected is None or row!=expected:raise ValueError('Unowned history stage')
        root=tree(row['stage']);asset=tree(row['assetPath'])
        if root.parent!=asset.parent or not root.name.startswith('.studiolibrary_plus_history_'):raise ValueError('Invalid history stage')
        for key in ('snapshot','history'):
            if path(row[key]).parent!=root:raise ValueError('Invalid stage child')
        return root,asset
    def restore(row):
        if not row:return True
        root,asset=checked(row);snapshot=tree(row['snapshot']);history=tree(row['history'])
        if not snapshot.is_dir():return False
        # Build the whole recovery before moving a partially written target.
        recovery=root/'recovered';shutil.copytree(snapshot,recovery)
        if history.is_dir():shutil.copytree(history,recovery/'.history')
        elif (asset/'.history').is_dir():shutil.copytree(asset/'.history',recovery/'.history')
        displaced=root/'failed_asset'
        if asset.exists():shutil.move(str(asset),str(displaced))
        try:shutil.move(str(recovery),str(asset))
        except Exception:
            if displaced.exists() and not asset.exists():shutil.move(str(displaced),str(asset))
            raise
        # A failed partial asset is preserved for inspection, not discarded.
        owned.pop(row['stage'],None)
        return True
    def merge(source,dest):
        source=tree(source);dest=tree(dest)
        if not source.is_dir():return
        rows=list(source.iterdir())
        if any((dest/p.name).exists() for p in rows):raise FileExistsError('History collision; recovery stage preserved')
        dest.mkdir(exist_ok=True)
        for p in rows:shutil.move(str(p),str(dest/p.name))
    def commit(row,asset):
        checked(row);tree(asset)
        if path(asset)!=path(row['assetPath']):raise ValueError('Destination changed during save')
        result=original_commit(row,asset);owned.pop(row['stage'],None);return result
    module.stage_existing_asset=stage;module.restore_stage=restore;module._merge_history=merge;module.commit_stage=commit
''')
put(PKG/'runtime.py',r'''"""Owned full Studio Library runtime, transactional reversible integration hooks."""
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
''')
put(PKG/'__init__.py',r'''"""Full Studio Library PlusPatch candidate with pure preflight and explicit IO."""
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import guards
ACTIONS=['inspect','show_ui','close_ui','install_extension','uninstall_extension','apply_theme','repair_cache','capture_pose','save_pose','load_pose','capture_animation','save_animation','load_animation','install_theme','uninstall_theme','set_language','show_history']
class StudioLibraryPatchTool(BaseMayaTool):
    tool_id='studiolibrary_patch';tool_name='Studio Library 世界空间与主题扩展';category='animation';version='1.0.0'
    description='Complete bundled Studio Library, world pose/animation, version history, Chinese localization and reversible ModernDark theme'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':ACTIONS,'default':'inspect'},'objects':{'type':'array','items':{'type':'string'},'maxItems':4096},
        'asset_path':{'type':'string'},'library_root':{'type':'string'},'resource_path':{'type':'string'},
        'frame_start':{'type':'number','default':1},'frame_end':{'type':'number','default':24},'sample_by':{'type':'number','exclusiveMinimum':0,'default':1},
        'blend':{'type':'number','minimum':0,'maximum':100,'default':100},'key':{'type':'boolean','default':False},'additive':{'type':'boolean','default':False},
        'start_frame':{'type':'number'},'option':{'type':'string','enum':['replace','merge','insert'],'default':'replace'},
        'language':{'type':'string','enum':['en_US','zh_CN']},'enabled':{'type':'boolean'}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in ACTIONS or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/arguments')
            for k in ('key','additive','enabled'):
                if k in kw and type(kw[k]) is not bool:raise ValueError('Boolean required: '+k)
            if not 0<=guards.finite(kw.get('blend',100))<=100:raise ValueError('Blend 0-100 required')
            if kw.get('option','replace') not in ('replace','merge','insert'):raise ValueError('Invalid paste option')
            if 'start_frame' in kw:guards.finite(kw['start_frame'])
            if action in ('capture_animation','save_animation'):guards.frames(kw.get('frame_start',1),kw.get('frame_end',24),kw.get('sample_by',1))
            if action in ('capture_pose','save_pose','load_pose','capture_animation','save_animation','load_animation'):guards.targets(kw.get('objects'),action.startswith('load'))
            if action in ('save_pose','load_pose','save_animation','load_animation'):guards.asset(kw.get('asset_path'),action.endswith('animation'),action.startswith('save'))
            if action=='show_ui' and not guards.path(kw.get('library_root')).is_dir():raise ValueError('Existing library root required')
            if action in ('install_theme','uninstall_theme'):
                from .theme_io import target
                target(kw.get('resource_path'))
            if action=='set_language' and kw.get('language') not in ('en_US','zh_CN'):raise ValueError('Language required')
            if action=='show_history' and 'enabled' not in kw:raise ValueError('Explicit enabled flag required')
            return ToolResult.ok(message='无副作用预检通过；未导入Studio Library或安装钩子',data={'action':action})
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        from . import runtime
        if action=='inspect':return ToolResult.ok(data={'features':['full_studio_library','world_pose','world_animation','history','localization','ModernDark'],'dependency_commit':'d2173f64460f3fa413ebb3696c28efacc60ef0dd','gui_acceptance':'not_run'})
        if action=='show_ui':runtime.show(kw['library_root']);return ToolResult.ok(data={'window':'MTB_StudioLibraryPlusPatch'})
        if action=='close_ui':
            if runtime.window:runtime.window.close();runtime.window=None
            return ToolResult.ok()
        if action=='install_extension':return ToolResult.ok(data=runtime.activate())
        if action=='uninstall_extension':return ToolResult.ok(data=runtime.deactivate())
        if action=='apply_theme':return ToolResult.ok(data=runtime.apply_theme())
        if action=='repair_cache':return ToolResult.ok(data=runtime.repair())
        if action in ('install_theme','uninstall_theme'):
            from . import theme_io
            return ToolResult.ok(data=getattr(theme_io,action.split('_')[0])(kw['resource_path']))
        if action in ('set_language','show_history'):
            runtime.activate()
            from studiolibrary_wanimation import localization
            if action=='set_language':localization.set_language(kw['language'])
            else:localization.set_history_enabled(kw['enabled'])
            localization.retranslate_windows([runtime.window] if runtime.window else [])
            return ToolResult.ok(data={'settings_written':True,'undo':'Use inverse settings action; not Maya Undo'})
        posemod,animmod=runtime.core();objects=guards.targets(kw['objects'],action.startswith('load'))
        from maya import cmds
        time=cmds.currentTime(q=True);selection=cmds.ls(sl=True,long=True) or []
        try:
            if action in ('capture_pose','save_pose'):world=posemod.WorldPose.capture(objects)
            elif action in ('capture_animation','save_animation'):world=animmod.WorldAnimation.capture(objects,(kw.get('frame_start',1),kw.get('frame_end',24)),kw.get('sample_by',1))
            if action.startswith('capture'):return ToolResult.ok(data={'world_data':world.data})
            if action.startswith('save'):
                import mutils
                p=guards.asset(kw['asset_path'],action.endswith('animation'),True);p.mkdir()
                try:
                    if action=='save_pose':mutils.savePose(str(p/'pose.json'),objects);world.save(str(p/'world_pose.json'))
                    else:
                        # Preserve the original world-only pose branch and
                        # full native anim.ma branch for keyed custom attrs.
                        frame_range=(kw.get('frame_start',1),kw.get('frame_end',24))
                        standard=any(cmds.keyframe(obj+'.'+attr,q=True,keyframeCount=True,time=frame_range) for obj in objects for attr in (cmds.listAttr(obj,keyable=True,unlocked=True) or []) if attr not in animmod.WORLD_ATTRIBUTES)
                        if standard:mutils.saveAnim(objects,str(p),time=frame_range,sampleBy=kw.get('sample_by',1),fileType='mayaAscii',bakeConnected=False)
                        else:
                            anim=mutils.Animation.fromObjects(objects);anim.setMetadata('startFrame',frame_range[0]);anim.setMetadata('endFrame',frame_range[1]);mutils.Pose.save(anim,str(p/'pose.json'))
                        world.save(str(p/'world_transform.json'))
                except Exception as e:raise RuntimeError('Save failed; partial NEW asset retained at '+str(p)+': '+str(e))
                return ToolResult.ok(data={'asset_path':str(p),'files':[q.name for q in p.iterdir()],'undo':'External asset files cannot be undone'})
            p=guards.asset(kw['asset_path'],action.endswith('animation'))
            if action=='load_pose':report=posemod.load_wpose(str(p),objects=objects,blend=kw.get('blend',100),key=kw.get('key',False),additive=kw.get('additive',False),refresh=False,clearSelection=False)
            else:report=animmod.load_wanimation(str(p),objects=objects,start_frame=kw.get('start_frame'),option=kw.get('option','replace'))
            if report.get('failed') or report.get('cancelled'):return ToolResult.fail(message='Native load reported incomplete result; use Undo and inspect',errors=[str(report)],data=report)
            return ToolResult.ok(data=report)
        finally:
            cmds.currentTime(time,edit=True);cmds.select(selection,r=True) if selection else cmds.select(clear=True)
    def show_ui(self,parent=None):
        # Full original library; ask for an existing asset root through Maya UI.
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        selected=cmds.fileDialog2(fileMode=3,caption='StudioLibrary 候选：选择已有资产目录')
        if not selected:return None
        from .runtime import show
        return show(selected[0],parent)
''')
# Standalone theme entries remain available but must choose an explicit external target.
for name in ('install','uninstall'):
    put(NATIVE/f'StudioLibrary_ThemePatch/{name}_theme.py',f'''"""Guarded explicit theme {name}; external files cannot be Maya-undone."""
def {name}_theme(resource_path):
    from maya_toolkit.tools.studiolibrary_patch.theme_io import {name}
    return {name}(resource_path)
''')
put(RC/'docs/tools/studiolibrary_patch.md','''# Studio Library PlusPatch 完整待验候选

保留用户17个原文件精确SHA归档，完整世界空间姿态/动画、Save/Load widgets、中文菜单/表单/历史版本、ModernDark CSS；补齐官方 krathjen/studiolibrary 固定提交 d2173f64460f3fa413ebb3696c28efacc60ef0dd 的257文件（StudioLibrary 2.21.7、studioqt/studiovendor/mutils/studiolibrarymaya、字体/图标/UI/XML/配置及 LGPL3/各嵌入组件通知）。vendor/dependency_provenance.json记录逐文件SHA及公开CDN下载来源，全部未来正式目录自包含，第三方库保留模块名和许可。candidate native修改源与精确依赖原档可对比，未推定原自有扩展有另行公开授权。

默认inspect/validate不导入Studio/Qt，不注册hooks、启动callback或写cache；install_extension/show_ui才显式激活。若用户先加载另一个Studio Library/mutils/Qt shim，明确拒绝混用，需新Maya会话加载本候选。完整库窗口 name=MTB_StudioLibraryPlusPatch，选择已有资产root，禁用本窗口更新检查，不修改系统安装、userSetup；原有标准pose/anim/set/mirror item通过原config注册，扩展增加WPose/WAnimation。世界姿态保持匹配、父层级优先、blend/key/mirrorTable/additive，世界动画保持完整non-world attrs、replace/merge/insert、自定义SaveWidget和采样收集器。高级镜像/名称替换/连接bake选项保留完整原GUI；公开API使用显式objects以避免不明确目标。

API类 StudioLibraryPatchTool，actions见Schema：inspect、show/close_ui、install/uninstall_extension、capture/save/load_pose与animation、apply_theme、install/uninstall_theme、repair_cache、set_language、show_history。frame_start/end/sample_by正有限与样本数量上限，JSON重复key/非有限值/不正确matrix/向量/时间次序拒绝，1–4096精确非wildcard transforms，全部目标锁定/外部非animCurve驱动先检，坏末项不会先cutKey。world捕获时间/选择恢复在Base UndoChunk内；load返回native failed/cancelled即fail，不能把半成功称全通过。底层UI world入口同样加数据/目标预检，不自动覆盖锁轴；生产约束/joint/shear/负scale/跨rotateOrder的最终匹配仍须真实验收。

save仅已有parent的新绝对.wpose/.wanim资产：标准pose.json与world_pose.json，或完整mutils Animation原生anim.ma/pose.json及world_transform.json；不是仅world JSON壳。异常保留本次新建的部分资产供恢复，不能scene Undo文件写入。原GUI safeSave可明确覆盖资产并生成.history/v####只读虚拟item：覆盖前完整snapshot与历史移入同卷自有stage；失败重建整个原资产+历史，失败半成品留stage，不只恢复历史。历史合并遇到同名版本拒绝并留恢复stage，不删除旧版本；symlink/未知stage拒绝。成功后历史版本与元数据保留原时间/类型，原base删除到trash和外部保存不由scene Undo撤销，需备份库验收。

ModernDark在候选自有窗口内用Theme.options解析CSS所有颜色/资源/DPI token；apply_theme不改磁盘或外来窗口。standalone install/uninstall_theme须明确外部resource_path（css/default.css已存在、非symlink、不可本bundle）：先exclusive精确备份+hash核验+receipt，再同卷atomic换CSS；已有receipt只允许同内容重入，外部修改或备份损坏拒绝卸载、不覆盖用户变动；restore原CSS，保留backup供检查。不再备份失败仍覆盖、不全局热重载/自动saveSettings。主题、资产、QSettings、cache均外部写入，不能Maya Undo；set_language/show_history反向动作恢复偏好。

repair_cache仅显式自有窗口，数据库必须chosenroot内，先精确备份；扫描/旧cachedpath限定root，不自动修复所有实例。安装hook记录每class原callable/Field/item注册，失败回滚，uninstall只还原自身仍持有的函数和item，foreign后安装wrapper拒绝强覆盖。关闭UI不等同卸载扩展；使用uninstall_extension明确撤hooks。组合：标准pose和动画可衔接时间/关键帧整理工具；不是仅静态import就证明复杂rig跨工具链成功。

离线history/theme恢复与外部改动拒绝、Schema/defaultinspect纯导入及未来完整layout检查；mayapy世界捕获/保存/加载/一次Undo与坏末项预检，单独Qt核验基础组件及原integration接口。均不替代真实Maya GUI；全部真实窗口/交互/标准和扩展资产生产rig/镜像/cache/覆盖历史/跨版本为not_run，验收前不迁正式。
''')
put(RC/'acceptance.md','''# Studio Library PlusPatch Maya GUI 验收 not_run

1. 新Maya会话用launch_candidate.show_ui选择备份资产root；原标准pose/anim/set/mirror与WPose/WAnimation菜单、完整Save/Load/采样/缩略图/sequence、namespace/名称替换/镜像选项，中文切换和Last Modified/历史显示均逐项响应。inspect/dry前后无Qt/hook/cache写入，只有主动启用才patch，不启动自动cache修复。
2. 备份rig层级变换/不同rotateOrder/约束/锁轴/缩放/world pose blend/additive/mirror，world animation replace/merge/insert非world custom attrs/多帧/采样bake与一次UndoRedo；最后无效或锁住对象应在首项写入前拒绝。原native report任何failed/cancelled不能记全成功。
3. 新.wpose/.wanim完整pose.json/anim.ma/worldJSON roundtrip；同名资产仅GUI明确覆盖，历史v####原payload与thumbnail/metadata精确保留，只读虚拟历史回读。模拟保存失败恢复原本体和.history；collision/损坏/symlink不静默删版本，保留stage/partial新资产供检查，外部文件不由Maya Undo撤回。
4. ModernDark原CSS所有token/DPI/字体图标实际显示；候选apply_theme只本窗口不写bundle文件。外部resource install先备份、重复install、uninstall还原，原CSS被另一工具改过拒绝restore而保留它；cache repair自有root限定/精确backup，无自动全局修复，QSettings语言/历史显式改变可反向恢复。
5. 重复install/uninstall无叠加；foreign后装wrapper/item registry变化拒绝强覆盖，关闭/重开窗口不操作其他库。Maya2025与所需旧版本真实核验；记录candidate_sha256/maya_version/accepted_by/date/passed=true后再promotion。当前任何离线/isolated mayapy/Qt均非真实GUI实测。
''')
put(RC/'tests/test_studiolibrary_patch.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.studiolibrary_patch import StudioLibraryPatchTool
    tool=StudioLibraryPatchTool()
from maya_toolkit.tools.studiolibrary_patch import guards,theme_io,history_safety
class Checks(unittest.TestCase):
    def test_pure_preflight_and_theme_exact_restore(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('studiolibrary',sys.modules)
        with self.assertRaises(ValueError):guards.frames(1,float('inf'),1)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'css').mkdir();p=root/'css/default.css';p.write_bytes(b'original\r\nCSS')
            row=theme_io.install(str(root));self.assertEqual(Path(row['backup']).read_bytes(),b'original\r\nCSS');theme_io.install(str(root))
            p.write_bytes(b'foreign')
            with self.assertRaises(ValueError):theme_io.uninstall(str(root))
            self.assertEqual(p.read_bytes(),b'foreign');p.write_bytes(theme_io.CSS.read_bytes());theme_io.uninstall(str(root));self.assertEqual(p.read_bytes(),b'original\r\nCSS')
    def test_history_payload_failure_and_success(self):
        source=Path(history_safety.__file__).parent/'native/studiolibrary_wanimation/history.py';spec=importlib.util.spec_from_file_location('offline_history',source);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);history_safety.install(h)
        class Item:EXTENSION='.wpose'
        with tempfile.TemporaryDirectory() as td:
            asset=Path(td)/'x.wpose';asset.mkdir();(asset/'payload').write_bytes(b'old');(asset/'.history/v0001').mkdir(parents=True);(asset/'.history/v0001/data').write_bytes(b'version')
            row=h.stage_existing_asset(str(asset),Item());(asset/'payload').write_bytes(b'broken');self.assertTrue(h.restore_stage(row));self.assertEqual((asset/'payload').read_bytes(),b'old');self.assertEqual((asset/'.history/v0001/data').read_bytes(),b'version')
            row=h.stage_existing_asset(str(asset),Item());(asset/'payload').write_bytes(b'new');version=h.commit_stage(row,str(asset));self.assertEqual(Path(version).name,'v0002');self.assertEqual((Path(version)/'payload').read_bytes(),b'old');self.assertEqual((asset/'.history/v0001/data').read_bytes(),b'version');self.assertEqual((asset/'payload').read_bytes(),b'new')
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_studiolibrary_patch_maya.py',r'''import importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Maya process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya_toolkit.tools.studiolibrary_patch import runtime,guards
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True)
    def test_pose_full_roundtrip_one_undo_and_preflight(self):
        parent=cmds.createNode('transform',name='parent');node=cmds.createNode('transform',name='control',parent=parent);cmds.setAttr(parent+'.tx',10);cmds.setAttr(node+'.tx',3);cmds.select(node);cmds.currentTime(7)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'test.wpose');result=tool.run(action='save_pose',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertTrue((Path(p)/'pose.json').is_file());self.assertTrue((Path(p)/'world_pose.json').is_file())
            cmds.setAttr(node+'.tx',8);cmds.flushUndo();result=tool.run(action='load_pose',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertAlmostEqual(cmds.xform(node,q=True,ws=True,t=True)[0],13);self.assertEqual(cmds.currentTime(q=True),7);self.assertEqual(cmds.ls(sl=True),[node]);cmds.undo();self.assertAlmostEqual(cmds.getAttr(node+'.tx'),8)
            cmds.setAttr(node+'.rz',lock=True);self.assertFalse(tool.run(action='load_pose',objects=[node],asset_path=p,dry_run=True).success);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),8)
    def test_world_animation_capture_paste_and_bad_last(self):
        node=cmds.createNode('transform',name='control');cmds.setKeyframe(node,at='tx',t=1,v=2);cmds.setKeyframe(node,at='tx',t=3,v=6);cmds.currentTime(9);cmds.select(node)
        result=tool.run(action='capture_animation',objects=[node],frame_start=1,frame_end=3,sample_by=1);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.currentTime(q=True),9)
        wp,wa=runtime.core();world=wa.WorldAnimation(result.data['world_data']);cmds.cutKey(node,clear=True);cmds.setAttr(node+'.tx',20);cmds.flushUndo()
        cmds.undoInfo(openChunk=True)
        try:report=wa.paste_world_animation(world,objects=[node]);cmds.currentTime(9)
        finally:cmds.undoInfo(closeChunk=True)
        self.assertFalse(report['failed']);self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),3);cmds.undo();self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),0);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),20)
        self.assertFalse(tool.validate(action='capture_pose',objects=[node,'absent']).success)
    def test_animation_asset_full_roundtrip(self):
        node=cmds.createNode('transform',name='control');cmds.setKeyframe(node,at='tx',t=1,v=2);cmds.setKeyframe(node,at='tx',t=3,v=6);cmds.currentTime(9);cmds.select(node)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'test.wanim');result=tool.run(action='save_animation',objects=[node],asset_path=p,frame_start=1,frame_end=3);self.assertTrue(result.success,result.errors);self.assertTrue((Path(p)/'pose.json').exists());self.assertTrue((Path(p)/'world_transform.json').exists())
            cmds.cutKey(node,clear=True);cmds.setAttr(node+'.tx',20);cmds.flushUndo();result=tool.run(action='load_animation',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),3);cmds.undo();self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),0);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),20)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_studiolibrary_patch_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process only; no Maya standalone init')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.studiolibrary_patch import runtime
class QtChecks(unittest.TestCase):
    def test_full_extension_interfaces_theme_and_hook_ownership(self):
        runtime.ensure_paths()
        import studiolibrary,studiolibrary.libraryitem,studiolibrary.librarywindow,studiolibrary.widgets,studioqt
        from studiolibrary_wanimation import localization
        with tempfile.TemporaryDirectory() as td:
            QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat);QtCore.QSettings.setPath(QtCore.QSettings.IniFormat,QtCore.QSettings.UserScope,td)
            original=studiolibrary.libraryitem.LibraryItem.safeSave;runtime.activate();own=studiolibrary.libraryitem.LibraryItem.safeSave
            try:
                self.assertIsNot(own,original);self.assertEqual({cls.__name__ for cls in studiolibrary.registeredItems()},{'WPoseItem','WAnimationItem'})
                callback=lambda:None;schema=[{'name':'Blend','label':'Blend','callback':callback}];copy=localization.translate_schema(schema);self.assertIs(copy[0]['callback'],callback);self.assertEqual(schema[0]['label'],'Blend')
                theme=studiolibrary.widgets.Theme();theme.setAccentColor('rgb(108, 92, 231)');theme.setBackgroundColor('rgb(24, 25, 32)')
                from maya_toolkit.tools.studiolibrary_patch.theme_io import CSS
                css=studioqt.StyleSheet.fromPath(str(CSS),options=theme.options(),dpi=theme.dpi()).data();self.assertNotIn('FOREGROUND_COLOR_R',css);self.assertNotIn('RESOURCE_DIRNAME',css);self.assertIn('108',css)
                menu=studioqt.menu.Menu();menu.addAction('Settings');self.assertIsNotNone(menu.findAction('Settings'));menu.deleteLater()
                win=studiolibrary.librarywindow.LibraryWindow(name='MTB_offscreen_fixture');win.setCheckForUpdateEnabled(False)
                runtime.window=win;runtime.apply_theme();self.assertIn('108',win.styleSheet());win.close();runtime.window=None;win.deleteLater()
                def foreign(*args,**kw):return own(*args,**kw)
                studiolibrary.libraryitem.LibraryItem.safeSave=foreign
                with self.assertRaises(RuntimeError):runtime.deactivate()
                self.assertIs(studiolibrary.libraryitem.LibraryItem.safeSave,foreign);studiolibrary.libraryitem.LibraryItem.safeSave=own
            finally:
                studiolibrary.libraryitem.LibraryItem.safeSave=own;runtime.deactivate()
            self.assertIs(studiolibrary.libraryitem.LibraryItem.safeSave,original)
if __name__=='__main__':unittest.main()
''')
# Snapshot .py files are inert exact originals; live vendor source is parsed/tested.
for p in (RC/'dependency_source').rglob('*.py'):p.rename(p.with_suffix('.py.original'))
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/studiolibrary_patch','--class-name','StudioLibraryPatchTool','--summary','Complete pinned Studio Library world-pose/animation/history/localization/theme with explicit reversible hooks and recoverable external IO','--dependencies','Bundled StudioLibrary official pinned commit d2173f64460f3fa413ebb3696c28efacc60ef0dd LGPL3 and embedded notices','Maya cmds/API2 and PySide6/PySide2','--limitations','Real Maya GUI/production rigs/history overwrite/cache/mirror/advanced native save and cross-version acceptance not_run'],check=True)
