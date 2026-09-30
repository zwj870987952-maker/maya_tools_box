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
    from maya_toolkit.tools.keyframe_reduction import KeyframeReductionTool
    TOOL = KeyframeReductionTool()
from maya_toolkit.tools.keyframe_reduction.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.keyframe_reduction'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_whole_archive_python3_full_algorithm_and_ui(self):
        data = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(60, len(data['raw_files']))
        for item in data['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        for identity, names in data['methods'].items():
            path, name = identity.split(':')
            tree = ast.parse((PACKAGE / 'native' / path).read_text(encoding='utf-8'))
            cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == name)
            self.assertEqual(names, [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        self.assertEqual(12, len(data['methods']))
        self.assertEqual(68, sum(len(v) for v in data['methods'].values()))
        self.assertTrue((PACKAGE / 'upstream/LICENSE').is_file())
        self.assertTrue((PACKAGE / 'upstream/icons/KR_icon.png').is_file())
        self.assertIn('PySide6', (PACKAGE / 'native/ui.py').read_text(encoding='utf-8'))

    def test_lazy_schema_and_types(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('keyframe_reduction', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'curves': ['a', 'a']}, {'curves': ['a.tx']}, {'error': 0}, {'step': 0}, {'weightedTangents': 1}, {'error': float('nan')}, {'action': 'bad'}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
