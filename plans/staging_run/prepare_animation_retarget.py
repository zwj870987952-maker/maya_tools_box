"""Archive the owned source and adapt the complete Qt presentation to the API."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import textwrap

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/animation_retarget'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/animation_retarget'

BRIDGE = '''
def _pairs(self, all_rows=False):
    from .contracts import pairs
    items = [] if all_rows else self.record_list.selectedItems()
    items = items or [self.record_list.item(i) for i in range(self.record_list.count())]
    return pairs([{'text': item.text(), 'modes': item.modes} for item in items], allow_empty=True)

def _run(self, **kwargs):
    from .tool import AnimationRetargetTool
    result = AnimationRetargetTool().run(**kwargs)
    if result.success:
        if result.warnings:
            cmds.warning('\\n'.join(result.warnings))
        cmds.confirmDialog(title='完成', message=result.message, button=['OK'])
        return result.data
    cmds.confirmDialog(title='错误', message=result.message + '\\n场景操作可能已部分完成；请检查并按 Undo 撤回。', button=['OK'])
    return None

def _rebuild(self, rows):
    self.record_list.clear()
    for row in rows:
        item = CustomListWidgetItem(row['source'] + ' , ' + row['target'])
        item.modes = dict(row['modes'])
        item.set_flags()
        self.record_list.addItem(item)

def align_objects_only(self):
    try:
        self._run(action='align', pairs=self._pairs())
    except Exception as error:
        cmds.warning(str(error))

def bake_animation(self, smart=False):
    try:
        self._run(action='bake', pairs=self._pairs(), smart=bool(smart))
    except Exception as error:
        cmds.warning(str(error))

def load_from_info_node(self):
    data = self._run(action='load_scene')
    if data is not None:
        self._rebuild(data['pairs'])

def apply_pose_info(self):
    try:
        self._run(action='restore_pose', pairs=self._pairs())
    except Exception as error:
        cmds.warning(str(error))

def save_data(self):
    path = cmds.fileDialog2(dialogStyle=2, fileMode=0, caption='保存为新 JSON 文件（不覆盖）', fileFilter='JSON Files (*.json)')
    if path:
        try:
            self._run(action='save_config', pairs=self._pairs(all_rows=True), path=path[0])
        except Exception as error:
            cmds.warning(str(error))

def load_data(self):
    path = cmds.fileDialog2(dialogStyle=2, fileMode=1, caption='读取配置', fileFilter='JSON Files (*.json)')
    if path:
        data = self._run(action='load_config', path=path[0])
        if data is not None:
            self._rebuild(data['pairs'])

def preview_operation(self):
    try:
        from .tool import AnimationRetargetTool
        result = AnimationRetargetTool().run(action='align', pairs=self._pairs(), dry_run=True)
        cmds.confirmDialog(title='只读预检', message=result.message, button=['OK'])
    except Exception as error:
        cmds.warning(str(error))
'''


def main():
    source = UNIT / '动画重定向.py'
    upstream = PACKAGE / 'upstream/动画重定向.py'
    upstream.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, upstream)
    original = source.read_text(encoding='utf-8')
    tree = ast.parse(original)
    bridge = ast.parse(textwrap.dedent(BRIDGE)).body
    removed = {'create_rematch_group', 'get_valid_objects', 'record_pose_info', 'apply_numeric_copy', 'copy_numeric_keys'}
    replacements = {node.name for node in bridge}
    output = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)) and (getattr(node, 'module', '') in ('PySide2', 'shiboken2') or any(alias.name == 'maya.OpenMayaUI' for alias in getattr(node, 'names', []))):
            continue
        if isinstance(node, ast.If) or (isinstance(node, ast.FunctionDef) and node.name == 'maya_main_window'):
            continue
        if isinstance(node, ast.ClassDef) and node.name == 'AutoAlignUI':
            node.body = [child for child in node.body if not isinstance(child, ast.FunctionDef) or child.name not in removed | replacements]
            # QAction triggered passes checked=False; make the default bake button explicit.
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                    text = ast.unparse(child).replace('self.bake_button.clicked.connect(self.bake_animation)', 'self.bake_button.clicked.connect(lambda checked=False: self.bake_animation(smart=False))')
                    text += "\n    preview_button = QtWidgets.QPushButton('只读预检')\n    self.button_layout.addWidget(preview_button)\n    preview_button.clicked.connect(self.preview_operation)"
                    node.body[node.body.index(child)] = ast.parse(text).body[0]
            node.body.extend(bridge)
        output.append(node)
    tree.body = output
    adapted = ast.unparse(ast.fix_missing_locations(tree))
    # Qt6 keeps enum aliases, but exec_ and mouse position APIs vary by binding.
    adapted = adapted.replace('menu.exec_(', '_menu_exec(menu, ').replace('event.pos()', '_event_pos(event)')
    prefix = '''from maya_toolkit.core.ui_base import QtWidgets, QtCore, QtGui, get_maya_main_window

def _menu_exec(menu, position):
    method = getattr(menu, 'exec', None) or menu.exec_
    return method(position)

def _event_pos(event):
    return event.position().toPoint() if hasattr(event, 'position') else event.pos()

_WINDOW = None

def show_ui(parent=None):
    global _WINDOW
    import maya.cmds as cmds
    if cmds.about(batch=True) or QtWidgets is None or QtWidgets.QApplication.instance() is None:
        raise RuntimeError('请在真实 Maya 图形界面中打开此工具')
    if _WINDOW is not None:
        try:
            _WINDOW.close()
            _WINDOW.deleteLater()
        except RuntimeError:
            pass
    _WINDOW = AutoAlignUI()
    _WINDOW.setParent(parent or get_maya_main_window())
    _WINDOW.setWindowFlags(QtCore.Qt.Window)
    _WINDOW.show()
    return _WINDOW

'''
    final = '\n'.join(line.rstrip() for line in (prefix + adapted).splitlines()) + '\n'
    ast.parse(final)
    (PACKAGE / 'ui.py').write_text(final, encoding='utf-8')
    doc = RC / 'docs/tools/animation_retarget_ui_changes.diff'
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(''.join(difflib.unified_diff(original.splitlines(True), final.splitlines(True), fromfile='upstream/动画重定向.py', tofile='ui.py')), encoding='utf-8')
    catalog = {'source': 'upstream/动画重定向.py', 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'original_ui_methods': {node.name: [method.name for method in node.body if isinstance(method, ast.FunctionDef)] for node in ast.parse(original).body if isinstance(node, ast.ClassDef)},
               'retained_ui': ['colored channel dots', 'per-row and selected batch modes', 'selection input', 'drag reorder', 'list edit', 'delete', 'double click selection', 'default/smart bake', 'save/load JSON', 'load scene', 'restore poses'],
               'removed_scene_methods': sorted(removed), 'api_bridge_methods': sorted(replacements)}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [path for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    promotion = {'tool_id': 'animation_retarget', 'registration': {'module': 'animation_retarget', 'class_name': 'AnimationRetargetTool'},
                 'files': [{'source': file.relative_to(RC).as_posix(), 'target': file.relative_to(RC).as_posix()} for file in sorted(files)],
                 'resources': ['upstream/动画重定向.py', 'catalog.json'], 'dependencies': ['Maya Python 3', 'existing maya_toolkit framework/core/ui_base', 'PySide2 or PySide6 only for GUI'],
                 'source': '../动画重定向.py', 'change_summary': 'Complete owned retarget UI and business API; preserve modes/offsets/default and smart bake; UUID tracked owned constraints, typed JSON poses, source-frame numeric copying, old config and Rematch reading, read-only preflight, Undo grouping and exclusive file creation.',
                 'verification_limitations': ['Real Maya GUI pending', 'Legacy comma/colon custom attribute pose data can be ambiguous', 'Bake affects all bakeable channels regardless of pair modes', 'Restore skips locked/driven/unmatched attributes', 'Execution errors may leave partial scene changes; Undo the complete chunk'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'raw_source_preserved': source.read_bytes() == upstream.read_bytes()}))


if __name__ == '__main__':
    main()
