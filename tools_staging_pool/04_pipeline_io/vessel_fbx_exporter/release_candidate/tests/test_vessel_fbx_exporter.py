import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.vessel_fbx_exporter import VesselFbxExporterTool
    TOOL=VesselFbxExporterTool()
from maya_toolkit.tools.vessel_fbx_exporter.tool import normalize
import maya_toolkit.tools.vessel_fbx_exporter as package
class Checks(unittest.TestCase):
    def test_archive_schema_and_reset(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('vessel_fbx_exporter',TOOL.to_mcp_tool()['name']); self.assertEqual(-90,normalize({})['reset_values'][3])
    def test_strict_options(self):
        for p in ({'action':'run_all'},{'reset_transforms':1},{'keyword':'../evil'},{'start':True},{'end':float('nan')},{'reset_values':[0]*8},{'timeout':True},{'output_dir':'relative'}):
            with self.assertRaises(ValueError): normalize(p)
if __name__=='__main__': unittest.main()
