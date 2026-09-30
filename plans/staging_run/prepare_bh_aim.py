"""Prepare complete purchased MEL suite privately; preserve all original resources."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/bh_aim_tools_v1_1'
SOURCE = UNIT / 'bh_aimTools_v1.1'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/bh_aim_tools_v1_1'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SOURCE.rglob('*') if p.is_file())
    resources = []
    for file in files:
        relative = file.relative_to(SOURCE)
        target = PACKAGE / 'upstream' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': 'upstream/' + relative.as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    entry = SOURCE / 'bh_aimTools.mel'
    original = entry.read_text(encoding='utf-8-sig')
    info = audit(entry)
    names = [row['name'] for row in info['procedures']]
    top = {int(row.split(':', 1)[0]) for row in info['top_level_lines']}
    if len(top) != 1 or not info['top_level_lines'][0].endswith('bh_aimTools;'):
        raise ValueError('Unexpected top-level code')
    adapted = ''.join('\n' if i + 1 in top else line for i, line in enumerate(original.splitlines(True)))
    adapted = re.sub(r'(?<!global )\bproc\b', 'global proc', adapted)
    for name in names:
        adapted = re.sub(r'\b' + re.escape(name) + r'\b', 'mtbAim_' + name, adapted)
    for name in ('keysOnlyAttachSwitch', 'keysOnlyBakeSwitch', 'mainCol'):
        adapted = re.sub(r'\b' + name + r'\b', 'mtbAim_' + name, adapted)
    # Controller names may be long paths and generated names may already exist.
    adapted = adapted.replace('string $ng = $each + "_AIM_LOCATOR";', 'string $ng = `match "[^|]*$" $each` + "_AIM_LOCATOR";')
    adapted = adapted.replace('string $ng = $targetObj + "_ROOTLOCATOR";', 'string $ng = `match "[^|]*$" $targetObj` + "_ROOTLOCATOR";')
    adapted = adapted.replace('return $ng;', 'return $tempNull[0];')
    # Replace the original confirmation by explicit args. UI asks before dispatch.
    pattern = r'string \$checkIt=`confirmDialog[\s\S]*?-dismissString "No"`;'
    adapted, count = re.subn(pattern, 'global int $mtbAim_deleteKeys;\nstring $checkIt = "No";\nif ($mtbAim_deleteKeys) $checkIt = "Yes";', adapted)
    if count != 1:
        raise ValueError('Expected one rotation-key confirmation')
    adapted = adapted.replace('global proc mtbAim_bh_bakeCtrlAllFrames()\n{', 'global proc mtbAim_bh_bakeCtrlAllFrames()\n{\nstring $pairBlendNodesFound[];')
    adapted = adapted.replace('select -r $findPtCns; doDelete;', 'python("import maya_toolkit.tools.bh_aim_tools_v1_1.runtime as _a; _a.delete_parent_constraints()");')
    adapted = adapted.replace('delete $target;', 'python("import maya_toolkit.tools.bh_aim_tools_v1_1.runtime as _a; _a.delete_locator()");')
    # Keep original layout and option toggles; four scene buttons use the API.
    for name, action in {'bh_createAimLoc': 'create', 'bh_attachLoc': 'attach', 'bh_aimCtrlAtLoc': 'aim', 'bh_bakeFromAimLoc': 'bake'}.items():
        callback = 'python(' + json.dumps("import maya_toolkit.tools.bh_aim_tools_v1_1.ui as _u; _u.dispatch('" + action + "')") + ');'
        adapted = adapted.replace('-c mtbAim_' + name + ';', '-c ' + json.dumps(callback) + ';')
    adapted = adapted.replace('`checkBox -q -v mtbAim_keysOnlyAttachSwitch`', '`mtbAim_read_keys_only`').replace('`checkBox -q -v mtbAim_keysOnlyBakeSwitch`', '`mtbAim_read_keys_only`')
    # Direct internal scene procedures cannot bypass the standard adapter.
    masked = masked_source(adapted)
    points = []
    pure = {'bh_aimTools', 'selectFlag', 'bh_dummy', 'floatArrayRemoveDuplicates'}
    for match in re.finditer(r'global proc\s+(?:(?:string|float|int)\s*(?:\[\s*\])?\s+)?(mtbAim_\w+)\([^)]*\)', masked):
        if match.group(1)[len('mtbAim_'):] not in pure:
            points.append(masked.index('{', match.end()) + 1)
    guard = '\npython("import maya_toolkit.tools.bh_aim_tools_v1_1.runtime as _a; _a.require_active()");\n'
    for index in reversed(points):
        adapted = adapted[:index] + guard + adapted[index:]
    adapted += '\nglobal proc int mtbAim_read_keys_only() { global int $mtbAim_keysOnly; return $mtbAim_keysOnly; }\n'
    adapted = '\n'.join(line.expandtabs(4).rstrip() for line in adapted.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'bh_aim_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/bh_aimTools.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'bh_aim_tools_v1_1', 'raw_files': resources, 'original_procedures': names,
               'runtime_procedures': ['mtbAim_' + name for name in names] + ['mtbAim_read_keys_only'],
               'original_audit': info, 'runtime_audit': audit(PACKAGE / 'runtime.mel'),
               'source_license': 'Purchased author tool; README explicitly requests not sharing. Local preparation only; no public publication.',
               'guide_reviewed': 'Complete ReadMe.txt', 'localized_variant': 'Archived intact; runtime uses the original English algorithm/UI',
               'changes': ['Definition-only and private procedure/control names', 'Full original algorithm/UI with standard callbacks', 'Explicit rotation deletion flag instead of business confirmation', 'Unique actual temporary locator name; long-path-safe leaf naming', 'Original parent cleanup and locator deletion routed through ownership guard', 'All-frames pairBlend variable declaration and runtime finally guards']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'bh_aim_tools_v1_1', 'registration': {'module': 'bh_aim_tools_v1_1', 'class_name': 'BhAimTool'},
                   'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)],
                   'resources': [row['path'] for row in resources] + ['runtime.mel', 'catalog.json'],
                   'dependencies': ['Maya Python3/native MEL', 'Real Maya GUI for window', 'Existing maya_toolkit framework/core Undo'],
                   'source': '../bh_aimTools_v1.1/bh_aimTools.mel', 'change_summary': 'Complete locator attach/aim/bake suite and original UI with arguments, UUID ownership/preflight, guarded cleanup, explicit key deletion and runtime state recovery; original purchased resources privately preserved.',
                   'verification_limitations': ['Real Maya GUI and production rigs pending', 'Original axis heuristic, pairBlend routing and Euler filter behavior preserved; complex rigs require acceptance', 'Original keys-only rotation deletion can remove all rotation keys when explicitly requested', 'Maya-generated pairBlend nodes/attributes may remain to preserve original animation; report survivors'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'procedures': len(names), 'runtime_procedures': len(names) + 1, 'resources': len(files), 'top_level': catalog['runtime_audit']['top_level_lines']}))


if __name__ == '__main__':
    main()
