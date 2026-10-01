import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.world_transform_v4 import WorldTransformV4Tool
    TOOL=WorldTransformV4Tool()
from maya_toolkit.tools.world_transform_v4.tool import normalize,check_snapshot
import maya_toolkit.tools.world_transform_v4 as package


class Checks(unittest.TestCase):
    def test_archive_schema_and_defaults(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('world_transform_v4',TOOL.to_mcp_tool()['name']); self.assertEqual('inspect',normalize({})['action'])

    def test_invalid_inputs_and_strict_json(self):
        for p in ({'action':'delete'},{'objects':[]},{'objects':['a.vtx[0]']},{'path':'x.json'},{'action':'save','path':'x.json'},{'action':'paste','start':1},{'action':'paste','start':10,'end':1},{'action':'paste','max_attempts':True},{'action':'paste','only_keyframes':1},{'action':'paste','max_attempts':0}):
            with self.assertRaises(ValueError): normalize(p)
        s=dict(version=1,linear_unit='cm',angle_unit='deg',rows=[dict(uuid='12345678-1234-1234-1234-123456789abc',path='|a',pos=[0.,1.,2.],rot=[0.,0.,0.],rotate_order=0)])
        checked=check_snapshot(s); checked['rows'][0]['pos'][0]=10; self.assertEqual(0,s['rows'][0]['pos'][0])
        for bad in (dict(s,extra=True),dict(s,rows=s['rows']*2),dict(s,angle_unit='grad'),dict(s,version=True)):
            with self.assertRaises(ValueError): check_snapshot(bad)


if __name__=='__main__': unittest.main()
