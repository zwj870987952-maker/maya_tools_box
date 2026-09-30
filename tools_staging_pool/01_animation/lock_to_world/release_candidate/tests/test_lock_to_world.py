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
    from maya_toolkit.tools.lock_to_world import LockToWorldTool
    TOOL = LockToWorldTool()
from maya_toolkit.tools.lock_to_world.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.lock_to_world'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_source_and_full_ui_algorithm(self):
        data = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(2, len(data['raw_files']))
        for item in data['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        self.assertEqual(set(data['functions']), {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})
        ui = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(set(data['ui_methods']), {n.name for n in ui.body if isinstance(n, ast.FunctionDef)})
        text = (PACKAGE / 'native.py').read_text(encoding='utf-8')
        self.assertNotIn('loadPlugin', text)
        self.assertIn('range(min, max + 1)', text)
        self.assertIn('selectedTranslation', text)

    def test_lazy_import_schema_and_strict_integer_mask(self):
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('lock_to_world', TOOL.to_mcp_tool()['name'])
        for kwargs in ({'start': 1.5}, {'end': True}, {'objects': ['x', 'x']}, {'objects': ['a.tx']}, {'attributes': ['sx']}, {'attributes': ['tx', 'tx']}, {'attributes': ['tx'], 'use_channel_box': True}, {'start': 2, 'end': 1}, {'unknown': 1}):
            with self.assertRaises(ValueError):
                normalize(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
