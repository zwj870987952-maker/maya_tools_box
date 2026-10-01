import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').exists():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0,str(RC))
    from maya_toolkit.tools.root_motion_bake import RootMotionBakeTool
    TOOL=RootMotionBakeTool()
from maya_toolkit.tools.root_motion_bake.tool import normalize
PKG=Path(sys.modules['maya_toolkit.tools.root_motion_bake'].__file__).parent


class Offline(unittest.TestCase):
    def test_whole_original_and_no_automatic_ui(self):
        cat=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(13,len(cat['methods']))
        for row in cat['raw_files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'upstream'/row['path']).read_bytes()).hexdigest())
        src=(PKG/'native.py').read_bytes()
        self.assertEqual(cat['native_sha256'],hashlib.sha256(src).hexdigest())
        tree=ast.parse(src)
        klass=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        self.assertEqual(set(cat['methods']),{n.name for n in klass.body if isinstance(n,ast.FunctionDef)})
        self.assertFalse(any(isinstance(n,ast.Try) for n in tree.body))
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('root_motion_bake',TOOL.to_mcp_tool()['name'])

    def test_strict_schema_inputs(self):
        for kw in ({'unknown':1},{'action':'bad'},{'maintain_offset':1},{'snapshot_center':1},{'groups':[]},{'groups':[{'root':'a'}]},{'translate_axes':['z','z']},{'rotate_axes':['q']},{'start':1},{'start':float('nan'),'end':3},{'time_range':'explicit'}):
            with self.assertRaises(ValueError):
                normalize(**kw)
        self.assertIsNone(normalize(groups=[{'root':'a','center':'b'}])['groups'][0].get('ring'))


if __name__=='__main__':
    unittest.main(verbosity=2)
