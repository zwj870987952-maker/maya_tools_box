import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.gpu_cache_to_mesh import GpuCacheToMeshTool
    TOOL=GpuCacheToMeshTool()
from maya_toolkit.tools.gpu_cache_to_mesh.tool import normalize
PKG=Path(sys.modules[TOOL.__class__.__module__].__file__).parent


class Checks(unittest.TestCase):
    def test_complete_original_and_protocol(self):
        c=json.loads((PKG/'catalog.json').read_text(encoding='utf8'))
        self.assertEqual(1,len(c['files']))
        for row in c['files']: self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('gpu_cache_to_mesh',TOOL.to_mcp_tool()['name'])
    def test_strict_arguments(self):
        for p in ({'objects':[]},{'objects':['A','A']},{'objects':'A'},{'hide_original':1},{'extra':True}):
            with self.assertRaises(ValueError): normalize(p)
        self.assertTrue(normalize({})['hide_original'])


if __name__=='__main__': unittest.main()
