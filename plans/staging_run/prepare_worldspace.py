"""Full native source conversion and complete EB bundle provenance."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
from lib2to3.refactor import RefactoringTool,get_fixers_from_package

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/03_transforms_modeling/eblabs_world_space_tools'
SOURCE=UNIT/'WorldSpaceTools'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/eblabs_world_space_tools'
WRITES={'setAttr','addAttr','deleteAttr','setKeyframe','cutKey','pasteKey','copyKey','bufferCurve','keyframe','keyTangent','filterCurve','connectAttr','disconnectAttr','delete','parent','parentConstraint','pointConstraint','orientConstraint','aimConstraint','scaleConstraint','circle','curve','group','spaceLocator','createNode','rebuildCurve','pathAnimation','move','rotate','xform','ikHandle','rename','sets'}


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    files=[]
    definitions={}
    ports=[]
    missing=[]
    converter=RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
    for src in sorted(SOURCE.rglob('*')):
        if not src.is_file() or '__pycache__' in src.parts:
            continue
        rel=src.relative_to(SOURCE)
        dst=PKG/'upstream'/rel
        if src.suffix=='.py':
            dst=dst.with_suffix('.py.original')
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        files.append({'path':rel.as_posix(),'archive':dst.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
        dst=PKG/'bundle'/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix!='.py':
            shutil.copyfile(src,dst)
            continue
        source=src.read_text(encoding='utf-8-sig')
        try:
            tree=ast.parse(source)
        except SyntaxError:
            source=str(converter.refactor_string(source+'\n',str(rel)))
            tree=ast.parse(source)
            ports.append(rel.as_posix())
        definitions[rel.as_posix()]=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        for n in ast.walk(tree):
            if isinstance(n,ast.ImportFrom) and n.level==1 and n.module and n.module.endswith(('_310','_39','_37','_27')):
                if not (src.parent/(n.module+'.py')).exists():
                    missing.append((rel.parent/(n.module+'.py')).as_posix())
            if isinstance(n,ast.ImportFrom) and n.level==1 and not n.module:
                for alias in n.names:
                    if alias.name.endswith(('_310','_39','_37','_27')) and not (src.parent/(alias.name+'.py')).exists():
                        missing.append((rel.parent/(alias.name+'.py')).as_posix())
        if rel.as_posix() in ('WorldSpaceTools.py','WorldSpaceToolsbeta.py'):
            tree.body=[n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
            source=ast.unparse(tree)
        put(dst,source)
    raw=(SOURCE/'eblabs_hub/WorldSpaceTools/scripts/worldspace.py').read_text(encoding='utf-8-sig')
    tree=ast.parse(raw)
    wrapped=[]
    for cls in tree.body:
        if not isinstance(cls,ast.ClassDef):
            continue
        for method in cls.body:
            if not isinstance(method,ast.FunctionDef):
                continue
            if cls.name=='Functions' and method.name in ('suspendUI','suspendUI_wrapped') or cls.name=='SuspendUI' and method.name=='setState':
                method.body=ast.parse('return None  # Runtime owns AutoKey/refresh/chunks, no global pane/isolate changes.').body
            if method.name in ('addIsolatedObjectsForModelPanel','isViewIsolated'):
                method.body=ast.parse('return False  # No unrelated viewport isolation changes.').body
            if cls.name=='PrefsBase':
                replacements={'loadPrefsFromFile':'self.rawData=_r.preference_load(self.prefsGroup)', 'writePrefsToFile':'self.rawData["data"][self.activeProfile]=self.data\n_r.preference_save(self.prefsGroup,self.rawData)', 'getScenePref':'return _r.scene_preference(self.prefsGroup,key,default)', 'refreshData':'self.loadPrefsFromFile()\nself.rawData.setdefault("data",{}).setdefault(self.activeProfile,{})\nself.data=self.rawData["data"][self.activeProfile]'}
                if method.name in replacements:
                    method.body=ast.parse(replacements[method.name]).body
                for node in ast.walk(method):
                    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='prefsPath' for t in node.targets):
                        node.value=ast.Constant('session://worldspace/preferences')
            if cls.name=='ObjectProperties' and method.name in ('setStringProperty','getStringProperty'):
                method.body=ast.parse('return _r.set_property(node,key,value)' if method.name=='setStringProperty' else 'return _r.get_property(node,key,defaultValue)').body
            if cls.name=='CopyAtoB' and method.name=='copyAtoB':
                for n in ast.walk(method):
                    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='getSpecialKeyTickTimes' and n.args:
                        n.args[0]=ast.List(elts=[n.args[0]],ctx=ast.Load())
                    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='setKeys' and n.args and isinstance(n.args[0],ast.List):
                        n.args[0]=ast.Name(id='mayaControls',ctx=ast.Load())
            if cls.name=='WorldSpaceFunctions' and method.name=='toWorldSpaceExec':
                for n in ast.walk(method):
                    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='orientConstraint' and n.args and isinstance(n.args[0],ast.Name) and n.args[0].id=='s':
                        n.args[0]=ast.Name(id='targetObject',ctx=ast.Load())
            if method.name=='getWorldSpaceControlMetaData':
                for n in ast.walk(method):
                    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='getAttr':
                        replacement=ast.parse('_r.get_property(worldSpaceControl,attr,"")',mode='eval').body
                        n.func,n.args,n.keywords=replacement.func,replacement.args,replacement.keywords
            if method.name=='generateWorldSpaceControlName':
                method.body=ast.parse('return _r.helper_name(s,"WorldSpaceControl")').body
            for n in ast.walk(method):
                if isinstance(n,ast.ExceptHandler):
                    if method.name in ('toWorldSpace','toLocalSpace','toIKChainSpace','copyAtoB_button','snapAtoB_button','plotGimbalInfo'):
                        n.body.insert(0,ast.parse('_r.capture_error(True)').body[0])
            calls=[n for n in ast.walk(method) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='cmds' and n.func.attr in WRITES and not any(k.arg in ('q','query') and isinstance(k.value,ast.Constant) and k.value.value for k in n.keywords)]
            entry=(cls.name=='WorldSpaceFunctions' and method.name in ('toWorldSpace','toLocalSpace','toIKChainSpace')) or (cls.name=='CopyAtoB' and method.name=='copyAtoB_button')
            if (calls or entry) and cls.name not in ('PrefsBase',):
                method.decorator_list.append(ast.parse('_r.native_operation('+repr(cls.name+'.'+method.name)+')',mode='eval').body)
                wrapped.append(cls.name+'.'+method.name)
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module in ('maya','data'))]
    tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and (n.module=='Version' or n.module is None and any(a.name=='Version' for a in n.names)))]
    for n in ast.walk(tree):
        if isinstance(n,ast.Constant) and n.value=='WS2':
            n.value='mtbWS2'
    header=ast.parse('from .proxy import cmds,mel\nfrom maya import OpenMayaUI\nfrom .metadata import PackageData,Version\nfrom . import runtime as _r').body
    put(PKG/'native.py',ast.unparse(ast.fix_missing_locations(ast.Module(body=header+tree.body,type_ignores=[]))))
    put(PKG/'catalog.json',json.dumps({'files':files,'definitions':definitions,'wrapped':wrapped,'python2_ports':ports,'missing_version_modules':sorted(set(missing)),'legacy_source':'eblabs_hub/WorldSpaceTools/scripts/worldspace.py','license':'Eric Bates / EB Labs copyrighted supplied bundle. No redistribution grant inferred. License managers unaltered; native source original commented check retained.'},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','WorldSpaceTools/** -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','eblabs_world_space_tools').replace('RootMotionBakeTool','WorldSpaceToolsTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'eblabs_world_space_tools','registration':{'module':'eblabs_world_space_tools','class_name':'WorldSpaceToolsTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[x['path'] for x in files],'dependencies':['Maya cmds/API2; complete native legacy runtime','Beta Hub needs absent proprietary version modules, matching supported Python/Qt and original licensed EB Labs environment'], 'acceptance_required':True,'change_summary':'Complete supplied WorldSpaceTools/Hub/assets and all legacy classes/methods preserved, self-contained metadata and session preferences, all original legacy UI and world/parent/local/IK/path/COG/gimbal/copy business, explicit API, guarded native callbacks, UUID helper ownership and cleanup, Undo/finally, full docs/tests/registration/promotion.','verification_limitations':['Actual native GUI/production space/IK/path/COG/gimbal workflows not_run','Beta Hub proprietary version modules absent in supplied bundle, kept complete provided source and actionable dependency diagnostics; no license bypass or fabricated implementation','Source native full suite independent of missing Hub metadata/Version readers; actual legacy source API tests do not verify beta Hub','Anim clipboard/buffer keys changed by original algorithms; Undo actual scope requires Maya acceptance','Session prefs differ from original automatic userAppDir writes; persistence via explicit JSON export only','No public publication rights inferred']},ensure_ascii=False,indent=2))
    print(json.dumps({'files':len(files),'modules':len(definitions),'definitions':sum(map(len,definitions.values())),'legacy_wrapped':len(wrapped),'missing_hybrid_modules':len(set(missing))}))


if __name__=='__main__':
    main()
