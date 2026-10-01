"""Bundle all Stagger assets and privately preserve its original GUI."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/stagger_gui'
RAW=UNIT/'stagger'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/stagger_gui'


def put(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8',newline='\n')


def main():
    files=[]
    for src in sorted(RAW.rglob('*')):
        if not src.is_file():
            continue
        rel=src.relative_to(RAW)
        dst=PKG/'upstream'/rel
        if src.suffix=='.py':
            dst=dst.with_suffix('.py.original')
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        files.append({'path':rel.as_posix(),'archive':dst.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
        if src.suffix!='.py':
            dst=PKG/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
    source=(RAW/'ui.py').read_text(encoding='utf-8-sig')
    tree=ast.parse(source)
    stagger=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='stagger_it')
    source_lines=source.splitlines(True)
    source_lines[stagger.lineno-1:stagger.end_lineno]=["def stagger_it():\n    from .ui_bridge import apply_ui\n    return apply_ui()\n"]
    native=''.join(source_lines)
    # Preserve the original drawing/layout callbacks with private control names.
    names=('stagger_window','sf','ef','fl','pb','form','stagger_amount','stagger_it','start_frame','end_frame')
    for name in names:
        native=native.replace("'"+name+"'",repr('mayaToolkitStagger_'+name))
    put(PKG/'ui.py',native)
    put(PKG/'catalog.json',json.dumps({'files':files,'author':'Animation Creation','copyright':'2022 animationcreation.com','version':'1.1.0','license':'No independent license supplied; preserve credits, local preparation only','original_functions':[n.name for n in tree.body if isinstance(n,ast.FunctionDef)]},ensure_ascii=False,indent=2)+'\n')
    put(UNIT/'.gitattributes','stagger/** -text\n')
    put(RC/'.gitattributes','* -text\n')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','stagger_gui').replace('RootMotionBakeTool','StaggerGuiTool')
    put(RC/'launch_candidate.py',launch)
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'stagger_gui','registration':{'module':'stagger_gui','class_name':'StaggerGuiTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[x['path'] for x in files],'dependencies':['Maya cmds/MEL/OpenMaya (no external Python package)','All eight SVG images, original demo GIF and three-page installation PDF included'],'acceptance_required':True,'change_summary':'Full original stagger resampling algorithm, original GUI layout/slider/range buttons and all assets preserved. Scoped curve API, read-only validation, Undo, private UI names and finally progress restoration added.','verification_limitations':['Real Maya GUI/timeline/SVG rendering pending','Weighted/nonlinear production curves and other Maya versions require acceptance','No separate distribution license supplied; local preparation only','Original animation outside range is intended preserved via boundary insertion; existing interior keys are not removed']},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'files':len(files),'functions':len([n for n in tree.body if isinstance(n,ast.FunctionDef)])}))


if __name__=='__main__':
    main()
