import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.per_frame_bs_fbx import PerFrameBsFbxTool
    TOOL=PerFrameBsFbxTool()
from maya_toolkit.tools.per_frame_bs_fbx.tool import normalize
import maya_toolkit.tools.per_frame_bs_fbx as package
class Checks(unittest.TestCase):
    def test_archive_and_schema(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('per_frame_bs_fbx',TOOL.to_mcp_tool()['name'])
    def test_strict_parameters(self):
        for p in ({'step':0},{'start':True},{'end':float('nan')},{'root':'*'},{'output_group':'a:b'},{'ascii':1},{'action':'build_export'},{'output':'relative.fbx'}):
            with self.assertRaises(ValueError): normalize(p)
if __name__=='__main__': unittest.main()
