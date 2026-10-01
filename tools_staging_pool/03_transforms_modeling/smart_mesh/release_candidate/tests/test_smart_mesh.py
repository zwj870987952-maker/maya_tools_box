import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.smart_mesh import SmartMeshTool
    TOOL=SmartMeshTool()
from maya_toolkit.tools.smart_mesh.tool import normalize
from maya_toolkit.tools.smart_mesh.install import command
import maya_toolkit.tools.smart_mesh as package


class Checks(unittest.TestCase):
    def test_original_full_mel_readme_and_schema(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(2,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        raw=(pkg/'upstream/dpSmartMeshTools.mel').read_text(encoding='utf8')
        for entry in ('dpSmartCombine','dpSmartSeparate','dpSmartExtractDuplicate','dpSmartMeshToolButton','stHotkey','stMenuHotkey','stAbout'): self.assertIn('proc '+entry,raw)
        self.assertEqual('smart_mesh',TOOL.to_mcp_tool()['name'])
        for i in range(5):
            self.assertNotIn('staging',command(i)); compile(command(i),'installedcommand','exec')

    def test_strict_action_install_and_selection(self):
        for p in ({'action':'smart'},{'custom_names':1},{'objects':[]},{'objects':['a','a']},{'action':'duplicate','objects':['a']},{'action':'hotkey','key':' '},{'action':'hotkey','key':'a','alt':1},{'action':'hotkey','option':4,'key':'a'},{'action':'shelf','option':True}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
