import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Disposable isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC=Path(__file__).resolve().parents[1]
TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.pose_transfer_remote import runtime


class Maya(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        cmds.namespace(add='rig')
        self.root=cmds.createNode('transform',name='rig:ROOT_ctrl')
        self.child=cmds.createNode('transform',name='rig:hand_ctrl',parent=self.root)
        cmds.setAttr(self.child+'.tx',2)
        cmds.setAttr(self.child+'.rz',30)
        cmds.select(self.root)
        cmds.currentTime(5)
        cmds.autoKeyframe(state=True)

    def ok(self,**kw):
        r=TOOL.run(**kw)
        self.assertTrue(r.success,str((r.message,r.errors)))
        return r.data

    def state(self):
        return [cmds.currentTime(q=True),cmds.ls(sl=True,long=True),cmds.autoKeyframe(q=True,state=True),cmds.namespaceInfo(currentNamespace=True),cmds.namespace(q=True,relativeNames=True)]

    def test_dry_detect_scoped_and_direct_body_guard(self):
        external=cmds.createNode('transform',name='foreign_ctrl')
        control_set=cmds.sets([external,self.child],name='rig:ControlSet')
        cmds.select(self.root)
        before,names,undo=self.state(),sorted(cmds.ls(long=True)),cmds.undoInfo(q=True,undoName=True)
        detected=self.ok(action='detect',root=self.root,control_set=control_set)
        self.assertEqual(2,len(detected['controllers']))
        self.assertNotIn(external,detected['controllers'])
        self.ok(dry_run=True,action='capture',root=self.root)
        self.assertEqual(before,self.state())
        self.assertEqual(names,sorted(cmds.ls(long=True)))
        self.assertEqual(undo,cmds.undoInfo(q=True,undoName=True))
        from maya_toolkit.tools.pose_transfer_remote.native import PoseTransfer
        with self.assertRaises(ValueError):
            PoseTransfer().create_locators_and_record_pose()

    def test_capture_shift_repeat_apply_cleanup_undo_scene_roundtrip(self):
        before=self.state()
        capture=self.ok(action='capture',root=self.root,controllers=[self.child,self.root])
        locs=capture['locators']
        self.assertEqual(2,len(locs))
        self.assertEqual(before,self.state())
        cmds.setAttr(self.root+'.tx',10)
        self.ok(action='shift')
        positions=[cmds.xform(n,q=True,ws=True,t=True) for n in locs]
        self.ok(action='shift')
        self.assertEqual(positions,[cmds.xform(n,q=True,ws=True,t=True) for n in locs])
        cmds.setAttr(self.child+'.tx',7)
        self.ok(action='apply')
        self.assertAlmostEqual(12,cmds.xform(self.child,q=True,ws=True,t=True)[0])
        self.assertAlmostEqual(30,cmds.getAttr(self.child+'.rz'))
        cmds.undo()
        self.assertAlmostEqual(17,cmds.xform(self.child,q=True,ws=True,t=True)[0])
        cmds.redo()
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'pose.ma')
            cmds.file(rename=path);cmds.file(save=True,type='mayaAscii')
            cmds.file(path,open=True,force=True)
            self.ok(action='inspect')
            self.ok(action='cleanup')
            self.assertTrue(all(not cmds.objExists(n) for n in locs))
            cmds.undo()
            self.assertTrue(all(cmds.objExists(n) for n in locs))
            self.ok(action='shift')

    def test_foreign_child_locked_and_tampered_controller_refused(self):
        cap=self.ok(action='capture',root=self.root)
        loc=cap['locators'][0]
        foreign=cmds.createNode('transform',name='foreignChild',parent=loc)
        self.assertFalse(TOOL.run(action='cleanup').success)
        self.assertTrue(cmds.objExists(foreign))
        cmds.delete(foreign)
        cmds.setAttr(self.child+'.sx',lock=True)
        self.assertFalse(TOOL.run(action='apply').success)
        cmds.setAttr(self.child+'.sx',lock=False)
        cmds.setAttr(loc+'.original_controller','persp',type='string')
        self.assertFalse(TOOL.run(action='apply').success)

    def test_partial_capture_failure_context_restore_and_undo(self):
        before=self.state()
        from maya_toolkit.tools.pose_transfer_remote import native
        original=native.cmds.xform
        count=[0]
        def fail(*args,**kw):
            if kw.get('worldSpace') and 'matrix' in kw and not kw.get('query'):
                count[0]+=1
                if count[0]==2:
                    raise RuntimeError('injected second helper xform')
            return original(*args,**kw)
        with patch.object(native.cmds,'xform',side_effect=fail):
            r=TOOL.run(action='capture',root=self.root)
            self.assertFalse(r.success)
        self.assertEqual(before,self.state())
        self.assertFalse(runtime.session()['complete'])
        self.assertFalse(TOOL.run(action='apply').success)
        cmds.undo()
        self.assertIsNone(runtime.session())

    def test_uuid_rename_and_deleted_control_cleanup(self):
        cap=self.ok(action='capture',root=self.root)
        self.root=cmds.rename(self.root,'rig:renamedRoot')
        self.child=cmds.rename('|rig:renamedRoot|rig:hand_ctrl','rig:renamedChild')
        self.ok(action='apply')
        self.assertTrue(cmds.objExists(self.child))
        cmds.delete(self.root)
        self.ok(action='cleanup')
        self.assertIsNone(runtime.session())
        self.assertTrue(all(not cmds.objExists(n) for n in cap['locators']))


if __name__=='__main__':
    unittest.main(verbosity=2)
