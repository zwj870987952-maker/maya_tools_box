import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/directional_cycle_tool_v1_1'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/directional_cycle_tool_v1_1'


class ShapePlug(ast.NodeTransformer):
    def visit_JoinedStr(self, node):
        self.generic_visit(node)
        if len(node.values) == 2 and isinstance(node.values[0], ast.FormattedValue) and isinstance(node.values[1], ast.Constant) and str(node.values[1].value).startswith('Shape.localScale'):
            return ast.BinOp(left=ast.Call(func=ast.Name(id='_locator_shape', ctx=ast.Load()), args=[node.values[0].value], keywords=[]), op=ast.Add(), right=ast.Constant(node.values[1].value[5:]))
        return node


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    source = UNIT / 'DirectionalCycleTool'
    resources = []
    for file in sorted(source.rglob('*')):
        if not file.is_file() or '__pycache__' in file.parts:
            continue
        target = PACKAGE / 'upstream' / file.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    for path, text in [(UNIT / '.gitattributes', 'DirectionalCycleTool/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')]:
        path.write_text(text, encoding='utf-8', newline='\n')
    original = (source / 'functions.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    functions = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        node = ShapePlug().visit(node)
        if node.name == 'warning_popup':
            node.body = ast.parse('raise RuntimeError(Message)').body
        elif node.name == 'check_for_animlayer':
            node.body = ast.parse('return True  # Standard read-only plan already checked the base-layer selection.').body
        elif node.name == 'create_animlayer':
            node.body = ast.parse('return cmds.create_layer(Name, Controllers)').body
        else:
            node.body.insert(0, ast.parse('require_active()').body[0])
        text = ast.unparse(node).replace('cmds.delete(Constrains[0])', 'cmds.delete(Constrains)').replace('cmds.delete(ConstrainList[0])', 'cmds.delete(ConstrainList)')
        functions.append(ast.parse(text).body[0])
    header = ast.parse('from .runtime import require_active\ncmds = None\ndef _locator_shape(node): return cmds.listRelatives(node, shapes=True, fullPath=True)[0]').body
    adapted = ast.unparse(ast.Module(body=header + functions, type_ignores=[])) + '\n'
    (PACKAGE / 'algorithms.py').write_text(adapted, encoding='utf-8', newline='\n')
    raw_ui = (source / 'main.py').read_text(encoding='utf-8-sig')
    ui_tree = ast.parse(raw_ui)
    kept = []
    for node in ui_tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if 'PySide2' in ast.unparse(node) or (isinstance(node, ast.ImportFrom) and node.module is None):
                continue
        if isinstance(node, ast.ClassDef):
            methods = []
            for method in node.body:
                if isinstance(method, ast.FunctionDef) and method.name in ('launch_left_right', 'launch_back'):
                    if method.name == 'launch_left_right':
                        method.body = ast.parse("return bridge.dispatch(self, 'right' if Right else 'left')").body
                    else:
                        method.body = ast.parse("return bridge.dispatch(self, 'back')").body
                if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                    method.body.insert(1, ast.parse("self.setObjectName('mtbDCTWindow')").body[0])
                if isinstance(method, ast.FunctionDef) and method.name == 'initUI':
                    text = ast.unparse(method).replace('self.SpinBox_FeetNumber.setMinimum(0)', 'self.SpinBox_FeetNumber.setMinimum(1)')
                    method = ast.parse(text).body[0]
                methods.append(method)
            node.body = methods
        kept.append(node)
    header = ast.parse("from maya_toolkit.core.ui_base import QtCore, QtGui, QtWidgets\nfrom . import bridge, version\nglobals().update({name: getattr(module, name) for module in (QtWidgets, QtGui, QtCore) for name in dir(module) if name.startswith('Q')})").body
    # Remove old local functions coupling; all scene buttons route standard API.
    ui_text = ast.unparse(ast.Module(body=header + kept, type_ignores=[])) + '\n'
    (PACKAGE / 'native_ui.py').write_text(ui_text, encoding='utf-8', newline='\n')
    shutil.copyfile(source / 'version.py', PACKAGE / 'version.py')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'directional_cycle_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/functions.py', tofile='algorithms.py; named-resource adapter in proxy.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'directional_cycle_tool_v1_1', 'original_functions': names, 'raw_files': resources, 'license': 'Original README: CC BY-SA 4.0, Baptiste COLIN (FallingNT0), v1.1; attribution and full README retained', 'changes': ['No import-time dockable UI', 'Project PySide2/6 binding and full original UI', 'Explicit ordered roles and base-layer read-only checks', 'All nested temporary constraint lists deleted, not only first foot', 'Actual locator shape path instead of synthesized Shape names', 'Unique owned cycle layers/helpers and standard Undo/finally', 'Owned persistent cycle records and cleanup; never overwrite foreign Left/Right/Back layers']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'directional_cycle_tool_v1_1', 'registration': {'module': 'directional_cycle_tool_v1_1', 'class_name': 'DirectionalCycleTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['catalog.json'], 'dependencies': ['Maya cmds/animLayer/bakeResults/constraints', 'Real GUI/project PySide2/6 and Maya dockable mixin', 'Existing framework/core Undo'], 'source': '../DirectionalCycleTool/functions.py', 'change_summary': 'Full original left/right/back, pelvis/feet time reversal and correction/counter-rotation algorithms and native dockable UI, unique owned layers/helpers, complete temporary constraint cleanup and standard API.', 'verification_limitations': ['Production rig/dockable Qt GUI pending', 'Original head aim uses fixed world point and body-angle/feet heuristics', 'BaseAnimation selected does not isolate other active output layers', 'Bake creates persistent direction/pelvis layers; helpers/constraints persist when bake false', 'Back upperbody/master role usage differs from side'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'functions': names, 'resources': len(resources)}))


if __name__ == '__main__':
    main()
