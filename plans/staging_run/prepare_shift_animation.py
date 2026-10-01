"""Bundle the complete licensed MEL distribution without modifying vendor code."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/shift_animation_v3_2'
RAW=UNIT/'Shift_animation_v3_2'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/shift_animation_v3_2'


def main():
    PKG.mkdir(parents=True,exist_ok=True)
    files=[]
    for src in sorted(RAW.rglob('*')):
        if src.is_file():
            relative=src.relative_to(RAW)
            dst=PKG/'vendor'/relative
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
            files.append({'path':relative.as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    text=(RAW/'barnev_Shift_animation_code.mel').read_text(encoding='utf-8-sig')
    procs=re.findall(r'^global\s+proc\s+(?:(?:string|float|int|vector)\s*(?:\[\s*\])?\s+)?(\w+)\s*\(',text,re.M)
    globals={}
    for kind,name,array in re.findall(r'global\s+(string|float|int|vector)\s+\$(\w+)(\[\])?\s*;',text):
        if name!='gPlayBackSlider':
            globals[name]={'type':kind,'array':bool(array)}
    catalog={'files':files,'procedures':procs,'unique_procedures':sorted(set(procs)),'globals':globals,'vendor_modified':False,'license':'Barnev Pavel, Copyright 2018-2030; internal use, commercial purchase required, no redistribution or modification. Original license and notices retained unchanged.'}
    (PKG/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (UNIT/'.gitattributes').write_text('Shift_animation_v3_2/** -text\n',encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n',encoding='utf-8')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','shift_animation_v3_2').replace('RootMotionBakeTool','ShiftAnimationTool')
    (RC/'launch_candidate.py').write_text(launch,encoding='utf-8',newline='\n')
    payload=[p for f in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in f.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    data={'tool_id':'shift_animation_v3_2','registration':{'module':'shift_animation_v3_2','class_name':'ShiftAnimationTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[r['path'] for r in files],'dependencies':['Maya cmds/MEL and standard UI/animation-layer/cached-playback utilities','Original licensed Shift Animation v3.2 MEL engine (complete unchanged bundle)'],'acceptance_required':True,'change_summary':'Complete unmodified licensed MEL engine, original UI/installer, guides and icon retained. Separate adapter exposes full MATCH/AUTOPATH/manual/circle/root-motion/curve utilities with scene preflight, explicit original custom-attribute cleanup option, Undo and environment restoration.','verification_limitations':['Full MATCH/path/circle/root-motion workflows require interactive Maya animation-layer/timeline builtins; batch numeric/procedure checks do not verify these workflows','Original vendor code cannot be patched under supplied license; source bugs must be reported and checked in real Maya','Original root-motion/path cleanup deletes user-defined control attributes; explicit allowance and backup are required if such attrs exist','Original MEL names/globals remain shared; do not run two vendor versions or native and candidate UI concurrently','License forbids redistribution/modification; commercial use requires purchase; no purchases or publishing performed']}
    (RC/'promotion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'files':len(files),'procedures':len(procs),'unique_procedures':len(set(procs)),'globals':len(globals)}))


if __name__=='__main__':
    main()
