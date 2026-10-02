"""Complete Maya config UI and independent UE importer with shared pure config logic."""
import ast
import json
from prepare_external_candidate import ROOT, put
UNIT = ROOT / 'tools_staging_pool/05_ue_pipeline/ue_fbx_auto_import'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/ue_fbx_auto_import'
UE = RC / 'engine_toolkit/tools/ue_fbx_auto_import'

put(UE / 'config.py', r'''"""Pure configuration: exact legacy JSON shape, no Maya/UE imports."""
from pathlib import Path
import hashlib
import json
import os
import re

KEYS = {'fbx_files', 'destination_content_path', 'skeleton_path'}

def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def package_path(value):
    if not isinstance(value, str) or not re.fullmatch(r'/Game(?:/[A-Za-z0-9_]+)+', value):
        raise ValueError('Expected /Game/... package path (no file extension/object suffix): ' + str(value))
    return value

def check_config(data):
    if not isinstance(data, dict) or set(data) != KEYS: raise ValueError('Config must contain exactly the three legacy keys')
    package_path(data['destination_content_path']); package_path(data['skeleton_path'])
    paths = data['fbx_files']
    if not isinstance(paths, list) or not 1 <= len(paths) <= 1000: raise ValueError('fbx_files needs 1..1000 paths')
    seen, sources = set(), []
    for raw in paths:
        if not isinstance(raw, str): raise ValueError('FBX path must be string')
        path = Path(raw)
        if not path.is_absolute() or path.suffix.lower() != '.fbx' or not path.is_file(): raise ValueError('Existing absolute .fbx required: ' + str(raw))
        path = path.resolve(); key = str(path).casefold()
        if key in seen: raise ValueError('Duplicate source FBX: ' + str(path))
        if not re.fullmatch(r'[A-Za-z0-9_]+', path.stem): raise ValueError('Use UE-safe ASCII FBX basename: ' + path.name)
        seen.add(key); sources.append({'path': str(path), 'sha256': file_hash(path), 'name': path.stem})
    names = [s['name'].casefold() for s in sources]
    if len(set(names)) != len(names): raise ValueError('Duplicate FBX basenames in configuration')
    return {'config': dict(data, fbx_files=[s['path'] for s in sources]), 'sources': sources}

def load_config(path):
    path = Path(path)
    if path.stat().st_size > 4 * 1024 * 1024: raise ValueError('Config exceeds 4 MB')
    return check_config(json.loads(path.read_text(encoding='utf-8-sig')))

def content_root(path):
    root = Path(path).resolve()
    if not root.is_dir(): raise ValueError('Content/project directory missing')
    if root.name.casefold() == 'content': return root
    content = root / 'Content'
    if not content.is_dir(): raise ValueError('Select project root containing Content, or Content itself')
    return content.resolve()

def convert_to_ue_path(path, content=None):
    p = Path(path).resolve()
    if content is None:
        roots = [q for q in (p, *p.parents) if q.name.casefold() == 'content']
        if not roots: raise ValueError('Path is outside Content')
        content = roots[0]
    rel = p.relative_to(Path(content).resolve())
    if p.suffix.casefold() == '.uasset': rel = rel.with_suffix('')
    return package_path('/Game/' + rel.as_posix())

def find_target_paths(base):
    content = content_root(base); anim, skeleton = [], []
    count = 0
    for directory, dirs, files in os.walk(content, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
        count += len(dirs) + len(files)
        if count > 200000: raise ValueError('Content scan exceeds 200000 entries')
        for name in dirs:
            if name.casefold() == 'anim': anim.append(str(Path(directory) / name))
        for name in sorted(files):
            if 'skeleton' in name.casefold() and Path(name).suffix.casefold() == '.uasset': skeleton.append(str(Path(directory) / name))
    return anim, skeleton

def generate_config(data, output_dir):
    plan = check_config(data); directory = Path(output_dir).resolve()
    # This explicit file-writing operation alone creates the requested directory.
    directory.mkdir(parents=True, exist_ok=True)
    name = plan['config']['skeleton_path'].rsplit('/', 1)[1] + '_config'
    for index in range(100000):
        target = directory / (name + (('_' + str(index)) if index else '') + '.json')
        try:
            with target.open('x', encoding='utf-8', newline='\n') as stream:
                try: json.dump(plan['config'], stream, ensure_ascii=False, indent=4); stream.write('\n')
                except Exception: stream.close(); target.unlink(); raise
            return {'output': str(target), **plan}
        except FileExistsError: continue
    raise ValueError('Could not allocate unique configuration filename')
''')

put(UE / '__init__.py', r'''"""Explicit UE animation import. Dry-run never creates import options/tasks/assets."""
from pathlib import Path
from .config import load_config, file_hash

parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'import'], 'default': 'inspect'},
    'config_paths': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 1000},
    'config_directory': {'type': 'string', 'description': 'Explicit directory of JSON configurations'},
    'save_assets': {'type': 'boolean', 'default': True},
    'confirm_import': {'type': 'boolean', 'default': False}}, 'description': 'Legacy FBX animation import into wholly fresh /Game destination folders'}

def _unreal():
    import unreal
    return unreal

def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']): raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in ('inspect', 'import'): raise ValueError('Invalid action')
    if not isinstance(kwargs.get('save_assets', True), bool) or not isinstance(kwargs.get('confirm_import', False), bool): raise ValueError('Boolean flags required')
    paths, directory = kwargs.get('config_paths'), kwargs.get('config_directory')
    if (paths is None) == (directory is None): raise ValueError('Provide config_paths OR config_directory explicitly')
    if directory is not None:
        root = Path(directory)
        if not root.is_dir(): raise ValueError('Config directory missing')
        paths = [str(p) for p in sorted(root.glob('*.json'))]
    if not isinstance(paths, list) or not 1 <= len(paths) <= 1000 or any(not isinstance(p, str) for p in paths): raise ValueError('1..1000 config paths required')
    plans = [dict(load_config(p), config_path=str(Path(p).resolve()), config_sha256=file_hash(p)) for p in paths]
    u = _unreal(); seen = []
    for plan in plans:
        config = plan['config']; dest = config['destination_content_path']; folded = dest.casefold()
        if any(folded == old or folded.startswith(old + '/') or old.startswith(folded + '/') for old in seen): raise ValueError('Overlapping config destinations')
        seen.append(folded)
        if u.EditorAssetLibrary.does_directory_exist(dest): raise ValueError('Destination must be a completely new folder: ' + dest)
        skeleton = u.load_asset(config['skeleton_path'])
        if not isinstance(skeleton, u.Skeleton): raise ValueError('Configured Skeleton asset is missing/wrong type: ' + config['skeleton_path'])
    return {'action': action, 'configs': plans, 'save_assets': kwargs.get('save_assets', True),
        'confirm_import': kwargs.get('confirm_import', False), 'asset_impact': 'New AnimationSequences and native importer metadata; shared Skeleton may gain curve metadata; import/save is not promised undoable',
        'file_impact': 'Source FBX/JSON unchanged; save_assets=True writes new UE packages; failures can leave partial assets'}

def get_import_options(skeleton_path):
    u = _unreal(); skeleton = u.load_asset(skeleton_path)
    if not isinstance(skeleton, u.Skeleton): raise ValueError('Invalid Skeleton')
    options = u.FbxImportUI(); options.reset_to_default()
    for key, value in {'automated_import_should_detect_type': False, 'mesh_type_to_import': u.FBXImportType.FBXIT_ANIMATION,
        'skeleton': skeleton, 'import_as_skeletal': True, 'import_animations': True, 'import_mesh': False, 'import_materials': False, 'import_textures': False}.items():
        options.set_editor_property(key, value)
    options.anim_sequence_import_data.set_editor_property('animation_length', u.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    # Original writes skeletal settings onto static_mesh_import_data; these are not applicable to animation-only import.
    return options

def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect': return plan
    if not plan['confirm_import']: raise ValueError('confirm_import=True required for native import/save')
    u = _unreal()
    # Pre-create all transient import options before any native importer runs.
    options = [get_import_options(p['config']['skeleton_path']) for p in plan['configs']]
    tasks = []
    for config, opts in zip(plan['configs'], options):
        if file_hash(config['config_path']) != config['config_sha256']: raise ValueError('Config changed after preflight')
        for source in config['sources']:
            if file_hash(source['path']) != source['sha256']: raise ValueError('FBX changed after preflight')
            task = u.AssetImportTask()
            # Private per-file child avoids multi-take FBX name collisions between files.
            for key, value in {'filename': source['path'], 'destination_path': config['config']['destination_content_path'] + '/' + source['name'],
                'destination_name': source['name'], 'replace_existing': False, 'replace_existing_settings': False, 'save': plan['save_assets'],
                'automated': True, 'options': opts, 'factory': u.FbxFactory()}.items(): task.set_editor_property(key, value)
            tasks.append((task, source))
    result = dict(plan, imports=[], success=True)
    for config in plan['configs']:
        if u.EditorAssetLibrary.does_directory_exist(config['config']['destination_content_path']): raise ValueError('Destination appeared after preflight')
    tools = u.AssetToolsHelpers.get_asset_tools()
    for task, source in tasks:
        try:
            if file_hash(source['path']) != source['sha256']: raise ValueError('FBX changed immediately before import')
            tools.import_asset_tasks([task])
            paths = [str(p) for p in task.imported_object_paths]
            row = {'source': source['path'], 'imported_object_paths': paths, 'success': bool(paths)}
            if not paths: row['error'] = 'Native importer returned no assets'
        except Exception as error:
            row = {'source': source['path'], 'imported_object_paths': [], 'success': False, 'error': str(error)}
        result['imports'].append(row)
        if not row['success']:
            result['success'] = False
            break
    return result

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        success = data.get('success', True)
        return {'success': success, 'tool_id': 'ue_fbx_auto_import', 'dry_run': dry_run, 'data': data,
                'errors': [] if success else ['Native import failed; inspect per-file results and partial new assets']}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_fbx_auto_import', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui():
    raise RuntimeError('UE importer uses explicit configuration API; Maya config generator supplies the full dialog')
''')

put(PKG / '__init__.py', r'''"""Maya configuration generator only. UE importing lives in engine_toolkit."""
from pathlib import Path
from maya_toolkit.framework import BaseMayaTool, ToolResult
from engine_toolkit.tools.ue_fbx_auto_import import config as c

class UEFbxAutoImportTool(BaseMayaTool):
    tool_id = 'ue_fbx_auto_import'
    tool_name = 'UE FBX 动画配置生成器'
    category = 'engine_bridge'
    description = 'Maya配置生成窗口与纯文件API；不在Maya执行UE资产导入'
    parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
        'action': {'type': 'string', 'enum': ['inspect_config', 'generate_config', 'detect_paths', 'show_ui'], 'default': 'inspect_config'},
        'config': {'type': 'object'}, 'output_dir': {'type': 'string'}, 'root_path': {'type': 'string'}}}
    def plan(self, **kwargs):
        if set(kwargs) - set(self.parameters_schema['properties']): raise ValueError('Unknown parameters')
        action = kwargs.get('action', 'inspect_config')
        if action not in self.parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
        if action == 'show_ui':
            from maya import cmds
            if cmds.about(batch=True): raise ValueError('UI requires interactive Maya')
            return {'action': action}
        if action == 'detect_paths':
            root = kwargs.get('root_path', ''); anim, skeleton = c.find_target_paths(root)
            return {'action': action, 'anim_paths': [c.convert_to_ue_path(p, c.content_root(root)) for p in anim], 'skeleton_paths': [c.convert_to_ue_path(p, c.content_root(root)) for p in skeleton]}
        plan = c.check_config(kwargs.get('config'))
        if action == 'generate_config':
            directory = Path(kwargs.get('output_dir') or (Path.home() / 'Desktop/FBX_Configs')).resolve()
            if directory.exists() and not directory.is_dir(): raise ValueError('Output directory is a file')
            plan['output_dir'] = str(directory)
        return {'action': action, **plan}
    def validate(self, **kwargs):
        try: return ToolResult.ok(message='配置预检通过；不写文件、不导入UE资产', data=self.plan(**kwargs), dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e), errors=[str(e)], dry_run=True)
    def execute(self, **kwargs):
        plan = self.plan(**kwargs)
        if plan['action'] == 'generate_config': return ToolResult.ok(message='已独占生成新JSON；文件不受Maya Undo撤销', data=c.generate_config(plan['config'], plan['output_dir']))
        if plan['action'] == 'show_ui': self.show_ui(); return ToolResult.ok(message='配置窗口已打开')
        return ToolResult.ok(message='配置查询完成', data=plan)
    def show_ui(self):
        from .ui import show_fbx_config_generator
        return show_fbx_config_generator()
''')

ui_source = (UNIT / 'ue导入fbx配置.py').read_text(encoding='utf-8')
ui_source = ui_source.replace('from PySide2 import QtWidgets, QtCore\nimport shiboken2', 'try:\n    from PySide6 import QtWidgets, QtCore\n    import shiboken6 as shiboken2\nexcept ImportError:\n    from PySide2 import QtWidgets, QtCore\n    import shiboken2\nfrom engine_toolkit.tools.ue_fbx_auto_import import config as config_api')
# Preserve original widget/layout/drag-drop/load/detect interaction; replace IO functions only.
tree = ast.parse(ui_source); lines = ui_source.splitlines(keepends=True); edits = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'find_target_paths':
        edits.append((node.lineno-1, node.end_lineno, 'def find_target_paths(base_path):\n    return config_api.find_target_paths(base_path)\n'))
    if isinstance(node, ast.FunctionDef) and node.name == 'convert_to_ue_path':
        edits.append((node.lineno-1, node.end_lineno, 'def convert_to_ue_path(windows_path):\n    return config_api.convert_to_ue_path(windows_path)\n'))
    if isinstance(node, ast.FunctionDef) and node.name == 'generate_config':
        edits.append((node.lineno-1, node.end_lineno, '''    def generate_config(self):
        data = {'destination_content_path': self.destination_path_combo.currentText().strip(),
                'skeleton_path': self.skeleton_path_combo.currentText().strip(),
                'fbx_files': [p.strip() for p in self.fbx_files_text.toPlainText().splitlines() if p.strip()]}
        try:
            result = config_api.generate_config(data, os.path.join(os.path.expanduser('~'), 'Desktop', 'FBX_Configs'))
            QtWidgets.QMessageBox.information(self, 'Success', 'Config saved to ' + result['output'])
        except Exception as error:
            QtWidgets.QMessageBox.critical(self, 'Error', str(error))
'''))
    if isinstance(node, ast.FunctionDef) and node.name == 'detect_paths':
        edits.append((node.lineno-1, node.end_lineno, '''    def detect_paths(self):
        try:
            base = self.root_path.text().strip()
            anim, skeleton = config_api.find_target_paths(base)
            content = config_api.content_root(base)
            anim = [config_api.convert_to_ue_path(p, content) for p in anim]
            skeleton = [config_api.convert_to_ue_path(p, content) for p in skeleton]
            self.destination_path_combo.clear(); self.skeleton_path_combo.clear()
            self.destination_path_combo.addItems(anim); self.skeleton_path_combo.addItems(skeleton)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, 'Warning', str(error))
'''))
for start, end, replacement in sorted(edits, reverse=True): lines[start:end] = [replacement]
ui_source = ''.join(lines)
ui_source = ui_source.replace('                    config_data = json.load(config_file)', '                    config_data = config_api.check_config(json.load(config_file))["config"]')
ui_source = ui_source.replace('options = QtWidgets.QFileDialog.Options()', 'options = QtWidgets.QFileDialog.Option(0)')
ui_source = ui_source.replace('QtCore.Qt.Window)', 'QtCore.Qt.WindowType.Window)')
ui_source = ui_source.rsplit('\nshow_fbx_config_generator()', 1)[0]
ui_source = ui_source.replace('    fbx_config_window.show()', '    fbx_config_window.show()\n    return fbx_config_window')
put(PKG / 'ui.py', ui_source)

put(RC / 'tests/test_ue_fbx_auto_import.py', r'''from pathlib import Path
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_fbx_auto_import as t
from engine_toolkit.tools.ue_fbx_auto_import import config as c

class Obj:
    def __init__(self): self.props = {}; self.imported_object_paths = []
    def set_editor_property(self, key, value): self.props[key] = value
    def reset_to_default(self): self.anim_sequence_import_data = Obj()
class Skeleton: pass
class Tests(unittest.TestCase):
    def setup_files(self, d):
        fbx = Path(d) / 'Walk.FBX'; fbx.write_bytes(b'test fbx content')
        data = {'fbx_files': [str(fbx)], 'destination_content_path': '/Game/NewAnims', 'skeleton_path': '/Game/Hero_Skeleton'}
        config = Path(d) / 'config.json'; config.write_text(json.dumps(data))
        return fbx, data, config
    def fake(self, calls, existing=False, fail=False):
        def importer(tasks):
            calls.extend(tasks)
            for task in tasks: task.imported_object_paths = [] if fail else [task.props['destination_path'] + '/Walk.Walk']
        return types.SimpleNamespace(Skeleton=Skeleton, load_asset=lambda p: Skeleton(),
            EditorAssetLibrary=types.SimpleNamespace(does_directory_exist=lambda p: existing), FbxImportUI=Obj,
            FBXImportType=types.SimpleNamespace(FBXIT_ANIMATION=1), FBXAnimationLengthImportType=types.SimpleNamespace(FBXALIT_EXPORTED_TIME=2),
            AssetImportTask=Obj, FbxFactory=Obj, AssetToolsHelpers=types.SimpleNamespace(get_asset_tools=lambda: types.SimpleNamespace(import_asset_tasks=importer)))
    def test_config_detection_exclusive_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d)
            root = Path(d) / 'Project/Content/Hero/anim'; root.mkdir(parents=True)
            skeleton = root.parent / 'Hero_Skeleton.uasset'; skeleton.write_bytes(b'asset')
            (root.parent / 'Skeleton.txt').write_text('not an asset')
            anim, skel = c.find_target_paths(Path(d) / 'Project')
            self.assertEqual(anim, [str(root)]); self.assertEqual(skel, [str(skeleton)])
            self.assertEqual(c.convert_to_ue_path(skeleton), '/Game/Hero/Hero_Skeleton')
            with self.assertRaises(ValueError): c.convert_to_ue_path(fbx)
            out = Path(d) / 'Configs'; first = c.generate_config(data, out); old = Path(first['output']).read_bytes()
            second = c.generate_config(data, out); self.assertNotEqual(first['output'], second['output'])
            self.assertEqual(Path(first['output']).read_bytes(), old); self.assertEqual(c.load_config(second['output'])['config'], data)
    def test_dryrun_wholepreflight_native_success_and_failure(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d); calls = []
            with patch.object(t, '_unreal', return_value=self.fake(calls)):
                self.assertTrue(t.run(action='import', config_paths=[str(config)])['success']); self.assertEqual(calls, [])
                self.assertFalse(t.run(dry_run=False, action='import', config_paths=[str(config)])['success']); self.assertEqual(calls, [])
                result = t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config)])
                self.assertTrue(result['success'], result); task = calls[0]
                self.assertEqual(task.props['destination_path'], '/Game/NewAnims/Walk')
                self.assertFalse(task.props['replace_existing']); self.assertTrue(task.props['save'])
                self.assertFalse(task.props['options'].props['import_mesh']); self.assertFalse(task.props['options'].props['import_materials'])
            with patch.object(t, '_unreal', return_value=self.fake([], existing=True)):
                self.assertFalse(t.run(action='import', config_paths=[str(config)])['success'])
            with patch.object(t, '_unreal', return_value=self.fake([], fail=True)):
                self.assertFalse(t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config)])['success'])
            self.assertEqual(fbx.read_bytes(), b'test fbx content')
    def test_invalid_last_config_no_import(self):
        with tempfile.TemporaryDirectory() as d:
            fbx, data, config = self.setup_files(d); bad = Path(d) / 'bad.json'; bad.write_text('{}'); calls=[]
            with patch.object(t, '_unreal', return_value=self.fake(calls)):
                self.assertFalse(t.run(dry_run=False, action='import', confirm_import=True, config_paths=[str(config), str(bad)])['success']); self.assertEqual(calls, [])
if __name__ == '__main__': unittest.main()
''')
put(RC / 'tests/test_ue_fbx_auto_import_maya.py', r'''from pathlib import Path
import json
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
candidate = Path(__file__).resolve().parents[1]
# Staging launch must supply the independent engine package path itself.
import importlib.util
spec = importlib.util.spec_from_file_location('candidate_launcher', candidate / 'launch_candidate.py')
launcher = importlib.util.module_from_spec(spec); spec.loader.exec_module(launcher)
tool_instance = launcher.load_tool()
class Tests(unittest.TestCase):
    def test_config_only_preserves_dirty_scene_and_dryrun(self):
        with tempfile.TemporaryDirectory() as d:
            cmds.file(new=True, force=True); cube = cmds.polyCube()[0]; cmds.setAttr(cube + '.tx', 7)
            before = (cmds.ls(uuid=True), cmds.file(q=True, modified=True), cmds.file(q=True, sceneName=True), cmds.undoInfo(q=True, undoName=True))
            fbx = Path(d) / 'Walk.fbx'; fbx.write_bytes(b'fbx')
            config = {'fbx_files':[str(fbx)], 'destination_content_path':'/Game/Anim', 'skeleton_path':'/Game/Hero_Skeleton'}
            out = Path(d) / 'Configs'; tool = tool_instance
            self.assertTrue(tool.run(dry_run=True, action='generate_config', config=config, output_dir=str(out)).success)
            self.assertFalse(out.exists())
            result = tool.run(action='generate_config', config=config, output_dir=str(out))
            self.assertTrue(result.success, result); self.assertEqual(json.loads(Path(result.data['output']).read_text()), config)
            self.assertEqual((cmds.ls(uuid=True), cmds.file(q=True, modified=True), cmds.file(q=True, sceneName=True), cmds.undoInfo(q=True, undoName=True)), before)
            self.assertFalse(tool.run(dry_run=True, action='show_ui').success)
if __name__ == '__main__': unittest.main()
''')
put(RC / 'docs/tools/ue_fbx_auto_import.md', '''# Maya配置生成与UE FBX动画批量导入候选

双入口完整保留：Maya PySide根路径智能Anim/Skeleton检测、可编辑两combo、FBX文本/URL拖放、Load Config、Generate Config、新编号桌面JSON；UE批量JSON读取→Skeleton检查→FbxImportUI动画设置→AssetImportTask自动导入/保存/逐文件结果。原两文件SHA归档。所有import取消自动开窗/执行，未迁入正式库。

Maya UEFbxAutoImportTool才继承Base，tool_id=ue_fbx_auto_import/category=engine_bridge/JSON Schema/ToolResult；action inspect_config默认，generate_config/config/output_dir写独占新JSON（不受Undo），detect_paths/root_path只读查Content，show_ui需真实GUI。默认桌面FBX_Configs目录仅真正generate创建；原文件永不覆盖。只检测Content中anim目录与Skeleton名称.uasset，不把Skeleton.txt当资产；/Game路径用明确Content根relative_to转换，不在字符串中截取任意/Content，不支持plugin mount自动转换。原widget/layout/drag/load流程保留，Qt6/Qt5兼容；配置三键格式完全兼容。

```python
from maya_toolkit.tools.ue_fbx_auto_import import UEFbxAutoImportTool
tool = UEFbxAutoImportTool()
tool.show_ui()
# UE Editor内独立执行（正式项目根需在UE sys.path）
from engine_toolkit.tools import ue_fbx_auto_import as ue
ue.run(action='import', config_directory=r'D:/FBX_Configs')
ue.run(dry_run=False, action='import', config_directory=r'D:/FBX_Configs', confirm_import=True)
```

UE API完全无Maya依赖，validate/execute/run返回success/tool_id/dry_run/data/errors；dry_run默认True，不创建任务/选项，不调用import/save。显式config_paths或config_directory二选一，最多1000cfg/每cfg1000FBX，JSON4MB上限；源绝对现存FBX/ASCII安全basename/重复名/配置destination重叠全批检查，源SHA保存执行前复核。Skeleton必须真实正确类型；目标/子目录须是完全全新的/Game包目录，原路径不写。每FBX放destination_content_path/<stem>/隔离多take命名冲突（明确新增层级与原不同），AssetImportTask destination_name=<stem>、replace_existing=False、replace_existing_settings=False、save_assets默认True（原行为），automated=True、FbxFactory明确legacy importer。目标在实际导入前再查，不能对抗其他编辑器进程在native importer内竞争，需单写者。

原把skeletal设置写到static_mesh_import_data并吞掉异常，候选只用动画必需设置，所有FbxImportUI mandatory参数失败在首次导入前停止；不启用update_reference_pose/import_mesh/morph/material/texture，动画长度仍EXPORTED_TIME。即使动画-only导入，UE factory可能修改共享Skeleton曲线元数据/标dirty，不能承诺既有Skeleton完全不变；请先备份项目。原生import/save没有可靠跨资产Undo，save_assets=True写UE包，False仅不主动save，仍可产生内存资产；失败/空返回停止后续，结果保留此前paths，人工清理新目标目录与审核Skeleton。源FBX/JSON不写；UE import不能在Maya执行，Maya面板只生成配置。

自包含共享纯config模块供两端用；晋级清单同时复制maya_toolkit工具UI、engine_toolkit纯UE importer/config、docs/tests，再注册Maya配置工具；真实Maya配置UI与真实UE导入均必须验收。本机仅Maya2025隔离配置API/离线mock可验，UE Editor/真实FBX/Skeleton/Interchange与FbxFactory选择/多take导入not_run。原脚本不是现有正式core的业务重复，纯文件路径与UE资产协议未下沉core。

人工验收双runtime后记录Maya版本与UE版本，promotion脚本Maya gate保持；即使Maya API测试通过，不能只测Maya窗口就批准UE端。关联vessel/普通FBX exporter输出仅候选输入，需要真实Skeleton绑定与曲线采样核对。
''')
put(RC / 'acceptance.md', '''# 双运行时验收 not_run

1. 备份Maya scene和UE项目/共享Skeleton，空临时目录。Maya窗口打开/根Content检测anim与uasset/两combo/URL拖放/加载旧JSON/Generate独占编号JSON；中文/Content大小写/坏最后FBX/非/Game/重名/外Content路径应拒绝。dry_run与detect/load不写文件，不改当前dirty场景/Undo。
2. UE启用Python Editor Script/EditorScriptingUtilities以及目标引擎legacy FBX importer，使用实际动画FBX和正确Skeleton、完全全新/Game目标。inspect/dry-run无tasks/asset writes；confirm_import=False拒绝实际导入。真实导入每FBX独立stem子目录，检查AnimationSequence绑定Skeleton/帧段/曲线/多take，无mesh/material/texture意外资产；save True磁盘新包/False内存区别；原FBX/JSON和既有其他包保持、共享Skeleton变化如实审查。
3. 坏最后配置/缺Skeleton/目标已有/配置destination重叠首次import前拒绝；某FBX损坏或native空返回必须失败且保留之前成功outputs信息。不用UE Undo期待回滚保存；清理只能操作已确认新目标目录，不覆盖正式动画。Maya真实GUI与UE真实导入均not_run，mock/mayapy不替代。两端满意才记录current candidate_sha256/tool_id/maya_version/runtime_version/accepted_by/date/passed=true晋级；目标清单与Maya注册预制，UE无需Maya继承。
''')

# Ordinary candidate archives the two originals under the meaningful Maya adapter.
import subprocess, sys
subprocess.run([sys.executable, str(ROOT / 'plans/staging_run/prepare_small_candidate.py'), '--tool', '05_ue_pipeline/ue_fbx_auto_import', '--class-name', 'UEFbxAutoImportTool', '--summary', 'Complete Maya Qt config generator plus standalone UE legacy animation importer with whole-batch preflight and fresh destinations', '--dependencies', 'Maya cmds/Qt5-or-6', 'UE PythonScriptPlugin/EditorScriptingUtilities/FbxFactory', '--limitations', 'Real Maya configuration GUI and Unreal Editor animation import not_run'], check=True)
desc = json.loads((RC / 'promotion.json').read_text(encoding='utf-8'))
desc['runtime'] = 'maya_unreal'
desc['verification_limitations'].append('Both Maya GUI and UE import acceptance required before promotion')
for p in sorted((RC / 'engine_toolkit').rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc': desc['files'].append({'source':p.relative_to(RC).as_posix(), 'target':p.relative_to(RC).as_posix()})
put(RC / 'promotion.json', json.dumps(desc, ensure_ascii=False, indent=2))
launcher = RC / 'launch_candidate.py'
put(launcher, launcher.read_text(encoding='utf-8').replace('def load_tool():\n', 'def load_tool():\n    sys.path.insert(0, str(Path(__file__).resolve().parent))\n'))
