import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.batch_importer_v3 import BatchImporterV3Tool
    TOOL=BatchImporterV3Tool()
from maya_toolkit.tools.batch_importer_v3.tool import normalize,namespace_base
import maya_toolkit.tools.batch_importer_v3 as package


class Checks(unittest.TestCase):
    def test_archive_schema_and_names(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('batch_importer_v3',TOOL.to_mcp_tool()['name']); self.assertEqual('shot_asset_v3',namespace_base('shot.asset.v3.ma')); self.assertEqual('file_12',namespace_base('12.ma'))

    def test_strict_rows_ranges_actions_and_scope(self):
        for p in ({},{'items':[]},{'items':[{'path':'relative.ma'}]},{'items':[{'path':'C:/x.ma','count':True}]},{'items':[{'path':'C:/x.ma','count':0}]},{'items':[{'path':'C:/x.ma','namespace':'a:b'}]},{'action':'delete'},{'action':'remove_reference','items':[{'path':'C:/x.ma'}]},{'action':'remove_reference','objects':['a'],'reference_nodes':['r']}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
