"""Package byte-identical licensed suite; do not rewrite original software."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
from prepare_small_candidate import put
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/asset_it_v1_2'
RC=UNIT/'release_candidate'; PKG=RC/'maya_toolkit/tools/asset_it_v1_2'
rows=[]; definitions=[]
for source in sorted(UNIT.rglob('*')):
    if not source.is_file() or any(p in ('release_candidate','__pycache__') for p in source.relative_to(UNIT).parts) or source.name=='.gitattributes': continue
    rel=source.relative_to(UNIT); target=PKG/'bundle'/rel
    if source.name=='Drag_Me_In_Viewport.py': target=PKG/'upstream'/rel.with_suffix('.py.original')
    target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,target)
    rows.append({'path':rel.as_posix(),'archive':target.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bytes':source.stat().st_size})
    if source.suffix=='.py':
        tree=ast.parse(source.read_bytes())
        definitions.extend({'file':rel.as_posix(),'name':n.name,'line':n.lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)))
put(UNIT/'.gitattributes','* -text'); put(RC/'.gitattributes','* -text')
put(PKG/'catalog.json',json.dumps({'files':rows,'functions':definitions,'license':'AssetIt supplied EULA retained byte-for-byte; limited personal noncommercial license and restriction on modifications/third-party distribution; no broader grant inferred','native_code_modified':False},ensure_ascii=False,indent=2))
launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','asset_it_v1_2').replace('RootMotionBakeTool','AssetItTool')
put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
files=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
put(RC/'promotion.json',json.dumps({'tool_id':'asset_it_v1_2','registration':{'module':'asset_it_v1_2','class_name':'AssetItTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(files)],'resources':[r['path'] for r in rows],'dependencies':['Maya','PySide2/shiboken2','PyMel','Arnold mtoa','Original suite installed at Maya version scripts/AssetIt path for full native UI'],'acceptance_required':True,'change_summary':'978 originals/290 library models plus 3 creation scenes/225 definitions and complete native UI/resource bundle unchanged; separate bounded inventory/metadata/owned import Undo-Redo and fresh install/native launch adapter; exclusive install/path/namespace/evidence and full legacy impact documentation','verification_limitations':['Native full UI and licensed suite advanced operations not_run','PyMel unavailable; Arnold actually autoloaded during isolated model import, renderer acceptance not_run','Original suite cleanup/delete/rename/import/render/preferences retain original effects, not silently made undo-safe']},ensure_ascii=False,indent=2))
print(json.dumps({'original_files':len(rows),'functions':len(definitions),'payload_files':len(files),'bytes':sum(r['bytes'] for r in rows),'native_code_modified':False}))
