import ast
import hashlib
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.eblabs_whiskey import WhiskeyTool
    TOOL = WhiskeyTool()
from maya_toolkit.tools.eblabs_whiskey.contracts import normalize
from maya_toolkit.tools.eblabs_whiskey.tool import file_path
PACKAGE = Path(sys.modules['maya_toolkit.tools.eblabs_whiskey'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_complete_resources_and_native_catalog(self):
        catalog = TOOL.execute(action='inventory').data
        self.assertEqual(133, len(catalog['raw_files']))
        for row in catalog['raw_files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PACKAGE / row['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        found = {n.name: {m.name for m in n.body if isinstance(m, ast.FunctionDef)} for n in tree.body if isinstance(n, ast.ClassDef)}
        self.assertEqual(22, len(found))
        self.assertEqual(272, sum(map(len, found.values())))
        for item in catalog['methods']:
            self.assertIn(item['method'], found[item['class']])
        for name in ('slider_tween', 'slider_snapshot', 'slider_worldSpace', 'slider_inOut', 'slider_PosePusher', 'slider_multiply'):
            self.assertIn(name, found)
        self.assertEqual(15, len(catalog['wrapped_scene_methods']))

    def test_schema_lazy_import_and_preference_overwrite(self):
        self.assertTrue(TOOL.validate(action='inventory').success)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('eblabs_whiskey', TOOL.to_mcp_tool()['name'])
        for args in ({'value': float('nan')}, {'value': 2}, {'objects': ['x', 'x']}, {'objects': ['x.tx']}, {'special': 1}, {'start': 1.5}, {'action': 'bad'}, {'x': 1}):
            with self.assertRaises(ValueError):
                normalize(**args)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'prefs.json'
            path.write_text('{}', encoding='utf-8')
            self.assertFalse(TOOL.validate(action='export_preferences', file_path=str(path)).success)
            self.assertTrue(TOOL.validate(action='export_preferences', file_path=str(path), overwrite_file=True).success)
            self.assertTrue(TOOL.validate(action='import_preferences', file_path=str(path)).success)
            path.write_text('[]', encoding='utf-8')
            self.assertFalse(TOOL.validate(action='import_preferences', file_path=str(path)).success)
            with self.assertRaises(ValueError):
                file_path('relative.json')


if __name__ == '__main__':
    unittest.main(verbosity=2)
