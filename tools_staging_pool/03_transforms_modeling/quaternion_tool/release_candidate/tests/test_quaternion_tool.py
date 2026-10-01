import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.quaternion_tool import QuaternionMathTool
    TOOL=QuaternionMathTool()
from maya_toolkit.tools.quaternion_tool.tool import normalize,ACTIONS
import maya_toolkit.tools.quaternion_tool as package


class Checks(unittest.TestCase):
    def test_full_math_and_ui_definitions_archive_contract(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']
        self.assertEqual(1,len(rows)); row=rows[0]; source=(pkg/row['archive']).read_bytes()
        self.assertEqual(row['sha256'],hashlib.sha256(source).hexdigest())
        original=ast.parse(source); native=ast.parse((pkg/'native.py').read_text(encoding='utf8'))
        self.assertEqual({n.name for n in ast.walk(original) if isinstance(n,(ast.ClassDef,ast.FunctionDef))},{n.name for n in ast.walk(native) if isinstance(n,(ast.ClassDef,ast.FunctionDef))})
        self.assertEqual(11,len(ACTIONS)); self.assertEqual('quaternion_tool',TOOL.to_mcp_tool()['name'])

    def test_strict_action_numeric_and_scope_types(self):
        self.assertEqual([0,0,0],normalize({})['euler'])
        for p in ({'action':'unknown'},{'euler':[1,2]},{'euler':[True,2,3]},{'euler':[float('nan'),2,3]},{'euler':[1e13,2,3]},{'action':'slerp','t':'0.5'},{'action':'to_euler','axis':[1,0,0]},{'action':'apply','objects':[]},{'action':'apply','objects':['a','a']}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
