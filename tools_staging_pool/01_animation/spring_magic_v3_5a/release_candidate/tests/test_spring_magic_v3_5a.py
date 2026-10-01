import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
import xml.etree.ElementTree as ET

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.spring_magic_v3_5a import SpringMagicTool
    TOOL=SpringMagicTool()
from maya_toolkit.tools.spring_magic_v3_5a.tool import normalize,ACTIONS
from maya_toolkit.tools.spring_magic_v3_5a import runtime,ui_support
PKG=Path(sys.modules['maya_toolkit.tools.spring_magic_v3_5a'].__file__).parent


class Offline(unittest.TestCase):
    def test_complete_archive_and_lazy_framework_import(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(46,len(catalog['files']))
        self.assertEqual(46,runtime.integrity())
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertNotIn('pymel.core',sys.modules)
        self.assertEqual('spring_magic_v3_5a',TOOL.to_mcp_tool()['name'])
        self.assertEqual(list(ACTIONS),TOOL.to_openai_tool()['function']['parameters']['properties']['action']['enum'])
        for row in catalog['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())

    def test_every_original_runtime_function_retained(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        for name,original in catalog['definitions'].items():
            tree=ast.parse((PKG/'native'/name).read_text(encoding='utf-8'))
            names=[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]
            self.assertEqual(sorted(original),sorted(names),name)
        math_original=ast.parse((PKG/'upstream/springMath.py.original').read_text(encoding='utf-8-sig'))
        math_port=ast.parse((PKG/'native/springMath.py').read_text(encoding='utf-8'))
        self.assertEqual(ast.dump(math_original,include_attributes=False),ast.dump(math_port,include_attributes=False))
        original=ast.parse((PKG/'upstream/core.py.original').read_text(encoding='utf-8-sig'))
        port=ast.parse((PKG/'native/core.py').read_text(encoding='utf-8'))
        names={'apply_inertia','apply_wind','detect_collision','detect_plane_hit','compute_up_vector','aim_by_ratio','extend_bone','bakeAnim','preCheckCollision','repeatMoveToPlane','createCapsuleGeometry','addCapsuleSphereConstraint','bindControls','addCapsuleBody'}
        for name in names:
            a=next(n for n in ast.walk(original) if isinstance(n,ast.FunctionDef) and n.name==name)
            b=next(n for n in ast.walk(port) if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False),name)

    def test_all_languages_icons_and_no_resource_rewrites(self):
        hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (PKG/'native').rglob('*.ui')}
        for language in ('','chn','eng','jpn'):
            tree=ET.fromstring(ui_support.ui_text(language))
            widgets={n.attrib.get('name') for n in tree.iter('widget')}
            self.assertTrue({'springApply_Button','springSubDiv_lineEdit','springSpring_lineEdit','springTension_lineEdit','springInertia_lineEdit','springExtend_lineEdit','springLoop_checkBox','springPoseMatch_checkBox','springBind_Button','springBake_Button','springAddBody_Button','springAddPlane_Button','springWind_Button'}<=widgets)
            for n in tree.iter():
                for value in (n.text,n.tail):
                    if value and '/native/icons/' in value:
                        self.assertTrue(Path(value).is_file(),value)
        self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes})
        ui=(PKG/'native/ui.py').read_text(encoding='utf-8')
        show=next(n for n in ast.walk(ast.parse(ui)) if isinstance(n,ast.FunctionDef) and n.name=='show')
        self.assertNotIn('checkUpdate',ast.unparse(show))
        self.assertNotIn('copyfile(',ui)
        self.assertNotIn('execfile(',ui)
        self.assertNotIn('urllib2.urlopen(',ui)

    def test_input_guards(self):
        for bad in ({'x':1},{'action':'wrong'},{'action':'compute'},{'action':'compute','pose_match':True,'subdivision':0},{'action':'compute','pose_match':True,'spring':float('nan')},{'action':'compute','pose_match':True,'start':2,'end':1},{'action':'compute','pose_match':True,'collision':1},{'action':'bind_pose'},{'action':'straight','start':1},{'objects':['a','a']},{'action':'bake_controls','start':True}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        p=normalize(action='compute',pose_match=True)
        self.assertEqual(0.7,p['spring'])
        self.assertEqual(0.7,p['twist'])
        self.assertFalse(p['allow_key_cleanup'])
        self.assertTrue(normalize(action='compute',allow_key_cleanup=True)['allow_key_cleanup'])


if __name__=='__main__':
    unittest.main(verbosity=2)
