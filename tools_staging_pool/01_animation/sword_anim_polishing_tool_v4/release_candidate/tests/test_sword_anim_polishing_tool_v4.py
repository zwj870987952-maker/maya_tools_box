import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.sword_anim_polishing_tool_v4 import SwordAnimPolishTool
    TOOL=SwordAnimPolishTool()
from maya_toolkit.tools.sword_anim_polishing_tool_v4.tool import normalize,ACTIONS
PKG=Path(sys.modules['maya_toolkit.tools.sword_anim_polishing_tool_v4'].__file__).parent


class Offline(unittest.TestCase):
    def test_unmodified_complete_vendor_suite_and_lazy_schema(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertFalse(catalog['vendor_modified'])
        self.assertEqual(9,len(catalog['files']))
        self.assertEqual(57,len(catalog['procedures']))
        self.assertEqual(56,len(catalog['unique_procedures']))
        for row in catalog['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'vendor'/row['path']).read_bytes()).hexdigest())
        src=(PKG/'vendor/sword_anim_polish_tool.mel').read_text(encoding='utf-8-sig')
        self.assertEqual(catalog['procedures'],re.findall(r'^global\s+proc\s+(?:(?:string|float|int|vector)\s*(?:\[\s*\])?\s+)?(\w+)\s*\(',src,re.M))
        self.assertIn('scriptJob -ro 1',src)
        self.assertIn('You may not', (PKG/'vendor/License.txt').read_text())
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('sword_anim_polishing_tool_v4',TOOL.to_mcp_tool()['name'])
        self.assertEqual(list(ACTIONS),TOOL.parameters_schema['properties']['action']['enum'])

    def test_action_specific_schema_guards(self):
        for bad in ({'unknown':1},{'action':'bad'},{'action':'arc_polish','knots':1},{'action':'arc_polish','knots':True},{'action':'arc_polish','show_source':1},{'action':'begin_aim','size':float('nan')},{'action':'bake','start':4,'end':1},{'action':'status','knots':5},{'action':'select_group'},{'objects':['a','a']}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        self.assertEqual(1,normalize(action='begin_aim')['size'])
        self.assertEqual(3,normalize(action='arc_polish')['knots'])


if __name__=='__main__':
    unittest.main(verbosity=2)
