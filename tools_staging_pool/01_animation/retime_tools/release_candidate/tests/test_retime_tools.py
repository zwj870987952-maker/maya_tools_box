import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.retime_tools import RetimeToolsTool
    TOOL = RetimeToolsTool()
from maya_toolkit.tools.retime_tools.tool import normalize
from maya_toolkit.tools.retime_tools.runtime import read_keys, inverse_lookup
PKG = Path(sys.modules['maya_toolkit.tools.retime_tools'].__file__).parent


class Offline(unittest.TestCase):
    def test_whole_original_suite_and_lazy_import(self):
        cat = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(28,len(cat['raw_files']))
        self.assertEqual(211,sum(map(len,cat['classes'].values())))
        self.assertEqual(38,len(cat['mel_procedures']))
        for row in cat['raw_files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'upstream'/row['path']).read_bytes()).hexdigest())
        for f in ('native','engine'):
            self.assertEqual(cat[f+'_sha256'],hashlib.sha256((PKG/(f+'.py')).read_bytes()).hexdigest())
        native = {n.name:{m.name for m in n.body if isinstance(m,ast.FunctionDef)} for n in ast.parse((PKG/'native.py').read_bytes()).body if isinstance(n,ast.ClassDef)}
        self.assertEqual({k:set(v) for k,v in cat['classes'].items()},native)
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('retime_tools',TOOL.to_openai_tool()['function']['name'])

    def test_parsers_and_zero_negative_inverse(self):
        from types import SimpleNamespace
        lookup = SimpleNamespace(sections=[{-2:-4,0:0,2:4}],value_time_cache={})
        self.assertEqual([(0.0,2.0)],inverse_lookup(lookup,0))
        self.assertEqual([(-0.5,2.0)],inverse_lookup(lookup,-1))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'c.txt'
            p.write_text('-2 -4\n0 0\n2 4\n',encoding='utf-8')
            self.assertEqual([(-2,-4),(0,0),(2,4)],read_keys(str(p))[1])
            p.write_text('nan 3\n2 4\n',encoding='utf-8')
            with self.assertRaises(ValueError):
                read_keys(str(p))
        for kw in ({'unknown':1},{'action':'bad'},{'clean':1},{'nodes':[]},{'nodes':['a','a']}):
            with self.assertRaises(ValueError):
                normalize(**kw)


if __name__=='__main__':
    unittest.main(verbosity=2)
