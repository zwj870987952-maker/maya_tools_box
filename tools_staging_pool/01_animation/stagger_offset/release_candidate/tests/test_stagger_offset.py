import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.stagger_offset import StaggerOffsetTool
    TOOL=StaggerOffsetTool()
from maya_toolkit.tools.stagger_offset.tool import normalize,offsets
PKG=Path(sys.modules['maya_toolkit.tools.stagger_offset'].__file__).parent


class Offline(unittest.TestCase):
    def test_original_sources_complete_lazy_and_schema(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(2,len(catalog['files']))
        for row in catalog['files']:
            self.assertEqual(row['sha256'],hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
            source=(PKG/row['archive']).read_text(encoding='utf-8')
            self.assertIn('def deselect_and_offset_frames',source)
            self.assertIn('cmds.showWindow',source)
        self.assertNotIn('maya.cmds',sys.modules)
        self.assertEqual('stagger_offset',TOOL.to_mcp_tool()['name'])

    def test_repeated_remove_offsets_and_rejections(self):
        self.assertEqual([0,5,10,15],offsets(4,5,'batch'))
        self.assertEqual([0,-0.5,-0.5,-0.5],offsets(4,-0.5,'once'))
        for bad in ({'offset':float('nan')},{'offset':True},{'mode':'other'},{'update_selection':1},{'objects':['a']},{'objects':['a','a']},{'unknown':1}):
            with self.assertRaises(ValueError):
                normalize(**bad)


if __name__=='__main__':
    unittest.main(verbosity=2)
