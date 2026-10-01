"""Complete selected joint/locator forest duplication, preserve original bytes."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/skeleton_generator'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/skeleton_generator'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(line.rstrip() for line in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    source = next(UNIT.glob('*.py'))
    target = PKG / 'vendor' / (source.name+'.original')
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    tree = ast.parse(source.read_bytes())
    tree.body = [n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))]
    write(PKG/'original_logic.py',ast.unparse(tree))
    write(PKG/'catalog.json',json.dumps({'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'function':'duplicate_skeleton_hierarchy','behavior':'Selected joints and locator transforms only; preserve immediate selected-parent edges, match world position/rotation without scale, copy radius/drawStyle for joints, select result','license':'No attribution/license provided; no publishing rights inferred'},ensure_ascii=False,indent=2))
    write(UNIT/'.gitattributes','*.py -text')
    write(RC/'.gitattributes','* -text')
    launch = (ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','skeleton_generator').replace('RootMotionBakeTool','SkeletonGeneratorTool')
    write(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    description = {'tool_id':'skeleton_generator','registration':{'module':'skeleton_generator','class_name':'SkeletonGeneratorTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[source.name],'dependencies':['Maya cmds/API2'],'acceptance_required':True,'change_summary':'Complete original selected joint/locator forest creation with copied world TR and joint radius/drawStyle; original bytes and full function retained, no auto execution; exact selected hierarchy edges, suffix/name collision checks, no scale or unselected hierarchy copying, iterative deep forests, dry scope and Undo, deferred complete UI.','verification_limitations':['Real Maya GUI, production mixed/scaled rigs and other versions not_run','Creates a posed new skeleton, not copied animation/skin/bindPose or original jointOrient channels','Original selected-child-only behavior retained; unselected parents separate roots, no inferred missing edges']}
    write(RC/'promotion.json',json.dumps(description,ensure_ascii=False,indent=2))
    print(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}))


if __name__=='__main__':
    main()
