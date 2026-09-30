import ast
import difflib
import hashlib
import json
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction'
SOURCE = UNIT / 'maya-keyframe-reduction-master'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/keyframe_reduction'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    raw = []
    for source in sorted(SOURCE.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        relative = source.relative_to(SOURCE)
        target = PACKAGE / 'upstream' / relative
        if target.suffix == '.py':
            target = target.with_suffix('.py.original')  # Raw Python2 archival, not executable Python3.
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        raw.append({'path': target.relative_to(PACKAGE).as_posix(), 'source': relative.as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    for path, text in ((UNIT / '.gitattributes', 'maya-keyframe-reduction-master/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')):
        path.write_text(text, encoding='utf-8', newline='\n')
    converter = RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
    methods, diffs = {}, []
    src = SOURCE / 'scripts/keyframeReduction'
    for source in sorted(src.rglob('*.py')):
        original = source.read_text(encoding='utf-8-sig')
        converted = str(converter.refactor_string(original.rstrip() + '\n', str(source)))
        relative = source.relative_to(src)
        tree = ast.parse(converted)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods[relative.as_posix() + ':' + node.name] = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
        if relative.as_posix() in ('classes/keyframeReduction.py', 'utils.py'):
            tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == 'maya' and any(a.name == 'cmds' for a in n.names))]
            # Relative depth: native/classes -> candidate/proxy (3 dots), native -> candidate (2).
            import_node = ast.ImportFrom(module='proxy', names=[ast.alias(name='cmds')], level=3 if len(relative.parts) == 2 else 2)
            tree.body.insert(0, import_node)
        if relative.as_posix() == 'classes/keyframeReduction.py':
            tree.body.insert(0, ast.ImportFrom(module='runtime', names=[ast.alias(name='reduce_bridge')], level=3))
            for n in ast.walk(tree):
                if not isinstance(n, ast.FunctionDef):
                    continue
                if n.name == 'reduce':
                    n.decorator_list.append(ast.Name(id='reduce_bridge', ctx=ast.Load()))
                elif n.name == '_findTangentSplitAuto':
                    n.body.insert(0, ast.parse('if not angles or max(angles) <= 0 or max(angles) - min(angles) < 1e-10:\n    return []').body[0])
                elif n.name == '_removeKeys':
                    n.body = ast.parse('cmds.cutKey(self.path, index=(1, len(frames)-1), option="keys", clear=True)\ncmds.keyframe(self.path, edit=True, index=(0,), timeChange=start)').body
        if relative.as_posix() == 'utils.py':
            for n in tree.body:
                if isinstance(n, ast.FunctionDef) and n.name == 'validateAnimationCurve':
                    n.body = ast.parse('from ..runtime import suitable\nreturn suitable(animationCurve)').body
        if relative.as_posix() == 'ui.py':
            # Qt module import is lazy from execute(open_ui), never during API import.
            converted = ast.unparse(ast.fix_missing_locations(tree))
            start = converted.index('qtVersion =')
            end = converted.index('FONT = QFont()')
            converted = converted[:start] + 'try:\n    from PySide6.QtGui import *\n    from PySide6.QtCore import *\n    from PySide6.QtWidgets import *\n    import shiboken6 as shiboken\nexcept ImportError:\n    from PySide2.QtGui import *\n    from PySide2.QtCore import *\n    from PySide2.QtWidgets import *\n    import shiboken2 as shiboken\n\n' + converted[end:]
            converted = converted.replace('BOLT_FONT.setWeight(100)', 'BOLT_FONT.setBold(True)')
            tree = ast.parse(converted)
            for n in ast.walk(tree):
                if not isinstance(n, ast.FunctionDef):
                    continue
                if n.name == 'getIconPath':
                    n.body = ast.parse('from pathlib import Path\nreturn str(Path(__file__).resolve().parents[1] / "upstream/icons" / name)').body
                elif n.name == 'reduce' and len(n.args.args) == 1:
                    n.body = ast.parse('from ..runtime import run_ui\nreturn run_ui(self)').body
                elif n.name == 'show':
                    n.body.append(ast.Return(value=ast.Name(id='keyframeReduction', ctx=ast.Load())))
                elif n.name == 'removeCallback':
                    n.body.append(ast.parse('self._id = None').body[0])
        text = ast.unparse(ast.fix_missing_locations(tree))
        text = '\n'.join(s.rstrip() for s in text.splitlines()) + '\n'
        target = PACKAGE / 'native' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8', newline='\n')
        diffs.extend(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/' + relative.as_posix(), tofile='native/' + relative.as_posix()))
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'keyframe_reduction_changes.diff').write_text(''.join(diffs), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': raw, 'methods': methods, 'license': 'MIT Copyright (c) 2019 Robert Joosten; full LICENSE included; fitting port from Paper.js attributed.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/jop_retarget_anim_v09/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('jop_retarget_anim', 'keyframe_reduction').replace('JopRetargetTool', 'KeyframeReductionTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'keyframe_reduction', 'registration': {'module': 'keyframe_reduction', 'class_name': 'KeyframeReductionTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in raw] + ['catalog.json'], 'dependencies': ['Maya cmds/OpenMaya API1; Python3', 'Native Qt UI PySide6/shiboken6 or PySide2/shiboken2', 'BaseMayaTool/Undo'], 'source': '../maya-keyframe-reduction-master/scripts/keyframeReduction/classes/keyframeReduction.py', 'change_summary': 'Whole upstream archive/native Python3 library and full Qt UI, original Bezier least-squares/recursive fit and tangent splits, strict time-curve scope/dry/Undo/UI bridge; constant Auto split and near-first-key deletion fixed.', 'verification_limitations': ['Real Qt GUI/production sample interpolation quality pending', 'Error is 2D sample geometric fitting tolerance, not guaranteed final Maya subframe max channel error', 'Whole curve resampled floor(first)..ceil(last)+1 exclusive, may move fractional endpoints', 'Only writable local unshared TL/TA/TU curves without step tangents/time remapping accepted'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'resources': len(raw), 'classes': len(methods), 'methods': sum(len(x) for x in methods.values())}))


if __name__ == '__main__':
    main()
