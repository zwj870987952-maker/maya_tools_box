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
    from maya_toolkit.tools.cg_shake_py3 import CgShakeTool
    TOOL = CgShakeTool()
from maya_toolkit.tools.cg_shake_py3.contracts import normalize, preset_data
PACKAGE = Path(sys.modules['maya_toolkit.tools.cg_shake_py3'].__file__).parent
PRESET = {'Frame': 1, **{c: 5 for c in ['TX', 'TY', 'TZ', 'RX', 'RY', 'RZ']}, 'Points': '0,1,3,1,0,3'}


class OfflineTests(unittest.TestCase):
    def test_complete_source_images_and_native_surface(self):
        data = TOOL.execute(action='inventory').data
        self.assertEqual(7, len(data['raw_files']))
        for row in data['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        source = (PACKAGE / 'native_ui.py').read_text(encoding='utf-8')
        cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))
        self.assertTrue(set(data['original_methods']).issubset({n.name for n in cls.body if isinstance(n, ast.FunctionDef)}))
        self.assertIn('mtbCGShakeFalloffCurve', source)
        self.assertIn('vignetteFrame.png', source)
        self.assertNotIn('mayaMainWindowPtr', source)
        self.assertNotIn('loadPlugin(', source)
        self.assertNotIn('six.moves', source)
        self.assertEqual(4, len(list((PACKAGE / 'images').glob('*.png'))))

    def test_strict_contract_and_preset_triplets(self):
        for args in [{'step': 0}, {'step': True}, {'amounts': {'tx': 1}}, {'falloff_samples': [float('nan')]}, {'object': 'a.x'}, {'overwrite_file': 1}, {'seed': '0'}, {'unknown': 1}]:
            with self.assertRaises(ValueError):
                normalize(**args)
        for value in [dict(PRESET, Frame=0), dict(PRESET, Points='0,1'), dict(PRESET, Points='0,2,3,1,0,3'), dict(PRESET, Points='0,1,4,1,0,3')]:
            with self.assertRaises(ValueError):
                preset_data(value)
        self.assertEqual(PRESET, preset_data(PRESET))

    def test_readonly_file_plan_and_no_maya_inventory(self):
        with tempfile.TemporaryDirectory() as scratch:
            target = Path(scratch) / 'new/preset.cgsk'
            result = TOOL.validate(action='save_preset', file_path=str(target), preset=PRESET)
            self.assertTrue(result.success, result.message)
            self.assertFalse(target.parent.exists())
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertEqual('cg_shake_py3', TOOL.to_mcp_tool()['name'])
        self.assertNotIn('maya.cmds', sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
