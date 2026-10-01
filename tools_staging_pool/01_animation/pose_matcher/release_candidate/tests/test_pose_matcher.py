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
    from maya_toolkit.tools.pose_matcher import PoseMatcherTool
    TOOL = PoseMatcherTool()
from maya_toolkit.tools.pose_matcher.tool import normalize, validate_map
PACKAGE = Path(sys.modules['maya_toolkit.tools.pose_matcher'].__file__).parent


class Offline(unittest.TestCase):
    def test_full_source_and_lazy_schema(self):
        data = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(55, len(data['original_functions']))
        self.assertEqual(data['raw_sha256'], hashlib.sha256((PACKAGE / 'upstream/PoseMatcher.py.original').read_bytes()).hexdigest())
        source = (PACKAGE / 'native.py').read_bytes()
        self.assertEqual(data['native_sha256'], hashlib.sha256(source).hexdigest())
        names = {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
        self.assertFalse(set(data['original_functions']) - names)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('pose_matcher', TOOL.to_mcp_tool()['name'])

    def test_strict_inputs(self):
        for bad in ({'overwrite': 1}, {'action': 'bad'}, {'decimals': True}, {'decimals': -1}, {'meshes': ['a', 'a']}, {'joint_map': {'root:x': 'y'}}, {'frame': 3}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        self.assertEqual({'s': 't'}, validate_map({'s': 't'}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
