import ast
import hashlib
import json
from pathlib import Path
import shutil
from lib2to3.refactor import RefactoringTool,get_fixers_from_package

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/03_transforms_modeling/fcm_hider'
SOURCE=UNIT/'FCM_Hider Install'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/fcm_hider'
NAMES=['All_Sets_Hider','Head_Hider','Torso_Hider','Arm_R_Hider','Arm_L_Hider','Leg_R_Hider','Leg_L_Hider','Extra_One_Hider','Extra_Two_Hider','Extra_Three_Hider','FCM_Hider_Settings']


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    files=[]
    for src in sorted(SOURCE.rglob('*')):
        if not src.is_file(): continue
        rel=src.relative_to(SOURCE)
        dst=PKG/'upstream'/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
        files.append({'path':rel.as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    raw=(SOURCE/'FCM_Hider Shelf Button.txt').read_text(encoding='utf-8-sig')
    converted=str(RefactoringTool(get_fixers_from_package('lib2to3.fixes')).refactor_string(raw+'\n','fcm_hider.py'))
    tree=ast.parse(converted)
    definitions=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    callbacks=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            for k in n.keywords:
                if k.arg in ('c','command','postMenuCommand','enterCommand') and isinstance(k.value,ast.Constant) and isinstance(k.value.value,str):
                    callbacks.append(k.value.value.rstrip(','))
    for f in tree.body:
        if not isinstance(f,ast.FunctionDef): continue
        replaced={'declaringNameSpaces':'_r.bind_globals(globals())',
          'createHiderInTheScene':'_r.bind_globals(globals())\ncreateSettingsHider()\ncreateAllSets()',
          'removeNameSpace':'global setHider\nsetHider=setHider.rsplit(":",1)[-1]',
          'addNameSpace':'global setHider\nsetHider=namespaceHider+setHider.rsplit(":",1)[-1]',
          'queryNamespace':'return _r.current_system()',
          'queryAllSet':'return _r.query_members(globals())',
          'removeSet':'return _r.clear_current_set()',
          'hidePolys':'return _r.hide_member_polys(polys)',
          'showPolys':'return _r.show_member_polys(polys)',
          'saveSetsHider':'return _r.file_dialog("export_sets")',
          'LoadSetsHider':'return _r.file_dialog("import_sets")',
          'showAllHiddenFaces':'return _r.show_member_faces()',
          'unlockAllVisible':'return _r.unlock_members(False)',
          'unlockAllVismeshes':'return _r.unlock_members(True)',
          'mirrorHider':'return _r.mirror_sets()',
          'mirrorPolyHider':'return _r.mirror_faces_into(setHiderParent,setHiderChild)',
          'helpWindow':'return _r.help_window()',
          'toggleImageHelpWindow':'return _r.help_window()',
          'waitAndRefresh':'cmds.refresh()' }
        if f.name in replaced:
            nested=[n for n in ast.walk(f) if isinstance(n,ast.FunctionDef) and n is not f]
            f.body=nested+ast.parse(replaced[f.name]).body
        if f.name in ('createAllSets','createSettingsHider','removeAllHider'):
            class Names(ast.NodeTransformer):
                def visit_Constant(self,n):
                    if isinstance(n.value,str) and n.value in NAMES:
                        return ast.copy_location(ast.Name(id=n.value,ctx=ast.Load()),n)
                    if isinstance(n.value,str) and n.value.startswith('FCM_Hider_Settings.'):
                        return ast.copy_location(ast.BinOp(left=ast.Name(id='FCM_Hider_Settings',ctx=ast.Load()),op=ast.Add(),right=ast.Constant(n.value[len('FCM_Hider_Settings'):])) ,n)
                    return n
            Names().visit(f)
    tree.body=[n for n in tree.body if not (isinstance(n,ast.Import) and any(a.name in ('maya.cmds','maya.mel','subprocess') for a in n.names)) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='HiderUI')]
    for f in tree.body:
        if isinstance(f,ast.FunctionDef) and f.name=='tryNomenclaturesMirror':
            for n in ast.walk(f):
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='L_Variable' for t in n.targets) and isinstance(n.value,ast.Constant) and n.value.value=='r_': n.value.value='l_'
    for n in ast.walk(tree):
        if isinstance(n,ast.Constant) and isinstance(n.value,str):
            n.value=n.value.replace('Show all hidden faces in the scene','Show hidden faces in Hider sets').replace('unlock all layer display on the scene','unlock layers wholly covered by Hider members').replace('Unlock All Visible Meshes','Unlock Hider Mesh Members').replace('Unlock All Visible','Unlock Hider Members')
    tree.body=ast.parse('from .proxy import cmds,mel\nfrom . import runtime as _r').body+tree.body
    put(PKG/'native.py',ast.unparse(ast.fix_missing_locations(tree)))
    put(PKG/'catalog.json',json.dumps({'files':files,'definitions':definitions,'callbacks':sorted(set(callbacks)),'version':'FCM_Hider Beta2.0','author':'Francisco Cerchiara Montero','missing_help_art':['Help_1_Hider.png','Help_2_On_Hider.png','Help_2_Off_Hider.png'],'license':'Author/contact preserved. No license grant in supplied original, no publication rights inferred.'},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','FCM_Hider*/* -text\nFCM_Hider*/** -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','fcm_hider').replace('RootMotionBakeTool','FcmHiderTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'fcm_hider','registration':{'module':'fcm_hider','class_name':'FcmHiderTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[x['path'] for x in files],'dependencies':['Maya cmds/MEL/API2; original native Maya UI','Existing Base/Undo framework'], 'acceptance_required':True,'change_summary':'Full original shelf embedded Python2 source/UI/functions and all supplied icons preserved, private Python3 native runtime, explicit owned namespace/set scope, JSON data IO replacing arbitrary Python execution, no global scene unlock/show/delete, topology-safe mirror membership, callable private UI callbacks, full protocol/docs/tests/promotion.','verification_limitations':['Actual full GUI/face hiding/polygon holes/mirror/selection mask/rig scene acceptance not_run','Original help images absent; complete textual help replaces missing artwork','Legacy .py set files deliberately unsupported, convert only in trusted original environment','Component hide/polyHole may change mesh hidden-face data; scene backup and actual Undo required','Selection modes/display color/reflection and original UI effects require manual restoration','Original global unlock/show actions now limited to candidate system members and privately covered layers','No installation of shelf/icons/user files; no public publication rights inferred']},ensure_ascii=False,indent=2))
    print(json.dumps({'files':len(files),'definitions':len(definitions),'callbacks':len(set(callbacks))}))


if __name__=='__main__': main()
