import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.uv_set_renamer import UVSetRenamerTool
    TOOL=UVSetRenamerTool()
from maya_toolkit.tools.uv_set_renamer.tool import normalize
import maya_toolkit.tools.uv_set_renamer as package


class Checks(unittest.TestCase):
    def test_archive_schema_and_defaults(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('uv_set_renamer',TOOL.to_mcp_tool()['name']); self.assertEqual('inspect',normalize({})['action'])

    def test_strict_types_empty_mapping_and_ascii_names(self):
        for p in ({'action':'merge'},{'renames':{'map1':'x'}},{'action':'rename','renames':{}},{'action':'rename','renames':{'map1':'a;b'}},{'action':'rename','renames':{'map1':1}},{'objects':[]},{'objects':['a','a']}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
