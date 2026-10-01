"""Preserve both complete original timeline interfaces and prepare promotion."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/timeline_enhanced'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/timeline_enhanced'


def main():
    rows, methods = [], {}
    for src in sorted(UNIT.iterdir()):
        if not src.is_file() or src.name.startswith('.'):
            continue
        dst = PKG / 'upstream' / (src.name + ('.original' if src.suffix == '.py' else ''))
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        rows.append({'path': src.name, 'archive': dst.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
        if src.suffix != '.py':
            continue
        text = src.read_text(encoding='utf-8')
        tree = ast.parse(text)
        methods[src.name] = [n.name for cls in tree.body if isinstance(cls, ast.ClassDef) for n in cls.body if isinstance(n, ast.FunctionDef)]
        # Drop auto-running __main__ guard, retain all declarations/layouts.
        guard = next(n for n in tree.body if isinstance(n, ast.If))
        text = '\n'.join(text.splitlines()[:guard.lineno - 1]) + '\n'
        text = text.replace('minValue=1,', 'minValue=-10000000,')
        text = text.replace('"blockPropertiesWindow"', 'self.window_name + "_properties"')
        text = text.replace('cmds.columnLayout(adjustableColumn=True, margin=10)', 'cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 10))')
        text = text.replace('cmds.rowLayout(numberOfColumns=8,', 'cmds.rowColumnLayout(numberOfColumns=8,')
        text = text.replace('columnWidth8=(50, 50, 50, 50, 50, 50, 50, 50)', 'columnWidth=[(i + 1, 50) for i in range(8)]')
        # This source row contains nine controls, not eight.
        text = text.replace('cmds.rowColumnLayout(numberOfColumns=8,\n                      columnWidth8=(60, 60, 60, 60, 80, 80, 80, 100)', 'cmds.rowColumnLayout(numberOfColumns=9,\n                      columnWidth=[(i + 1, w) for i, w in enumerate((60, 60, 60, 60, 80, 80, 80, 100, 100))]')
        old = "self.blocks[frame_num]['label'] = new_label\n            self.blocks[frame_num]['name'] = new_name\n            self.blocks[frame_num]['color'] = new_color"
        text = text.replace(old, 'self.apply_properties(frame_num, new_label, new_name, new_color)')
        text = text.replace('maxValue=500,', 'maxValue=1000,')
        text = '# Complete legacy UI declarations; modified candidate layout fixes 2026-10-01.\n' + text
        text = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
        ast.parse(text)
        name = 'native_enhanced.py' if 'enhanced' in src.name else 'native_basic.py'
        (PKG / name).write_text(text, encoding='utf-8', newline='\n')
    (PKG / 'catalog.json').write_text(json.dumps({'files': rows, 'original_methods': methods, 'license': 'User prototype scripts, no separate license supplied'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (UNIT / '.gitattributes').write_text('*.py -text\n*.md -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'timeline_enhanced').replace('RootMotionBakeTool', 'TimelineEnhancedTool')
    (RC / 'launch_candidate.py').write_text(launch, encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'timeline_enhanced', 'registration': {'module': 'timeline_enhanced', 'class_name': 'TimelineEnhancedTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in rows], 'dependencies': ['Maya cmds; Qt5/Qt6 for window-local shortcuts, no external dependencies'], 'acceptance_required': True, 'change_summary': 'Both complete basic/enhanced source interfaces and all methods preserved; full pure marker-document API, all block types/edit/copy/paste/selection/drag/config/playback. Safe config schema/read-only previews, explicit file replace backups, correct parent/layout/negative frames, working modes/fit/reset/keyboard shortcuts and local document Undo/Redo. No scene animation-key editing.', 'verification_limitations': ['Real Maya basic/enhanced GUI/shortcut/playback acceptance not_run', 'Planning blocks are memory/JSON, not Maya animation keys', 'Local document Undo differs from Maya scene Undo; filesystem/time/playback are separately described', 'Original example/hotkey setup file mentioned in README is missing and not fabricated; window-local shortcuts supplied', 'View fit caps at 8 pixels/frame and large documents remain scrollable']}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'files': len(rows), 'methods': {k: len(v) for k, v in methods.items()}}))


if __name__ == '__main__':
    main()
