import ast
import hashlib
from pathlib import Path
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.directional_cycle_tool_v1_1 import DirectionalCycleTool
    TOOL = DirectionalCycleTool()
from maya_toolkit.tools.directional_cycle_tool_v1_1.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.directional_cycle_tool_v1_1'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_source_license_and_complete_algorithm(self):
        catalog = TOOL.execute(action='inventory').data
        self.assertEqual(5, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'algorithms.py').read_text(encoding='utf-8'))
        self.assertTrue(set(catalog['original_functions']) <= {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        self.assertIn('CC BY-SA 4.0', catalog['license'])
        text = (PACKAGE / 'algorithms.py').read_text(encoding='utf-8')
        self.assertNotIn('delete(Constrains[0])', text)
        self.assertNotIn('delete(ConstrainList[0])', text)
        self.assertIn('timeScale=-1', text)
        self.assertIn('CounterRotationValue = FeetAngle - MainRotation', text)
        self.assertIn('_locator_shape(CorrectionLoc[0])', text)

    def test_lazy_inventory_schema_and_contract(self):
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('directional_cycle_tool_v1_1', TOOL.to_mcp_tool()['name'])
        for args in ({'feet_number': 0}, {'feet_number': True}, {'angle': 91}, {'start': float('nan')}, {'controllers': ['a', 'a']}, {'bake': 1}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)

    def test_ui_buttons_and_binding(self):
        text = (PACKAGE / 'native_ui.py').read_text(encoding='utf-8')
        self.assertIn('MayaQWidgetDockableMixin', text)
        self.assertIn('maya_toolkit.core.ui_base', text)
        self.assertIn('SpinBox_FeetNumber.setMinimum(1)', text)
        self.assertIn("bridge.dispatch(self, 'back')", text)
        self.assertNotIn('functions.run_', text)
        self.assertNotIn('PySide2', text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
