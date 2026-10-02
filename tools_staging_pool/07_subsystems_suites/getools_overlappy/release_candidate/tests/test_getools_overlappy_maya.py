import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Isolated Maya only')
import importlib.util
from pathlib import Path
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py');launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
class Tests(unittest.TestCase):
    def test_complete_native_import_no_scene_change_and_com_undo(self):
        cmds.undoInfo(state=True)
        before=cmds.ls(uuid=True)
        from maya_toolkit.tools.getools_overlappy import runtime
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.modules import GeneralWindow,Overlappy,Tools,Rigging,CenterOfMass,Experimental,Transformations
        self.assertEqual(cmds.ls(uuid=True),before)
        self.assertTrue(tool.run(dry_run=True,action='create_com').success);self.assertEqual(cmds.ls(uuid=True),before)
        a=cmds.group(empty=True,name='massA');b=cmds.group(empty=True,name='massB');cmds.setAttr(b+'.tx',10);cmds.select(a)
        old_time=cmds.currentTime(q=True);bounds=(cmds.playbackOptions(q=True,min=True),cmds.playbackOptions(q=True,max=True))
        result=tool.run(action='create_com');self.assertTrue(result.success,result)
        com=result.data['com_object'];uuid=cmds.ls(com,uuid=True)[0]
        self.assertEqual(cmds.ls(selection=True),[a]);self.assertEqual(cmds.currentTime(q=True),old_time)
        self.assertTrue(tool.run(action='add_com_targets',targets=[a,b]).success)
        self.assertAlmostEqual(cmds.getAttr(com+'.tx'),5)
        cmds.undo();self.assertAlmostEqual(cmds.getAttr(com+'.tx'),0)
        self.assertTrue(tool.run(action='delete_com').success);self.assertFalse(cmds.objExists(com))
        cmds.undo();self.assertEqual(cmds.ls(com,uuid=True),[uuid])
        self.assertEqual((cmds.playbackOptions(q=True,min=True),cmds.playbackOptions(q=True,max=True)),bounds)
        result=tool.run(action='activate_com',targets=[a]);self.assertTrue(result.success)
        self.assertFalse(tool.run(action='delete_com').success);self.assertTrue(cmds.objExists(a))
        self.assertFalse(tool.run(dry_run=True,action='show_ui').success)
    def test_foreign_setup_refused_and_preset_global_not_polluted(self):
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.modules import Overlappy,Options
        from maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils import File
        instance=Overlappy.Overlappy(Options.PluginVariables())
        group=cmds.group(empty=True,name=Overlappy.OverlappySettings.nameGroup)
        with self.assertRaises(RuntimeError):instance.ParticleSetupDelete()
        self.assertTrue(cmds.objExists(group))
        fixture=Path(File.__file__).parents[1]/'PRESETS/overlappyDefault.txt'
        data=File.ReadLogic(str(fixture));self.assertIn('flagLayer',data[0]);self.assertFalse(hasattr(File,'flagLayer'))
        cmds.delete(group)
if __name__=='__main__':unittest.main()
