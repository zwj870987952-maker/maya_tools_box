import ast
import hashlib
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.copy_animation import CopyAnimationTool
    TOOL = CopyAnimationTool()
from maya_toolkit.tools.copy_animation.contracts import normalize, pair_data
from maya_toolkit.tools.copy_animation.tool import parse_config
PACKAGE = Path(sys.modules['maya_toolkit.tools.copy_animation'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_source_and_algorithm_ast_preserved(self):
        catalog = TOOL.execute(action='inventory').data
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        original = ast.parse((PACKAGE / catalog['raw_files'][0]['path']).read_text(encoding='utf-8-sig'))
        original = next(n for n in original.body if isinstance(n, ast.ClassDef) and n.name == 'AutoAlignUI')
        algorithms = next(n for n in ast.parse((PACKAGE / 'algorithms.py').read_text(encoding='utf-8')).body if isinstance(n, ast.ClassDef))
        before = {n.name: n for n in original.body if isinstance(n, ast.FunctionDef)}
        for node in algorithms.body:
            node.body = node.body[1:]
            self.assertEqual(ast.dump(before[node.name], include_attributes=False), ast.dump(node, include_attributes=False))
        ui = (PACKAGE / 'native_ui.py').read_text(encoding='utf-8')
        for name in ('CustomListWidgetItem', 'CustomItemDelegate', 'CustomListWidget', 'EditDialog', 'AutoAlignUI'):
            self.assertIn('class ' + name, ui)
        self.assertIn('old_modes', ui)
        self.assertNotIn('old_items = self._items()', ui)

    def test_contract_config_and_no_maya_inventory(self):
        for args in [{'start': True}, {'pairs': [{'source': 'a', 'target': 'b', 'modes': {'other': 'frame'}}]}, {'pairs': [{'source': 'a.x', 'target': 'b'}]}, {'overwrite_file': 1}, {'extra': 1}]:
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertEqual('frame', pair_data({'source': 'a', 'target': 'b'})['modes']['translate'])
        self.assertEqual('a', parse_config([{'text': 'a , b'}])[0]['source'])
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('copy_animation', TOOL.to_mcp_tool()['name'])

    def test_file_preflight_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as scratch:
            target = Path(scratch) / 'notCreated/config.json'
            result = TOOL.validate(action='save_config', file_path=str(target), pairs=[{'source': 'a', 'target': 'b'}])
            self.assertTrue(result.success, result.message)
            self.assertFalse(target.parent.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
