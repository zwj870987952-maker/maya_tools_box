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
    from maya_toolkit.tools.tweener_v1_0_2 import TweenerTool
    TOOL = TweenerTool()
from maya_toolkit.tools.tweener_v1_0_2.tool import normalize
PKG = Path(sys.modules['maya_toolkit.tools.tweener_v1_0_2'].__file__).parent


class Offline(unittest.TestCase):
    def test_all_resources_sources_license_and_algorithms(self):
        data = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(27, len(data['files']))
        for row in data['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG / row['archive']).read_bytes()).hexdigest())
        self.assertTrue((PKG / 'native/LICENSE').is_file())
        original = ast.parse((PKG / 'upstream/mods/tween.py.original').read_bytes())
        port = ast.parse((PKG / 'native/mods/tween.py').read_bytes())
        for name in ('interpolate_between', 'interpolate_towards', 'interpolate_average', 'interpolate_curve_tangent', 'interpolate_default', 'lerp_between', 'lerp_towards'):
            old = next(x for x in original.body if isinstance(x, ast.FunctionDef) and x.name == name)
            new = next(x for x in port.body if isinstance(x, ast.FunctionDef) and x.name == name)
            # The only change in these full algorithms is dict iteration porting.
            old_text = ast.unparse(old).replace('.iteritems()', '.items()')
            self.assertEqual(ast.dump(ast.parse(old_text)), ast.dump(ast.parse(ast.unparse(new))), name)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('tweener_v1_0_2', TOOL.to_mcp_tool()['name'])

    def test_math_exact_unclamped_modes_and_arguments(self):
        tree = ast.parse((PKG / 'native/mods/tween.py').read_bytes())
        scope = {}
        definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('lerp_between', 'lerp_towards')]
        exec(compile(ast.Module(body=definitions, type_ignores=[]), 'complete_legacy_math', 'exec'), scope)
        self.assertEqual(5, scope['lerp_between'](0, 10, 0))
        self.assertEqual(15, scope['lerp_between'](0, 10, 2))
        self.assertEqual(15, scope['lerp_towards'](0, 10, .5, 20))
        for p in ({'blend': float('nan')}, {'blend': True}, {'mode': 'bad'}, {'objects': []}, {'objects': ['a'], 'curves': ['c']}, {'time_range': [2, 1]}, {'key_indices': {'c': [-1]}}, {'action': 'activate_tool', 'blend': 0}):
            with self.assertRaises(ValueError):
                normalize(**p)


if __name__ == '__main__':
    unittest.main(verbosity=2)
