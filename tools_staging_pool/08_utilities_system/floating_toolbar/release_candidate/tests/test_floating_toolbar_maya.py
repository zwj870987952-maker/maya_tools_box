import importlib.util,os,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.floating_toolbar import session
class Checks(unittest.TestCase):
    def test_python_statements_mel_language_and_explicit_execution(self):
        cmds.file(new=True,force=True);node=cmds.createNode('transform',name='control');cmds.setAttr(node+'.tx',7)
        class Button:command="import maya.cmds as cmds\nvalue=9\ncmds.setAttr('control.tx',value)";source_type='python'
        with self.assertRaises(ValueError):session.execute_button(Button())
        self.assertEqual(cmds.getAttr(node+'.tx'),7);cmds.flushUndo();session.execute_button(Button(),True);self.assertEqual(cmds.getAttr(node+'.tx'),9);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),7)
        button=Button();button.source_type='mel';button.command='setAttr control.tx 13';cmds.flushUndo();session.execute_button(button,True);self.assertEqual(cmds.getAttr(node+'.tx'),13);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),7)
if __name__=='__main__':unittest.main()
