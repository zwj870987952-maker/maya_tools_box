"""Preserve all six licensed assets and audit every original declaration."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/joint_optimal_pro_v4_1'
RAW = UNIT / 'Joint_Optimal_Pro_Application_v4.1'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/joint_optimal_pro_v4_1'


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
    source = RAW / 'barnev_Joint_Optimal_Pro_Application_code.mel'
    report = audit(source)
    if report['top_level_lines']:
        raise ValueError('Do not source automatic scene/UI actions')
    lines = source.read_bytes().decode('latin-1').splitlines()
    procedures = {}
    effects = ('delete', 'deleteAttr', 'cutKey', 'bakeResults', 'parent', 'setAttr', 'connectAttr', 'eval', 'python', 'system', 'optionVar', 'selectPref', 'undoInfo', 'window')
    for procedure in report['procedures']:
        body = '\n'.join(lines[procedure['line'] - 1:procedure['end_line']])
        procedure['direct_effects'] = [effect for effect in effects if re.search(r'\b' + effect + r'\b', body)]
        # Retain original annotations instead of inventing names for hashed procedures.
        procedure['ui_references'] = [{'line': i + 1, 'text': line.strip()} for i, line in enumerate(lines[:560]) if procedure['name'] in line and not line.startswith('global proc')]
        procedures[procedure['name']] = procedure
    public = {name: definition for name, definition in procedures.items() if name != 'find'}
    c = {'files': files, 'procedures': procedures, 'public': public, 'declaration_count': len(report['procedures']), 'duplicate_names': report['duplicate_names'], 'top_level_lines': [], 'vendor_modified': False, 'license': 'Copyright Barnev Pavel 2018-2022. Original License.txt retained: no modification/redistribution, commercial use requires purchase. No purchase or publishing performed.'}
    write(PKG / 'catalog.json', json.dumps(c, ensure_ascii=False, indent=2))
    write(UNIT / '.gitattributes', 'Joint_Optimal_Pro_Application_v4.1/** -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'joint_optimal_pro_v4_1').replace('RootMotionBakeTool', 'JointOptimalProTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'joint_optimal_pro_v4_1', 'registration': {'module': 'joint_optimal_pro_v4_1', 'class_name': 'JointOptimalProTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in files], 'dependencies': ['Maya cmds/MEL with interactive viewport for complete original workflows', 'Entire original MEL, PDF guide, README, license, icon and installer retained; installer never executed'], 'acceptance_required': True, 'change_summary': 'Complete unmodified Joint Optimal Pro 4.1 distribution, all 144 declarations / 143 unique procedures, original full UI and 142 typed callable signatures. Independent read-only inspect/dry-run, scope/channel checks, true DAG instance guards, nested Undo handling and caller environment restoration. Original installer and system-based find helper are not executed.', 'verification_limitations': ['Real Maya GUI, vertex workflows, chain insertion/removal, orient/freeze, mirror, bake/reparent and production rigs not_run', 'Original callbacks expand beyond explicit input scope; native catchQuiet may hide partial failure', 'Original duplicate declaration, shared find/global names and native eval/Python retained unchanged; fresh Maya session required for conflicts', 'Original UI callbacks/preferences are outside API restoration and scene Undo; vendor bytes never rewritten', 'License retained, no commercial license verification or redistribution/publishing performed']}
    write(RC / 'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(files), 'declarations': len(report['procedures']), 'unique': len(procedures), 'public': len(public)}))


if __name__ == '__main__':
    main()
