import hashlib
import json
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/bh_speedlines'
else:
    from maya_toolkit.tools.bh_speedlines import SpeedLinesTool
    load_tool = SpeedLinesTool
    PACKAGE = Path(sys.modules[SpeedLinesTool.__module__].__file__).parent
tool = load_tool()
from maya_toolkit.tools.bh_speedlines.contracts import normalize, ACTIONS


class OfflineTests(unittest.TestCase):
    def test_all_eight_resources_preserved(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['raw_files']), 8)
        for row in catalog['raw_files']:
            file = PACKAGE / row['path']
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), row['sha256'])

    def test_full_suite_ui_and_definition_only(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['original_procedures']), 21)
        self.assertEqual(len(catalog['runtime_procedures']), 22)
        self.assertFalse(catalog['runtime_audit']['top_level_lines'])
        code = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        for text in ('loft -ch 0 -polygon 1', 'polyReduce', 'rebuildCurve', 'SmoothHairCurves', 'polyNormal', 'setKeyframe  -s 0', 'EPCurveTool', 'PencilCurveTool', 'mtbSL_consumeCurves', '_u.dispatch', 'remove_plane_only()', '-closeCommand'):
            self.assertIn(text, code)
        self.assertNotIn('delete "mtbSL_SL_Draw_Plane"', code)
        self.assertNotIn('`scriptJob', code)

    def test_contract_rejects_bad_boolean_camera_objects_and_depth(self):
        for args in ({'on_layer': 1}, {'objects': ['a.cv[0]']}, {'camera': 'a.tx'}, {'depth': float('nan')}, {'depth': True}, {'action': 'unknown'}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertTrue(normalize()['consume_curves'])

    def test_schema_inventory_without_maya(self):
        self.assertTrue(tool.validate(action='inventory').success)
        self.assertTrue(tool.execute(action='inventory').success)
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(tool.to_mcp_tool()['name'], 'bh_speedlines')
        self.assertEqual(tool.to_openai_tool()['function']['parameters']['properties']['action']['enum'], ACTIONS)


if __name__ == '__main__':
    unittest.main(verbosity=2)
