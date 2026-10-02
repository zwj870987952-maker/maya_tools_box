import importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Maya process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_sl',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya_toolkit.tools.studiolibrary_patch import runtime,guards
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True)
    def test_pose_full_roundtrip_one_undo_and_preflight(self):
        parent=cmds.createNode('transform',name='parent');node=cmds.createNode('transform',name='control',parent=parent);cmds.setAttr(parent+'.tx',10);cmds.setAttr(node+'.tx',3);cmds.select(node);cmds.currentTime(7)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'test.wpose');result=tool.run(action='save_pose',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertTrue((Path(p)/'pose.json').is_file());self.assertTrue((Path(p)/'world_pose.json').is_file())
            cmds.setAttr(node+'.tx',8);cmds.flushUndo();result=tool.run(action='load_pose',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertAlmostEqual(cmds.xform(node,q=True,ws=True,t=True)[0],13);self.assertEqual(cmds.currentTime(q=True),7);self.assertEqual(cmds.ls(sl=True),[node]);cmds.undo();self.assertAlmostEqual(cmds.getAttr(node+'.tx'),8)
            cmds.setAttr(node+'.rz',lock=True);self.assertFalse(tool.run(action='load_pose',objects=[node],asset_path=p,dry_run=True).success);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),8)
    def test_world_animation_capture_paste_and_bad_last(self):
        node=cmds.createNode('transform',name='control');cmds.setKeyframe(node,at='tx',t=1,v=2);cmds.setKeyframe(node,at='tx',t=3,v=6);cmds.currentTime(9);cmds.select(node)
        result=tool.run(action='capture_animation',objects=[node],frame_start=1,frame_end=3,sample_by=1);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.currentTime(q=True),9)
        wp,wa=runtime.core();world=wa.WorldAnimation(result.data['world_data']);cmds.cutKey(node,clear=True);cmds.setAttr(node+'.tx',20);cmds.flushUndo()
        cmds.undoInfo(openChunk=True)
        try:report=wa.paste_world_animation(world,objects=[node]);cmds.currentTime(9)
        finally:cmds.undoInfo(closeChunk=True)
        self.assertFalse(report['failed']);self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),3);cmds.undo();self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),0);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),20)
        self.assertFalse(tool.validate(action='capture_pose',objects=[node,'absent']).success)
    def test_animation_asset_full_roundtrip(self):
        node=cmds.createNode('transform',name='control');cmds.setKeyframe(node,at='tx',t=1,v=2);cmds.setKeyframe(node,at='tx',t=3,v=6);cmds.currentTime(9);cmds.select(node)
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'test.wanim');result=tool.run(action='save_animation',objects=[node],asset_path=p,frame_start=1,frame_end=3);self.assertTrue(result.success,result.errors);self.assertTrue((Path(p)/'pose.json').exists());self.assertTrue((Path(p)/'world_transform.json').exists())
            cmds.cutKey(node,clear=True);cmds.setAttr(node+'.tx',20);cmds.flushUndo();result=tool.run(action='load_animation',objects=[node],asset_path=p);self.assertTrue(result.success,result.errors);self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),3);cmds.undo();self.assertEqual(cmds.keyframe(node,at='tx',q=True,keyframeCount=True),0);self.assertAlmostEqual(cmds.getAttr(node+'.tx'),20)
if __name__=='__main__':unittest.main()
