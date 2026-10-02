from prepare_external_candidate import ROOT, put, prepare
RC = ROOT / 'tools_staging_pool/05_ue_pipeline/ue_context_menu/release_candidate'
PKG = RC / 'engine_toolkit/tools/ue_context_menu'
put(PKG / '__init__.py', '''"""Explicit UE source-path menu lifecycle and read-only import data reporting."""
OWNER = 'EngineToolkitUESourcePaths'
ENTRY = 'EngineToolkitPrintSourcePaths'
MENU = 'ContentBrowser.AssetContextMenu'
SECTION = 'EngineToolkitSourcePaths'
parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'print_source_paths', 'register_menu', 'unregister_menu'], 'default': 'inspect'}}}

def _unreal():
    import unreal
    return unreal

def read_source_paths(asset):
    """All available import paths with provenance; no has_editor_property assumption."""
    row = {'asset': str(asset.get_path_name()), 'name': str(asset.get_name()), 'paths': [], 'method': None, 'errors': []}
    try:
        data = asset.get_editor_property('asset_import_data')
    except Exception as error:
        row['status'] = 'no_import_data'; row['errors'].append(str(error)); return row
    if data is None:
        row['status'] = 'no_import_data'; return row
    for method in ('get_all_filenames', 'extract_filenames', 'get_first_filename'):
        if not callable(getattr(data, method, None)):
            continue
        try:
            value = getattr(data, method)()
            paths = [value] if method == 'get_first_filename' else list(value or [])
            paths = list(dict.fromkeys(str(p) for p in paths if p))
            if paths:
                row.update(paths=paths, method=method, status='resolved'); return row
        except Exception as error:
            row['errors'].append(method + ': ' + str(error))
    try:
        info = data.get_source_data() if callable(getattr(data, 'get_source_data', None)) else data.get_editor_property('source_data')
        paths = list(dict.fromkeys(str(f.relative_filename) for f in info.source_files if f.relative_filename))
        row.update(paths=paths, method='source_data_raw', status='raw_relative' if paths else 'unresolved')
    except Exception as error:
        row['errors'].append('source_data: ' + str(error)); row['status'] = 'unresolved'
    return row

def validate(**kwargs):
    if set(kwargs) - {'action'}: raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in parameters_schema['properties']['action']['enum']: raise ValueError('Invalid action')
    u = _unreal()
    if action in ('register_menu', 'unregister_menu'):
        if not hasattr(u, 'ToolMenus'): raise RuntimeError('UE ToolMenus unavailable')
        return {'action': action, 'menu': MENU, 'section': SECTION, 'owner': OWNER, 'asset_mutations': []}
    assets = list(u.EditorUtilityLibrary.get_selected_assets())
    if len(assets) > 10000: raise ValueError('Selection exceeds 10000 assets')
    return {'action': action, 'rows': [read_source_paths(a) for a in assets], 'asset_mutations': [], 'files_written': []}

def unregister_menu():
    u = _unreal(); menus = u.ToolMenus.get()
    menus.unregister_owner_by_name(OWNER)
    menus.refresh_all_widgets()

def register_menu():
    u = _unreal(); menus = u.ToolMenus.get()
    menus.unregister_owner_by_name(OWNER)
    try:
        menu = menus.extend_menu(MENU)
        entry = u.ToolMenuEntry(name=ENTRY, owner=u.ToolMenuOwner(name=OWNER), type=u.MultiBlockType.MENU_ENTRY,
            insert_position=u.ToolMenuInsert('', u.ToolMenuInsertType.FIRST))
        entry.set_label('Print Source Paths')
        entry.set_tool_tip('Read selected assets import sources; no file writes')
        entry.set_string_command(u.ToolMenuStringCommandType.PYTHON, '',
            "from engine_toolkit.tools import ue_context_menu as t; t.run(dry_run=False, action='print_source_paths')")
        menu.add_menu_entry(SECTION, entry)
        menus.refresh_all_widgets()
    except Exception:
        menus.unregister_owner_by_name(OWNER)
        raise

def execute(**kwargs):
    plan = validate(**kwargs)
    action = plan['action']
    if action == 'register_menu': register_menu()
    elif action == 'unregister_menu': unregister_menu()
    elif action == 'print_source_paths':
        u = _unreal(); u.log('========== Selected Assets: Source File Paths ==========')
        if not plan['rows']: u.log_warning('No assets selected.')
        for row in plan['rows']:
            u.log(row['name'] + ': ' + row['status'])
            for path in row['paths']: u.log('  ' + path)
            for error in row['errors']: u.log_warning('  ' + error)
        u.log('=======================================================')
    return plan

def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool): raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        return {'success': True, 'tool_id': 'ue_context_menu', 'dry_run': dry_run, 'data': data, 'errors': []}
    except Exception as error:
        return {'success': False, 'tool_id': 'ue_context_menu', 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}

def show_ui(): return run(dry_run=False, action='register_menu')
''')
put(RC / 'tests/test_ue_context_menu.py', '''from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_context_menu as t
class Asset:
    def __init__(self, data=None): self.data = data
    def get_name(self): return 'Mesh'
    def get_path_name(self): return '/Game/Mesh.Mesh'
    def get_editor_property(self, name):
        if self.data is None: raise Exception('No property')
        return self.data
class Entry:
    def __init__(self, **kwargs): self.values = kwargs
    def set_label(self, value): self.label = value
    def set_tool_tip(self, value): self.tip = value
    def set_string_command(self, *args): self.command = args[-1]
class Menus:
    def __init__(self): self.entries = {}; self.refresh = 0
    def unregister_owner_by_name(self, name): self.entries = {k:v for k,v in self.entries.items() if v.values['owner'].name != name}
    def refresh_all_widgets(self): self.refresh += 1
    def extend_menu(self, name): self.menu = name; return self
    def add_menu_entry(self, section, entry): self.entries[entry.values['name']] = entry
class Tests(unittest.TestCase):
    def test_all_paths_fallback_and_unresolved(self):
        d = types.SimpleNamespace(get_all_filenames=lambda: [], extract_filenames=lambda: ['C:/a.fbx', 'C:/b.fbx', 'C:/a.fbx'])
        row = t.read_source_paths(Asset(d)); self.assertEqual(row['paths'], ['C:/a.fbx', 'C:/b.fbx'])
        self.assertEqual(t.read_source_paths(Asset())['status'], 'no_import_data')
        raw = types.SimpleNamespace(get_source_data=lambda: types.SimpleNamespace(source_files=[types.SimpleNamespace(relative_filename='../x.fbx')]))
        self.assertEqual(t.read_source_paths(Asset(raw))['status'], 'raw_relative')
        broken = types.SimpleNamespace(extract_filenames=lambda: (_ for _ in ()).throw(ValueError('read failed')), get_first_filename=lambda: 'C:/first.fbx')
        row = t.read_source_paths(Asset(broken)); self.assertEqual(row['paths'], ['C:/first.fbx']); self.assertTrue(row['errors'])
    def test_readonly_preview_and_owned_idempotent_menu(self):
        menus = Menus(); logs = []
        u = types.SimpleNamespace(ToolMenus=types.SimpleNamespace(get=lambda: menus), ToolMenuEntry=Entry,
            ToolMenuOwner=lambda name: types.SimpleNamespace(name=name), MultiBlockType=types.SimpleNamespace(MENU_ENTRY=1),
            ToolMenuInsert=lambda *a: None, ToolMenuInsertType=types.SimpleNamespace(FIRST=0),
            ToolMenuStringCommandType=types.SimpleNamespace(PYTHON=1), EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: []), log=logs.append, log_warning=logs.append)
        with patch.object(t, '_unreal', return_value=u):
            self.assertTrue(t.run(action='register_menu')['success']); self.assertEqual(menus.entries, {}); self.assertEqual(logs, [])
            for _ in range(2): self.assertTrue(t.run(dry_run=False, action='register_menu')['success'])
            self.assertEqual(len(menus.entries), 1)
            self.assertIn('engine_toolkit.tools', list(menus.entries.values())[0].command)
            self.assertTrue(t.run(dry_run=False, action='unregister_menu')['success']); self.assertEqual(menus.entries, {})
            self.assertTrue(t.run(dry_run=False, action='print_source_paths')['success']); self.assertIn('No assets selected.', logs)
if __name__ == '__main__': unittest.main()
''')
put(RC / 'docs/tools/ue_context_menu.md', '''# UE 资产源路径菜单候选

完整保留原 Content Browser 右键 Print Source Paths 与逐资产多路径 Output Log。单文件 SHA 精确归档；import 不注册菜单、不打印日志。修复原 asset.has_editor_property 的不可靠调用，改 try get_editor_property；逐方法读取错误不吞掉为成功，get_all_filenames→extract_filenames→get_first_filename→source_data raw 四回退保持。raw_relative 原相对路径明确标记，不按 cwd 拼成错误绝对路径；此工具不判断源文件存在，不修复导入元数据。

UE原生 package engine_toolkit.tools.ue_context_menu 无Maya依赖；parameters_schema/validate/execute/run 提供结构化结果。action 默认 inspect（读选区）；print_source_paths 输出日志；register_menu/unregister_menu 更改该 owner 的临时菜单、不改资产/文件、不受Undo管理。dry_run=True只检查，不注册、不注销、不日志。空选区返回空rows，打印时提示；超过10000拒绝。show_ui显式注册菜单；重复注册先注销自己的 owner，不动其他菜单。

```python
from engine_toolkit.tools import ue_context_menu as t
t.run(action='inspect')
t.run(dry_run=False, action='register_menu')
t.run(dry_run=False, action='print_source_paths')
t.run(dry_run=False, action='unregister_menu')
```

菜单路径改为通用 ContentBrowser.AssetContextMenu 的自有 EngineToolkitSourcePaths section，避免原把 AssetActions section误当菜单名；标签/靠前插入保留；callback使用完整正式模块名，不依赖原临时路径。ToolMenuOwner + unregister_owner_by_name 在关闭或热重载时需显式注销；不自动改UE启动脚本。右键操作读取执行时Content Browser全选区，不保证仅菜单上下文资产。UE版本菜单布局仍待实测。需要Python Editor Script/Editor Scripting Utilities/ToolMenus；无UE安装，真实菜单/多类型import_data检查 not_run。

纯查询结果可供骨骼导出、源文件复制预检，不能把未解析/缺元数据当做资产无源。extract_filenames可多源；raw仅原字串。target/package/docs/tests晋级由promotion.json与临时promote_candidate.py负责，不改Maya注册表，--apply必须UE runtime_version与当前SHA人工验收。

参考：[AssetImportData](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportData?application_version=5.1)、[ToolMenuEntry](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuEntry)。离线mock/临时布局通过不等于UE直验。
''')
put(RC / 'acceptance.md', '''# UE 验收 not_run

备份UE项目启用Python Editor Script/Editor Scripting Utilities。候选根加sys.path后import无UI变化；dry_run register不加菜单。实际register两次只有一个Print Source Paths，右键点击多选SkeletalMesh/Texture/无importdata资产，Output Log保留多源/缺失/错误分类。实际相对路径回退不误报绝对路径，空选区提示，unregister删除仅自己菜单；重载/重启手动注册回调使用正式完整模块路径。Asset/uasset与外部文件均不变。UE菜单路径/section/版本兼容必须实测，不能把mock当UE验收。通过后以tool_id=ue_context_menu/current candidate_sha256/runtime_version/accepted_by/date/passed=true记录晋级依据。Maya验收不适用于此UE原生工具。
''')
prepare('05_ue_pipeline/ue_context_menu', 'Complete explicit UE source-path query/menu lifecycle with all fallback methods, schema, dry-run, provenance and no asset/file writes', ['Unreal Editor PythonScriptPlugin/EditorScriptingUtilities/ToolMenus'], ['Real UE context menus/import data types/target versions not_run'], 'UE Content Browser owned Print Source Paths entry; explicit registration/unregistration')
