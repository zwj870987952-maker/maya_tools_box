import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.fcm_hider import runtime


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.a=cmds.polyCube(name='R_arm')[0]; self.b=cmds.polyCube(name='L_arm')[0]
        self.other=cmds.polyCube(name='untouched')[0]; cmds.select(self.a)
        result=TOOL.run(action='initialize'); self.assertTrue(result.success,result.message)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.autoKeyframe(query=True,state=True))

    def test_full_system_members_visibility_dry_and_undo(self):
        before=self.state(); result=TOOL.run(action='add',objects=[self.a],dry_run=True)
        self.assertTrue(result.success,result.message); self.assertEqual(before,self.state())
        result=TOOL.run(action='add',objects=[self.a]); self.assertTrue(result.success,result.message)
        self.assertEqual(0,cmds.getAttr(self.a+'.visibility')); self.assertEqual(1,cmds.getAttr(self.other+'.visibility'))
        self.assertIn(self.a,cmds.sets('mtbFCM:Head_Hider',query=True))
        cmds.undo(); self.assertEqual(1,cmds.getAttr(self.a+'.visibility')); self.assertFalse(cmds.sets('mtbFCM:Head_Hider',query=True))
        result=TOOL.run(action='add',objects=[self.a],set='Torso_Hider'); self.assertTrue(result.success,result.message)
        self.assertTrue(TOOL.run(action='show',set='Torso_Hider').success); self.assertEqual(1,cmds.getAttr(self.a+'.visibility'))
        self.assertTrue(TOOL.run(action='hide_all').success); self.assertEqual(0,cmds.getAttr(self.a+'.visibility'))
        self.assertTrue(TOOL.run(action='show_all').success); self.assertEqual(1,cmds.getAttr(self.a+'.visibility'))

    def test_mirror_JSON_no_overwrite_and_cleanup_Undo(self):
        result=TOOL.run(action='add',objects=[self.a],set='Arm_R_Hider'); self.assertTrue(result.success,result.message)
        result=TOOL.run(action='mirror'); self.assertTrue(result.success,result.message)
        self.assertIn(self.b,cmds.sets('mtbFCM:Arm_L_Hider',query=True))
        with tempfile.TemporaryDirectory() as d:
            path=str(Path(d)/'sets.json')
            self.assertTrue(TOOL.run(action='export_sets',path=path).success)
            self.assertFalse(TOOL.run(action='export_sets',path=path).success)
            self.assertTrue(TOOL.run(action='clear_body').success)
            self.assertTrue(TOOL.run(action='import_sets',path=path).success)
            self.assertIn(self.a,cmds.sets('mtbFCM:Arm_R_Hider',query=True))
        before=set(cmds.ls(long=True)); result=TOOL.run(action='cleanup'); self.assertTrue(result.success,result.message)
        self.assertTrue(cmds.objExists(self.a)); self.assertTrue(cmds.objExists(self.other)); self.assertFalse(cmds.objExists('mtbFCM:FCM_Hider_Settings'))
        cmds.undo(); self.assertEqual(before,set(cmds.ls(long=True)))

    def test_face_scope_and_unlock_keeps_other_mesh(self):
        face=self.a+'.f[0]'
        result=TOOL.run(action='add',objects=[face],shape_mode=True,set='Extra_One_Hider'); self.assertTrue(result.success,result.message)
        self.assertTrue(cmds.sets(face,isMember='mtbFCM:Extra_One_Hider'))
        self.assertEqual(1,cmds.getAttr(self.other+'.visibility'))
        self.assertTrue(TOOL.run(action='show',set='Extra_One_Hider').success)
        self.assertTrue(TOOL.run(action='add',objects=[self.a],set='Head_Hider').success)
        cmds.setAttr(self.a+'.overrideDisplayType',2); cmds.setAttr(self.other+'.overrideDisplayType',2)
        self.assertTrue(TOOL.run(action='unlock_visible').success)
        self.assertEqual(0,cmds.getAttr(self.a+'.overrideDisplayType')); self.assertEqual(2,cmds.getAttr(self.other+'.overrideDisplayType'))
        cmds.undo(); self.assertEqual(2,cmds.getAttr(self.a+'.overrideDisplayType'))

    def test_foreign_collision_lock_GUI_and_child_guards(self):
        before=self.state(); self.assertFalse(TOOL.run(action='open_ui',dry_run=True).success); self.assertEqual(before,self.state())
        cmds.namespace(add='mtbFCMforeign'); cmds.group(empty=True,name='mtbFCMforeign:FCM_Hider_Settings')
        self.assertFalse(TOOL.run(action='initialize',system='mtbFCMforeign',dry_run=True).success)
        cmds.setAttr(self.a+'.visibility',lock=True)
        self.assertFalse(TOOL.run(action='add',objects=[self.a],dry_run=True).success)
        cmds.setAttr(self.a+'.visibility',lock=False)
        child=cmds.group(empty=True,name='foreignChild'); cmds.parent(child,'mtbFCM:FCM_Hider_Settings')
        self.assertFalse(TOOL.run(action='cleanup',dry_run=True).success)


if __name__=='__main__': unittest.main()
