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
    from maya_toolkit.tools.pose_transfer_remote import PoseTransferRemoteTool
    TOOL=PoseTransferRemoteTool()
from maya_toolkit.tools.pose_transfer_remote.tool import normalize
PKG=Path(sys.modules['maya_toolkit.tools.pose_transfer_remote'].__file__).parent


class Offline(unittest.TestCase):
    def test_all_original_methods_resources_and_lazy_schema(self):
        c=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        for row in c['raw_files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/'upstream'/row['path']).read_bytes()).hexdigest())
        native=(PKG/'native.py').read_bytes()
        self.assertEqual(c['native_sha256'],hashlib.sha256(native).hexdigest())
        klass=next(n for n in ast.parse(native).body if isinstance(n,ast.ClassDef))
        self.assertEqual(set(c['methods']),{n.name for n in klass.body if isinstance(n,ast.FunctionDef)})
        self.assertEqual(9,len(c['methods']))
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('pose_transfer_remote',TOOL.to_mcp_tool()['name'])

    def test_strict_inputs(self):
        for kw in ({'action':'bad'},{'root':''},{'controllers':['a','a']},{'controllers':[]},{'allow_reference_edits':1},{'unknown':3}):
            with self.assertRaises(ValueError):
                normalize(**kw)


if __name__=='__main__':
    unittest.main(verbosity=2)
