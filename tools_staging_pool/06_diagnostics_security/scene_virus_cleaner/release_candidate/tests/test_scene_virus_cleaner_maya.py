from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class Tests(unittest.TestCase):
    def test_actual_saved_ma_filtered_and_reopened_without_scene_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);cmds.file(new=True,force=True);cube=cmds.polyCube(name='ReviewCube')[0];cmds.setAttr(cube+'.tx',7)
            cmds.scriptNode(name='vaccine_gene',beforeScript='print("fixture; not run")',scriptType=0,sourceType='python')
            cmds.scriptNode(name='legalScript',beforeScript='print("preserve; text")',scriptType=0,sourceType='python')
            source=root/'source.ma';cmds.file(rename=str(source));cmds.file(save=True,type='mayaAscii',force=True);original=source.read_bytes()
            cmds.setAttr(cube+'.ty',9);cmds.select(cube);before=(cmds.ls(),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True),cmds.getAttr(cube+'.ty'))
            result=tool.run(action='clean',files=[str(source)],output_dir=str(root/'new'));self.assertTrue(result.success,result)
            self.assertEqual((cmds.ls(),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True),cmds.getAttr(cube+'.ty')),before);self.assertEqual(source.read_bytes(),original)
            row=result.data['completed'][0];self.assertEqual(Path(row['backup']).read_bytes(),original)
            cmds.file(row['output'],open=True,force=True,executeScriptNodes=False)
            self.assertTrue(cmds.objExists(cube));self.assertEqual(cmds.getAttr(cube+'.tx'),7);self.assertFalse(cmds.objExists('vaccine_gene'));self.assertTrue(cmds.objExists('legalScript'))
if __name__=='__main__':unittest.main()
