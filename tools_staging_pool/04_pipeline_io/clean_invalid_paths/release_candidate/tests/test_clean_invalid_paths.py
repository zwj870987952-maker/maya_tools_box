import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.clean_invalid_paths import CleanInvalidPathsTool
    TOOL=CleanInvalidPathsTool()
from maya_toolkit.tools.clean_invalid_paths.tool import reasons,normalize
import maya_toolkit.tools.clean_invalid_paths as package
class Checks(unittest.TestCase):
    def test_archive_schema_and_character_policies(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(2,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('clean_invalid_paths',TOOL.to_mcp_tool()['name'])
        self.assertTrue(reasons('D:/合法路径/贴图.png')); self.assertEqual([],reasons('D:/é.png','cjk')); self.assertEqual([],reasons('D:/中文.png','replacement')); self.assertTrue(reasons('D:/bad\ufffd.png','replacement')); self.assertEqual([],reasons('missing_ascii.png'))
    def test_strict_scope(self):
        for p in ({'action':'erase'},{'policy':'missing_file'},{'nodes':[]},{'nodes':['*']},{'nodes':[{}]},{'allow_reference_removal':1}):
            with self.assertRaises(ValueError): normalize(p)
if __name__=='__main__': unittest.main()
