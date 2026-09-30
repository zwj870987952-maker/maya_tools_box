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
    from maya_toolkit.tools.bh_wave_it import WaveItTool
    TOOL = WaveItTool()
from maya_toolkit.tools.bh_wave_it.contracts import normalize, values
PACKAGE = Path(sys.modules['maya_toolkit.tools.bh_wave_it'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_full_source_and_resource_hashes(self):
        catalog = TOOL.execute(action='inventory').data
        self.assertEqual(10, len(catalog['original_procedures']))
        self.assertEqual(14, len(catalog['runtime_procedures']))
        self.assertEqual(3, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        self.assertEqual([], catalog['runtime_audit']['top_level_lines'])
        source = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
        self.assertIn('float $factor=(6.28/(`size $sel`));', source)
        self.assertIn('`rad_to_deg $math`', source)
        self.assertIn("_u.dispatch('interactive')", source)
        self.assertIn('mtbWI_objects', source)

    def test_strict_contract_and_presets(self):
        for args in [{'amplitude': True}, {'phase': float('nan')}, {'phase': 11}, {'rotate_axes': ['XX']}, {'objects': ['a', 'a']}, {'objects': ['a.vtx[0]']}, {'custom_attributes': ['a.b']}, {'frequency': 2}, {'extra': 1}]:
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertEqual(.5, normalize(action='basic_c', frequency=-1, phase=9)['frequency'])
        self.assertEqual(0, normalize(action='basic_c', phase=9)['phase'])
        self.assertEqual(-.3, normalize(action='invert', frequency=.3)['frequency'])

    def test_schema_and_inventory_no_maya(self):
        self.assertEqual('bh_wave_it', TOOL.to_mcp_tool()['name'])
        self.assertFalse(TOOL.parameters_schema['additionalProperties'])
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)

    def test_first_offset_and_frequency_inside_sine(self):
        args = normalize(amplitude=0, base_offset=5)
        self.assertEqual([-5, 0, 0], values(args, 3))
        args = normalize(action='basic_c', amplitude=.5)
        self.assertGreater(values(args, 4)[1], 28)
        self.assertLess(abs(values(args, 4)[3]), .1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
