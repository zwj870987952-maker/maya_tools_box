import ast
import hashlib
import io
import json
from pathlib import Path
import pickle
import runpy
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.cvwrap_weightdriver import CvWrapWeightDriverTool
    TOOL=CvWrapWeightDriverTool()
from maya_toolkit.tools.cvwrap_weightdriver import runtime,safe_data
from maya_toolkit.tools.cvwrap_weightdriver.tool import normalize
import maya_toolkit.tools.cvwrap_weightdriver as package
PKG=Path(package.__file__).parent


class Checks(unittest.TestCase):
    def test_complete_all_originals_native_resources_and_definitions(self):
        data=json.loads((PKG/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(532,len(data['files']))
        self.assertEqual(363,len(data['definitions']))
        self.assertEqual(4614,sum(len(v) for v in data['definitions'].values()))
        for row in data['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest(),row['path'])
            if not row['path'].endswith('.py'):
                self.assertEqual(row['sha256'],hashlib.sha256((PKG/'native'/row['path']).read_bytes()).hexdigest(),row['path'])
        for path,names in data['definitions'].items():
            tree=ast.parse((PKG/'native'/path).read_bytes())
            actual=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
            self.assertEqual(sorted(names),sorted(actual),path)
        self.assertEqual('cvwrap_weightdriver',TOOL.to_mcp_tool()['name'])

    def test_full_ui_icon_closure_and_no_automatic_usersetup(self):
        ui_files=list((PKG/'native').rglob('*.ui'))
        self.assertEqual(80,len(ui_files))
        for path in ui_files:
            ET.parse(path)
        data=json.loads((PKG/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(29,len(data['menu_icon_fallbacks']))
        for name in data['menu_icon_fallbacks']:
            ET.parse(PKG/'native/icons'/name)
        tree=ast.parse((PKG/'native/userSetup.py').read_bytes())
        self.assertTrue(all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) for n in tree.body))
        self.assertIn('mGear_menu_loader',[n.name for n in tree.body if isinstance(n,ast.FunctionDef)])

    def test_schema_and_namespace_conflict_without_importing_third_party(self):
        self.assertEqual('status',normalize({})['action'])
        for p in ({'action':'delete'},{'action':'status','radius':0.1},{'action':'create_wrap','radius':float('inf')},{'action':'create_wrap','new_bind_mesh':1},{'action':'load_plugin','plugin':'other','path':'x'},{'action':'rebind','wrap':'x'},{'action':'import_binding','wrap':'x'},{'action':'create_wrap','objects':['x','x']}):
            with self.assertRaises(ValueError):
                normalize(p)
        fake=types.ModuleType('mgear')
        fake.__file__='/another/mgear/__init__.py'
        original=sys.modules.get('mgear')
        sys.modules['mgear']=fake
        try:
            with self.assertRaises(RuntimeError):
                runtime.namespace_preflight()
        finally:
            if original is None:
                del sys.modules['mgear']
            else:
                sys.modules['mgear']=original

    def test_exclusive_external_path_and_data_only_binary_skin_compatibility(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bind.wrap'
            self.assertEqual(path,runtime.path_output(str(path)))
            path.write_bytes(b'existing opaque binding')
            with self.assertRaises(ValueError):
                runtime.path_output(str(path))
            self.assertEqual(path,runtime.path_input(str(path)))
        values={'objs':['body'],'objDDic':[{'weights':{'joint':[0.2,0.8]},'skinningMethod':0}]}
        self.assertEqual(values,safe_data.load_basic_pickle(io.BytesIO(pickle.dumps(values))))
        class Evil:
            def __reduce__(self):
                return eval,('1/0',)
        with self.assertRaises(ValueError):
            safe_data.load_basic_pickle(io.BytesIO(pickle.dumps({'unsafe':Evil()})))


if __name__=='__main__':
    unittest.main()
