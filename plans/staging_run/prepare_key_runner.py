"""Copy every original file and extract native controls without executing them."""
import ast
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/anim_layer_key_runner'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/anim_layer_key_runner'


def main():
    archive = PACKAGE / 'upstream'
    archive.mkdir(parents=True, exist_ok=True)
    for name in ('anim_layer_key_runner.py', 'anim_layer_key_runner.mel', 'README.md'):
        shutil.copyfile(UNIT / name, archive / name)
    source = (UNIT / 'anim_layer_key_runner.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    ui = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    presets = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PRESET_COMMANDS' for t in n.targets))
    lines = source.splitlines()
    native = 'import maya.cmds as cmds\nimport maya.mel as mel\nfrom .operations import get_scene_anim_layers\n\n'
    native += '\n'.join(lines[presets.lineno-1:presets.end_lineno]) + '\n\n'
    native += '\n'.join(lines[ui.lineno-1:ui.end_lineno]) + '\n'
    native = '\n'.join(line.rstrip() for line in native.splitlines()) + '\n'
    (PACKAGE / 'native_ui.py').write_text(native, encoding='utf-8')
    files = sorted(p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests')
                   for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    description = {
        'tool_id': 'anim_layer_key_runner',
        'registration': {'module': 'anim_layer_key_runner', 'class_name': 'AnimLayerKeyRunnerTool'},
        'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in files],
        'resources': ['upstream/anim_layer_key_runner.py', 'upstream/anim_layer_key_runner.mel', 'upstream/README.md', 'launch_ui.mel'],
        'dependencies': ['maya.cmds/maya.mel', 'existing maya_toolkit framework/core', 'Python 3', 'Advanced Skeleton only for asAutoSwitchFKIK preset'],
        'source': '../anim_layer_key_runner.py',
        'change_summary': 'Layer-specific frame scheduling with normalized curve results and no cross-layer fallback; isolated preflight never executes commands; preserve MEL/Python engines/presets, restore time/selection, report per-frame errors, complete source archives/native UI/promotion package.',
        'verification_limitations': ['Actual Maya GUI and Advanced Skeleton preset pending', 'Custom commands execute with normal Maya process privileges and may have effects outside Undo', 'Other Maya versions/Python 2 unverified'],
        'acceptance_required': True,
    }
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Complete Python/MEL source archive and native UI prepared')


if __name__ == '__main__':
    main()
