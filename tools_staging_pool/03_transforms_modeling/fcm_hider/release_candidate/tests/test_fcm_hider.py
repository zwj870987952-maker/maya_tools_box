import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.fcm_hider import FcmHiderTool
    TOOL=FcmHiderTool()
from maya_toolkit.tools.fcm_hider import runtime
from maya_toolkit.tools.fcm_hider.tool import SETS,normalize
PKG=Path(sys.modules[TOOL.__class__.__module__].__file__).parent


class Checks(unittest.TestCase):
    def test_original_bytes_functions_and_assets(self):
        c=json.loads((PKG/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(57,len(c['files']))
        for row in c['files']: self.assertEqual(row['sha256'],hashlib.sha256((PKG/'upstream'/row['path']).read_bytes()).hexdigest())
        tree=ast.parse((PKG/'native.py').read_text(encoding='utf8'))
        self.assertEqual(sorted(c['definitions']),sorted(n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))))
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='exec' for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) for n in tree.body))
        self.assertEqual('fcm_hider',TOOL.to_mcp_tool()['name'])

    def test_strict_parameters_and_owned_data(self):
        for p in ({'action':'add','objects':['A','A']},{'shape_mode':1},{'action':'mirror','mirror_tolerance':float('nan')},{'action':'export_sets'},{'action':'hide','set':'unknown'},{'action':'inspect','objects':['A']}):
            with self.assertRaises(ValueError): normalize(p)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.json'; value={'format':'mtbFCM-1','sets':{k:[] for k in SETS}}
            p.write_text(json.dumps(value),encoding='utf8'); self.assertEqual(value,runtime.read_sets(str(p)))
            with self.assertRaises(ValueError): runtime.path_check(str(p),True)
            p.write_text('import os; os.system("bad")',encoding='utf8')
            with self.assertRaises(ValueError): runtime.read_sets(str(p))
            with self.assertRaises(ValueError): runtime.path_check(str(Path(d)/'legacy.py'))


if __name__=='__main__': unittest.main()
