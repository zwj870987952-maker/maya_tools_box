"""Whole-source Python3 conversion with explicit marker/UI adaptations."""
import ast
import difflib
import hashlib
import json
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/maya_timeline_marker'
SOURCE = UNIT / 'maya-timeline-marker-master'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/timeline_marker'


def replace_functions(tree, replacements):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in replacements:
            n.body = ast.parse(replacements[n.name]).body
            n.decorator_list = n.decorator_list  # Preserve original property/wraps contracts.


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    raw = []
    for source in sorted(SOURCE.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        relative = source.relative_to(SOURCE)
        target = PACKAGE / 'upstream' / relative
        if target.suffix == '.py':
            target = target.with_suffix('.py.original')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        raw.append({'path': target.relative_to(PACKAGE).as_posix(), 'source': relative.as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, value in ((UNIT / '.gitattributes', 'maya-timeline-marker-master/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(value, encoding='utf-8', newline='\n')
    converter = RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
    methods, functions, diffs = {}, {}, []
    for source in sorted((SOURCE / 'scripts/timelineMarker').glob('*.py')):
        original = source.read_text(encoding='utf-8-sig')
        converted = str(converter.refactor_string(original.rstrip() + '\n', str(source)))
        tree = ast.parse(converted)
        functions[source.name] = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                methods[source.name + ':' + n.name] = [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
        if source.name == '__init__.py':
            tree.body = [n for n in tree.body if not isinstance(n, ast.ImportFrom) or n.module != 'ui']
            tree.body.extend(ast.parse('def install():\n    from ..runtime import run_api\n    return run_api(action="open_ui")\ndef uninstall():\n    from ..runtime import run_api\n    return run_api(action="close_ui")').body)
        elif source.name == 'decorators.py':
            tree.body = [n for n in tree.body if not isinstance(n, ast.ImportFrom) or n.module is not None]
            replace_functions(tree, {'getTimelineMarker': 'from ..runtime import CommandsAdapter\n@wraps(func)\ndef wrapper(*args, **kwargs):\n    return func(CommandsAdapter(), *args, **kwargs)\nreturn wrapper'})
        elif source.name == 'commands.py':
            replace_functions(tree, {
                'add': 'return timelineMarker.add(frame, color, comment)',
                'remove': 'from ..runtime import run_api\nreturn run_api(action="remove", frames=frames if isinstance(frames, list) else [frames])',
                'clear': 'return timelineMarker.clear()',
                'set': 'from ..runtime import run_api\nreturn run_api(action="set", frames=frames, colors=colors, comments=comments)'
            })
        elif source.name == 'hotkey.py':
            replace_functions(tree, {'hotkey': 'from ..runtime import widget\nif action not in ("add", "remove", "clear"):\n    raise ValueError("未知hotkey action")\nif widget() is None:\n    raise ValueError("先打开候选Timeline Marker")\nif action == "add":\n    return timelineMarker.addFromUI()\nif action == "remove":\n    return timelineMarker.removeFromUI()\nreturn timelineMarker.clear()'})
        elif source.name == 'utils.py':
            qt_start = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'qtVersion' for t in n.targets))
            qt_end = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.FunctionDef))
            qt = 'try:\n    from PySide6.QtGui import *\n    from PySide6.QtCore import *\n    from PySide6.QtWidgets import *\n    import shiboken6 as shiboken\nexcept ImportError:\n    from PySide2.QtGui import *\n    from PySide2.QtCore import *\n    from PySide2.QtWidgets import *\n    import shiboken2 as shiboken\n'
            tree.body[qt_start:qt_end] = ast.parse(qt).body
            replace_functions(tree, {'getTimelineRange': 'r = cmds.timeControl(getMayaTimeline(), query=True, ra=True)\nstart, end = int(r[0]), int(r[1])\nif end < start or end - start > 20000:\n    raise ValueError("timeline selection范围超限")\nreturn list(range(start, end))'})
        elif source.name == 'ui.py':
            tree.body.insert(0, ast.ImportFrom(module=None, names=[ast.alias(name='gui_bridge', asname='bridge')], level=2))
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TimelineMarker')
            replace_functions(cls, {
                'readFromCurrentScene': 'return bridge.read(self)',
                'saveToCurrentScene': 'return bridge.write(self, action="set", frames=self.frames, colors=self.colors, comments=self.comments)',
                'addFromUI': 'frames = utils.getTimelineRange()\nif not frames:\n    return\nresult = bridge.write(self, action="add", frames=frames, color=list(self.menu.colorA.property("rgb")), comment=self.menu.commentL.text())\nself.menu.commentL.setText("")\nreturn result',
                'add': 'return bridge.write(self, action="add", frames=[frame], color=color, comment=comment)',
                'removeFromUI': 'frames = utils.getTimelineRange()\nif frames:\n    return bridge.write(self, action="remove", frames=frames)',
                'remove': 'return bridge.write(self, action="remove", frames=[frame])',
                'clear': 'return bridge.write(self, action="clear")',
                'releaseCommand': 'return bridge.release(self)',
                'addCallbacks': 'return bridge.add_callbacks(self)',
                'removeCallbacks': 'return bridge.remove_callbacks(self)',
                'update': 'return utils.QWidget.update(self)',
                'deleteLater': 'self.removeCallbacks()\nself.menu.deleteLater()\nreturn utils.QWidget.deleteLater(self)'
            })
            for n in cls.body:
                if not isinstance(n, ast.FunctionDef):
                    continue
                if n.name == '__init__':
                    for node in ast.walk(n):
                        if isinstance(node, ast.Constant) and node.value == 'timelineMarker':
                            node.value = 'mtkTimelineMarkerCandidate'
                    n.body[-2:] = ast.parse('try:\n    self.readFromCurrentScene()\n    self.addCallbacks()\nexcept Exception:\n    self.removeCallbacks()\n    self.menu.deleteLater()\n    raise').body
                elif n.name == 'event':
                    n.body.insert(0, ast.parse('if self.total is None or not self.step or self.start is None:\n    return utils.QWidget.event(self, event)').body[0])
                    for node in ast.walk(n):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'showText':
                            node.args[1] = ast.BoolOp(op=ast.Or(), values=[node.args[1], ast.Constant(value='')])
                elif n.name == 'draw':
                    for node in ast.walk(n):
                        if isinstance(node, ast.Attribute) and node.attr == 'setWidth':
                            node.attr = 'setWidthF'
                elif n.name == 'pressCommand':
                    n.body.insert(0, ast.parse('self._range = None').body[0])
            menu = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TimelineMarkerMenu')
            replace_functions(menu, {'deleteLater': 'return bridge.delete_menu(self)'})
            replace_functions(tree, {'install': 'import sys\nreturn bridge.install(sys.modules[__name__])'})
            tree.body.extend(ast.parse('def uninstall():\n    import sys\n    return bridge.uninstall(sys.modules[__name__])').body)
        text = '# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.\n' + ast.unparse(ast.fix_missing_locations(tree)) + '\n'
        target = PACKAGE / 'native' / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('\n'.join(s.rstrip() for s in text.splitlines()) + '\n', encoding='utf-8', newline='\n')
        diffs.extend(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/' + source.name, tofile='native/' + source.name))
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'timeline_marker_changes.diff').write_text(''.join(diffs), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': raw, 'methods': methods, 'functions': functions, 'license': 'GPL-3.0-or-later Copyright(C) 2015 Robert Joosten. Original complete GPLv3 LICENSE retained.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('keyframe_reduction', 'timeline_marker').replace('KeyframeReductionTool', 'TimelineMarkerTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'timeline_marker', 'registration': {'module': 'timeline_marker', 'class_name': 'TimelineMarkerTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in raw] + ['catalog.json'], 'dependencies': ['Maya cmds/OpenMaya API1+API2 and Python3', 'PySide6/shiboken6 or PySide2/shiboken2 for genuine GUI', 'Privately loaded undo_plugin command; no autoload or userSetup install', 'BaseMayaTool/Undo'], 'source': '../maya-timeline-marker-master/scripts/timelineMarker/ui.py', 'change_summary': 'Full upstream archive/functions/timeline overlay/menu/color/comment/range movement; Python3 lazy Qt, same fileInfo format via undoable private command, strict schema/read-only load/dry, atomic collision-safe remap and callback ownership cleanup.', 'verification_limitations': ['Real native timeline GUI/Qt event dispatch and sound scrubbing pending', 'UI/session/plugin callbacks are not scene Undo; plugin remains loaded while command Undo history exists', 'Integer-only markers; remap truncates toward zero and later source wins collisions', 'Malformed existing metadata refused; no automatic repair/overwrite', 'Existing original timelineMarker widget must be closed first; Python callable timeline hooks refused'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'resources': len(raw), 'classes': len(methods), 'methods': sum(len(v) for v in methods.values()), 'functions': sum(len(v) for v in functions.values())}))


if __name__ == '__main__':
    main()
