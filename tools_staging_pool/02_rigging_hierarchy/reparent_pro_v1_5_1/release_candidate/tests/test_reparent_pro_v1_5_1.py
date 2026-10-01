import hashlib
import json
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve()
RC = HERE.parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.reparent_pro_v1_5_1 import ReParentProTool
    TOOL = ReParentProTool()
from maya_toolkit.tools.reparent_pro_v1_5_1.tool import normalize, ACTIONS
import maya_toolkit.tools.reparent_pro_v1_5_1 as package
PKG = Path(package.__file__).parent


class Checks(unittest.TestCase):
    def test_whole_original_assets_and_every_business_procedure(self):
        catalog = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(13, len(catalog['original_procedures']))
        for row in catalog['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG / 'vendor' / row['path']).read_bytes()).hexdigest())
        adapted = (PKG / 'native.mel').read_text(encoding='utf-8')
        for row in catalog['original_procedures']:
            self.assertIn('proc rppstg_' + row['name'] + '(', adapted)
        self.assertNotIn('($currentL+":"+$currentR)', adapted)
        self.assertIn('($currentR+":"+$currentL)', adapted)
        self.assertNotIn('`checkBox -q -v ', adapted)
        self.assertTrue(catalog['original_top_level_ui_deferred'])
        self.assertIn('global proc rppstg_showUI()', (PKG / 'native_ui.mel').read_text(encoding='utf-8'))

    def test_schema_and_strict_types(self):
        self.assertEqual(ACTIONS, TOOL.parameters_schema['properties']['action']['enum'])
        for p in ({'action': 'unknown'}, {'action': 'inspect', 'pin': True}, {'objects': []}, {'objects': ['a', 'a']}, {'frame_range': [5, 1]}, {'frame_range': [1, True]}, {'allow_clear_animation': 1}, {'action': 'relative', 'pin': True}, {'action': 'reparent', 'bake_on_layer': True}, {'action': 'manual_go', 'objects': ['a']}):
            with self.assertRaises(ValueError):
                normalize(**p)
        self.assertEqual([1, 4], normalize(action='reparent', frame_range=[1, 4])['frame_range'])
        self.assertEqual('reparent_pro_v1_5_1', TOOL.to_mcp_tool()['name'])


if __name__ == '__main__':
    unittest.main()
