import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.skeleton_generator import SkeletonGeneratorTool
    TOOL = SkeletonGeneratorTool()
from maya_toolkit.tools.skeleton_generator.tool import normalize
import maya_toolkit.tools.skeleton_generator as package


class Checks(unittest.TestCase):
    def test_complete_original_function_and_protocol(self):
        pkg = Path(package.__file__).parent
        c = json.loads((pkg/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(c['sha256'],hashlib.sha256((pkg/'vendor'/(c['source']+'.original')).read_bytes()).hexdigest())
        tree = ast.parse((pkg/'original_logic.py').read_text(encoding='utf8'))
        self.assertEqual(['duplicate_skeleton_hierarchy'],[n.name for n in tree.body if isinstance(n,ast.FunctionDef)])
        self.assertTrue(all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) for n in tree.body))
        self.assertEqual('skeleton_generator',TOOL.to_mcp_tool()['name'])

    def test_strict_name_scope_types(self):
        for p in ({'suffix':''},{'suffix':'_bad:name'},{'suffix':'_bad|path'},{'suffix':'_x;delete'},{'objects':[]},{'objects':['a','a']},{'select_result':1},{'action':'inspect','suffix':'_copy'},{'recursive':True}):
            with self.assertRaises(ValueError):
                normalize(**p)
        self.assertTrue(normalize()['select_result'])


if __name__=='__main__':
    unittest.main()
