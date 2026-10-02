from pathlib import Path
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
