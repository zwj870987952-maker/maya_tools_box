"""Complete native Maya shelf manager; bounded scans and recoverable disk operations."""
import ast,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/08_utilities_system/shelf_manager';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/shelf_manager'
put(PKG/'backend.py',r'''from pathlib import Path
import hashlib,json,os,re,shutil,uuid
DEFAULTS={'Animation','Arnold','Bifrost','Cexport','CurvesSurfaces','Custom','FX','FXCaching','MASH','MotionGraphics','MSPlugin','Polygons','Rendering','Rigging','Sculpting','TURTLE','XGen','Brushes','Display','Dynamics','General','Help','Modeling','Paint Effects','Stereo','Subdivision','Surfaces','UV'}
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Valid absolute path required')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def roots(values):
    if not isinstance(values,list) or not 1<=len(values)<=32:raise ValueError('1-32 explicit roots required')
    result=[]
    for value in values:
        p=path(value)
        if not p.is_dir():raise ValueError('Existing Maya preference root required')
        if p.resolve() not in result:result.append(p.resolve())
    return result
def detect():
    values=[Path.home()/'Documents/maya',Path.home()/'maya'];env=os.environ.get('MAYA_APP_DIR')
    if env:values.append(Path(env))
    return [str(p) for p in values if p.is_dir() and not any(q.is_symlink() for q in (p,*p.parents))]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def scan(values,include_defaults=False):
    base=roots(values);rows=[]
    for root in base:
        for version in range(2018,2027):
            for lang,sub in (('zh','zh_CN/prefs/shelves'),('en','prefs/shelves')):
                folder=root/str(version)/sub
                if not folder.is_dir():continue
                if any(q.is_symlink() for q in (folder,*folder.parents)):continue
                for p in sorted(folder.glob('shelf_*.mel')):
                    if not p.is_file() or p.is_symlink() or not p.stem[6:] or p.stat().st_size>16*1024*1024:continue
                    name=p.stem[6:]
                    if not include_defaults and name in DEFAULTS:continue
                    rows.append({'root':str(root),'version':str(version),'language':lang,'name':name,'path':str(p.resolve()),'icon':str(p.with_suffix('.png')) if p.with_suffix('.png').is_file() and not p.with_suffix('.png').is_symlink() else None,'sha256':sha(p)})
                    if len(rows)>10000:raise ValueError('Shelf scan exceeds 10000 files')
    return rows
def selected(values,files,icons=True):
    base=roots(values)
    if not isinstance(files,list) or not 1<=len(files)<=1000 or len(set(files))!=len(files):raise ValueError('1-1000 unique explicit shelf paths required')
    catalog={r['path']:r for r in scan(values,True)};rows=[]
    for value in files:
        p=path(value).resolve();row=catalog.get(str(p))
        if row is None:raise ValueError('File is not a scanned shelf in an explicit root: '+str(p))
        rows.append({'source':p,'root':Path(row['root']),'sha256':row['sha256']})
        if icons and row['icon']:
            icon=path(row['icon']);rows.append({'source':icon,'root':Path(row['root']),'sha256':sha(icon)})
    return rows
def migration(values,files,target,icons=True,overwrite=False):
    destination=path(target)
    if not destination.is_dir():raise ValueError('Existing migration directory required')
    if Path(__file__).parent.resolve() in (destination.resolve(),*destination.resolve().parents):raise ValueError('Candidate bundle is immutable')
    rows=selected(values,files,icons);seen=set()
    for row in rows:
        output=destination/row['source'].name
        if os.path.normcase(str(output)) in seen:raise ValueError('Two selected sources collide at destination')
        seen.add(os.path.normcase(str(output)));path(str(output))
        if output.resolve()==row['source'].resolve():raise ValueError('Source/destination identical')
        if output.exists() and (not output.is_file() or not overwrite):raise ValueError('Existing migration target requires explicit overwrite')
        row['target']=output
    return rows
def migrate(rows):
    receipts=[]
    for row in rows:
        source=row['source'];target=row['target']
        if sha(source)!=row['sha256']:raise RuntimeError('Source changed after preflight; previous completed copies preserved')
        backup=None
        if target.exists():
            backup=target.with_name(target.name+'.mtb_backup_'+uuid.uuid4().hex)
            with target.open('rb') as f,backup.open('xb') as out:shutil.copyfileobj(f,out)
            if sha(target)!=sha(backup):raise IOError('Backup mismatch')
        temporary=target.with_name('.mtb_copy_'+uuid.uuid4().hex)
        try:
            with source.open('rb') as f,temporary.open('xb') as out:shutil.copyfileobj(f,out)
            if sha(temporary)!=row['sha256'] or sha(source)!=row['sha256']:raise IOError('Copy/source hash mismatch')
            if not backup:
                # Exclusive final creation preserves a concurrent new destination.
                with temporary.open('rb') as f,target.open('xb') as out:shutil.copyfileobj(f,out)
            else:
                if sha(target)!=sha(backup):raise RuntimeError('Destination changed after backup; preserve foreign edit')
                os.replace(temporary,target)
            receipts.append({'source':str(source),'target':str(target),'backup':str(backup) if backup else None,'sha256':row['sha256']})
        finally:
            if temporary.exists():temporary.unlink()
    return receipts
def quarantine(rows):
    receipts=[];folders={}
    for row in rows:
        source=row['source'];root=row['root'].resolve()
        if root not in source.resolve().parents or sha(source)!=row['sha256']:raise RuntimeError('Source scope/hash changed; previous quarantined files recoverable')
        if root not in folders:
            folder=root/('.mtb_shelf_trash_'+uuid.uuid4().hex);folder.mkdir();folders[root]=folder
        folder=folders[root];target=folder/(uuid.uuid4().hex+'_'+source.name)
        if root not in target.resolve().parents or target.exists():raise ValueError('Invalid quarantine destination')
        source.rename(target);receipts.append({'source':str(source),'quarantine':str(target),'sha256':row['sha256']})
        (folder/'receipt.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return receipts
''')
put(PKG/'session.py',r'''from pathlib import Path
import importlib,json
from . import backend
window=None;source_roots=None;own_ui={};loaded={}
def close():
    global window
    if window is None:return
    from maya import cmds,OpenMayaUI
    name=window.window_name
    if cmds.window(name,exists=True):
        if not own_ui.get(name) or int(OpenMayaUI.MQtUtil.findWindow(name) or 0)!=own_ui[name]:raise RuntimeError('Foreign window replacement preserved')
        cmds.deleteUI(name,window=True)
    own_ui.pop(name,None);window=None
def show(values=None):
    global window,source_roots
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    source_roots=[str(p) for p in backend.roots(values or backend.detect())];close();module=importlib.import_module('maya_toolkit.tools.shelf_manager.native');window=module.ShelfManager();return window
class Commands:
    def __getattr__(self,name):
        from maya import cmds,OpenMayaUI
        fn=getattr(cmds,name)
        def call(*args,**kw):
            if name=='deleteUI':
                if not args or args[0] not in own_ui:raise ValueError('Foreign UI deletion refused')
                if int(OpenMayaUI.MQtUtil.findWindow(args[0]) or 0)!=own_ui[args[0]]:raise ValueError('Foreign UI replacement preserved')
            if name=='window' and args and not any(kw.get(k) for k in ('exists','ex','query','q','edit','e')) and cmds.window(args[0],exists=True):raise ValueError('Existing manager window preserved')
            result=fn(*args,**kw)
            if name=='window' and not any(kw.get(k) for k in ('exists','ex','query','q','edit','e')):own_ui[result]=int(OpenMayaUI.MQtUtil.findWindow(result) or 0)
            if name=='deleteUI':own_ui.pop(args[0],None)
            return result
        return call
cmds=Commands()
def load_shelf(value):
    from maya import cmds,mel,OpenMayaUI
    path=backend.path(value)
    name=path.stem[6:]
    top=mel.eval('$tmp=$gShelfTopLevel');before=cmds.tabLayout(top,q=True,childArray=True) or []
    for child in before:
        if child.rsplit('|',1)[-1]==name or cmds.shelfLayout(child,q=True,annotation=True)==name:raise ValueError('Existing shelf UI preserved; rename incoming shelf first')
    mel.eval('loadNewShelf '+json.dumps(str(path).replace('\\','/'))+';')
    after=cmds.tabLayout(top,q=True,childArray=True) or []
    for child in set(after)-set(before):loaded[child]=int(OpenMayaUI.MQtUtil.findLayout(child) or 0)
    return {'source':str(path),'added_layouts':sorted(set(after)-set(before)),'executes_mel':True}
def gui_load(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    files=[r[1] for r in selected];backend.selected(manager.user_paths,files,False)
    if cmds.confirmDialog(title='加载工具架',message='加载会执行所选MEL文件代码，仅继续信任的工具架。',button=['Load','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')!='Load':return
    results=[load_shelf(value) for value in files];cmds.text(manager.status_text,e=True,label='已加载 {} 个工具架'.format(len(results)))
def gui_delete(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    rows=backend.selected(manager.user_paths,[r[1] for r in selected],True)
    if cmds.confirmDialog(title='移入可恢复目录',message='将所选工具架及同名PNG移入源root下独立隔离目录；保留receipt，不删除已存在的外来shelf UI。',button=['Quarantine','Cancel'],defaultButton='Cancel',cancelButton='Cancel',dismissString='Cancel')!='Quarantine':return
    result=backend.quarantine(rows);manager._initial_scan();cmds.text(manager.status_text,e=True,label='已隔离 {} 个文件；源root的.mtb_shelf_trash_*中可恢复'.format(len(result)))
def gui_migrate(manager):
    from maya import cmds
    selected=manager._get_selected_shelves()
    if not selected:return cmds.warning('请先选择工具架')
    targets=cmds.fileDialog2(fileMode=3,caption='选择复制目标目录（源文件保留，已有同名拒绝）')
    if not targets:return
    rows=backend.migration(manager.user_paths,[r[1] for r in selected],targets[0],True,False);result=backend.migrate(rows);cmds.text(manager.status_text,e=True,label='已复制 {} 个文件，源文件保留'.format(len(result)))
''')
source=(UNIT/'shelf_manager.py').read_text(encoding='utf-8-sig');s=source.replace('import maya.cmds as cmds','from maya_toolkit.tools.shelf_manager.session import cmds').replace('import maya.mel as mel','# MEL import deferred to explicit session.load_shelf').replace('self.window_name = "ShelfManagerWindow"','self.window_name = "MTB_ShelfManagerWindow"')
methods={
'_detect_maya_user_paths':'''def _detect_maya_user_paths(self):
    from maya_toolkit.tools.shelf_manager import session,backend
    return session.source_roots or backend.detect()''',
'_scan_versions_in_path':'''def _scan_versions_in_path(self,base_path):
    from maya_toolkit.tools.shelf_manager.backend import scan
    rows=scan([base_path],True)
    for row in rows:
        version=row['version'];lang=row['language']
        if version not in self.maya_versions:self.maya_versions.append(version);self.shelf_data[version]={'zh':[],'en':[]}
        if row['path'] not in self.shelf_data[version][lang]:self.shelf_data[version][lang].append(row['path'])
    return bool(rows)''',
'_update_shelf_lists':'''def _update_shelf_lists(self):
    if not self.current_version:return
    self.zh_shelf_map.clear();self.en_shelf_map.clear()
    for lang,control,mapping in [('zh',self.zh_shelf_list,self.zh_shelf_map),('en',self.en_shelf_list,self.en_shelf_map)]:
        cmds.textScrollList(control,edit=True,removeAll=True)
        for shelf_path in sorted(self.shelf_data.get(self.current_version,{}).get(lang,[])):
            name=os.path.basename(shelf_path)[6:-4]
            if not self.show_default_shelves and name in self.default_shelves:continue
            display=name+' ['+shelf_path+']';mapping[display]=shelf_path
            cmds.textScrollList(control,edit=True,append=[display])''',
'_get_selected_shelves':'''def _get_selected_shelves(self):
    rows=[]
    for lang,control,mapping in [('zh',self.zh_shelf_list,self.zh_shelf_map),('en',self.en_shelf_list,self.en_shelf_map)]:
        for display in cmds.textScrollList(control,query=True,selectItem=True) or []:
            if display in mapping:
                p=mapping[display];rows.append((os.path.basename(p)[6:-4],p,lang))
    return rows''',
'load_shelves':'''def load_shelves(self,*args):
    from maya_toolkit.tools.shelf_manager.session import gui_load
    return gui_load(self)''',
'delete_shelves':'''def delete_shelves(self,*args):
    from maya_toolkit.tools.shelf_manager.session import gui_delete
    return gui_delete(self)''',
'migrate_shelves':'''def migrate_shelves(self,*args):
    from maya_toolkit.tools.shelf_manager.session import gui_migrate
    return gui_migrate(self)''',
}
tree=ast.parse(s);lines=s.splitlines();edits=[]
for n in ast.walk(tree):
    if isinstance(n,ast.FunctionDef) and n.name in methods:edits.append((n.lineno-1,n.end_lineno,'\n'.join(' '*n.col_offset+line for line in methods[n.name].splitlines())))
for a,b,t in sorted(edits,reverse=True):lines[a:b]=t.splitlines()
put(PKG/'native.py','\n'.join(lines)+'\n')
put(PKG/'__init__.py',r'''from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import backend
class ShelfManagerTool(BaseMayaTool):
    tool_id='shelf_manager';tool_name='跨版本工具架管理器';category='scene_hygiene';version='1.0.0'
    description='Complete original bilingual/version shelf manager with scoped scans, explicit MEL loading, recoverable quarantine and collision-safe migration'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','scan','show_ui','close_ui','load','quarantine','migrate'],'default':'inspect'},'roots':{'type':'array','items':{'type':'string'},'maxItems':32},'files':{'type':'array','items':{'type':'string'},'maxItems':1000},'target_dir':{'type':'string'},'include_defaults':{'type':'boolean','default':False},'include_icons':{'type':'boolean','default':True},'overwrite':{'type':'boolean','default':False},'confirm_execute_mel':{'type':'boolean','default':False},'confirm_quarantine':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/argument')
            for key in ('include_defaults','include_icons','overwrite','confirm_execute_mel','confirm_quarantine'):
                if key in kw and type(kw[key]) is not bool:raise ValueError('Strict boolean '+key)
            if action not in ('inspect','close_ui'):backend.roots(kw.get('roots'))
            if action in ('load','quarantine'):backend.selected(kw['roots'],kw.get('files'),kw.get('include_icons',True))
            if action=='load' and not kw.get('confirm_execute_mel'):raise ValueError('Loading executes MEL; explicit confirm_execute_mel required')
            if action=='quarantine' and not kw.get('confirm_quarantine'):raise ValueError('Explicit quarantine confirmation required')
            if action=='migrate':backend.migration(kw['roots'],kw.get('files'),kw.get('target_dir'),kw.get('include_icons',True),kw.get('overwrite',False))
            return ToolResult.ok(message='只读文件预检/扫描，无MEL执行/UI/复制或移动')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'complete_original':True,'versions':'2018-2026','default_delete':'recoverable quarantine','gui_acceptance':'not_run'})
        if action=='scan':return ToolResult.ok(data={'shelves':backend.scan(kw['roots'],kw.get('include_defaults',False))})
        if action=='migrate':return ToolResult.ok(data={'receipts':backend.migrate(backend.migration(kw['roots'],kw['files'],kw['target_dir'],kw.get('include_icons',True),kw.get('overwrite',False)))})
        if action=='quarantine':return ToolResult.ok(data={'receipts':backend.quarantine(backend.selected(kw['roots'],kw['files'],kw.get('include_icons',True)))})
        from . import session
        if action=='show_ui':session.show(kw['roots']);return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya shelf GUI required')
        return ToolResult.ok(data={'loaded':[session.load_shelf(value) for value in kw['files']]})
    def show_ui(self,parent=None):
        from . import session
        return session.show()
''')
put(RC/'tests/test_shelf_manager.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_shelf',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.shelf_manager import ShelfManagerTool
    tool=ShelfManagerTool()
from maya_toolkit.tools.shelf_manager import backend
class Checks(unittest.TestCase):
    def test_scoped_bilingual_duplicate_names_collision_backup_and_quarantine(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.shelf_manager.native',sys.modules)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'maya';en=root/'2025/prefs/shelves';zh=root/'2025/zh_CN/prefs/shelves';en.mkdir(parents=True);zh.mkdir(parents=True);output=Path(td)/'out';output.mkdir()
            a=en/'shelf_CustomTool.mel';a.write_text('global proc shelf_CustomTool() {}');a.with_suffix('.png').write_bytes(b'icon');b=zh/'shelf_CustomTool.mel';b.write_text('different content');(en/'shelf_Animation.mel').write_text('default')
            roots=[str(root)];rows=backend.scan(roots);self.assertEqual(len(rows),2);self.assertEqual({r['language'] for r in rows},{'zh','en'})
            with self.assertRaises(ValueError):backend.migration(roots,[str(a),str(b)],str(output))
            self.assertEqual(list(output.iterdir()),[])
            receipts=backend.migrate(backend.migration(roots,[str(a)],str(output)));self.assertEqual(len(receipts),2);self.assertTrue(a.is_file());target=output/a.name;old=target.read_bytes();a.write_text('updated content')
            with self.assertRaises(ValueError):backend.migration(roots,[str(a)],str(output))
            receipts=backend.migrate(backend.migration(roots,[str(a)],str(output),overwrite=True));self.assertEqual(Path(receipts[0]['backup']).read_bytes(),old)
            with self.assertRaises(ValueError):backend.selected(roots,[str(a),str(output/a.name)])
            self.assertTrue(a.exists());receipts=backend.quarantine(backend.selected(roots,[str(a)]));self.assertFalse(a.exists());self.assertTrue(b.exists());self.assertTrue(all(Path(r['quarantine']).exists() for r in receipts));self.assertTrue(list(root.glob('.mtb_shelf_trash_*/receipt.json')))
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_shelf_manager_native.py',r'''import importlib.util,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_shelf',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.shelf_manager import session
class FakeCommands:
    def __init__(self):self.count=0;self.items={};self.values={};self.selections={}
    def __getattr__(self,name):
        def call(*args,**kw):
            if name=='window' and kw.get('exists'):return False
            if name=='about':return '2025'
            if kw.get('query'):
                if kw.get('selectItem'):return self.selections.get(args[0],[])
                return self.values.get(args[0],[])
            if kw.get('edit'):
                target=args[0]
                if kw.get('removeAll') or kw.get('deleteAllItems'):self.items[target]=[]
                if 'append' in kw:self.items.setdefault(target,[]).extend(kw['append'])
                if 'value' in kw:self.values[target]=kw['value']
                return target
            self.count+=1;value=args[0] if args and name=='window' else name+str(self.count);self.items.setdefault(value,[]);return value
        return call
class NativeChecks(unittest.TestCase):
    def test_complete_native_ui_scan_lists_and_full_path_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'2025/prefs/shelves';folder.mkdir(parents=True);p=folder/'shelf_Mine.mel';p.write_text('global proc shelf_Mine() {}')
            session.source_roots=[str(root)]
            import maya_toolkit.tools.shelf_manager.native as native
            fake=FakeCommands();native.cmds=fake;win=native.ShelfManager();self.assertGreater(fake.count,20);self.assertEqual(win.maya_versions,['2025']);self.assertEqual(len(win.en_shelf_map),1)
            display=next(iter(win.en_shelf_map));fake.selections[win.en_shelf_list]=[display];self.assertEqual(win._get_selected_shelves()[0][1],str(p.resolve()))
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/shelf_manager.md','''# 跨版本工具架管理器完整候选

原源码SHA精确归档，完整cmds窗口/中英文双列表/2018-2026自动版本/默认工具架toggle/refresh/选择/加载/迁移/删除交互保留。Base/API/Schema/无副作用预检/未来注册面板预制，默认inspect不native/MEL/UI。扫描明确1-32现有non-symlink Maya prefs roots，仅root/2018..2026/{zh_CN/}prefs/shelves/文件名shelf_*.mel，max10000/16MiB；GUI可建议HOME/MAYA_APP_DIR标准已存目录，移除原C/D盘recursive全盘fallback。多root同版本同名按完整路径显示/选中，不再被name_version映射覆盖；默认shelf数据全部收集后toggle显示而不是初扫永久遗漏。

迁移实际是复制，源保留；先整批预检碰撞/坏末项/范围/同src-target/PNG伙伴，再hash核对与exclusive新输出，overwrite=True明确先exact备份现有目标、临时copy hash核验并atomic替换；目标并发改动拒绝覆盖。相邻同名PNG可include_icons；不会查找/迁移任意全局图片依赖，跨版本MEL实际兼容和外部图标路径待直验。运行中IO失败可能有前项已完成，不能声称事务all-or-none，成功返回receipt/data列出目标/备份；运行中异常的失败结果不含完整已完成列表，应按目标目录和.mtb_backup_*材料逐项核对恢复；普通碰撞在写任何项前拒绝。

原删除硬盘文件和按同名annotation删任意shelf UI，改明确Quarantine把源mel/同名png移入对应root独立.mtb_shelf_trash_UUID，receipt记录原路径/SHA/隔离文件，可手动精确恢复，不rmtree/unlink原文件。明确roots/选择/确认后才移，不清foreign已载shelf UI、共用图标或注册startup；文件复制/覆盖/移动和Maya shelf UI不可scene Undo。若恢复时原路径已存在，先比较SHA/备份，不盲覆盖。

加载MEL可执行用户脚本，API confirm_execute_mel/GUI明确Load按钮确认，不在scan/dry/migrate/delete执行。源路径MEL json quoting，已有目标同名shelf UI预检保留；实际MEL可任意改UI/scene/files，不声称静态检查证明其安全，候选只对信任临时shelf直验。own manager窗口MQt pointer跟踪/foreign重名拒绝删除，关闭只manager不删用户loaded shelf。完整原UI的本机临时mock构造/双语言/完整路径选择和后台文件扫描/冲突/backup/坏末项/可恢复隔离/future注册离线检查；真实Maya shelf加载/UI版本和外部图标/生产MELnot_run。
''')
put(RC/'acceptance.md','''# 工具架管理器真实Maya验收 not_run

1. 仅复制好的临时prefs root，在真实Maya打开完整版本选择、中英文双列、默认shelf toggle/refresh、多root同名完整路径区分；不扫C/D全盘、不自动loadMEL。
2. 仅信任临时shelf，Load提示会执行MEL，取消无执行；同名现有shelf UI拒绝覆盖，旧代码/外部icon路径实际兼容2018-2026分别核验。
3. 迁移=复制源保留，整批同名/坏最后拒绝无首项写；已有API overwrite明确backup，PNG伙伴/hash一致。IO失败可能留有前项已完成的目标和备份；失败结果不提供完整已完成列表，按目标目录和.mtb_backup_*材料逐项核对恢复。文件写不可scene Undo。
4. Quarantine确认后mel/png到source root独立目录，receipt包含原路径/SHA，手动恢复准确，不删foreign shelf UI；manager close/reopen只自己的MQt窗口，不删shelf资源。
5. accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/shelf_manager','--class-name','ShelfManagerTool','--summary','Complete native bilingual/version shelf manager with scoped scans, recoverable quarantine, explicit MEL execution and collision-safe migration','--dependencies','Real Maya shelf cmds/MEL GUI','Original shelf MEL and external icon dependencies require target-version acceptance','--limitations','Real Maya shelf UI/loading/production MEL/cross-version/external icon dependency acceptance not_run; IO failures may leave prior completed file operations recoverable'],check=True)
