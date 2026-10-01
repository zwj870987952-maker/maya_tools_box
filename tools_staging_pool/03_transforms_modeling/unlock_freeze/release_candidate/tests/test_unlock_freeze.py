import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.unlock_freeze import UnlockFreezeTool
    TOOL=UnlockFreezeTool()
from maya_toolkit.tools.unlock_freeze.tool import normalize
import maya_toolkit.tools.unlock_freeze as package


class Checks(unittest.TestCase):
    def test_archive_and_contract(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(1,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('unlock_freeze',TOOL.to_mcp_tool()['name'])
        self.assertFalse(normalize({})['restore_locks'])

    def test_strict_types_and_scope(self):
        for p in ({'objects':[]},{'objects':'a'},{'objects':['a','a']},{'restore_locks':1},{'translate':True}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
