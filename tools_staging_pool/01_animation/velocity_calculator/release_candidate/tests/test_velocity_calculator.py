import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.velocity_calculator import VelocityCalculatorTool
    TOOL = VelocityCalculatorTool()
from maya_toolkit.tools.velocity_calculator.tool import normalize, get_linear_distance
PKG = Path(sys.modules['maya_toolkit.tools.velocity_calculator'].__file__).parent


class Offline(unittest.TestCase):
    def test_source_complete_and_original_distance_expression(self):
        catalog = json.loads((PKG / 'catalog.json').read_text())
        row = catalog['files'][0]
        original = (PKG / row['archive']).read_bytes()
        self.assertEqual(row['sha256'], hashlib.sha256(original).hexdigest())
        tree = ast.parse(original)
        old = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'get_linear_distance')
        new = next(n for n in ast.parse((PKG / 'tool.py').read_bytes()).body if isinstance(n, ast.FunctionDef) and n.name == 'get_linear_distance')
        self.assertEqual(ast.dump(old.body[-1]), ast.dump(new.body[-1]))
        self.assertEqual(5., get_linear_distance([0, 0, 0], [3, 4, 0]))
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('velocity_calculator', TOOL.to_mcp_tool()['name'])

    def test_scope_mode_and_finite_parameter_guards(self):
        for bad in ({'mode': 'bad'}, {'objects': []}, {'objects': ['a', 'a']}, {'frame': float('nan')}, {'mode': 'instant', 'sample_step': 0}, {'mode': 'instant', 'start_frame': 1}, {'sample_step': .5}, {'show_result': 1}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
