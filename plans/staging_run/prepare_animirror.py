"""Extract the complete embedded MEL command without running the shelf installer."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit, masked_source

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/animirror_v2_0'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/animirror_v2_0'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    sources = [file for file in UNIT.iterdir() if file.is_file() and file.suffix.lower() in ('.mel', '.pdf')]
    for file in sources:
        target = PACKAGE / 'upstream' / file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
    installer = next(file for file in sources if file.suffix == '.mel')
    original = installer.read_text(encoding='utf-8-sig')
    commands = re.findall(r'-command\s+("(?:\\.|[^"\\])*")', original)
    if len(commands) != 1:
        raise ValueError('Expected exactly one embedded shelf command')
    extracted = json.loads(commands[0], strict=False)
    (PACKAGE / 'embedded_original.mel').write_text(extracted, encoding='utf-8')
    info = audit(PACKAGE / 'embedded_original.mel')
    names = re.findall(r'\bproc\s+(?:int\s+|float\s+|string\s+|vector\s+)?([A-Za-z_]\w*)\s*\(', extracted)
    if len(names) != 9:
        raise ValueError('Expected all nine original procedures, found: ' + str(names))
    globals_ = sorted(set(re.findall(r'global\s+(?:string|float|int)\s+\$([A-Za-z_]\w*)', extracted)) - {'gPlayBackSlider'})
    # Remove exactly the two audited top-level calls. Keep reset calls inside procs.
    top_calls = {int(row.split(':', 1)[0]) for row in info['top_level_lines'] if row.split(':', 1)[1].strip() in ('aniMirror_menu();', 'globals_variables();')}
    if len(top_calls) != 2:
        raise ValueError('Unexpected top-level executable code')
    adapted = ''.join('\n' if i + 1 in top_calls else line for i, line in enumerate(extracted.splitlines(True)))
    adapted = re.sub(r'(?<!global )\bproc\b', 'global proc', adapted)
    for name in names:
        adapted = re.sub(r'\b' + name + r'\b', 'mtbAV2_' + name, adapted)
    for name in globals_:
        adapted = re.sub(r'\$' + name + r'\b', '$mtbAV2_' + name, adapted)
    controls = ['AniMirror', 'TranslationsCheckbox', 'RotationsCheckbox', 'XAxisTransRadio', 'YAxisTransRadio', 'ZAxisTransRadio', 'XAxisRotCheckbox', 'YAxisRotCheckbox', 'ZAxisRotCheckbox', 'MirrorRealButton', 'UndoMirrorButton', 'BakeMirrorButton', 'MirrorBakeButton']
    for name in controls:
        adapted = re.sub(r'\b' + name + r'\b', 'mtbAV2_' + name, adapted)
    # Reset after baking used to increment the cleared counter to one, leaving gaps.
    adapted = adapted.replace('if ($withBake == 1) mtbAV2_fast_bake(1);    \n    $mtbAV2_ind = $mtbAV2_ind + 1;', '$mtbAV2_ind = $mtbAV2_ind + 1;\n    if ($withBake == 1) mtbAV2_fast_bake(1);')
    # Read options from explicit execution arguments rather than requiring widgets.
    # Leave change_options_mirror's native UI enable/disable queries untouched.
    masked = masked_source(adapted)
    definitions = []
    for match in re.finditer(r'global proc\s+(mtbAV2_\w+)\([^)]*\)', masked):
        opening = masked.index('{', match.end())
        depth, end = 1, opening + 1
        while depth:
            depth += (masked[end] == '{') - (masked[end] == '}')
            end += 1
        definitions.append((match.group(1), opening, end))
    controls_to_flags = {name: name for name in ('TranslationsCheckbox', 'RotationsCheckbox', 'XAxisRotCheckbox', 'YAxisRotCheckbox', 'ZAxisRotCheckbox', 'XAxisTransRadio', 'YAxisTransRadio', 'ZAxisTransRadio')}
    guard = '\n    python("import maya_toolkit.tools.animirror_v2_0.runtime as _av2; _av2.require_active()");\n'
    for name, opening, end in reversed(definitions):
        body = adapted[opening:end]
        if name in ('mtbAV2_mirror_animation', 'mtbAV2_transform_connect_operator', 'mtbAV2_rotate_connect_operator'):
            for control in controls_to_flags:
                command = 'radioButton -q -sl' if control.endswith('Radio') else 'checkBox -q -v'
                body = body.replace('`' + command + ' mtbAV2_' + control + '`', '`mtbAV2_read_flag "' + control + '"`')
            body = '{' + guard + body[1:]
        elif name == 'mtbAV2_delete_all_created':
            body = '{\n    python("import maya_toolkit.tools.animirror_v2_0.runtime as _av2; _av2.clear_owned()");\n    mtbAV2_globals_variables();\n}'
        elif name == 'mtbAV2_fast_bake':
            body = '{' + guard + body[1:]
        adapted = adapted[:opening] + body + adapted[end:]
    flags = list(controls_to_flags)
    adapted += '\nglobal proc int mtbAV2_read_flag(string $name)\n{\n    global int $mtbAV2_flags[];\n'
    for index, name in enumerate(flags):
        adapted += '    if ($name == "' + name + '") return $mtbAV2_flags[' + str(index) + '];\n'
    adapted += '    error "Unknown AniMirror option";\n    return 0;\n}\n'
    adapted += '''
global proc string[] mtbAV2_read_cache(string $name)
{
    global string $mtbAV2_centerJoint[];
    global string $mtbAV2_operatorTrans[];
    global string $mtbAV2_operatorRotate[];
    if ($name == "centerJoint") return $mtbAV2_centerJoint;
    if ($name == "operatorTrans") return $mtbAV2_operatorTrans;
    if ($name == "operatorRotate") return $mtbAV2_operatorRotate;
    error "Unknown AniMirror cache";
    string $empty[];
    return $empty;
}
'''
    # Preserve the original window and route its four scene buttons through run().
    callbacks = {'mtbAV2_mirror_animation(0);': 'mirror', 'mtbAV2_delete_all_created()': 'clear',
                 'mtbAV2_fast_bake(1)': 'bake', 'mtbAV2_mirror_animation(1)': 'mirror_bake'}
    for command, action in callbacks.items():
        code = "import maya_toolkit.tools.animirror_v2_0.ui as _av2ui; _av2ui.dispatch('" + action + "')"
        mel_callback = 'python(' + json.dumps(code) + ');'
        adapted = adapted.replace('-c ' + json.dumps(command), '-c ' + json.dumps(mel_callback))
    adapted = adapted.replace('-title "mtbAV2_AniMirror v2.00"', '-title "AniMirror v2.00 - Candidate"')
    adapted = '\n'.join(line.expandtabs(4).rstrip() for line in adapted.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(adapted, encoding='utf-8')
    current = audit(PACKAGE / 'runtime.mel')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'animirror_runtime_changes.diff').write_text(''.join(difflib.unified_diff(extracted.splitlines(True), adapted.splitlines(True), fromfile='embedded_original.mel', tofile='runtime.mel')), encoding='utf-8')
    catalog = {'tool_id': 'animirror_v2_0', 'entry': 'runtime.mel', 'raw_files': [{'path': 'upstream/' + file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in sources],
               'original_procedures': names, 'runtime_procedures': ['mtbAV2_' + name for name in names] + ['mtbAV2_read_flag', 'mtbAV2_read_cache'], 'globals': globals_, 'controls': controls, 'flag_order': flags,
               'original_audit': info, 'runtime_audit': current, 'guide': 'upstream/AniMirror- Mirror Animation Tool.pdf', 'guide_pages_reviewed': [1, 2],
               'source_license': 'No standalone redistribution license found; author contact in bundled guide; retain privately',
               'label_plane_mapping': {'XZ': 'mirrorXY', 'YX': 'mirrorYZ', 'ZY': 'mirrorXZ'},
               'status': 'candidate prepared; real GUI acceptance pending',
               'adapter_changes': ['Definition-only loader and preserved internal reset', 'Arguments replace business UI queries; original UI enable/disable retained', 'Nine original functions plus two typed option/cache readers', 'Original scene button callbacks use the standard API', 'UUID ownership metadata and safe clear replaces stale-name delete', 'Increment-before-bake ordering; Python records helpers before immediate bake']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [file for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for file in folder.rglob('*') if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc']
    promotion = {'tool_id': 'animirror_v2_0', 'registration': {'module': 'animirror_v2_0', 'class_name': 'AnimirrorV2Tool'},
                 'files': [{'source': file.relative_to(RC).as_posix(), 'target': file.relative_to(RC).as_posix()} for file in sorted(files)],
                 'resources': ['runtime.mel', 'embedded_original.mel', 'catalog.json'] + ['upstream/' + file.name for file in sources],
                 'dependencies': ['Maya Python 3', 'Autodesk lookdevKit for floatMath; explicit user loading', 'Native Maya GUI only for the original window', 'Existing maya_toolkit framework/core Undo'],
                 'source': '../AniMirror(Drag&Drop Install).mel', 'change_summary': 'Complete embedded nine-procedure mirror suite and original window; explicit argument options without business UI dependency, UUID and Undo-aware scene metadata, owned-constraint detachment to protect empty targets, source-origin/internal invocation guards, and cleanup/bake/runtime restoration protections.',
                 'verification_limitations': ['Real Maya GUI and production skeleton/AdvancedSkeleton acceptance pending', 'Original author guide supports Maya2016-2022; adapter Python3 and Maya2025 standalone do not verify that full range', 'Bake applies to all accumulated candidate targets including static channel deletion/filterCurve', 'Target locked/referenced/already driven channels are refused', 'Original rotation/local-space/center-transform behavior retained; realistic rigs and nondefault units need acceptance'],
                 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'raw_files': len(sources), 'procedures': names, 'runtime_has_no_installer': 'shelfButton' not in adapted, 'source_preserved': all(file.read_bytes() == (PACKAGE / 'upstream' / file.name).read_bytes() for file in sources)}))


if __name__ == '__main__':
    main()
