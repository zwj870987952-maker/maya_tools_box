import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.fbx_batch_exporter_v7 import FbxBatchExporterV7Tool
    TOOL=FbxBatchExporterV7Tool()
from maya_toolkit.tools.fbx_batch_exporter_v7.tool import normalize,configuration,safe_name
import maya_toolkit.tools.fbx_batch_exporter_v7 as package
class Checks(unittest.TestCase):
    def test_archive_schema_and_legacy_settings(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(2,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('fbx_batch_exporter_v7',TOOL.to_mcp_tool()['name'])
        converted=configuration({'objects':['a b'],'time_ranges':['1.5,3.5'],'asciiCheckBox':True,'export_animation':False})
        self.assertEqual(['a','b'],converted['jobs'][0]['objects']); self.assertEqual(1.5,converted['jobs'][0]['start']); self.assertFalse(converted['options']['export_animation'])
    def test_bad_ranges_names_and_options(self):
        for p in ({},{'jobs':[{'objects':['a'],'start':2,'end':1}]},{'jobs':[{'objects':['a'],'start':True,'end':2}]},{'jobs':[{'objects':['a'],'start':1,'end':2}],'options':{'ascii':1}},{'action':'save_settings','settings_path':'C:/x.json','configuration':{}},{'action':'bake','objects':['a'],'start':0,'end':float('nan')}):
            with self.assertRaises(ValueError): normalize(p)
        for name in ('../bad.fbx','CON.fbx','bad.fbx.','bad:f.fbx'):
            with self.assertRaises(ValueError): safe_name(name)
        with self.assertRaises(ValueError): configuration({'objects':['a'],'time_ranges':[]})
if __name__=='__main__': unittest.main()
