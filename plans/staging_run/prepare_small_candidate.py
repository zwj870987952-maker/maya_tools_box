"""Archive exact original files and prepare complete future layout metadata."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--tool',required=True); parser.add_argument('--class-name',required=True)
    parser.add_argument('--summary',required=True); parser.add_argument('--dependencies',nargs='*',default=['Maya cmds/API2'])
    parser.add_argument('--limitations',nargs='*',default=['Real Maya GUI and production scene acceptance not_run'])
    args=parser.parse_args(); unit=ROOT/'tools_staging_pool'/args.tool; tool=unit.name
    rc=unit/'release_candidate'; pkg=rc/'maya_toolkit/tools'/tool
    rows=[]
    for src in sorted(unit.rglob('*')):
        if not src.is_file() or 'release_candidate' in src.relative_to(unit).parts or '__pycache__' in src.parts or src.name=='.gitattributes': continue
        rel=src.relative_to(unit); dst=pkg/'upstream'/rel
        if src.suffix=='.py': dst=dst.with_suffix('.py.original')
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
        rows.append({'path':rel.as_posix(),'archive':dst.relative_to(pkg).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    put(unit/'.gitattributes','* -text')
    put(rc/'.gitattributes','* -text')
    put(pkg/'catalog.json',json.dumps({'files':rows,'license':'Supplied original source notices preserved; no redistribution grant inferred'},ensure_ascii=False,indent=2))
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake',tool).replace('RootMotionBakeTool',args.class_name)
    put(rc/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (rc/'maya_toolkit',rc/'docs',rc/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(rc/'promotion.json',json.dumps({'tool_id':tool,'registration':{'module':tool,'class_name':args.class_name},'files':[{'source':p.relative_to(rc).as_posix(),'target':p.relative_to(rc).as_posix()} for p in sorted(payload)],'resources':[r['path'] for r in rows],'dependencies':args.dependencies,'acceptance_required':True,'change_summary':args.summary,'verification_limitations':args.limitations},ensure_ascii=False,indent=2))
    print(json.dumps({'tool':tool,'original_files':len(rows),'payload_files':len(payload)}))


if __name__=='__main__': main()
