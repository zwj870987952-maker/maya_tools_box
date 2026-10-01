import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.skin_weight_transfer import SkinWeightTransferTool
    TOOL=SkinWeightTransferTool()
from maya_toolkit.tools.skin_weight_transfer.algorithms import normalize,task_line,merged_rows
import maya_toolkit.tools.skin_weight_transfer as package


class Checks(unittest.TestCase):
    def test_original_full_source_and_framework(self):
        pkg=Path(package.__file__).parent
        data=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(data['sha256'],hashlib.sha256((pkg/'upstream'/(data['source']+'.original')).read_bytes()).hexdigest())
        tree=ast.parse((pkg/'original_logic.py').read_text(encoding='utf8'))
        self.assertEqual(data['functions'],[n.name for n in tree.body if isinstance(n,ast.FunctionDef)])
        self.assertFalse(any(isinstance(n,ast.Expr) for n in tree.body))
        self.assertEqual('skin_weight_transfer',TOOL.to_mcp_tool()['name'])

    def test_all_task_grammar_exact_flags_and_strict_schema(self):
        row=task_line('a => b => m1,m2 => DelSkin')
        self.assertEqual(['m1','m2'],row['meshes'])
        self.assertTrue(row['remove_source'])
        self.assertIsNone(task_line('a => b')['meshes'])
        self.assertEqual(2,len(normalize({'task_text':'a => b\n\nb => c => mesh'})['tasks']))
        for p in ({},{'tasks':[]},{'tasks':[{'source_joint':'a','target_joint':'b','remove_source':1}]},{'task_text':'a=>b=>m,m'},{'task_text':'a=>b=>m=>Delete'},{'task_text':'a=>b=>m=>DelSkin=>extra'},{'task_text':'a=>b','tasks':[]},{'task_text':'a=>b','unknown':True}):
            with self.assertRaises(ValueError):
                normalize(p)

    def test_original_merge_normalization_preserves_other_and_zero_rows(self):
        values=merged_rows([0.2,0.3,0.5, 0.8,0.4,0.8, 0,0,0],3,0,1)
        self.assertEqual([0,0.5,0.5],values[0])
        self.assertAlmostEqual(0.6,values[1][1])
        self.assertAlmostEqual(0.4,values[1][2])
        self.assertEqual([0,0,0],values[2])
        for args in (([1,0],2,0,0),([1,float('nan')],2,0,1),([1,-0.2],2,0,1),([1],2,0,1)):
            with self.assertRaises(ValueError):
                merged_rows(*args)


if __name__=='__main__':
    unittest.main()
