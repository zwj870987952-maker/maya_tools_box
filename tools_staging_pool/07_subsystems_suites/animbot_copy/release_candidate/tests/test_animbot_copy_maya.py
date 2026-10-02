import os
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Use isolated runner')
import importlib.util
from pathlib import Path
import sys
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_launcher',ROOT/'launch_candidate.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher);tool=launcher.load_tool()
from maya_toolkit.tools.animbot_copy import workspace

class Tests(unittest.TestCase):
    def test_scene_and_undo_untouched(self):
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',7)
        before=(cmds.ls(uuid=True),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True))
        self.assertTrue(tool.run(dry_run=True,action='apply_preset',preset='Expert').success)
        self.assertTrue(tool.run(action='configure',config={'alignment':'right','active_tools':['slider_ease','slider_tween']}).success)
        self.assertTrue(tool.run(action='apply_preset',preset='Compact').success)
        self.assertEqual((cmds.ls(uuid=True),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True)),before)
        self.assertFalse(tool.run(dry_run=True,action='show_ui').success)
        self.assertNotIn('maya_toolkit.tools.animbot_copy.native.qt',sys.modules)
if __name__=='__main__':unittest.main()
