import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.stagger_gui import StaggerGuiTool
    TOOL=StaggerGuiTool()
from maya_toolkit.tools.stagger_gui.tool import normalize
PKG=Path(sys.modules['maya_toolkit.tools.stagger_gui'].__file__).parent


class Offline(unittest.TestCase):
    def test_complete_assets_credits_and_lazy_import(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(12,len(catalog['files']))
        for row in catalog['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
            if not row['path'].endswith('.py'):
                self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['path']).read_bytes()).hexdigest())
        self.assertEqual(8,len(list((PKG/'images').glob('*.svg'))))
        ui=(PKG/'ui.py').read_text(encoding='utf-8')
        self.assertEqual(catalog['original_functions'],[n.name for n in ast.parse(ui).body if isinstance(n,ast.FunctionDef)])
        self.assertIn("__author__ = 'Animation Creation'",ui)
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('stagger_gui',TOOL.to_mcp_tool()['name'])

    def test_range_and_slider_guards(self):
        for bad in ({},{'start':0,'end':2},{'start':True,'end':8},{'start':0,'end':8,'amount':float('inf')},{'start':0,'end':8,'amount':2},{'start':0,'end':8,'objects':[]},{'start':0,'end':8,'objects':['a','a']},{'start':0,'end':8,'unknown':1}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        self.assertEqual(3.1,normalize(start=-10,end=-7)['amount'])


if __name__=='__main__':
    unittest.main(verbosity=2)
