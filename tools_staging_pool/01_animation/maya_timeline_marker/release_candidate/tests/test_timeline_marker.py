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
    from maya_toolkit.tools.timeline_marker import TimelineMarkerTool
    TOOL = TimelineMarkerTool()
from maya_toolkit.tools.timeline_marker import model
from maya_toolkit.tools.timeline_marker.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.timeline_marker'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_whole_source_resources_license_functions_and_gui(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(49, len(catalog['raw_files']))
        for item in catalog['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        for identity, methods in catalog['methods'].items():
            path, name = identity.split(':')
            tree = ast.parse((PACKAGE / 'native' / path).read_text(encoding='utf-8'))
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
            self.assertEqual(methods, [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        for path, functions in catalog['functions'].items():
            tree = ast.parse((PACKAGE / 'native' / path).read_text(encoding='utf-8'))
            self.assertTrue(set(functions) <= {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        self.assertEqual(26, sum(len(v) for v in catalog['methods'].values()))
        self.assertIn('GNU GENERAL PUBLIC LICENSE', (PACKAGE / 'upstream/LICENSE').read_text(encoding='utf-8'))

    def test_schema_strict_and_lazy(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertNotIn('maya_toolkit.tools.timeline_marker.native.ui', sys.modules)
        self.assertEqual('timeline_marker', TOOL.to_mcp_tool()['name'])
        from maya_toolkit.tools.timeline_marker.native import add, remove, clear, set, hotkey, install
        self.assertNotIn('maya_toolkit.tools.timeline_marker.native.ui', sys.modules)
        for a in ({'action': 'add'}, {'action': 'set', 'frames': [1], 'colors': [], 'comments': []}, {'action': 'add', 'frames': [True]}, {'action': 'add', 'frames': [1], 'color': [0, 300, 0]}, {'action': 'inspect', 'frames': [1]}, {'action': 'remap', 'old_range': [1, 1], 'new_range': [2, 3]}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**a)

    def test_remap_snapshots_and_negative_truncation(self):
        data = {'frames': [1, 2, 3, 4], 'colors': [[0, 255, 0]] * 4, 'comments': ['a', 'b', 'c', 'foreign']}
        moved = model.remap(data, [1, 3], [2, 4])
        self.assertEqual(dict(zip(moved['frames'], moved['comments'])), {2: 'a', 3: 'b', 4: 'c'})
        self.assertEqual(data['frames'], [1, 2, 3, 4])
        collapsed = model.remap(data, [1, 3], [9, 9])
        self.assertEqual(dict(zip(collapsed['frames'], collapsed['comments'])), {4: 'foreign', 9: 'c'})
        negative = model.remap(data, [1, 3], [-2, -1])
        self.assertEqual(dict(zip(negative['frames'], negative['comments'])), {4: 'foreign', -2: 'a', -1: 'c'})
        raw = json.dumps(data)
        self.assertEqual(data, model.decode(raw))
        self.assertEqual(data, model.decode(json.dumps(raw)[1:-1]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
