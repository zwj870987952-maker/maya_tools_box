"""Preserve source and reuse reviewed layer lookup without staging path dependencies."""
import ast
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/anim_layer_keyframe_bookmark'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/anim_layer_keyframe_bookmark'


def main():
    archive = PACKAGE / 'upstream'
    archive.mkdir(parents=True, exist_ok=True)
    for name in ('anim_layer_keyframe_bookmark.py', 'README.md'):
        shutil.copyfile(UNIT / name, archive / name)
    source = (UNIT / 'anim_layer_keyframe_bookmark.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    lines = source.splitlines()
    palette = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'COLOR_PALETTES' for t in n.targets))
    ui = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    (PACKAGE / 'palettes.py').write_text('\n'.join(lines[palette.lineno-1:palette.end_lineno]) + '\n', encoding='utf-8')
    native = 'import maya.cmds as cmds\nfrom .palettes import COLOR_PALETTES\nfrom .layer_queries import get_scene_anim_layers, get_active_anim_layer\n\n'
    native += '\n'.join(lines[ui.lineno-1:ui.end_lineno]) + '\n'
    (PACKAGE / 'native_ui.py').write_text('\n'.join(line.rstrip() for line in native.splitlines()) + '\n', encoding='utf-8')
    # This is an independent runtime module, not an import from another release_candidate.
    runner = ROOT / 'tools_staging_pool/01_animation/anim_layer_key_runner/release_candidate/maya_toolkit/tools/anim_layer_key_runner/operations.py'
    lookup = runner.read_text(encoding='utf-8').split('\ndef run_frames(', 1)[0]
    lookup = lookup.replace('import sys\n', '').replace('import maya.mel as mel\n', '')
    # Original bookmark generator merges equal rounded times only, not the runner's 0.001 tolerance.
    lookup = lookup.replace("if not unique or abs(time - unique[-1]) > 0.001:", "if not unique or time != unique[-1]:")
    (PACKAGE / 'layer_queries.py').write_text(lookup.rstrip() + '\n', encoding='utf-8')
    files = sorted(p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests')
                   for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    description = {
        'tool_id': 'anim_layer_keyframe_bookmark',
        'registration': {'module': 'anim_layer_keyframe_bookmark', 'class_name': 'AnimLayerKeyframeBookmarkTool'},
        'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in files],
        'resources': ['upstream/anim_layer_keyframe_bookmark.py', 'upstream/README.md', 'palettes.py'],
        'dependencies': ['maya.cmds', 'timeSliderBookmark plugin explicitly loaded', 'existing maya_toolkit framework/core', 'Python 3'],
        'source': '../anim_layer_keyframe_bookmark.py',
        'change_summary': 'Retain palettes/native controls/original archive; exact layer-frame lookup, structured generate/clear/inspect API, read-only creation/deletion preview, explicit plugin setup, deletion guards, Undo and partial-failure evidence.',
        'verification_limitations': ['Actual Maya GUI/bookmark display pending', 'Other Maya versions/Python 2 unverified', 'generate clear_existing and clear action delete ALL scene bookmarks', 'plugin writeRequires setting is not restored by Maya Undo'],
        'acceptance_required': True,
    }
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Source/UI/palettes and independent layer lookup prepared')


if __name__ == '__main__':
    main()
