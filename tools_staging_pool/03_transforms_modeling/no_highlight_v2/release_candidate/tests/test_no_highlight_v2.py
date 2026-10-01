import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.no_highlight_v2 import NoHighlightTool
    TOOL=NoHighlightTool()
from maya_toolkit.tools.no_highlight_v2.tool import normalize
import maya_toolkit.tools.no_highlight_v2 as package


class Checks(unittest.TestCase):
    def test_source_archive_and_schema(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']
        self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('no_highlight_v2',TOOL.to_mcp_tool()['name'])
        self.assertIn('recover',TOOL.parameters_schema['properties']['action']['enum'])

    def test_strict_inputs(self):
        self.assertEqual('status',normalize({})['action'])
        for p in ({'action':'enable'},{'action':'start','panel':''},{'action':'stop','panel':'a'},{'action':'start','panel':1},{'selection':['a']}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
