"""Retain the original MEL bytes; full perspective reset candidate."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/03_transforms_modeling/camera_f_fix'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/camera_f_fix'


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(s.rstrip() for s in value.splitlines()).rstrip()+'\n',encoding='utf8',newline='\n')


def main():
    src=next(UNIT.glob('*.mel'))
    dst=PKG/'upstream'/src.name
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)
    put(PKG/'catalog.json',json.dumps({'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'behavior':'Select persp; ResetTransformations with Maya preferences; set local translate to (1,1,1)','implementation_evidence':'Installed Maya2025/scripts/startup/performResetTransformations.mel assembleCmd uses makeIdentity -apply false and resetTransformationsTranslate/Rotate/Scale options. No Autodesk script copied into candidate.','license':'No source attribution/license supplied; no publication rights inferred'},ensure_ascii=False,indent=2))
    put(UNIT/'.gitattributes','*.mel -text')
    put(RC/'.gitattributes','* -text')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf8').replace('root_motion_bake','camera_f_fix').replace('RootMotionBakeTool','CameraFFixTool')
    put(RC/'launch_candidate.py',launch+'\n\ndef show_ui():\n    return load_tool().show_ui()')
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'camera_f_fix','registration':{'module':'camera_f_fix','class_name':'CameraFFixTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[src.name],'dependencies':['Maya cmds/API2'],'acceptance_required':True,'change_summary':'Full original persp ResetTransformations plus local (1,1,1), with read-only Maya preference defaults and optional explicit flags, strict perspective target/writability/instance/driver checks, selection behavior preserved, AutoKey restoration, Undo, full API/UI/docs/tests/promotion and original byte archive.','verification_limitations':['Real interactive F framing behavior/viewport GUI and other versions not_run','This resets transform only; camera focal/clipping/COI/shape and viewport are not repaired','Original selects result camera; preserve_selection=True optionally keeps prior selection','Parented camera local channels reset; does not promise world-space pose or support rigs with transform children']},ensure_ascii=False,indent=2))
    print(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}))


if __name__=='__main__':
    main()
