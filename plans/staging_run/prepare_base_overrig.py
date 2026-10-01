"""Copy the complete licensed distribution unchanged; separate adapter only."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/base_overrig_v9_0'
RAW = UNIT / 'base_OverRig_scripts_V9_0'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/base_overrig_v9_0'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    files = []
    for source in sorted(RAW.rglob('*')):
        if source.is_file():
            target = PKG / 'vendor' / source.relative_to(RAW)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files.append({'path': source.relative_to(RAW).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    report = audit(RAW / 'base_OverRig_scripts.mel')
    if report['top_level_lines']:
        raise ValueError('Vendor no longer consists only of declarations')
    lines = (RAW / 'base_OverRig_scripts.mel').read_bytes().decode('latin-1').splitlines()
    procedures = {}
    effects = ('delete', 'deleteAttr', 'cutKey', 'bakeResults', 'parent', 'scriptJob', 'scriptNode', 'optionVar', 'loadPlugin', 'pluginInfo', 'file', 'undoInfo', 'python', 'evaluationManager', 'timeControl', 'window')
    for procedure in report['procedures']:
        body = '\n'.join(lines[procedure['line'] - 1:procedure['end_line']])
        procedure['direct_effects'] = [effect for effect in effects if re.search(r'\b' + effect + r'\b', body)]
        procedures[procedure['name']] = procedure
    public = {name: definition for name, definition in procedures.items() if not name.startswith('BOver9_0_') and name != 'find'}
    catalog = {'files': files, 'procedures': procedures, 'public': public, 'declaration_count': len(report['procedures']), 'duplicate_names': report['duplicate_names'], 'top_level_lines': [], 'vendor_modified': False, 'license': 'Barnev Pavel Copyright 2020-2028. No modification or redistribution; commercial use requires purchase. License.txt retained unchanged.'}
    write(PKG / 'catalog.json', json.dumps(catalog, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', 'base_OverRig_scripts_V9_0/** -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'base_overrig_v9_0').replace('RootMotionBakeTool', 'BaseOverRigTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'base_overrig_v9_0', 'registration': {'module': 'base_overrig_v9_0', 'class_name': 'BaseOverRigTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in files], 'dependencies': ['Maya cmds/MEL, real timeline/GraphEditor for native workflows', 'Bundled Jiggle_Bone_New.mb, icons and complete ENG/RUS PDF manuals', 'Native procedures may load Maya matrixNodes/lookdevKit and alter runtime autoload/UI preferences'], 'acceptance_required': True, 'change_summary': 'Complete unmodified licensed OverRig 9.0 distribution and all 308 declarations retained. Separate typed public-procedure API, resource/selection/lock/version preflight and read-only inspect, original full UI, Undo nesting and caller environment restoration. Installer/userSetup/hotkeys never executed.', 'verification_limitations': ['Native interactive GUI/bake/knots/IK/overlap/physics and production rigs not_run', 'Native public calls depend on selection, timeline, GraphEditor, objectSets and shared MEL globals; direct effects catalog is not a complete transitive safety proof', 'Vendor catches errors silently; an absence of fatal error does not prove each operation succeeded', 'Native Undo-disabled motion-trail code, callbacks/scriptNodes and runtime/UI/plugin settings cannot be guaranteed by scene Undo', 'Original duplicate procedure declaration retained; other versions or tools with shared global procedure names require a fresh Maya session', 'License forbids modifications/redistribution and requires commercial purchase; no purchase/publishing performed']}
    write(RC / 'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(files), 'declarations': len(report['procedures']), 'unique': len(procedures), 'public': len(public)}))


if __name__ == '__main__':
    main()
