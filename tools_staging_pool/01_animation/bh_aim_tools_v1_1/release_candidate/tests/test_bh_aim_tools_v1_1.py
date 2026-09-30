import hashlib
import json
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/bh_aim_tools_v1_1'
else:
    from maya_toolkit.tools.bh_aim_tools_v1_1 import BhAimTool
    load_tool = BhAimTool
    PACKAGE = Path(sys.modules[BhAimTool.__module__].__file__).parent
tool = load_tool()
from maya_toolkit.tools.bh_aim_tools_v1_1.contracts import normalize, ACTIONS


class OfflineTests(unittest.TestCase):
    def test_all_four_original_resources_preserved(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['raw_files']), 4)
        for row in catalog['raw_files']:
            archive = PACKAGE / row['path']
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), row['sha256'])

    def test_complete_suite_definition_only_and_original_ui(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['original_procedures']), 16)
        self.assertEqual(len(catalog['runtime_procedures']), 17)
        self.assertFalse(catalog['runtime_audit']['top_level_lines'])
        code = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        for text in ('Create Aim Locator', 'Attach Locator To Control', 'Aim Control At Locator', 'Key Control From Aim Locator', 'aimConstraint -mo', 'filterCurve', 'cutKey -cl'):
            self.assertIn(text, code)
        self.assertIn('delete_locator()', code)
        self.assertIn('delete_parent_constraints()', code)
        self.assertNotIn('delete $target;', code)
        self.assertNotIn('confirmDialog', code)
        self.assertIn('return $tempNull[0];', code)

    def test_explicit_rotation_deletion_and_bad_contracts(self):
        for args in ({'action': 'unknown'}, {'keys_only': 1}, {'objects': ['a.tx']}, {'start': 5, 'end': 1},
                     {'start': 1.2, 'end': 5}, {'delete_rotation_keys': True},
                     {'action': 'bake', 'keys_only': False, 'delete_rotation_keys': True}):
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertFalse(normalize()['delete_rotation_keys'])
        self.assertTrue(normalize(action='bake', delete_rotation_keys=True)['delete_rotation_keys'])

    def test_inventory_schema_without_maya(self):
        self.assertTrue(tool.validate(action='inventory').success)
        self.assertTrue(tool.execute(action='inventory').success)
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(tool.to_mcp_tool()['name'], 'bh_aim_tools_v1_1')
        self.assertEqual(tool.to_openai_tool()['function']['parameters']['properties']['action']['enum'], ACTIONS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
