import ast
import hashlib
import json
from pathlib import Path
import pickle
import runpy
import sys
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.shape_animation_tool import ShapeAnimationTool
    TOOL = ShapeAnimationTool()
from maya_toolkit.tools.shape_animation_tool.tool import normalize
from maya_toolkit.tools.shape_animation_tool.utils import decode_legacy
PKG = Path(sys.modules['maya_toolkit.tools.shape_animation_tool'].__file__).parent


class Offline(unittest.TestCase):
    def test_distribution_complete_and_import_is_lazy(self):
        cat = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(39,len(cat['raw_files']))
        self.assertEqual(6,len(cat['variants']))
        self.assertEqual(34,sum(map(len,cat['classes'].values())))
        for row in cat['raw_files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'upstream'/row['path']).read_bytes()).hexdigest())
        for name,digest in cat['ported_sha256'].items():
            self.assertEqual(digest,hashlib.sha256((PKG/name).read_bytes()).hexdigest())
        tree=ast.parse((PKG/'native.py').read_bytes())
        classes={n.name:[f.name for f in n.body if isinstance(f,ast.FunctionDef)] for n in tree.body if isinstance(n,ast.ClassDef)}
        self.assertEqual(cat['classes'],classes)
        self.assertFalse(any(isinstance(n,ast.Try) for n in tree.body))
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertNotIn('PySide6',sys.modules)
        self.assertEqual('shape_animation_tool',TOOL.to_mcp_tool()['name'])

    def test_contract_and_legacy_primitive_reader(self):
        for bad in ({'a':1},{'action':'bad'},{'frame':True},{'action':'begin_sculpt','frame':float('nan')},{'action':'set_enabled','enabled':1},{'action':'step_key','direction':'none'},{'action':'adopt_legacy'},{'action':'status','mesh':'a'},{'session':''}):
            with self.assertRaises(ValueError):
                normalize(**bad)
        self.assertEqual(['ns:a_LR1'],decode_legacy(str(pickle.dumps(['ns:a_LR1'],protocol=2))))
        self.assertEqual(False,decode_legacy(pickle.dumps(False,protocol=0).decode('latin1')))
        # A GLOBAL/REDUCE payload is rejected before any callable can run.
        with self.assertRaises(ValueError):
            decode_legacy("cos\nsystem\n(S'echo unexpected'\ntR.")


if __name__=='__main__':
    unittest.main(verbosity=2)
