"""Complete original task-list weight merge, with a self-contained safe runtime."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/02_rigging_hierarchy/skin_weight_transfer'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/skin_weight_transfer'


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    src=next(UNIT.glob('*.py'))
    archive=PKG/'upstream'/(src.name+'.original')
    archive.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,archive)
    tree=ast.parse(src.read_bytes())
    functions=[n.name for n in tree.body if isinstance(n,ast.FunctionDef)]
    tree.body=[n for n in tree.body if not isinstance(n,ast.Expr)]
    put(PKG/'original_logic.py',ast.unparse(tree))
    put(PKG/'catalog.json',json.dumps({'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'functions':functions,'license':'No attribution or independent license supplied; local preparation only','behavior':'Source weight added to target, source zero, all vertices normalize, optional remove source skin influence; multiline ordered tasks with source-linked automatic mesh discovery','changes':'Exact UUID/DAG matching instead of ambiguous short-name fallback; all-task preflight instead of silent per-mesh skip/partial success; API weight reads with undoable cmds writes, full task list UI/API'},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','*.py -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','skin_weight_transfer').replace('RootMotionBakeTool','SkinWeightTransferTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'skin_weight_transfer','registration':{'module':'skin_weight_transfer','class_name':'SkinWeightTransferTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[src.name],'dependencies':['Maya cmds/OpenMaya/OpenMayaAnim API2'],'acceptance_required':True,'change_summary':'Complete ordered multiline source->target->meshes->DelSkin business retained, original full function and bytes archive, native API bulk reads plus undoable exact influence row writes/normalization, remove source influence, auto discover linked skin meshes, strict scope/full-list simulated influence preflight, whole task-list UI/schema/docs/tests/promotion.','verification_limitations':['Real Maya GUI and production large meshes/other Maya versions not_run','Undoable per-vertex cmds writes may be slower than original non-undoable API bulk setWeights','Reject locked/reference/instanced/multi-skin/multi-geometry targets, ambiguous names, input-driven skin weight data and unsupported non-linear skin modes','All-list preflight rejects invalid tasks rather than silently skipping meshes; unexpected execution error may leave partial changes, Undo once before continuing']},ensure_ascii=False,indent=2))
    print(json.dumps({'functions':len(functions),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()}))


if __name__=='__main__':
    main()
