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
    from maya_toolkit.tools.gimbal_lock_fix import GimbalFixTool
    TOOL = GimbalFixTool()
from maya_toolkit.tools.gimbal_lock_fix.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.gimbal_lock_fix'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_full_source_and_native_algorithm_ui(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        for item in catalog['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        algorithm = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'GimbalLockFixer')
        self.assertEqual(set(catalog['source_methods']), {node.name for node in algorithm.body if isinstance(node, ast.FunctionDef)})
        self.assertEqual(8, len(catalog['source_methods']))
        text = (PACKAGE / 'native.py').read_text(encoding='utf-8')
        for item in ('create_gimbal_fix_ui', 'shortest_angle', 'quaternion_slerp', 'reorderIt(', 'quat2 = om.MQuaternion(quat2)', 'threshold=threshold'):
            self.assertIn(item, text)
        self.assertNotIn('cmds.currentTime(t)', text)

    def test_schema_types_and_lazy_import(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('gimbal_lock_fix', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'objects': ['x', 'x']}, {'objects': ['x.rx']}, {'threshold': 0}, {'threshold': float('nan')}, {'samples_per_frame': True}, {'samples_per_frame': 101}, {'start': 2, 'end': 1}, {'action': 'bad'}, {'unused': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
