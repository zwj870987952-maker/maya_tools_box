import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.isolate_selected import IsolateSelectedTool
    TOOL=IsolateSelectedTool()
import maya_toolkit.tools.isolate_selected as package
from maya_toolkit.tools.isolate_selected.tool import normalize,validate_snapshot


class Checks(unittest.TestCase):
    def test_archive_and_contract(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']
        self.assertEqual(2,len(rows))
        for row in rows:
            self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('isolate_selected',TOOL.to_mcp_tool()['name'])
        self.assertFalse(TOOL.parameters_schema['additionalProperties'])

    def test_strict_input_and_corrupt_snapshot(self):
        self.assertEqual('isolate',normalize({})['action'])
        for p in ({'objects':[]},{'objects':['a','a']},{'objects':'a'},{'panel':1},{'receipt':'a'},{'action':'restore','objects':['a']},{'unknown':1}):
            with self.assertRaises(ValueError): normalize(p)
        for value in ({},[],{'format':'mtbIsolate-1'}):
            with self.assertRaises(ValueError): validate_snapshot(value)


if __name__=='__main__': unittest.main()
