import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/copy_animation'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/copy_animation'
ALGORITHMS = ['_attribute_has_key', '_channel_has_key', '_match_and_key', 'apply_channel_modes', '_numeric_attributes', 'copy_numeric_values']


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    source = UNIT / '复制动画_修复优化版.py'
    original = source.read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    (PACKAGE / 'upstream').mkdir(exist_ok=True)
    shutil.copyfile(source, PACKAGE / 'upstream' / source.name)
    for path, text in [(UNIT / '.gitattributes', '*.py -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')]:
        path.write_text(text, encoding='utf-8', newline='\n')
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AutoAlignUI')
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    worker = ast.ClassDef(name='ChannelAlgorithms', bases=[], keywords=[], body=[methods[name] for name in ALGORITHMS], decorator_list=[])
    for method in worker.body:
        method.body.insert(0, ast.parse('require_active()').body[0])
    headers = ast.parse("from maya import cmds\nfrom .runtime import require_active, record_warning\n_warning=record_warning\nTRANSFORM_CHANNELS=('translate','rotate','scale')\nCHANNEL_LABELS={'translate':'位移','rotate':'旋转','scale':'缩放','other':'其他属性'}\ndef _object_exists(node): return bool(node and cmds.objExists(node))").body
    ast.fix_missing_locations(worker)
    (PACKAGE / 'algorithms.py').write_text(ast.unparse(ast.Module(body=headers + [worker], type_ignores=[])) + '\n', encoding='utf-8', newline='\n')
    # Native list/delegate/menus/layout remains; scene and file buttons use one standard API.
    tree = ast.parse(original)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AutoAlignUI')
    wrappers = ast.parse('''
def create_locators_for_all(self):
    return bridge.dispatch(self, 'create_locators')
def execute_alignment(self):
    return bridge.dispatch(self, 'execute')
def save_data(self):
    return bridge.save(self)
def load_data(self):
    return bridge.load(self)
def cleanup_candidates(self):
    return bridge.dispatch(self, 'cleanup')
''').body
    replacements = {n.name: n for n in wrappers}
    remove = set(ALGORITHMS) | {'_ensure_locator_group', '_delete_item_locators', '_create_locators_for_item', '_delete_item_constraints', '_create_channel_constraints'}
    body = []
    for method in cls.body:
        if method.name in remove:
            continue
        if method.name in replacements:
            method = replacements.pop(method.name)
        if method.name == 'edit_list':
            # clear() destroys native QListWidgetItems; never reuse dead C++ wrappers.
            text = ast.unparse(method).replace('old_items = self._items()', 'old_modes = [dict(item.modes) for item in self._items()]')
            start = text.index('        if index < len(old_items):')
            end = text.index('        self.record_list.addItem(item)', start)
            text = text[:start] + '        item = CustomListWidgetItem(line)\n        if index < len(old_modes):\n            item.modes = old_modes[index]\n' + text[end:]
            method = ast.parse(text).body[0]
        if method.name == '_build_ui':
            method.body.extend(ast.parse("self.cleanup_button = QtWidgets.QPushButton('清理候选辅助节点')\nmain_layout.addWidget(self.cleanup_button)").body)
        if method.name == '_connect_signals':
            method.body.append(ast.parse('self.cleanup_button.clicked.connect(self.cleanup_candidates)').body[0])
        body.append(method)
    cls.body = body + list(replacements.values())
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'UndoChunk':
            continue
        if isinstance(node, ast.FunctionDef) and node.name == '_set_members':
            continue
        if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test):
            continue
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('WINDOW_OBJECT_NAME', 'LOCATOR_GROUP_NAME', 'SOURCE_SET_NAME', 'TARGET_SET_NAME', 'LOCATOR_SET_NAME', 'CONSTRAINT_SET_NAME'):
                    node.value = ast.Constant('mtbCA_' + node.value.value)
        nodes.append(node)
    nodes.insert(1, ast.parse('from . import bridge').body[0])
    # future imports must stay ahead of regular imports/docstring.
    nodes = [n for n in nodes if not (isinstance(n, ast.ImportFrom) and n.module == '__future__')]
    ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    adapted = ast.unparse(ast.Module(body=nodes, type_ignores=[])) + '\n'
    (PACKAGE / 'native_ui.py').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'copy_animation_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/复制动画_修复优化版.py', tofile='native_ui.py; algorithms and scene adapters separated')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'copy_animation', 'raw_files': [{'path': 'upstream/' + source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}], 'original_classes': [n.name for n in tree.body if isinstance(n, ast.ClassDef)], 'algorithm_methods': ALGORITHMS, 'original_ui_methods': list(methods), 'source_license': 'User supplied revised script, no license file supplied; private preparation', 'changes': ['Full native list/delegate/modes/editor/config UI', 'Original six sampling/key/numeric algorithm AST preserved', 'Scene UUID pair record/helper/constraint ownership and private sets', 'Standard API read-only preflight/Undo and state finally', 'Explicit config file overwrite', 'Edit-list clones modes before deleting C++ items']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'copy_animation', 'registration': {'module': 'copy_animation', 'class_name': 'CopyAnimationTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': ['upstream/' + source.name, 'catalog.json'], 'dependencies': ['Maya cmds/matchTransform/constraints/key APIs', 'PySide2/6/shiboken real GUI for original widget', 'Existing framework/core Undo'], 'source': '../' + source.name, 'change_summary': 'Full original frame/constraint/numeric/none modes and native list/config UI, preserved sampling algorithm, owned UUID persistent pair helpers/sets/constraints and standard API.', 'verification_limitations': ['Real GUI/mode indicators/editor pending', 'Frame mode only samples integer frames containing source keys', 'Numeric keys every integer frame, scalar matching user attrs only', 'Constraint and helper nodes intentionally persist until explicit cleanup', 'Complex rig/nonuniform scale/layers pending'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'algorithm_methods': ALGORITHMS, 'native_ui_methods': len(methods)}))


if __name__ == '__main__':
    main()
