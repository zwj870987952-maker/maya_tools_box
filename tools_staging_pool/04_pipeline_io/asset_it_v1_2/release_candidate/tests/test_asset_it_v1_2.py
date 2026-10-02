import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.asset_it_v1_2 import AssetItTool
    TOOL=AssetItTool()
from maya_toolkit.tools.asset_it_v1_2.tool import normalize,inventory,asset_path,PKG


class Checks(unittest.TestCase):
    def test_entire_pristine_suite_and_inventory(self):
        catalog=json.loads((PKG/'catalog.json').read_text(encoding='utf8')); self.assertEqual(978,len(catalog['files'])); self.assertEqual(225,len(catalog['functions']))
        for row in catalog['files']:
            data=(PKG/row['archive']).read_bytes(); self.assertEqual(row['sha256'],hashlib.sha256(data).hexdigest()); self.assertEqual(row['bytes'],len(data))
            if row['path'].endswith('.py'): ast.parse(data)
        data=inventory(normalize({})); self.assertEqual(290,data['count']); self.assertTrue(all(a['thumbnail'] and a['metadata'] for a in data['assets']))
        self.assertEqual('asset_it_v1_2',TOOL.to_mcp_tool()['name']); self.assertFalse(catalog['native_code_modified'])
        meta=asset_path(normalize({'action':'metadata','asset':data['assets'][0]['relative']})); self.assertIsInstance(meta['metadata'],dict)

    def test_scope_namespace_scale_and_fields(self):
        for p in ({'asset':'../escape.ma'},{'asset':'/elsewhere.ma'},{'asset':'a/./b.ma'},{'action':'import_asset','asset':'a.ma'},{'action':'import_asset','asset':'a.ma','namespace':'a:b'},{'action':'import_asset','asset':'a.ma','namespace':'a','scale':True},{'action':'delete'},{'target_dir':'relative'},{'unknown':True}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
