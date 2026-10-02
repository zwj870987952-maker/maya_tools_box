"""Prepare the complete paid, supplied MEL shelf without executing it."""
import hashlib,json,re,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/malcolm341_mega_pack'
RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/malcolm341_mega_pack'
d=json.loads((ROOT/'plans/staging_run/malcolm341_source_review.json').read_text(encoding='utf8'))
s=(UNIT/d['source']).read_bytes().decode('utf8')
assert hashlib.sha256((UNIT/d['source']).read_bytes()).hexdigest()==d['sha256']
assert d['top_level_procedures']==['shelf_malcolm341_mega_pack']
MODULE='maya_toolkit.tools.malcolm341_mega_pack'
def mel_string(value):return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('\r','\\r').replace('\n','\\n')+'"'
edits=[]; rows=[]; guard_counts={}
for r in d['buttons']:
    callbacks=[]
    for c in r['callbacks']:
        original=c['command']; code=original.replace('m341_','MTB_m341_')
        # No native file export can silently overwrite an existing destination.
        replacements={
            'FBXExport -f $tbSaveLocation -s;':'mtbM341NewFile($tbSaveLocation); FBXExport -f $tbSaveLocation -s;',
            'sysFile -delete ($MTB_m341_uvGrab_DirPath + "/" + $queryFolderFirst[$delCounter]);':
            'mtbM341Backup(($MTB_m341_uvGrab_DirPath + "/" + $queryFolderFirst[$delCounter])); sysFile -delete ($MTB_m341_uvGrab_DirPath + "/" + $queryFolderFirst[$delCounter]);'}
        for before,after in replacements.items():
            count=code.count(before);guard_counts[before]=guard_counts.get(before,0)+count;code=code.replace(before,after)
        # Export statements in this exact supplied pack each occupy one line.
        code,n=re.subn(r'(?m)^(\s*)(file\s+[^\r\n]*\s-es\s+(\$\w+|"[^"\r\n]+")\s*;)',
                        r'\1mtbM341NewFile(\3); \2',code)
        guard_counts['file_export']=guard_counts.get('file_export',0)+n
        code,n=re.subn(r'(?m)^(\s*)(uvSnapshot\s+[^\r\n]*\s-n\s+(\$\w+)\s[^\r\n]*;)',
                        r'\1mtbM341NewFile(\3); \2',code)
        guard_counts['uvSnapshot']=guard_counts.get('uvSnapshot',0)+n
        # Exact fopen token, including backtick calls. Preserve all file modes,
        # but backup existing files before a/w in the UI's userSetup feature.
        code=re.sub(r'\bfopen\b','mtbM341Fopen',code)
        effects=[x for x in ('file','FBXExport','sysFile','optionVar','SavePreferences','userSetup','Quit','system','scriptJob','evalDeferred','loadPlugin') if re.search(r'\b'+re.escape(x)+r'\b',original)]
        callbacks.append({'event':c['event'],'label':c.get('label',''),'source_type':r['source_type'],
                          'original_sha256':hashlib.sha256(original.encode()).hexdigest(),
                          'sha256':hashlib.sha256(code.encode()).hexdigest(),'command':code,'effects':effects})
        if original:
            py=f"from {MODULE}.runtime import dispatch; dispatch('{r['id']}', '{c['event']}')"
            wrapper='python('+mel_string(py)+');'
            edits.append((c['offset'][0],c['offset'][1],mel_string(wrapper)))
    rows.append({'id':r['id'],'label':r['flags']['-label'],'annotation':r['flags']['-annotation'],
                 'image':r['flags']['-image'],'callbacks':callbacks})
# Keep every button, menu flag, double-click and appearance verbatim, changing
# only the top-level procedure name and nonempty trusted callbacks.
for start,end,value in sorted(edits,reverse=True):s=s[:start]+value+s[end:]
s=s.replace('global proc shelf_malcolm341_mega_pack ()','global proc MTB_shelf_malcolm341_mega_pack ()',1)
put(PKG/'native/shelf.mel',s)
put(PKG/'native/commands.json',json.dumps({'source_sha256':d['sha256'],'buttons':rows,'guard_counts':guard_counts},ensure_ascii=False,indent=2))
put(PKG/'native/guards.mel',r'''// Candidate guards: compile only; no automatic file writes.
global proc mtbM341NewFile(string $path) {
    python("from maya_toolkit.tools.malcolm341_mega_pack.file_guard import require_new; require_new(\"" + encodeString($path) + "\")");
}
global proc mtbM341Backup(string $path) {
    python("from maya_toolkit.tools.malcolm341_mega_pack.file_guard import backup_existing; backup_existing(\"" + encodeString($path) + "\")");
}
global proc int mtbM341Fopen(string $path, string $mode) {
    if ($mode == "w" || $mode == "a") { mtbM341Backup($path); }
    return `fopen $path $mode`;
}
''')
put(PKG/'file_guard.py',r'''"""Native output checks and exact-byte backups, independent of Maya."""
from pathlib import Path
import hashlib
import shutil
import uuid
backups=[]

def checked_path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid file path')
    path=Path(value)
    if not path.is_absolute():raise ValueError('Absolute file path required')
    if path.is_symlink():raise ValueError('Symlink destination refused')
    if not path.parent.is_dir():raise ValueError('Output parent must already exist')
    return path

def require_new(value):
    path=checked_path(value)
    if path.exists():raise FileExistsError('Existing output is preserved: '+str(path))
    return str(path)

def backup_existing(value):
    path=checked_path(value)
    if not path.exists():return None
    if not path.is_file():raise ValueError('Only file backup supported')
    if path.stat().st_size>128*1024*1024:raise ValueError('Backup file exceeds 128 MiB')
    dst=path.with_name(path.name+'.mtb_backup_'+uuid.uuid4().hex)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open('rb') as source,dst.open('xb') as target:shutil.copyfileobj(source,target)
    if hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError('Backup verification failed; original untouched')
    row={'source':str(path),'backup':str(dst),'sha256':digest};backups.append(row)
    return row
''')
put(PKG/'runtime.py',r'''"""Complete supplied native callbacks, owned shelf, lazy MEL execution."""
from pathlib import Path
import hashlib
import json
import re
from .file_guard import checked_path,require_new
HERE=Path(__file__).resolve().parent
SHELF='MTB_Malcolm341_Candidate'
TAG='maya_toolkit.malcolm341_mega_pack'
owned_shelf=None

def inventory():
    data=json.loads((HERE/'native/commands.json').read_text(encoding='utf8'))
    for row in data['buttons']:
        for c in row['callbacks']:
            if hashlib.sha256(c['command'].encode()).hexdigest()!=c['sha256']:raise RuntimeError('Native payload hash mismatch')
    return data

def lookup(button,event):
    row=next((r for r in inventory()['buttons'] if r['id']==button),None)
    if row is None:raise ValueError('Unknown button id')
    callback=next((c for c in row['callbacks'] if c['event']==event),None)
    if callback is None or not callback['command']:raise ValueError('No executable callback for this event')
    return row,callback

def metadata():
    d=inventory()
    return {'source_sha256':d['source_sha256'],'native_guard_counts':d['guard_counts'],
            'buttons':[{'id':r['id'],'label':r['label'],'description':r['annotation'],
                        'events':[{'event':c['event'],'label':c['label'],'effects':c['effects']}
                                  for c in r['callbacks'] if c['command']]} for r in d['buttons']],
            'gui_acceptance':'not_run','license':'Supplied paid pack; personal candidate, original notices retained'}

def temp_mode(button,event):
    if button not in ('button_006','button_007'):return None
    _,c=lookup(button,event)
    match=re.search(r'int \$mode = ([1-8]);',c['command'])
    if not match:raise ValueError('Native temporary transfer mode absent')
    return int(match.group(1))

def compile_guards():
    from maya import mel
    mel.eval((HERE/'native/guards.mel').read_text(encoding='utf8'))

def show_shelf():
    global owned_shelf
    from maya import cmds,mel
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    if cmds.shelfLayout(SHELF,exists=True):
        if not owned_shelf or not cmds.shelfLayout(owned_shelf,exists=True) or cmds.shelfLayout(owned_shelf,query=True,docTag=True)!=TAG:
            raise RuntimeError('A foreign shelf has this name; refusing overwrite')
        return owned_shelf
    top=mel.eval('$mtbM341ShelfTop = $gShelfTopLevel')
    old_parent=cmds.setParent(query=True)
    try:
        shelf=cmds.shelfLayout(SHELF,parent=top,docTag=TAG)
        owned_shelf=shelf
        cmds.setParent(shelf)
        mel.eval((HERE/'native/shelf.mel').read_text(encoding='utf8'))
        mel.eval('MTB_shelf_malcolm341_mega_pack();')
        children=cmds.shelfLayout(shelf,query=True,childArray=True) or []
        if len(children)!=49:raise RuntimeError('Expected 49 native buttons')
        cmds.tabLayout(top,edit=True,selectTab=shelf)
        return shelf
    except Exception:
        if owned_shelf and cmds.shelfLayout(owned_shelf,exists=True):cmds.deleteUI(owned_shelf)
        owned_shelf=None
        raise
    finally:
        if old_parent and cmds.layout(old_parent,exists=True):cmds.setParent(old_parent)

def close_shelf():
    global owned_shelf
    from maya import cmds
    if owned_shelf and cmds.shelfLayout(owned_shelf,exists=True):
        if cmds.shelfLayout(owned_shelf,query=True,docTag=True)!=TAG:raise RuntimeError('Shelf ownership changed')
        cmds.deleteUI(owned_shelf)
    owned_shelf=None

def run_native(button,event,file_path=None):
    from maya import cmds,mel
    from maya_toolkit.core.context import UndoChunkContext
    _,c=lookup(button,event); code=c['command'];mode=temp_mode(button,event)
    if mode and mode<=6:
        p=checked_path(file_path)
        if mode<=3:require_new(str(p))
        elif not p.is_file():raise FileNotFoundError(str(p))
        # Only trusted path literals in the transfer script are replaced. Input
        # is MEL-escaped; no arbitrary caller code is interpolated.
        quoted=json.dumps(p.as_posix(),ensure_ascii=False)
        parent=json.dumps(p.parent.as_posix(),ensure_ascii=False)
        code=re.sub(r'"(?:C:/MTB_m341_temp|/Users/Shared/MTB_m341_temp)/temp\.(?:ma|mlt|obj|fbx)"',lambda m:quoted,code)
        code=code.replace('"C:/MTB_m341_temp"',parent).replace('"/Users/Shared/MTB_m341_temp"',parent)
        code=code.replace('file  -ignoreVersion','file -executeScriptNodes false -ignoreVersion')
    compile_guards()
    before=cmds.ls(selection=True,long=True,flatten=True) or []
    with UndoChunkContext('Malcolm341_'+button+'_'+event):
        try:return mel.eval(code)
        finally:
            # Preserve the original selection for the proven pivot operation.
            # Other native tools intentionally produce a result selection.
            if button=='button_018' and event=='primary':
                cmds.select([n for n in before if cmds.objExists(n)],replace=True)

def dispatch(button,event):
    from maya import cmds
    from . import Malcolm341MegaPackTool
    row,c=lookup(button,event)
    mode=temp_mode(button,event);path=None
    if mode and mode<=6:
        ext={1:'ma',2:'obj',3:'fbx',4:'ma',5:'obj',6:'fbx'}[mode]
        chosen=cmds.fileDialog2(fileMode=0 if mode<=3 else 1,fileFilter='Native transfer (*.'+ext+')',caption='New output only' if mode<=3 else 'Import into backup scene')
        if not chosen:return None
        path=chosen[0]
    message='运行 '+row['label']+' / '+(c['label'] or event)+'。原功能可能修改场景、全局设置或文件。\n'
    message+='本候选已有文件导出拒绝覆盖；偏好/userSetup/快照删除保存副本，但文件与退出不由 Maya Undo 恢复。'
    if cmds.confirmDialog(title='Malcolm341 原功能',message=message,button=['执行','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')!='执行':return None
    result=Malcolm341MegaPackTool().run(action='run_button',button_id=button,event=event,file_path=path,confirm_native=True)
    if not result.success:cmds.warning(result.message)
    return result
''')
put(PKG/'__init__.py',r'''"""Complete personal native MEL suite with a bounded tool contract."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import runtime

class Malcolm341MegaPackTool(BaseMayaTool):
    tool_id='malcolm341_mega_pack'
    tool_name='Malcolm341 Mega Pack'
    category='modeling_surfacing'
    description='完整49按钮原生MEL建模/UV/材质套件，按固定按钮与菜单调用；文件与全局偏好影响详见说明'
    version='1.0.0'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','run_button'],'default':'inspect'},
        'button_id':{'type':'string','pattern':'^button_[0-9]{3}$'},
        'event':{'type':'string','enum':['primary','double','menu_001','menu_002','menu_003','menu_004','menu_005'],'default':'primary'},
        'confirm_native':{'type':'boolean','default':False},
        'file_path':{'type':['string','null'],'description':'临时导出/导入的显式绝对路径；导出只允许新文件'},
        'selection':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True,'description':'可选明确对象/组件，预检解析全部对象后才设置选择'}},'required':[]}

    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown argument')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Unknown action')
        confirm=kwargs.get('confirm_native',False)
        if type(confirm) is not bool:raise ValueError('confirm_native must be boolean')
        plan={'action':action,'gui_acceptance':'not_run'}
        if action=='inspect':return plan
        from maya import cmds
        if action in ('show_ui','close_ui'):
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required')
            return plan
        row,c=runtime.lookup(kwargs.get('button_id'),kwargs.get('event','primary'))
        if not confirm:raise ValueError('confirm_native=True required for supplied native operations')
        if cmds.about(batch=True) and (row['id'],c['event'])!=('button_018','primary'):
            raise ValueError('This native callback requires real Maya GUI acceptance')
        if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo before native operations')
        supplied=kwargs.get('selection')
        if supplied is not None and (not isinstance(supplied,list) or not supplied or any(not isinstance(n,str) or not n or '*' in n or '?' in n for n in supplied) or len(set(supplied))!=len(supplied)):
            raise ValueError('Selection must contain unique explicit objects/components')
        selection=[]
        for item in (supplied if supplied is not None else cmds.ls(selection=True,long=True,flatten=True) or []):
            found=cmds.ls(item,long=True,flatten=True) or []
            if not found or ('.' not in item and len(found)!=1):raise ValueError('Missing or ambiguous selection: '+item)
            for n in found:
                base=n.split('.')[0]
                if cmds.referenceQuery(base,isNodeReferenced=True) or any(cmds.lockNode(base,query=True,lock=True)):
                    raise ValueError('Locked/referenced selection refused: '+base)
                if n not in selection:selection.append(n)
        if row['id']=='button_018' and c['event']=='primary':
            vertices=cmds.ls(cmds.polyListComponentConversion(selection,toVertex=True),flatten=True,long=True) or []
            meshes={v.split('.')[0] for v in vertices}
            if not vertices or len(meshes)!=1:raise ValueError('Pivot requires nonempty vertices from exactly one polygon mesh')
            mesh=next(iter(meshes));shape=mesh if cmds.nodeType(mesh)=='mesh' else next(iter(cmds.listRelatives(mesh,shapes=True,noIntermediate=True,fullPath=True) or []),None)
            if not shape or cmds.nodeType(shape)!='mesh':raise ValueError('Polygon mesh required')
            transform=(cmds.listRelatives(shape,parent=True,fullPath=True) or [None])[0]
            if not transform:raise ValueError('Mesh transform required')
            if cmds.referenceQuery(transform,isNodeReferenced=True) or any(cmds.lockNode(transform,query=True,lock=True)):raise ValueError('Locked/referenced transform refused')
            if any(cmds.getAttr(transform+'.'+p+a,lock=True) for p in ('rotatePivot','scalePivot') for a in ('X','Y','Z')):raise ValueError('Pivot attributes locked')
        mode=runtime.temp_mode(row['id'],c['event']);path=kwargs.get('file_path')
        if mode and mode<=6:
            from .file_guard import checked_path,require_new
            p=checked_path(path);ext={1:'.ma',2:'.obj',3:'.fbx',4:'.ma',5:'.obj',6:'.fbx'}[mode]
            if p.suffix.lower()!=ext:raise ValueError('Transfer requires '+ext+' path')
            if mode<=3:require_new(str(p))
            elif not p.is_file():raise ValueError('Import source absent')
            path=str(p)
        elif path is not None:raise ValueError('file_path only applies to native temporary transfer')
        return {**plan,'button_id':row['id'],'label':row['label'],'event':c['event'],
                'effects':c['effects'],'selection':selection,'set_selection':supplied is not None,'file_path':path,
                'external_file_undo':False,'native_scope':'Original callback may use all scene objects/global preferences'}

    def validate(self,**kwargs):
        try:return ToolResult.ok('Native operation plan',data=self._plan(kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(str(e),errors=[str(e)])

    def execute(self,**kwargs):
        p=self._plan(kwargs);action=p['action']
        if action=='inspect':return ToolResult.ok('Complete native inventory',data=runtime.metadata())
        if action=='show_ui':return ToolResult.ok('Owned complete shelf',data={'shelf':runtime.show_shelf()})
        if action=='close_ui':runtime.close_shelf();return ToolResult.ok('Owned shelf closed')
        from maya import cmds
        from maya_toolkit.core.context import UndoChunkContext
        # Explicit selection writes belong to the same Undo group as the native operation.
        with UndoChunkContext('Malcolm341_'+p['button_id']):
            if p['set_selection']:cmds.select(p['selection'],replace=True)
            value=runtime.run_native(p['button_id'],p['event'],p['file_path'])
        return ToolResult.ok('Native callback completed; verify the scene/output in Maya',data={'button_id':p['button_id'],'event':p['event'],'native_result':value,'file_path':p['file_path']})

    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            result=self.validate(**kwargs)
            if result.success and not dry_run:result=self.execute(**kwargs)
        except Exception as e:result=ToolResult.fail(str(e),errors=[str(e)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;return result

    def show_ui(self,parent=None):return self.run(action='show_ui')
''')
put(RC/'tests/test_malcolm341_mega_pack.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_m341',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.malcolm341_mega_pack import Malcolm341MegaPackTool
    tool=Malcolm341MegaPackTool()
from maya_toolkit.tools.malcolm341_mega_pack import runtime,file_guard
class Checks(unittest.TestCase):
    def test_complete_source_and_inventory(self):
        result=tool.run();self.assertTrue(result.success,result.message)
        self.assertEqual(len(result.data['buttons']),49)
        self.assertEqual(result.data['buttons'][17]['label'],'pivot')
        self.assertNotIn('maya.mel',sys.modules)
        _,c=runtime.lookup('button_006','menu_002');self.assertEqual(runtime.temp_mode('button_006','menu_002'),2)
        self.assertGreater(len(c['command']),9000)
        self.assertIn('paid script pack',c['command'])
        self.assertIn('mtbM341NewFile',c['command'])
        self.assertIn('MTB_m341_',c['command'])
        self.assertFalse(tool.run(action='inspect',confirm_native=1).success)
        self.assertFalse(tool.run(action='not_real').success)
        with self.assertRaises(ValueError):runtime.lookup('button_001','menu_001')
    def test_no_overwrite_and_exact_backup(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'prefs.mel';p.write_bytes(b'// original\r\n\xff')
            before=p.read_bytes()
            with self.assertRaises(FileExistsError):file_guard.require_new(str(p))
            self.assertEqual(p.read_bytes(),before)
            backup=file_guard.backup_existing(str(p));self.assertEqual(Path(backup['backup']).read_bytes(),before)
            self.assertEqual(p.read_bytes(),before)
            out=Path(td)/'new.ma';self.assertEqual(file_guard.require_new(str(out)),str(out));self.assertFalse(out.exists())
            with self.assertRaises(ValueError):file_guard.require_new('relative.ma')
            with self.assertRaises(ValueError):file_guard.require_new(str(Path(td)/'missing/out.ma'))
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_malcolm341_mega_pack_maya.py',r'''import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
rc=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('launch_m341',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.malcolm341_mega_pack import runtime
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_full_shelf_declaration_and_guards(self):
        before=set(cmds.ls())
        runtime.compile_guards()
        mel.eval((runtime.HERE/'native/shelf.mel').read_text(encoding='utf8'))
        self.assertEqual(set(cmds.ls()),before)
        self.assertIn('Mel procedure',mel.eval('whatIs MTB_shelf_malcolm341_mega_pack'))
        self.assertFalse(tool.run(action='show_ui',dry_run=True).success)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'original.ma';p.write_text('preserved',encoding='utf8');before=p.read_bytes()
            with self.assertRaises(RuntimeError):mel.eval('mtbM341NewFile('+json.dumps(p.as_posix())+');')
            self.assertEqual(p.read_bytes(),before)
            prefs=Path(td)/'prefs.mel';prefs.write_bytes(b'old data')
            mel.eval('int $mtbFile = `mtbM341Fopen '+json.dumps(prefs.as_posix())+' "a"`; fprint $mtbFile "new data"; fclose $mtbFile;')
            copies=list(Path(td).glob('prefs.mel.mtb_backup_*'));self.assertEqual(len(copies),1);self.assertEqual(copies[0].read_bytes(),b'old data')
    def test_native_pivot_preflight_scene_and_one_undo(self):
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',5)
        cmds.xform(cube,worldSpace=True,pivots=(9,0,0));cmds.select(cube+'.vtx[0:7]',replace=True)
        selection=cmds.ls(selection=True,long=True,flatten=True);pivot=cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True)
        kwargs={'action':'run_button','button_id':'button_018','confirm_native':True}
        self.assertTrue(tool.run(dry_run=True,**kwargs).success)
        self.assertEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True),pivot)
        result=tool.run(**kwargs);self.assertTrue(result.success,result.message)
        self.assertAlmostEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True)[0],5)
        self.assertEqual(cmds.ls(selection=True,long=True,flatten=True),selection)
        cmds.undo();self.assertEqual(cmds.xform(cube,query=True,worldSpace=True,rotatePivot=True),pivot)
        self.assertEqual(cmds.ls(selection=True,long=True,flatten=True),selection)
        cmds.setAttr(cube+'.rotatePivotX',lock=True)
        self.assertFalse(tool.run(**kwargs).success);cmds.setAttr(cube+'.rotatePivotX',lock=False)
        other=cmds.polyCube()[0];cmds.select([cube,other]);self.assertFalse(tool.run(**kwargs).success)
        cmds.select(clear=True);self.assertFalse(tool.run(**kwargs).success)
if __name__=='__main__':
    result=unittest.main(exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
''')
table='\n'.join('| '+r['id']+' | '+r['label']+' | '+', '.join(c['event'] for c in r['callbacks'] if c['command'])+' |' for r in rows)
put(RC/'docs/tools/malcolm341_mega_pack.md','''# Malcolm341 Mega Pack（完整待验候选）

来源为用户提供20230114付费MEL shelf及安装说明；49按钮、119原始回调位（含空菜单分隔项）、全部建模/UV/材质/导入导出/测量/偏好/HUD/Shelf功能与源许可文字完整保存。个人已提供资源整理，不推定公开再分发许可。未下载商业资源，图标使用原Maya内置图标。upstream精确原bytes+SHA；运行包不依赖待整理池路径。

所有原button/mi/双击与尺寸/颜色/注释在自有Shelf完整保留，只替换为固定id分派包装；native完整代码置于commands.json，SHA可核。原m341_命名统一MTB_m341_，隔离窗口、optionVar与脚本名，未将第三方算法未经实测改为core。部分原无前缀helper如killScriptJob保留，勿在同Maya会话混用原版与候选；实际兼容需测试。默认inspect列全部工具，不自动source/安装Shelf/写prefs/导出/创建节点。show_ui只创建MTB_Malcolm341_Candidate，不保存所有Shelf；同名foreign拒绝，close_ui仅删自有Shelf，不广泛关闭native子窗口或kill scriptJobs。

```python
from maya_toolkit.tools.malcolm341_mega_pack import Malcolm341MegaPackTool
t=Malcolm341MegaPackTool()
t.run() # native inventory
t.show_ui() # 真实Maya49按钮、右键菜单、双击
t.run(action='run_button',button_id='button_018',event='primary',confirm_native=True,dry_run=True)
t.run(action='run_button',button_id='button_018',event='primary',confirm_native=True)
```

Schema/validate/ToolResult只接收固定button/event，拒绝用户代码/eval字符串。scene写入UndoChunk；当前selection或显式selection全表解析/不存在/含wildcard/锁/reference拒绝；pivot进一步非空单个poly mesh/components及pivot轴锁预检，原native平均顶点中心算法保留，多mesh原只改首项的含糊行为改拒绝。dry不设选择、不编译MEL/安装UI/改场景/创建文件。实际batch仅已检的pivot主操作允许，其余native需真实GUI。部分原功能主动读取全场景、切换工具/单位/颜色管理、操作layers等，不能将selection参数误解为限制其原始处理范围。

原临时导入导出6/7改显式file_path（绝对ma/obj/fbx，与模式匹配）：输出已有parent/新文件、不再固定C盘temp覆盖；UI选文件取消不执行；导入已存在文件，MA不执行scriptNodes。file导出/FBXExport/uvSnapshot实际路径在native执行前拒绝已存在文件，原nativeforce标志不能绕过guard。直接API模式输出只预制source中完整原算法，path字符串经过MEL转义，不是任意命令注入。由于其余原窗口内部为原菜单程序，子窗口后续动作仍按原代码运行；已经对明确file exports/FBX/uvSnapshot/userSetup写入和uvGrab删除加guard，但不宣称覆盖未知插件、shell或延迟写入。

原Shelf/HUD userSetup功能保留，fopen a/w及uvGrab删除在原处备份同目录新.mtb_backup_UUID文件，精确bytes/SHA核验，128MiB上限；backup失败不继续写，已有文件导出拒绝覆盖。备份与文件写入、MEL proc定义、optionVar、插件autoload、HUD/scriptJob、prefs/save所有shelf/窗口状态/退出Maya不由scene Undo撤回。close/sPref/HUD/Shelf按钮的原广范围动作须显式confirm_native与UI默认取消确认；不要在未保存正式场景执行close，使用备份prefs/临时目录验收。子窗口内部原confirm/按钮保留，未假称所有原UI动作均完全可回滚。文件检查与第三方write之间存在竞争窗口，验收使用独占临时路径。

可组合：先用inspect找到按钮与事件，再准备选择/备份、dry预检，确认原功能影响后run；建模/UV输出可接既有几何工具，材质copy/paste原全局clipboard依赖同session；原file exporter产物可接外部DCC。但未真实验证任何跨工具组合，不等于依赖import即可自动组合。晋级完整code/native/resources/docs/tests及ALL_TOOL_CLASSES注册已准备，真实GUI满意后按promotion执行。

离线检查为只读inventory/坏参数/防覆盖/exact备份；隔离Maya检查MEL完整Shelf声明编译（未调用建Shelf）、guard临时文件、polyCube顶点pivot/dry/一次Undo/锁与多mesh拒绝。全49按钮/原子窗口、右键与双击/延迟scriptJob/导出插件/真实GUI/跨版本 not_run；这些检查不代表整套实际Maya验收。

| button_id | 原标签 | 可调用event |
| --- | --- | --- |
'''+table+'\n')
put(RC/'acceptance.md','''# Malcolm341 全49工具真实Maya验收 not_run

1. 备份场景、prefs与userSetup，使用独占临时输出目录；load候选show_ui完整49按钮/内置图标、右键菜单/双击，重复开关仅自有Shelf，同名foreign拒绝，不source原版，不自动写prefs/windowPrefs/安装userSetup。
2. 逐行docs原49标签测试完整原子窗/slider/按钮响应、选择结果、建模/UV/材质/HUD/Shelf/导出；不是打开Shelf就整套通过。pivot单mesh顶点非空平均中心/锁/reference/多mesh/坏最后对象/dry零修改/一次Undo与Redo。原其他广范围清理/层/历史变化在备份场景验证Undo-Redo，部分全局状态如实记录不能Undo。
3. 临时ma/obj/fbx显式路径：导出只新文件、重复拒绝旧bytes保持、导入不执行MA scriptNodes、原插件autoload影响记录；OBJ/FBX/UV snapshot已存在路径拒绝。逐测native子窗口内有变量拼接的output、文件parent缺失/取消、Unicode与带引号路径，避免共用路径竞争。
4. userSetup fopen a/w和uvGrab删除前同目录独占备份存在且SHA一致；原file未写之前backup失败应拒绝。偏好/HUD/脚本job/延迟函数关闭清理按原功能确认，备份偏好手动恢复，不以scene Undo撤回文件。close只在已保存场景测试（原早Maya硬退出保留必须了解影响）；不自动删除windowPrefs、不执行安装说明中的系统路径删除。
5. 全体源license文字/资源/hash及无前缀helper冲突，Maya2017/2018旧版本及Maya2025逐测。candidate_sha256/maya_version/accepted_by/date/passed=true之后执行预制晋级；正式库当前未改。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/malcolm341_mega_pack','--class-name','Malcolm341MegaPackTool',
                '--summary','Complete supplied 49-button paid MEL suite, owned shelf and all callbacks, bounded API, namespace isolation and guarded external file operations',
                '--dependencies','Maya native MEL/UI and builtin icons','Optional OBJ/FBX/Unfold3D plugins for corresponding native functions',
                '--limitations','All 49 native GUI windows/actions, deferred jobs, broad preference/file operations and cross-version acceptance not_run'],check=True)
print(json.dumps({'buttons':len(rows),'callback_slots':sum(len(r['callbacks']) for r in rows),'guards':guard_counts}))
