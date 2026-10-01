import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.eblabs_world_space_tools import runtime


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.a=cmds.spaceLocator(name='A')[0]
        for t,v in ((1,2),(5,10),(9,4)):
            cmds.setKeyframe(self.a,attribute='tx',time=t,value=v)
        cmds.currentTime(3); cmds.select(self.a)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.autoKeyframe(query=True,state=True))

    def test_world_roundtrip_readonly_and_undo(self):
        before=self.state()
        result=TOOL.run(action='to_world',objects=[self.a],dry_run=True)
        self.assertTrue(result.success,result.message); self.assertEqual(before,self.state())
        result=TOOL.run(action='to_world',objects=[self.a])
        self.assertTrue(result.success,result.message+' '+str(result.errors))
        ctrl=result.data['native_result'][0]
        self.assertTrue(cmds.objExists(ctrl))
        self.assertEqual([1.,5.,9.],cmds.keyframe(ctrl+'.tx',query=True,timeChange=True))
        self.assertEqual([2.,10.,4.],cmds.keyframe(ctrl+'.tx',query=True,valueChange=True))
        self.assertEqual(3,cmds.currentTime(query=True)); self.assertEqual([self.a],cmds.ls(selection=True))
        cmds.undo(); self.assertFalse(cmds.objExists(ctrl))
        result=TOOL.run(action='to_world',objects=[self.a])
        self.assertTrue(result.success,result.message); ctrl=result.data['native_result'][0]
        self.a=cmds.rename(self.a,'RenamedA')
        snapshot=set(cmds.ls(long=True)); cmds.select(ctrl)
        result=TOOL.run(action='to_local',objects=[ctrl],dry_run=True)
        self.assertTrue(result.success,result.message); self.assertEqual(snapshot,set(cmds.ls(long=True)))
        result=TOOL.run(action='to_local',objects=[ctrl])
        self.assertTrue(result.success,result.message)
        self.assertFalse(cmds.objExists(ctrl))
        self.assertEqual([2.,10.,4.],cmds.keyframe(self.a+'.tx',query=True,valueChange=True))
        cmds.undo(); self.assertTrue(cmds.objExists(ctrl))

    def test_parent_space_snap_scope_guards_and_beta(self):
        b=cmds.spaceLocator(name='B')[0]; cmds.setAttr(b+'.ty',4)
        result=TOOL.run(action='to_parent',objects=[self.a,b])
        self.assertTrue(result.success,result.message)
        ctrl=result.data['native_result'][0]
        self.assertTrue(cmds.listRelatives(ctrl,parent=True)); cmds.undo()
        result=TOOL.run(action='snap',objects=[self.a,b]); self.assertTrue(result.success,result.message)
        self.assertAlmostEqual(cmds.xform(self.a,query=True,worldSpace=True,translation=True)[0],cmds.xform(b,query=True,worldSpace=True,translation=True)[0])
        cmds.undo()
        before=self.state()
        for p in ({'action':'to_world','objects':[self.a,self.a]},{'action':'to_local','objects':[self.a]},{'action':'open_beta'},{'action':'open_ui'}):
            result=TOOL.run(dry_run=True,**p); self.assertFalse(result.success,result.message); self.assertEqual(before,self.state())
        cmds.setAttr(self.a+'.tx',lock=True)
        self.assertFalse(TOOL.run(action='to_world',objects=[self.a],dry_run=True).success)

    def test_copy_all_targets_paths_baked_and_shared_guard(self):
        b=cmds.spaceLocator(name='B')[0]; c=cmds.spaceLocator(name='C')[0]
        result=TOOL.run(action='copy',objects=[self.a,b,c])
        self.assertTrue(result.success,result.message+' '+str(result.errors))
        for node in (b,c):
            self.assertEqual([2.,10.,4.],cmds.keyframe(node+'.tx',query=True,valueChange=True))
        cmds.undo()
        before=set(cmds.ls(long=True))
        result=TOOL.run(action='create_paths',objects=[self.a])
        self.assertTrue(result.success,result.message)
        new=set(cmds.ls(long=True))-before
        self.assertTrue(any(cmds.nodeType(n)=='nurbsCurve' for n in new)); cmds.undo()
        self.assertEqual(before,set(cmds.ls(long=True)))
        result=TOOL.run(action='to_world',objects=[self.a],on_keys=False,start=1,end=5)
        self.assertTrue(result.success,result.message)
        ctrl=result.data['native_result'][0]
        self.assertEqual([1.,2.,3.,4.,5.],cmds.keyframe(ctrl+'.tx',query=True,timeChange=True)); cmds.undo()
        curve=cmds.listConnections(self.a+'.tx',source=True,destination=False)[0]
        cmds.connectAttr(curve+'.output',b+'.tx',force=True)
        before=self.state()
        self.assertFalse(TOOL.run(action='to_world',objects=[self.a],dry_run=True).success)
        self.assertEqual(before,self.state())

    def test_foreign_child_cleanup_and_instance_rejected(self):
        result=TOOL.run(action='to_world',objects=[self.a]); self.assertTrue(result.success,result.message)
        ctrl=result.data['native_result'][0]
        foreign=cmds.group(empty=True,name='foreign'); cmds.parent(foreign,ctrl)
        before=self.state()
        result=TOOL.run(action='to_local',objects=[ctrl],dry_run=True)
        self.assertFalse(result.success); self.assertIn('foreign',result.message); self.assertEqual(before,self.state())
        cmds.file(new=True,force=True)
        a=cmds.group(empty=True,name='instanceA'); b=cmds.group(empty=True,name='instanceB')
        node=cmds.spaceLocator(name='shared')[0]; cmds.parent(node,a); cmds.parent(a+'|'+node,b,add=True)
        self.assertFalse(TOOL.run(action='to_world',objects=[a+'|'+node],dry_run=True).success)


if __name__=='__main__': unittest.main()
