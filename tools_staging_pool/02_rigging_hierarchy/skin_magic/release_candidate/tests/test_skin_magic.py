import ast
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest
import xml.etree.ElementTree as ET

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.skin_magic import SkinMagicTool
    TOOL=SkinMagicTool()
from maya_toolkit.tools.skin_magic import fileio,ui_support
from maya_toolkit.tools.skin_magic.tool import CATALOG,normalize,COMMANDS
import maya_toolkit.tools.skin_magic as package
PKG=Path(package.__file__).parent


class Checks(unittest.TestCase):
    def test_complete_archive_and_business_definitions(self):
        self.assertEqual(41,len(CATALOG['files']))
        for row in CATALOG['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest(),row['path'])
            if not row['path'].endswith('.py'):
                self.assertEqual(row['sha256'],hashlib.sha256((PKG/'native'/row['path']).read_bytes()).hexdigest())
        tree=ast.parse((PKG/'native/skinMagic.py').read_text(encoding='utf8'))
        functions=[n.name for n in tree.body if isinstance(n,ast.FunctionDef)]
        self.assertEqual(250,len(CATALOG['functions']))
        self.assertTrue(set(CATALOG['functions'])<=set(functions))
        self.assertFalse(any(isinstance(n,(ast.Expr,ast.Try,ast.If)) for n in tree.body))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertFalse(any(isinstance(n.func,ast.Name) and n.func.id in ('exec','eval','open') for n in calls))
        self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr=='undo' for n in calls))
        self.assertFalse(any(isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='pickle' for n in calls))
        self.assertEqual('skin_magic',TOOL.to_mcp_tool()['name'])

    def test_four_complete_ui_languages_no_global_python_callbacks(self):
        for language in ('','chn','eng','jpn'):
            root=ET.fromstring(ui_support.ui_text(language))
            self.assertEqual('skinMagicCandidate',root.find('widget').get('name'))
            self.assertFalse(any(p.get('name','').startswith('+') for p in root.iter('property')))
            filename='skinMagic'+('_'+language if language else '')+'.ui'
            self.assertEqual(101,len(CATALOG['ui_controls'][filename]))
            for row in CATALOG['ui_controls'][filename]:
                self.assertIn(row['function'],COMMANDS)
            for e in root.iter():
                if e.tag=='normaloff' and e.text:
                    self.assertTrue(Path(e.text).is_file(),e.text)

    def test_strict_arguments_no_unimplemented_dynamic_function_entry(self):
        for args in ({'weights':{}},{'action':'set_weights','weights':{'a':float('nan')}},{'action':'set_weights','weights':{'a':0.2}},{'action':'ui_command','command':'springApplyCmd'},{'action':'show_ui','language':'xx'},{'action':'ui_command','command':'renameMakeCmd','allow_scene_scope':1},{'action':'inspect_skin','objects':['a','a']},{'action':'import_weights'},{'action':'status','path':'x'}):
            with self.assertRaises(ValueError,msg=str(args)):
                normalize(args)
        self.assertEqual('status',normalize({})['action'])

    def test_safe_roundtrip_exclusive_files_reject_pickle_nonfinite_and_xml_entities(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'weights.VertexWeight')
            values={'mesh.vtx[0]':[['j1',0.4],['j2',0.6]]}
            fileio.write(path,'weights',values)
            self.assertEqual(values,fileio.read(path,'weights'))
            with self.assertRaises(FileExistsError):
                fileio.write(path,'weights',values)
            original=Path(path).read_bytes()
            self.assertEqual(original,Path(path).read_bytes())
            malicious=Path(folder)/'unsafe.VertexWeight'
            malicious.write_bytes(b'\x80\x04cos\nsystem\n(S\'bad\'\ntR.')
            with self.assertRaises(ValueError):
                fileio.read(str(malicious),'weights')
            xml=Path(folder)/'bad.xml'
            xml.write_text('<!DOCTYPE root [<!ENTITY x SYSTEM "file:///private">]><root>&x;</root>')
            with self.assertRaises(ValueError):
                fileio.xml_tree(str(xml))
            lod=str(Path(folder)/'rig.BoneList')
            fileio.write(lod,'lod',{'a':'b'})
            self.assertEqual({'a':'b'},fileio.read(lod,'lod'))
            for values in ({'mesh.vtx[0]':[['a',float('inf')]]},{'mesh.vtx[0]':[['a',0.4],['a',0.6]]},{'mesh.vtx[0]':[['a',1.1]]}):
                with self.assertRaises(ValueError):
                    fileio.validate_data({'format':'skin_magic/1','kind':'weights','data':values},'weights')

    def test_original_string_algorithms(self):
        tree=ast.parse((PKG/'native/skinMagic.py').read_text(encoding='utf8'))
        selected=ast.Module(body=ast.parse('import re').body+[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('replaceString','addString','find_between')],type_ignores=[])
        scope={}
        exec(compile(selected,'original_pure_helpers','exec'),scope)
        self.assertEqual('Left_ARM',scope['replaceString']('Left_Bone','Bone','ARM'))
        self.assertEqual('abNEWcd',scope['addString']('abcd','NEW',False,False,True,2))
        self.assertEqual('value',scope['find_between']('a<value>b','<','>'))


if __name__=='__main__':
    unittest.main()
