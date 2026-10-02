import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_tkm',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.the_key_machine import session
class MayaChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.temp=tempfile.TemporaryDirectory();cls.root=cls.temp.name
    @classmethod
    def tearDownClass(cls):session.close();cls.temp.cleanup()
    def setUp(self):cmds.file(new=True,force=True)
    def test_full_source_pose_copy_paste_one_undo(self):
        node=cmds.createNode('transform',name='control');cmds.setAttr(node+'.tx',7);cmds.select(node)
        result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.copy_pose',objects=[node]);self.assertTrue(result.success,result.errors)
        cmds.setAttr(node+'.tx',22);cmds.flushUndo();result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.paste_pose',objects=[node]);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.getAttr(node+'.tx'),7);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),22)
    def test_bad_last_lock_foreign_delete_and_job_ownership(self):
        node=cmds.createNode('transform',name='control');other=cmds.createNode('transform',name='other');cmds.setAttr(other+'.rz',lock=True);cmds.setAttr(node+'.tx',7)
        result=tool.run(action='invoke',data_root=self.root,operation='TheKeyMachine.mods.keyToolsMod.reset_object_values',objects=[node,other],dry_run=True);self.assertFalse(result.success);self.assertEqual(cmds.getAttr(node+'.tx'),7)
        session.configure(self.root);cmds.select(node)
        with self.assertRaises(ValueError):session.cmdshim.delete(other)
        self.assertTrue(cmds.objExists(other))
        # scriptJobs are inert in standalone Maya; exercise the gate without
        # claiming an actual GUI event lifecycle was validated.
        with self.assertRaises(ValueError):session.cmdshim.scriptJob(kill=987654321,force=True)
if __name__=='__main__':unittest.main()
