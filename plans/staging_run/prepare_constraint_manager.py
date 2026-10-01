"""Preserve both complete prototypes and every original UI method; no auto-run."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'tools_staging_pool/02_rigging_hierarchy/constraint_manager_v6'
RC = UNIT/'release_candidate'
PKG = RC/'maya_toolkit/tools/constraint_manager_v6'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [re.sub(r'^[ \t]+', lambda m: m[0].expandtabs(4), x.rstrip()) for x in text.rstrip().splitlines()]
    path.write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')


def main():
    files, declarations = [], {}
    for source in sorted(UNIT.glob('*.py')):
        target = PKG/'vendor'/(source.name+'.original')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        files.append({'path': source.name, 'archive': target.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size})
        text = source.read_text(encoding='utf-8-sig')
        tree = ast.parse(text)
        lines = text.splitlines(keepends=True)
        declarations[source.name] = {'functions': [n.name for n in tree.body if isinstance(n, ast.FunctionDef)], 'classes': {n.name: [m.name for m in n.body if isinstance(m, ast.FunctionDef)] for n in tree.body if isinstance(n, ast.ClassDef)}}
        chunks = [''.join(lines[n.lineno-1:n.end_lineno]) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign))]
        if 'ConstraintTool' in declarations[source.name]['classes']:
            imports = '''import maya.cmds as cmds
import maya.mel as mel
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import re
'''
            write(PKG/'native_ui.py', imports+'\n\n'+'\n\n'.join(chunks))
        else:
            write(PKG/'native_rebuild.py', 'import maya.cmds as cmds\nimport os\nimport json\n\n'+'\n\n'.join(chunks))
    write(PKG/'catalog.json', json.dumps({'files': files, 'declarations': declarations, 'source_modified': False}, ensure_ascii=False, indent=2))
    write(RC/'.gitattributes', '* -text')
    write(UNIT/'.gitattributes', '*.py -text')
    launch = (ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'constraint_manager_v6').replace('RootMotionBakeTool', 'ConstraintManagerTool')
    write(RC/'launch_candidate.py', launch+'\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC/'maya_toolkit', RC/'docs', RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'constraint_manager_v6', 'registration': {'module': 'constraint_manager_v6', 'class_name': 'ConstraintManagerTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in files], 'dependencies': ['Maya cmds/MEL, PySide6/shiboken6 or PySide2/shiboken2 for complete native UI', 'Axis/rest native Maya menu procedures require interactive Maya; batch explicitly refused'], 'acceptance_required': True, 'change_summary': 'Both complete prototypes and every native UI method preserved with explicit startup and Qt6/Qt5 imports. Typed API/full native UI bridge, actual target aliases/order/UUIDs, explicit key values, output-edge disconnect/restore preserving animation/offsets, true inverse constraints without cycles/overwriting drivers, full duplicate-based rebuild, scene list JSON and protected explicit snapshot files; original unsafe auto-run/file fallback never invoked.', 'verification_limitations': ['Real Maya GUI, every native button/context menu/color/list/tooltip and production namespaces/rigs not_run', 'Native Maya axis/rest menu dialogs and nonstandard constraint types require separate real GUI acceptance', 'Undo restores scene changes but not Python session snapshots or external snapshot files; current scene UUID/connection state is revalidated', 'External JSON copies are not scene-Undoable; partial errors require inspection/Undo, not automatic rollback', 'Reverse rejects existing target drivers/locked channels, descendants and incompatible graphs instead of silently replacing animation']}
    write(RC/'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'files': len(files), 'declarations': declarations}, ensure_ascii=True))


if __name__ == '__main__':
    main()
