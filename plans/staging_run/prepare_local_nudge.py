import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/bh_local_nudge'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/bh_local_nudge'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    original_files = sorted((UNIT / 'bh_localNudge').iterdir())
    for file in original_files:
        target = PACKAGE / 'upstream' / file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    entry = UNIT / 'bh_localNudge/bh_localNudge.mel'
    original = entry.read_text(encoding='utf-8-sig')
    info = audit(entry)
    top = {int(row.split(':', 1)[0]) for row in info['top_level_lines']}
    if len(top) != 1 or 'bh_localNudge;' not in info['top_level_lines'][0]:
        raise ValueError('Unexpected top-level code')
    adapted = ''.join('\n' if i + 1 in top else line for i, line in enumerate(original.splitlines(True)))
    names = [row['name'] for row in info['procedures']]
    for name in names + ['localNudgeUI', 'mainCol', 'NudgeVal', 'RotVal', 'nudgePosY', 'nudgeNegY', 'nudgeNegX', 'nudgePosX', 'nudgePosZ', 'nudgeNegZ', 'nudgeRotX', 'nudgeRotNegX', 'nudgeRotY', 'nudgeRotNegY', 'nudgeRotZ', 'nudgeRotNegZ']:
        adapted = re.sub(r'\b' + name + r'\b', 'mtbLN_' + name, adapted)
    for function, channel in (('bh_localNudgeIt', 'translate'), ('bh_localNudgeRotIt', 'rotate')):
        for axis in 'XYZ':
            for sign in ('positive', 'negative'):
                old = 'mtbLN_' + function + '(\\"' + axis + '\\",\\"' + sign + '\\")'
                callback = 'python(' + json.dumps("import maya_toolkit.tools.bh_local_nudge.ui as _u; _u.dispatch('" + channel + "','" + axis + "','" + sign + "')") + ');'
                adapted = adapted.replace('"' + old + '"', json.dumps(callback))
    guard = '\npython("import maya_toolkit.tools.bh_local_nudge.runtime as _r; _r.require_active()");\nglobal float $mtbLN_amount;\nglobal int $mtbLN_mods;\n'
    for name, widget in (('bh_localNudgeIt', 'NudgeVal'), ('bh_localNudgeRotIt', 'RotVal')):
        signature = 'global proc mtbLN_' + name + '(string $direction, string $plusMinus)\n{'
        if signature not in adapted:
            raise ValueError('Missing business function')
        start = adapted.index(signature)
        end = adapted.find('global proc', start + len(signature))
        if end < 0:
            end = len(adapted)
        body = adapted[start:end].replace(signature, signature + guard)
        body = body.replace('int $mods = `getModifiers`;', 'int $mods = $mtbLN_mods;')
        body = body.replace('`floatSliderGrp -q -v mtbLN_' + widget + '`', '$mtbLN_amount')
        adapted = adapted[:start] + body + adapted[end:]
    adapted = '\n'.join(line.expandtabs(4).rstrip() for line in adapted.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'bh_local_nudge_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/bh_localNudge.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'bh_local_nudge', 'original_procedures': names, 'runtime_procedures': ['mtbLN_' + name for name in names],
               'raw_files': [{'path': 'upstream/' + file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in original_files],
               'runtime_audit': audit(PACKAGE / 'runtime.mel'), 'source_license': 'Purchased tool; no independent redistribution license found; private preparation',
               'behavior': ['Local attribute arithmetic, not world/object-space vector translation', 'CTRL halves, ALT quarters; both reduce to one eighth', 'Right is negative X, Left positive X', 'No explicit setKeyframe; animation/key/autokey behavior needs GUI acceptance'],
               'changes': ['Definition-only private names', 'Explicit amount and modifier flags without business widgets', 'Original twelve UI buttons use standard API', 'Read-only preflight and grouped Undo']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    description = {'tool_id': 'bh_local_nudge', 'registration': {'module': 'bh_local_nudge', 'class_name': 'LocalNudgeTool'},
                   'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)],
                   'resources': [row['path'] for row in catalog['raw_files']] + ['runtime.mel', 'catalog.json'],
                   'dependencies': ['Maya Python3/native MEL', 'Actual Maya GUI for original window', 'Existing maya_toolkit framework/core Undo'],
                   'source': '../bh_localNudge/bh_localNudge.mel', 'change_summary': 'Complete original five-procedure native UI and local translation/rotation arithmetic with explicit arguments/modifiers, standard ToolResult/Undo and read-only channel preflight.',
                   'verification_limitations': ['Native GUI and actual modifier key state pending', 'Animation/autokey/layer behavior needs actual Maya acceptance', 'Uses current Maya linear/angular units; original Degrees print label is not a unit conversion'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'procedures': len(names), 'resources': len(original_files), 'top_level': catalog['runtime_audit']['top_level_lines']}))


if __name__ == '__main__':
    main()
