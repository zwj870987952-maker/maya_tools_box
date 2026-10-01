import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.overslapper import OverslapperTool
    TOOL = OverslapperTool()
from maya_toolkit.tools.overslapper.settings import normalize, validate_preset
PACKAGE = Path(sys.modules['maya_toolkit.tools.overslapper'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_complete_code_resource_provenance(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(9, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        for rel, original in catalog['source_inventory'].items():
            path = PACKAGE / 'native' / Path(rel).relative_to('overslapper')
            tree = ast.parse(path.read_text(encoding='utf-8'))
            self.assertEqual(set(original['functions']), {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
            for cls, methods in original['classes'].items():
                c = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
                self.assertTrue(set(methods) <= {n.name for n in c.body if isinstance(n, ast.FunctionDef)})
        license = (PACKAGE / 'upstream/LICENSE.txt').read_text(encoding='utf-8')
        self.assertIn('Reverse engineer, copy, modify', license)
        self.assertTrue((PACKAGE / 'upstream/overslapperDocumentation_v1_03.pdf').is_file())

    def test_lazy_api_and_strict_parameters(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertNotIn('PySide6', sys.modules)
        self.assertEqual('overslapper', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'typo': 1}, {'stiffness': float('nan')}, {'strength': True}, {'frame_range': [1, 1]}, {'frame_range': [1, 2.5]}, {'axes': 'xx'}, {'main_axis': 'x+', 'up_axis': 'x-'}, {'stiffness_values': [[1.1]]}, {'new_layer': True, 'target_layer': 'layer'}, {'distance_only': True}, {'overshoot': True, 'overshoot_strength': 0}, {'overshoot_frequency': 3.5}, {'cycle': 1}, {'targets': ['a', 'a']}, {'action': 'write_preset'}):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                normalize(**kwargs)
        self.assertEqual('translation', normalize(mode='translation', strength=0)['mode'])

    def test_full_presets_before_partial_ui_apply(self):
        data = json.loads((PACKAGE / 'native/default.json').read_text(encoding='utf-8'))
        self.assertEqual(data, validate_preset(data))
        extra = json.loads(json.dumps(data))
        extra['base_overlap']['frame_lag'] = '2.5'
        extra['wind']['strength'] = '-1.0'
        self.assertEqual(extra, validate_preset(extra))
        for mutation in (lambda d: d.pop('wind'), lambda d: d['overshoot'].update(frequency='3.0'), lambda d: d['base_overlap'].update(stifness='nan'), lambda d: d['complex_stiffness'].update(curve=['1,0,3', '4,1,3']), lambda d: d['base_overlap'].update(main_axis=6), lambda d: d['wind'].update(option=1)):
            invalid = json.loads(json.dumps(data))
            mutation(invalid)
            with self.assertRaises(ValueError):
                validate_preset(invalid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
