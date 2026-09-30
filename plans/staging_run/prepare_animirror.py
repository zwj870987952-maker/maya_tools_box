"""Extract the complete embedded MEL command without running the shelf installer."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from audit_mel_suite import audit

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/animirror_v2_0'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/animirror_v2_0'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    sources = [file for file in UNIT.iterdir() if file.is_file()]
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
    adapted = re.sub(r'^\s*(?:aniMirror_menu|globals_variables)\s*\(\s*\)\s*;\s*$', '', extracted, flags=re.MULTILINE)
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
    adapted = '\n'.join(line.expandtabs(4).rstrip() for line in adapted.splitlines()).rstrip() + '\n'
    (PACKAGE / 'runtime.mel').write_text(adapted, encoding='utf-8')
    current = audit(PACKAGE / 'runtime.mel')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'animirror_runtime_changes.diff').write_text(''.join(difflib.unified_diff(extracted.splitlines(True), adapted.splitlines(True), fromfile='embedded_original.mel', tofile='runtime.mel')), encoding='utf-8')
    catalog = {'tool_id': 'animirror_v2_0', 'entry': 'runtime.mel', 'raw_files': [{'path': 'upstream/' + file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in sources],
               'original_procedures': names, 'runtime_procedures': ['mtbAV2_' + name for name in names], 'globals': globals_, 'controls': controls,
               'original_audit': info, 'runtime_audit': current, 'guide': 'upstream/AniMirror- Mirror Animation Tool.pdf', 'guide_pages_reviewed': [1, 2],
               'source_license': 'No standalone redistribution license found; author contact in bundled guide; retain privately',
               'label_plane_mapping': {'XZ': 'mirrorXY', 'YX': 'mirrorYZ', 'ZY': 'mirrorXZ'},
               'status': 'working; API, safety guards, tests and acceptance not yet complete'}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'raw_files': len(sources), 'procedures': names, 'runtime_has_no_installer': 'shelfButton' not in adapted, 'source_preserved': all(file.read_bytes() == (PACKAGE / 'upstream' / file.name).read_bytes() for file in sources)}))


if __name__ == '__main__':
    main()
