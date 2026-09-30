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
    from maya_toolkit.tools.keyframe_overlap import KeyframeOverlapTool
    TOOL = KeyframeOverlapTool()
from maya_toolkit.tools.keyframe_overlap.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.keyframe_overlap'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_all_source_resources_algorithm_and_ui(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(6, len(catalog['raw_files']))
        for item in catalog['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            self.assertEqual(set(catalog['methods'][cls.name]), {n.name for n in cls.body if isinstance(n, ast.FunctionDef)})
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(any(isinstance(n.func, ast.Name) and n.func.id in ('exec', 'open') for n in calls))
        self.assertFalse(any(isinstance(n.func, ast.Attribute) and n.func.attr in ('urlopen', 'mkdir', 'rename', 'remove') for n in calls))
        self.assertIn('cmds.particle(', (PACKAGE / 'native.py').read_text(encoding='utf-8'))

    def test_schema_and_lazy_maya(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('keyframe_overlap', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'action': 'bad'}, {'objects': ['x', 'x']}, {'objects': ['x.tx']}, {'dynamic': float('nan')}, {'dynamic': 7}, {'distance': 0}, {'offset': -11}, {'smoothness': 1}, {'start': 2, 'end': 2}, {'start': True}, {'extra': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
