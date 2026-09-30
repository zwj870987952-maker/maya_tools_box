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
    from maya_toolkit.tools.brs_smooth_mocap import SmoothMocapTool
    TOOL = SmoothMocapTool()
from maya_toolkit.tools.brs_smooth_mocap.contracts import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.brs_smooth_mocap'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_raw_and_bundled_resources(self):
        catalog = TOOL.execute(action='inventory').data
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        self.assertTrue((PACKAGE / 'backend/upstream/BRSLocTransfer.py').exists())
        self.assertIn('maya_toolkit.brs_smooth_mocap.v1', (PACKAGE / 'backend/scene.py').read_text(encoding='utf-8'))
        source = (PACKAGE / 'runtime.py').read_text(encoding='utf-8')
        self.assertNotIn('scriptsDir', source)
        self.assertNotIn('exec(', source)

    def test_exact_original_average_ast(self):
        old = ast.parse((PACKAGE / 'upstream/BRSSmoothMocap.py').read_text(encoding='utf-8-sig'))
        old = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'valueAverage')
        new = ast.parse((PACKAGE / 'algorithms.py').read_text(encoding='utf-8')).body[-1]
        new.body = new.body[1:]
        self.assertEqual(ast.dump(old, include_attributes=False), ast.dump(new, include_attributes=False))

    def test_schema_contract_and_no_maya_inventory(self):
        for args in [{'strength': True}, {'strength': 0}, {'strength': 101}, {'root_joint': 'a.x'}, {'curves': ['a', 'a']}, {'selected_only': 1}, {'extra': 1}]:
            with self.assertRaises(ValueError):
                normalize(**args)
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertEqual('brs_smooth_mocap', TOOL.to_mcp_tool()['name'])
        self.assertNotIn('maya.cmds', sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
