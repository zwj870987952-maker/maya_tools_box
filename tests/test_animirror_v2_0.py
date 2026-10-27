"""Offline schemas, complete source extraction and ownership architecture checks."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
    PACKAGE = RC / 'maya_toolkit/tools/animirror_v2_0'
else:
    from maya_toolkit.tools.animirror_v2_0 import AnimirrorV2Tool
    load_tool = AnimirrorV2Tool
    PACKAGE = Path(sys.modules[AnimirrorV2Tool.__module__].__file__).parent
tool = load_tool()
from maya_toolkit.tools.animirror_v2_0.contracts import normalize, ACTIONS


class OfflineTests(unittest.TestCase):
    def test_all_raw_resources_preserved(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['raw_files']), 2)
        for row in catalog['raw_files']:
            archive = PACKAGE / row['path']
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), row['sha256'])
            original = RC.parent / archive.name
            if original.exists():
                self.assertEqual(original.read_bytes(), archive.read_bytes())

    def test_full_extracted_algorithm_and_window_present(self):
        code = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['original_procedures']), 9)
        self.assertEqual(len(catalog['runtime_procedures']), 11)
        self.assertFalse(catalog['runtime_audit']['top_level_lines'])
        self.assertIn('mirrorJoint -mirrorXY -mirrorBehavior', code)
        self.assertIn('makeIdentity', code)
        self.assertIn('shadingNode -asUtility floatMath', code)
        self.assertIn('delete -sc;', code)
        self.assertIn('filterCurve;', code)
        self.assertIn('Interactive Mirror', code)
        self.assertIn('Mirror with Bake', code)
        self.assertNotIn('shelfButton', code)
        self.assertNotIn('delete $mtbAV2_centerJoint', code)
        self.assertIn('_av2ui.dispatch', code)
        self.assertIn('require_active()', code)

    def test_parameter_contract_rejects_wrong_axis_boolean_count_and_ranges(self):
        for kwargs in ({'translation_axis': 'XY'}, {'translations': 1}, {'objects': ['a', 'b']}, {'objects': ['a.tx', 'b', 'c']},
                       {'invert_rotation': ['X', 'X']}, {'start': 2, 'end': 1}, {'start': float('nan'), 'end': 3}, {'unknown': True}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)
        self.assertEqual(normalize()['translation_axis'], 'X')
        self.assertEqual(normalize()['invert_rotation'], ['Y', 'Z'])

    def test_schema_exports_and_inventory_without_maya_scene(self):
        self.assertEqual(tool.category, 'animation')
        self.assertEqual(tool.to_mcp_tool()['name'], 'animirror_v2_0')
        self.assertEqual(set(tool.to_openai_tool()['function']['parameters']['properties']['action']['enum']), set(ACTIONS))
        self.assertTrue(tool.validate(action='inventory').success)
        result = tool.execute(action='inventory')
        self.assertTrue(result.success)
        self.assertEqual(len(result.data['original_procedures']), 9)

    def test_source_top_level_calls_removed_without_losing_internal_reset(self):
        original = (PACKAGE / 'embedded_original.mel').read_text(encoding='utf-8')
        adapted = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        self.assertIn('globals_variables();', original)
        self.assertIn('    mtbAV2_globals_variables();', adapted)
        self.assertNotIn('\nmtbAV2_globals_variables();', adapted)
        self.assertNotIn('\nmtbAV2_aniMirror_menu();', adapted)


if __name__ == '__main__':
    unittest.main(verbosity=2)
