import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.replace_references import ReplaceReferencesTool
    TOOL=ReplaceReferencesTool()
from maya_toolkit.tools.replace_references.tool import normalize
import maya_toolkit.tools.replace_references as package
class Checks(unittest.TestCase):
    def test_archive_schema_and_all_variants(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(3,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('replace_references',TOOL.to_mcp_tool()['name'])
        code=(pkg/'ui.py').read_text(encoding='utf8'); self.assertIn('class ReferenceReplacementTool',code); self.assertIn('def replaceReferenceUI',code); self.assertIn('def replace_references_in_maya',code)
    def test_strict_selection_and_empty_rules(self):
        for p in ({},{'action':'delete'},{'action':'batch','files':[]},{'new_file':'relative.ma'},{'rename_namespace':1},{'reference_nodes':['*']},{'reference_nodes':['a'],'objects':['b']},{'action':'batch','reference_nodes':['a']}):
            with self.assertRaises(ValueError): normalize(p)
if __name__=='__main__': unittest.main()
