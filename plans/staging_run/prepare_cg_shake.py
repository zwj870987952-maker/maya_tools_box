import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/cg_shake_py3'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/cg_shake_py3'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    source = UNIT / 'CgShake_py3'
    resources = []
    for file in sorted(source.rglob('*')):
        if not file.is_file() or '__pycache__' in file.parts:
            continue
        target = PACKAGE / 'upstream' / file.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        resources.append({'path': target.relative_to(PACKAGE).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        if file.parent.name == 'images':
            (PACKAGE / 'images').mkdir(exist_ok=True)
            shutil.copyfile(file, PACKAGE / 'images' / file.name)
    for path, value in [(UNIT / '.gitattributes', 'CgShake_py3/** -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')]:
        path.write_text(value, encoding='utf-8', newline='\n')
    original = (source / 'cgshake.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    original_methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    replacements = ast.parse('''
def attemptPluginLoad(self):
    from .files import plugin_loaded
    if not plugin_loaded():
        cmds.warning('Cache/Restore requires manually loaded animImportExport; opening/apply do not load it.')
def applyShake(self, *_):
    return bridge.apply(self)
def cacheObject(self, *_):
    return bridge.cache(self)
def restoreCache(self, *_):
    return bridge.restore(self)
def clearAnimationLayer(self):
    return bridge.clear(self)
def savePreset(self, *_):
    return bridge.save_preset(self)
def loadPreset(self, preset):
    return bridge.load_preset(self, preset)
def populatePresets(self):
    self.presetComboBox.blockSignals(True)
    self.presetComboBox.clear()
    self.presetComboBox.addItem('Default')
    if os.path.isdir(self.presetsPath):
        for name in sorted(os.listdir(self.presetsPath)):
            if name.endswith('.cgsk'):
                self.presetComboBox.addItem(name)
    self.presetComboBox.blockSignals(False)
def overwriteWarning(self, *_):
    if self.overwriteCheckBox.isChecked():
        QMessageBox.warning(self, 'Overwrite', 'Deletes object animation keys without a frame restriction; layer scope must be checked on a copy. Scene Undo cannot remove cache/preset files.')
def closeEvent(self, event):
    if cmds.control(self.range_ctr, exists=True):
        cmds.deleteUI(self.range_ctr)
    super(CgShake, self).closeEvent(event)
''').body
    by_name = {n.name: n for n in replacements}
    for i, node in enumerate(cls.body):
        if node.name in by_name:
            cls.body[i] = by_name.pop(node.name)
        elif node.name == '__init__':
            node.args.defaults = [ast.Constant(None)]
            node.body.insert(0, ast.parse('if parent is None: parent = get_maya_main_window()').body[0])
            text = ast.unparse(node).replace("self.cachePath = self.path + '/cache/'", "self.cachePath = str(default_data_root() / 'cache') + '/'").replace("self.presetsPath = self.path + '/presets/'", "self.presetsPath = str(default_data_root() / 'presets') + '/'")
            cls.body[i] = ast.parse(text).body[0]
        elif node.name == 'setUI':
            text = ast.unparse(node).replace('self.byFrameSpinBox.setValue(1.0)', 'self.byFrameSpinBox.setMinimum(1)\n    self.byFrameSpinBox.setValue(1)')
            text = text.replace("'shakeFalloffCurve'", "'mtbCGShakeFalloffCurve'").replace("'shakeFalloffCurveOptionVar'", "'mtbCGShakeFalloffCurveOptionVar'")
            text = text.replace('Apply to selected object(s)', 'Apply to first selected object')
            cls.body[i] = ast.parse(text).body[0]
        elif node.name == 'setWidgetStyleSheet':
            text = ast.unparse(node).replace('vignetteFrame)', 'vignetteFrame.png)')
            cls.body[i] = ast.parse(text).body[0]
    cls.body += list(by_name.values())
    header = ast.parse('''
from maya_toolkit.core.ui_base import QtCore, QtGui, QtWidgets, Qt, get_maya_main_window
from .files import default_data_root
from . import bridge
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os, webbrowser
from functools import partial
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance
''').body
    # The original wildcard Qt surface uses the project-selected supported binding.
    header += ast.parse("globals().update({name: getattr(module, name) for module in (QtWidgets, QtGui, QtCore) for name in dir(module) if name.startswith('Q')})").body
    output = ast.Module(body=header + [cls], type_ignores=[])
    ast.fix_missing_locations(output)
    adapted = ast.unparse(output) + '\n'
    (PACKAGE / 'native_ui.py').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'cg_shake_py3_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/cgshake.py', tofile='native_ui.py; business in runtime.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'cg_shake_py3', 'original_methods': original_methods, 'raw_files': resources, 'source_license': 'CgShake1.5 source supplied; no license file provided, private preparation', 'changes': ['Project PySide2/PySide6 binding, deferred parent, no six dependency', 'Full native gradient/layout/images/style', 'Explicit first-object algorithm and per-frame falloff samples', 'Single standard Undo and state finally', 'Private per-object UUID cache with SHA sidecar and overwrite opt-in', 'No plugin auto load; no missing-directory startup crash', 'File writes via explicit API, preset path sanitization']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'cg_shake_py3', 'registration': {'module': 'cg_shake_py3', 'class_name': 'CgShakeTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [r['path'] for r in resources] + ['images/' + p.name for p in (PACKAGE / 'images').iterdir()] + ['catalog.json'], 'dependencies': ['Maya cmds/key APIs', 'animImportExport manually loaded for .anim cache', 'Project Qt binding/shiboken and real GUI native gradient for UI', 'Existing framework/core Undo'], 'source': '../CgShake_py3/cgshake.py', 'change_summary': 'Full original UI/gradient/images, positive uniform shake on first object, explicit samples and seed, standard API/Undo with guarded cache/preset file paths and UUID/SHA restore.', 'verification_limitations': ['Native Qt/gradient/animation-layer scope pending', 'Cache/preset files cannot be undone by scene Undo', 'Original overwrite/restore clear object keys without time range', 'Default UI gradient sampled natively; API requires explicit weights', 'Plugin-loaded cache/restore and per-object target hash required'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'methods': len(original_methods), 'resources': len(resources)}))


if __name__ == '__main__':
    main()
