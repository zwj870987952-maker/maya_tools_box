import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.batch_processor_v3 import BatchProcessorV3Tool
    TOOL=BatchProcessorV3Tool()
from maya_toolkit.tools.batch_processor_v3.tool import normalize,output_plan,exclusive_copy
import maya_toolkit.tools.batch_processor_v3 as package

class Checks(unittest.TestCase):
    def test_archive_schema_and_rejected_rows(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('batch_processor_v3',TOOL.to_mcp_tool()['name'])
        for p in ({},{'files':[{}]},{'files':['relative.ma']},{'files':['C:/x.ma'],'scripts':[{}]},{'files':['C:/x.ma'],'overwrite':1},{'files':['C:/x.ma'],'timeout':True},{'action':'save_current','scripts':['C:/x.py']},{'action':'delete'}):
            with self.assertRaises(ValueError): normalize(p)

    def test_output_identity_and_exclusive_raw_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); paths=[]
            for folder in ('one','two'):
                source=root/folder/'scene.mb'; source.parent.mkdir(); source.write_bytes(b'binary original\x00'); paths.append(str(source))
            params=normalize(dict(files=paths,base_dir=str(root),save_backup=True,save_after=True)); rows=output_plan(params)['tasks']
            self.assertNotEqual(rows[0]['backup'],rows[1]['backup']); self.assertEqual('.ma',Path(rows[0]['after']).suffix)
            backup=Path(rows[0]['backup']); exclusive_copy(paths[0],backup); self.assertEqual(Path(paths[0]).read_bytes(),backup.read_bytes())
            with self.assertRaises(FileExistsError): exclusive_copy(paths[1],backup)
            with self.assertRaises(ValueError): output_plan(params)

if __name__=='__main__': unittest.main()
