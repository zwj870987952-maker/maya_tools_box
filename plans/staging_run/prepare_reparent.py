"""Preserve entire distribution and port all native procedures with scoped names."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/02_rigging_hierarchy/reparent_pro_v1_5_1'
RAW = UNIT / 'reParent_Pro_v1.5.1'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/reparent_pro_v1_5_1'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(line.rstrip() for line in value.splitlines()).rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    files = []
    for source in sorted(RAW.rglob('*')):
        if source.is_file():
            target = PKG / 'vendor' / source.relative_to(RAW)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files.append({'path': source.relative_to(RAW).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    source = RAW / 'reParentPro _v1.5.1.mel'
    original = source.read_text(encoding='utf-8-sig')
    report = audit(source)
    text = original
    for row in sorted(report['procedures'], key=lambda row: -len(row['name'])):
        text = re.sub(r'\b' + row['name'] + r'\b', 'rppstg_' + row['name'], text)
    for name in ('eulerFilterCurves', 'UpHierarchyObject', 'LockedAttr1', 'LockedAttr2'):
        text = text.replace('$' + name, '$rppstg_' + name)
    fixed = ['ReParentPanel', 'ManualWindow', 'reParentButton', 'onLayerMode', 'DelRed', 'PinCheckBox', 'IKCheckBox', 'IKCheckLocalBox', 'ManualCheckBox', 'FreezeCheckBox', 'RelativeCheckBox', 'aboutMenu', 'helpMenu', 'reParent_sets', 'All_Sessions_reParentControls_set', 'Last_Session_reParentControls_set', 'Last_Session_reParentLocator_set', 'All_Session_reParentLocator_set']
    for name in sorted(fixed, key=len, reverse=True):
        text = re.sub(r'\b' + name + r'\b', 'rppstg_' + name, text)
    for name in ('TempLocator', 'TempOrientConst', 'TempPointConst', 'TempParentConst'):
        text = text.replace(name, 'rppstg_' + name)
    # Prefix every explicitly constructed helper suffix, including IK handle/lock helpers.
    text = re.sub(r'"([^"\n]*)"', lambda m: '"' + re.sub(r'(_[Rr]eParent|ReParent|_ikHandle|poleVectorConstraint|tempLockedCtrl)', lambda n: '_RPPStage' + n.group(0), m.group(1)) + '"' if not m.group(1).startswith('rppstg_') and (any(s in m.group(1) for s in ('_ReParent', '_reParent', '_ikHandle', 'poleVectorConstraint', 'tempLockedCtrl')) or m.group(1) == 'ReParent') else m.group(0), text)
    # Fix the reversed native range in every bake, not just one branch.
    text = text.replace('($currentL+":"+$currentR)', '($currentR+":"+$currentL)')
    # Pin creates no temporary constraints; deleting an unmatched wildcard errors.
    text = re.sub(r'delete "rppstg_Temp(?:Orient|Point|Parent)Const\*"(?: "rppstg_Temp(?:Orient|Point|Parent)Const\*")*;', 'rppstg_deleteTemps();', text)
    options = ('PinCheckBox', 'FreezeCheckBox', 'RelativeCheckBox', 'IKCheckBox', 'ManualCheckBox', 'IKCheckLocalBox', 'DelRed')
    for key in options:
        text = re.sub(r'`(?:checkBox|menuItem)\s+-(?:q|query)\s+-(?:v|cb)\s+rppstg_' + key + r'`', 'rppstg_setting("' + key + '")', text)
    # Manual business operations work without a hidden dummy window.
    text = re.sub(r'window\s+-edit\s+-widthHeight 142 203 rppstg_ReParentPanel;', 'rppstg_manualUI(1);', text)
    text = re.sub(r'window\s+-edit\s+-widthHeight 142 159 rppstg_ReParentPanel;', 'rppstg_manualUI(0);', text)
    text = re.sub(r'button\s+-edit\s+-en [01] rppstg_reParentButton;', '', text)
    lines = text.splitlines()
    head = '\n'.join(lines[:47])
    head = head.replace('progressWindow -endProgress;', '').replace('optionVar -intValue animBlendingOpt 1;', '')
    body = '\n'.join(lines[49:])
    # Promote original three local helper procedures for explicit API/GUI invocation.
    body = re.sub(r'(?m)^proc (rppstg_\w+)\(', r'global proc \1(', body)
    helper = '''global proc int rppstg_setting(string $key) {
    return int(python("__import__('maya_toolkit.tools.reparent_pro_v1_5_1.runtime',fromlist=['native_setting']).native_setting('"+$key+"')"));
}
global proc rppstg_manualUI(int $active) {
    if (`window -exists rppstg_ReParentPanel`) {window -edit -widthHeight 310 (220+44*$active) rppstg_ReParentPanel;}
    if (`control -exists rppstg_reParentButton`) {button -edit -enable (!$active) rppstg_reParentButton;}
}
global proc rppstg_deleteTemps() {
    string $nodes[] = `ls "rppstg_TempOrientConst*" "rppstg_TempPointConst*" "rppstg_TempParentConst*"`;
    if (size($nodes)) {delete $nodes;}
}
'''
    write(PKG / 'native.mel', helper + body)
    write(PKG / 'native_ui.mel', 'global proc rppstg_showUI() {\n' + head + '\n}\n')
    adapted = audit(PKG / 'native.mel')
    if len(adapted['procedures']) != 16 or adapted['top_level_lines']:
        raise ValueError('Whole procedure coverage/no auto execution failed')
    write(PKG / 'catalog.json', json.dumps({'files': files, 'original_procedures': report['procedures'], 'adapted_procedures': adapted['procedures'], 'original_top_level_ui_deferred': True, 'copyright': 'Dmitrii Kolpakov 2020; no license file supplied; no redistribution rights inferred'}, indent=2))
    write(UNIT / '.gitattributes', 'reParent_Pro_v1.5.1/** -text')
    write(RC / '.gitattributes', '* -text')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'reparent_pro_v1_5_1').replace('RootMotionBakeTool', 'ReParentProTool')
    write(RC / 'launch_candidate.py', launch + '\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'reparent_pro_v1_5_1', 'registration': {'module': 'reparent_pro_v1_5_1', 'class_name': 'ReParentProTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in files], 'dependencies': ['Maya cmds/MEL; interactive Maya for full native GUI and freeze progress window'], 'acceptance_required': True, 'change_summary': 'Complete 13 original procedures, full native UI/icon and original bytes preserved. Explicit default/pin/manual start-go-cancel/relative/freeze/IK/local modes, independent MEL/options/helper names, corrected bake ranges, clear-all-TR acknowledgement, owned session checks, safe bake/delete, caller context and Undo grouping.', 'verification_limitations': ['Real Maya GUI and production FK/IK/manual pivot/freeze/advanced animation layers not_run', 'Original clear-all-TR behavior explicitly retained and requires allow_clear_animation', 'Native MEL declarations persist outside scene Undo; errors can leave partial edits requiring one Undo', 'Original anim-layer menu was inert; candidate implements it only for final bake_delete, not an invented per-locator native feature', 'Unsupported referenced/locked/instanced/shared animation/rig naming collisions rejected; no original session auto-import', 'Copyright retained; no license file supplied or publishing performed']}
    write(RC / 'promotion.json', json.dumps(description, ensure_ascii=False, indent=2))
    print(json.dumps({'original_procedures': len(report['procedures']), 'adapted_procedures': len(adapted['procedures']), 'assets': len(files)}))


if __name__ == '__main__':
    main()
