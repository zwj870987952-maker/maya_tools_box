"""Bundle the complete licensed weapon suite without modifying its code."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/sword_anim_polishing_tool_v4'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/sword_anim_polishing_tool_v4'


def main():
    rows=[]
    raw=[p for p in UNIT.rglob('*') if p.is_file() and not {'release_candidate','__pycache__'}.intersection(p.relative_to(UNIT).parts) and p.name!='.gitattributes']
    for src in sorted(raw):
        rel=src.relative_to(UNIT)
        dst=PKG/'vendor'/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        rows.append({'path':rel.as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    text=(UNIT/'sword_anim_polish_tool.mel').read_text(encoding='utf-8-sig')
    procs=re.findall(r'^global\s+proc\s+(?:(?:string|float|int|vector)\s*(?:\[\s*\])?\s+)?(\w+)\s*\(',text,re.M)
    globals={name:{'type':kind,'array':bool(array)} for kind,name,array in re.findall(r'global\s+(string|float|int|vector)\s+\$(\w+)(\[\])?\s*;',text) if name not in ('gMainPane','gPlayBackSlider')}
    PKG.mkdir(parents=True,exist_ok=True)
    # Reuse this repository's own tested external-adapter utilities, not the
    # licensed vendor implementation. Each candidate remains self contained.
    own=(ROOT/'tools_staging_pool/01_animation/shift_animation_v3_2/release_candidate/maya_toolkit/tools/shift_animation_v3_2/runtime.py').read_text(encoding='utf-8')
    keep={'catalog','resources','quote','array','identity','all_uuids','resolve','editable','node','Ledger','load_vendor','snapshot','restore'}
    tree=ast.parse(own)
    pieces=[ast.get_source_segment(own,n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in keep]
    header='import hashlib\nimport json\nfrom pathlib import Path\nimport re\nimport uuid\nimport maya.cmds as cmds\nimport maya.mel as mel\nPKG=Path(__file__).resolve().parent\nBRAND="sword_anim_polishing_candidate_v1"\nOWNER="mtkSwordCandidateSession"\nDATA="mtkSwordCandidateData"\nMENU="sword_anim_polish_tool"\nVENDOR=PKG/"vendor/sword_anim_polish_tool.mel"\n'
    adapter=header+'\n\n'+'\n\n'.join(pieces)+'\n'
    adapter=adapter.replace('mtkShift','mtkSword')
    (PKG/'vendor_adapter.py').write_text(adapter,encoding='utf-8',newline='\n')
    catalog={'files':rows,'procedures':procs,'unique_procedures':sorted(set(procs)),'globals':globals,'vendor_modified':False,'license':'Barnev Pavel Copyright 2018-2020; internal use, commercial purchase required, no redistribution/modification. Complete original license/notices retained.'}
    (PKG/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (UNIT/'.gitattributes').write_text('*.mel -text\n*.txt -text\n*.TXT -text\nmisc/** -text\nicons/** -text\n',encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n',encoding='utf-8')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','sword_anim_polishing_tool_v4').replace('RootMotionBakeTool','SwordAnimPolishTool')
    (RC/'launch_candidate.py').write_text(launch,encoding='utf-8',newline='\n')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    description={'tool_id':'sword_anim_polishing_tool_v4','registration':{'module':'sword_anim_polishing_tool_v4','class_name':'SwordAnimPolishTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[x['path'] for x in rows],'dependencies':['Maya cmds/MEL and actual interactive timeline/model panel for interactive setup/arc','Full unmodified licensed Sword Anim Polish MEL distribution, all help/installer/icon included','matrixNodes/decomposeMatrix and cached-playback utility for original Arc Polish'],'acceptance_required':True,'change_summary':'Complete licensed weapon/aim/reverse/parent/path/bake algorithms and original UI retained unmodified. Independent API/UI adds scope validation, explicit setup completion instead of unmanaged native callbacks, UUID session tracking, observed native Undo balancing/environment restoration and full promotion payload.','verification_limitations':['Real Maya GUI/interactive Parent In/aim/sword/reverse setup and full Arc Polish pending','Source license forbids modifying vendor defects or distributing; internal commercial use requires license','Original vendor MEL globals/procedures are shared; native and candidate UI must not run concurrently','Original native motion-path helper leaves an open Undo chunk; adapter balances observed opens on success/failure, complete interactive Arc still requires acceptance','Original Euler filter seeds a temporary zero key before first key; rotation outside bake range can change','Source bake catches errors internally; range-key checks cannot prove every production rig/layer baked correctly']}
    (RC/'promotion.json').write_text(json.dumps(description,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'files':len(rows),'procedures':len(procs),'unique_procedures':len(set(procs)),'globals':len(globals)}))


if __name__=='__main__':
    main()
