"""Source preservation, complete algorithm/UI and strict API checks without Maya."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/back2origin_v05_gaiv3'
else:
    from maya_toolkit.tools.back2origin_v05_gaiv3 import Back2OriginTool
    load_tool = Back2OriginTool
    PACKAGE = Path(sys.modules[Back2OriginTool.__module__].__file__).parent
tool = load_tool()
from maya_toolkit.tools.back2origin_v05_gaiv3.contracts import normalize, ACTIONS


class OfflineTests(unittest.TestCase):
    def test_raw_preserved_and_full_function_inventory(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['original_functions']), 36)
        for row in catalog['raw_files']:
            archive = PACKAGE / row['path']
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), row['sha256'])
            original = RC.parent / archive.name
            if original.exists():
                self.assertEqual(original.read_bytes(), archive.read_bytes())

    def test_original_eight_algorithm_bodies_identical(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        raw = ast.parse((PACKAGE / 'upstream/Back2Origin_v05_gaiv3.py').read_text(encoding='utf-8-sig'))
        code = ast.parse((PACKAGE / 'algorithms.py').read_text(encoding='utf-8'))
        originals = {node.name: node for node in raw.body if isinstance(node, ast.FunctionDef)}
        adapted = {node.name: node for node in code.body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(set(adapted), set(catalog['algorithm_functions']))
        for name, node in adapted.items():
            self.assertEqual(ast.dump(node), ast.dump(originals[name]))
        reverse = (PACKAGE / 'reverse.py').read_text(encoding='utf-8')
        self.assertIn('global_values', reverse)
        self.assertIn('cmds.xform', reverse)
        self.assertIn('cmds.cutKey', reverse)
        self.assertNotIn('textFieldButtonGrp', reverse)

    def test_import_no_installer_or_window_and_full_ui(self):
        code = (PACKAGE / 'native_ui.py').read_text(encoding='utf-8')
        tree = ast.parse(code)
        self.assertFalse(any(isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) for node in tree.body))
        self.assertIn('Convert to Root Motion', code)
        self.assertIn('Return Global Motion to Root', code)
        self.assertIn('Auto-Identify Controllers', code)
        self.assertIn('mtbB2O_frameStepField', code)
        self.assertIn("bridge.dispatch('convert')", code)
        self.assertIn("bridge.dispatch('reverse')", code)
        self.assertIn('lambda *_: clear_all()', code)
        self.assertNotIn('shutil.copy(', code)

    def test_contract_rejects_bad_types_axes_step_and_ranges(self):
        for kwargs in ({'channels': []}, {'channels': ['Y']}, {'channels': ['X', 'X']}, {'frame_step': 0},
                       {'frame_step': True}, {'start': 1.5, 'end': 5}, {'start': 6, 'end': 5},
                       {'start': 1}, {'ik_controls': 'a'}, {'namespace': '*'}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)
        self.assertEqual(normalize()['channels'], ['Z'])

    def test_inventory_and_schema_without_maya(self):
        self.assertTrue(tool.validate(action='inventory').success)
        self.assertTrue(tool.execute(action='inventory').success)
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(tool.to_mcp_tool()['name'], 'back2origin_v05_gaiv3')
        self.assertEqual(tool.to_openai_tool()['function']['parameters']['properties']['action']['enum'], ACTIONS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
