import hashlib
import json
from pathlib import Path
import re
import runpy
import sys
import unittest

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').exists():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.shift_animation_v3_2 import ShiftAnimationTool
    TOOL=ShiftAnimationTool()
from maya_toolkit.tools.shift_animation_v3_2.tool import normalize,ACTIONS
PKG=Path(sys.modules['maya_toolkit.tools.shift_animation_v3_2'].__file__).parent


class Offline(unittest.TestCase):
    def test_whole_licensed_distribution_unchanged_and_lazy_import(self):
        cat=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertFalse(cat['vendor_modified'])
        self.assertEqual(6,len(cat['files']))
        self.assertEqual(130,len(cat['procedures']))
        self.assertEqual(129,len(cat['unique_procedures']))
        for row in cat['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'vendor'/row['path']).read_bytes()).hexdigest())
        src=(PKG/'vendor/barnev_Shift_animation_code.mel').read_text(encoding='utf-8-sig')
        names=re.findall(r'^global\s+proc\s+(?:(?:string|float|int|vector)\s*(?:\[\s*\])?\s+)?(\w+)\s*\(',src,re.M)
        self.assertEqual(cat['procedures'],names)
        self.assertIn('deleteAttr -attribute',src)
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('shift_animation_v3_2',TOOL.to_mcp_tool()['name'])
        ui=(PKG/'ui.py').read_text(encoding='utf-8')
        for action in set(ACTIONS)-{'analyze_curve'}:
            self.assertIn(repr(action),ui)

    def test_schema_rejects_invalid_and_inapplicable_inputs(self):
        for bad in ({'unknown':1},{'action':'bad'},{'action':'root_motion','main':'a'},{'action':'auto_path','cv_count':True},{'action':'auto_path','cv_count':0},{'action':'apply_path','easing':-1},{'action':'auto_path','flat':1},{'action':'match','allow_attribute_cleanup':True},{'action':'extract','objects':['a','a']},{'action':'analyze_curve','curve':'a','end_value':float('inf')},{'action':'status','layer':'a'}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        self.assertFalse(normalize(action='root_motion',main='a',pelvis='b').get('allow_attribute_cleanup',False))


if __name__=='__main__':
    unittest.main(verbosity=2)
