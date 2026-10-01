"""Preserve the complete third-party suite, patch only private compatibility."""
import ast
import collections
import hashlib
import json
from pathlib import Path
import shutil
import re
from lib2to3.refactor import RefactoringTool,get_fixers_from_package

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/03_transforms_modeling/cvwrap_weightdriver'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/cvwrap_weightdriver'


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def audit():
    rows=[]
    definitions={}
    incompatible=[]
    tops=[]
    fixers=[f for f in get_fixers_from_package('lib2to3.fixes') if f.rsplit('.',1)[1] not in ('fix_import','fix_imports','fix_imports2')]
    converter=RefactoringTool(fixers)
    for src in sorted(UNIT.rglob('*')):
        if not src.is_file() or 'release_candidate' in src.relative_to(UNIT).parts or src.name=='.gitattributes' or '__pycache__' in src.parts:
            continue
        rel=src.relative_to(UNIT)
        rows.append({'path':rel.as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bytes':src.stat().st_size})
        if src.suffix!='.py':
            continue
        source=src.read_text(encoding='utf-8-sig')
        try:
            tree=ast.parse(source)
        except SyntaxError:
            source=str(converter.refactor_string(source+'\n',str(rel)))
            tree=ast.parse(source)
            incompatible.append(rel.as_posix())
        definitions[rel.as_posix()]=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        for node in tree.body:
            if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call):
                tops.append({'file':rel.as_posix(),'expression':ast.unparse(node)[:220]})
    return rows,definitions,incompatible,tops


def main():
    rows,definitions,incompatible,tops=audit()
    fixers=[f for f in get_fixers_from_package('lib2to3.fixes') if f.rsplit('.',1)[1] not in ('fix_import','fix_imports','fix_imports2')]
    converter=RefactoringTool(fixers)
    for row in rows:
        rel=Path(row['path'])
        src=UNIT/rel
        archive=PKG/'upstream'/rel
        if src.suffix=='.py':
            archive=archive.with_suffix('.py.original')
        archive.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,archive)
        row['archive']=archive.relative_to(PKG).as_posix()
        target=PKG/'native'/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix!='.py':
            shutil.copyfile(src,target)
            continue
        source=src.read_text(encoding='utf-8-sig')
        if row['path'] in incompatible:
            source=str(converter.refactor_string(source+'\n',str(rel)))
        tree=ast.parse(source)
        if row['path']=='mgear/core/skin.py':
            source=source.replace('pickle.load(fp)','candidate_load_pickle(fp)').replace("with open(filePath, 'r') as fp:","with open(filePath, 'rb') as fp:")
            tree=ast.parse(source)
            insert=1 if isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) else 0
            while insert<len(tree.body) and isinstance(tree.body[insert],ast.ImportFrom) and tree.body[insert].module=='__future__':
                insert+=1
            tree.body.insert(insert,ast.parse('from maya_toolkit.tools.cvwrap_weightdriver.safe_data import load_basic_pickle as candidate_load_pickle').body[0])
            source=ast.unparse(tree)
        if row['path']=='mgear/core/pyqt.py':
            for node in tree.body:
                if isinstance(node,ast.FunctionDef) and node.name=='get_icon_path':
                    node.body=ast.parse("folder=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','icons'))\nreturn os.path.join(folder,icon_name) if icon_name else folder").body
            ast.fix_missing_locations(tree)
            source=ast.unparse(tree)
        if row['path'] in ('mgear/rigbits/rbf_io.py','mgear/rigbits/weightNode_io.py'):
            # Original RBF scene recreation is retained, but user-file export
            # must not overwrite an earlier preset through these entrypoints.
            source=source.replace('open(filePath, "w")','open(filePath, "x")').replace("open(filePath, 'w')","open(filePath, 'x')")
            tree=ast.parse(source)
        if row['path']=='userSetup.py':
            # Complete explicit loader retained; never print/defer/menu at import.
            tree.body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
            source=ast.unparse(tree)
        elif row['path'] in ('cvwrap/menu.py','cvwrap/bindui.py'):
            tree.body=[n for n in tree.body if not isinstance(n,ast.If) or not any(isinstance(x,ast.ImportFrom) and x.module in ('PySide','PySide2') for x in ast.walk(n))]
            tree.body.insert(0,ast.parse('from maya_toolkit.tools.cvwrap_weightdriver.qt_compat import QtWidgets as QtGui').body[0])
            if row['path']=='cvwrap/menu.py':
                for node in tree.body:
                    if isinstance(node,ast.FunctionDef) and node.name in ('create_cvwrap','import_binding','export_binding','paint_cvwrap_weights'):
                        action={'create_cvwrap':'create_wrap','import_binding':'import_binding','export_binding':'export_binding','paint_cvwrap_weights':'paint_wrap'}[node.name]
                        node.body=ast.parse('from maya_toolkit.tools.cvwrap_weightdriver.ui import menu_dispatch\nreturn menu_dispatch('+repr(action)+')').body
            else:
                for node in ast.walk(tree):
                    if isinstance(node,ast.FunctionDef) and node.name=='rebind':
                        node.body=ast.parse('from maya_toolkit.tools.cvwrap_weightdriver.ui import rebind_dialog\nreturn rebind_dialog(self)').body
            ast.fix_missing_locations(tree)
            source=ast.unparse(tree)
            if row['path']=='cvwrap/menu.py':
                source=source.replace("return QtGui.QInputDialog.getItem(None, 'Select cvWrap node', 'cvWrap node:', wrap_nodes)","value, accepted = QtGui.QInputDialog.getItem(None, 'Select cvWrap node', 'cvWrap node:', wrap_nodes)\n        return str(value) if accepted else None")
        # The SDK_manager in this supplied Python3 distribution still uses the
        # removed Python2 builtin reload. Supply its real stdlib equivalent.
        if any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='reload' for n in ast.walk(tree)):
            if not any(isinstance(n,ast.ImportFrom) and n.module=='importlib' and any(a.name=='reload' for a in n.names) for n in tree.body):
                insertion=1 if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) else 0
                while insertion<len(tree.body) and isinstance(tree.body[insertion],ast.ImportFrom) and tree.body[insertion].module=='__future__':
                    insertion+=1
                tree.body.insert(insertion,ast.parse('from importlib import reload').body[0])
                source=ast.unparse(tree)
        put(target,source)
    icon_names=set()
    for row in rows:
        if row['path'].endswith('.py'):
            icon_names.update(re.findall(r'mgear_[A-Za-z0-9_-]+\.svg',(UNIT/row['path']).read_text(encoding='utf-8-sig')))
    for name in sorted(icon_names):
        # Source bundle supplied no menu SVGs: local text fallbacks are explicit,
        # not replicas falsely attributed to the upstream author.
        label=name.removeprefix('mgear_')[:2].upper()
        put(PKG/'native/icons'/name,'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><rect x="1" y="1" width="30" height="30" rx="5" fill="#354353"/><text x="16" y="21" text-anchor="middle" font-size="13" font-family="sans-serif" fill="#f4f4f4">'+label+'</text></svg>')
    put(PKG/'native/__init__.py','"""Complete third-party bundle; explicit guarded bootstrap only."""')
    put(PKG/'catalog.json',json.dumps({'files':rows,'definitions':definitions,'python2_ports':incompatible,'menu_icon_fallbacks':sorted(icon_names),'versions':{'mgear':'4.0.9','weightDriver_editor':'3.6','cvwrap':'Version not supplied'},'license':'Included anim_picker MIT license, Qt/six headers and Ingo Clemens MIT MEL notices retained; no inferred whole-bundle publishing permission','missing_dependencies':['No compiled cvwrap/weightDriver/mgear solver plugin binaries or C++ source provided','PyMel absent on installed Maya2025'],'module_import_effects':tops},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','*.py -text\n*.mel -text\nmgear/** -text\ncvwrap/** -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','cvwrap_weightdriver').replace('RootMotionBakeTool','CvWrapWeightDriverTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'cvwrap_weightdriver','registration':{'module':'cvwrap_weightdriver','class_name':'CvWrapWeightDriverTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[r['path'] for r in rows],'dependencies':['Maya cmds/MEL/Qt','Compatible native cvwrap / weightDriver / mgear_solvers binaries supplied by user environment; none provided in source unit','PyMel for bundled mGear 4.0.9'], 'acceptance_required':True,'change_summary':'Complete 532-file bundle/363 modules/4614 definitions and every 80 UI/rig templates/images/license retained, Python3 cvWrap port and explicit userSetup loader, guarded namespace/bootstrap/dependency preflight, complete cvWrap create/rebind/paint/binding IO and weightDriver/RBF/mGear entrypoints, originals and provenance, docs/tests/promotion.','verification_limitations':['Compiled native plugins absent from source and installed Maya; no fake implementation or plugin installation','PyMel missing: mGear full algorithms/UI not_run','Real GUI/native cvWrap bindings/RBF/rig production workflows unverified; complete third-party suite preserved, not rewritten wholesale','Explicit suite GUI operations retain upstream scene/file impact; use backup scenes and inspect original tool dialogs','mgear/cvwrap top-level namespace activation is explicit and refuses another already imported distribution; no userSetup/environment installation']},ensure_ascii=False,indent=2))
    print(json.dumps({'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'python_modules':len(definitions),'definitions':sum(len(v) for v in definitions.values()),'python2_files':incompatible},ensure_ascii=True))


if __name__=='__main__':
    main()
