import hashlib
import json
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/bh_local_nudge'
else:
    from maya_toolkit.tools.bh_local_nudge import LocalNudgeTool
    load_tool = LocalNudgeTool
    PACKAGE = Path(sys.modules[LocalNudgeTool.__module__].__file__).parent
tool = load_tool()
from maya_toolkit.tools.bh_local_nudge.contracts import normalize


class OfflineTests(unittest.TestCase):
    def test_all_resources_preserved(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['raw_files']), 3)
        for row in catalog['raw_files']:
            archive = PACKAGE / row['path']
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), row['sha256'])

    def test_complete_original_ui_and_guarded_parameterized_algorithm(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['runtime_procedures']), 5)
        self.assertFalse(catalog['runtime_audit']['top_level_lines'])
        code = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        self.assertEqual(code.count('_u.dispatch'), 12)
        self.assertIn('mtbLN_amount', code)
        self.assertIn('require_active()', code)
        self.assertIn('$mods / 4 % 2', code)
        self.assertIn('$mods / 8 % 2', code)
        self.assertNotIn('setKeyframe', code)

    def test_contract_bad_types_amount_axes_modifiers(self):
        for args in ({'amount': 0}, {'amount': float('inf')}, {'amount': True}, {'axis': ''}, {'axis': 1},
                     {'objects': ['a.tx']}, {'ctrl': 1}, {'direction': 'left'}, {'unknown': True}):
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertEqual(normalize(channel='rotate')['amount'], 1)

    def test_schema_inventory_without_maya(self):
        self.assertTrue(tool.validate(action='inventory').success)
        self.assertTrue(tool.execute(action='inventory').success)
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(tool.to_mcp_tool()['name'], 'bh_local_nudge')


if __name__ == '__main__':
    unittest.main(verbosity=2)
