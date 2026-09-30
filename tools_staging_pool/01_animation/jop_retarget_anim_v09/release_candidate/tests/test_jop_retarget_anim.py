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
    from maya_toolkit.tools.jop_retarget_anim import JopRetargetTool
    TOOL = JopRetargetTool()
from maya_toolkit.tools.jop_retarget_anim.tool import normalize, snapshot_rows
PACKAGE = Path(sys.modules['maya_toolkit.tools.jop_retarget_anim'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_full_source_resources_and_ui(self):
        catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(6, len(catalog['raw_files']))
        for item in catalog['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        self.assertEqual(set(catalog['functions']), {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        self.assertEqual(14, len(catalog['functions']))
        ui = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(set(catalog['ui_methods']), {n.name for n in ui.body if isinstance(n, ast.FunctionDef)})
        self.assertEqual(3, len(catalog['ui_methods']))
        self.assertNotIn('loadPlugin', (PACKAGE / 'native.py').read_text(encoding='utf-8'))

    def test_lazy_schema_and_snapshot_validation(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('jop_retarget_anim', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'bake': 1}, {'objects': ['a', 'a']}, {'objects': ['a.tx']}, {'start': True}, {'start': 5, 'end': 1}, {'snapshot_data': []}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)
        row = {'node_uuid': 'id', 'reference_uuid': '', 'samples': [{'time': 1, 'matrix': [1.0] * 16}]}
        data = {'format': 'maya_toolkit.jop_retarget_anim.v1', 'records': [row]}
        self.assertEqual([row], snapshot_rows(data))
        for bad in ({}, dict(data, records=[]), dict(data, records=[dict(row, samples=[{'time': True, 'matrix': [0] * 16}])]), dict(data, records=[dict(row, samples=[{'time': 1, 'matrix': [float('nan')] * 16}])])):
            with self.assertRaises(ValueError):
                snapshot_rows(bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
