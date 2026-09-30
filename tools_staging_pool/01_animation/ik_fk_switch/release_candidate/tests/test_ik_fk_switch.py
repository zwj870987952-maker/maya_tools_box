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
    from maya_toolkit.tools.ik_fk_switch import IKFKTool
    TOOL = IKFKTool()
from maya_toolkit.tools.ik_fk_switch.tool import normalize
from maya_toolkit.tools.ik_fk_switch.runtime import literal_data
PACKAGE = Path(sys.modules['maya_toolkit.tools.ik_fk_switch'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_full_original_sources_and_pro_panel(self):
        data = TOOL.execute(action='inventory').data
        self.assertEqual(3, len(data['raw_files']))
        for row in data['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        self.assertEqual(set(data['functions']), {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        ui = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FkIk_UI')
        self.assertEqual(set(data['ui_methods']), {n.name for n in ui.body if isinstance(n, ast.FunctionDef)})
        self.assertEqual(13, len(data['functions']))
        self.assertEqual(19, len(data['ui_methods']))
        text = (PACKAGE / 'native.py').read_text(encoding='utf-8')
        for name in ('poleVectorPosition', 'ikRPsolver', 'Bake IK >> FK AllKeys', 'Match FK >> IK', 'switchAttrRange', 'orientJoints', 'literal_data'):
            self.assertIn(name, text)
        self.assertNotIn('eval(value)', text)

    def test_schema_and_safe_offset_no_maya_or_pymel_import(self):
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertNotIn('pymel.core', sys.modules)
        self.assertEqual('ik_fk_switch', TOOL.to_mcp_tool()['name'])
        for args in ({'rotOffset': [0, float('nan'), 1]}, {'rotOffset': 'eval'}, {'switchAttrRange': 2}, {'switch0isfk': 1}, {'switchAttr': 'x.tx'}, {'start': 1.5}, {'action': 'bad'}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertEqual([0, 90, -90], literal_data('[0, 90, -90]'))
        with self.assertRaises((ValueError, SyntaxError)):
            literal_data("__import__('os').system('bad')")


if __name__ == '__main__':
    unittest.main(verbosity=2)
