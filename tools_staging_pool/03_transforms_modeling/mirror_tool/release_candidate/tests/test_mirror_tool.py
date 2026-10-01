import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.mirror_tool import MirrorTransformTool
    TOOL=MirrorTransformTool()
import maya_toolkit.tools.mirror_tool as package
from maya_toolkit.tools.mirror_tool.tool import normalize,opposite,mirrored_values


class Checks(unittest.TestCase):
    def test_full_source_ui_and_contract(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']
        self.assertEqual(1,len(rows)); row=rows[0]
        source=(pkg/row['archive']).read_bytes()
        self.assertEqual(row['sha256'],hashlib.sha256(source).hexdigest())
        original=ast.parse(source); native=ast.parse((pkg/'native.py').read_text(encoding='utf8'))
        self.assertEqual({n.name for n in ast.walk(original) if isinstance(n,(ast.ClassDef,ast.FunctionDef))},{n.name for n in ast.walk(native) if isinstance(n,(ast.ClassDef,ast.FunctionDef))})
        self.assertIn('mirror_tool',TOOL.to_mcp_tool()['name'])

    def test_strict_types_tokens_and_formula(self):
        for p in ({'mode':'magic'},{'plane':'X'},{'include_hierarchy':1},{'left':''},{'right':'_L_extra'},{'objects':['a','a']},{'pairs':[]},{'pairs':[{'source':'a'}]},{'pairs':[{'source':'a','target':'b'}],'objects':['a']},{'pairs':[{'source':'a','target':'b'}],'include_hierarchy':True}):
            with self.assertRaises(ValueError): normalize(p)
        self.assertEqual('char_L:hand_R',opposite('char_L:hand_L','_L','_R'))
        self.assertIsNone(opposite('center','_L','_R'))
        with self.assertRaises(ValueError): opposite('a_L_R','_L','_R')
        self.assertEqual([-2,4,6],mirrored_values([2,4,6],[10,20,30],[1,1,1],[1,2,3],'YZ','copy')['translation'])
        self.assertEqual([1,2,3],mirrored_values([2,4,6],[10,20,30],[1,1,1],[1,2,3],'YZ','copy')['rotation'])


if __name__=='__main__': unittest.main()
