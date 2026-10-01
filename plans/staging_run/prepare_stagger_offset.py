"""Bundle both complete original offset workflows and future-layout payload."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/stagger_offset'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/stagger_offset'


def main():
    rows=[]
    for src in sorted(UNIT.glob('*.py')):
        dst=PKG/'upstream'/(src.name+'.original')
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        rows.append({'path':src.name,'archive':dst.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    (PKG/'catalog.json').write_text(json.dumps({'files':rows,'license':'User legacy scripts, no separate license supplied','source_entry':'Two full original once/batch UI scripts, preserved without execution'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (UNIT/'.gitattributes').write_text('*.py -text\n',encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n',encoding='utf-8')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','stagger_offset').replace('RootMotionBakeTool','StaggerOffsetTool')
    (RC/'launch_candidate.py').write_text(launch,encoding='utf-8',newline='\n')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    data={'tool_id':'stagger_offset','registration':{'module':'stagger_offset','class_name':'StaggerOffsetTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[x['path'] for x in rows],'dependencies':['Maya cmds, no external dependencies'],'acceptance_required':True,'change_summary':'Both original single-remove and repeated-remove batch offset workflows retained, complete original sources archived. Dense-key-safe whole-curve translation replaces collision-prone per-time loops, explicit ordered whole-node scope, shared curve guards, dry-run/Undo and UI provided.','verification_limitations':['Real Maya GUI and production animation acceptance pending','Original ls(dag=True) expanded descendants; candidate deliberately uses explicitly ordered whole transforms','Keyframe times/values move together; Maya key clipboard/selection effects are separate from scene Undo','Original two auto-opening source entry points remain archive-only']}
    (RC/'promotion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'source_files':len(rows)}))


if __name__=='__main__':
    main()
