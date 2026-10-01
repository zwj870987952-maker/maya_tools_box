import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya.api import OpenMaya as om
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.unlock_freeze.tool import ATTRS


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.autoKeyframe(state=False)
        self.obj=cmds.polyCube(name='sourceMesh')[0]
        cmds.setAttr(self.obj+'.translate',2,4,6); cmds.setAttr(self.obj+'.rotate',20,30,40); cmds.setAttr(self.obj+'.scale',2,3,4)
        cmds.select(self.obj)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def points(self,node):
        shape=(cmds.listRelatives(node,shapes=True,noIntermediate=True,fullPath=True) or [node])[0]
        selection=om.MSelectionList(); selection.add(shape); path=selection.getDagPath(0)
        points=om.MFnMesh(path).getPoints(om.MSpace.kWorld) if cmds.nodeType(shape)=='mesh' else om.MFnNurbsCurve(path).cvPositions(om.MSpace.kWorld)
        return [(p.x,p.y,p.z) for p in points]

    def near(self,a,b):
        for pa,pb in zip(a,b):
            for x,y in zip(pa,pb): self.assertAlmostEqual(x,y,places=6)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.xform(self.obj,query=True,matrix=True,worldSpace=True),[cmds.getAttr(self.obj+'.'+a,lock=True) for a in ATTRS],self.points(self.obj),cmds.autoKeyframe(query=True,state=True))

    def test_full_original_freeze_world_points_unlock_dry_and_one_undo(self):
        for a in ('tx','ry','sz'): cmds.setAttr(self.obj+'.'+a,lock=True)
        cmds.setAttr(self.obj+'.visibility',lock=True); cmds.autoKeyframe(state=True); before=self.state()
        self.call(dry_run=True); self.assertEqual(before,self.state())
        self.call(); self.assertEqual((0,0,0),cmds.getAttr(self.obj+'.translate')[0]); self.assertEqual((0,0,0),cmds.getAttr(self.obj+'.rotate')[0]); self.assertEqual((1,1,1),cmds.getAttr(self.obj+'.scale')[0])
        self.near(before[6],self.points(self.obj)); self.assertFalse(any(self.state()[5])); self.assertTrue(cmds.getAttr(self.obj+'.v',lock=True)); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        cmds.undo(); self.near(before[6],self.points(self.obj)); self.assertEqual(before[4:6],self.state()[4:6]); self.assertEqual(before[1:4],self.state()[1:4])
        self.call(restore_locks=True); self.assertEqual(before[5],self.state()[5]); self.near(before[6],self.points(self.obj))

    def test_curve_group_hierarchy_and_joint_native_freeze(self):
        curve=cmds.circle(name='controller',normal=(0,1,0))[0]; cmds.setAttr(curve+'.translate',3,4,5); cmds.setAttr(curve+'.rotate',10,20,30)
        before=self.points(curve); self.call(objects=[curve]); self.near(before,self.points(curve)); cmds.undo(); self.near(before,self.points(curve))
        group=cmds.group(self.obj,name='groupRoot'); cmds.setAttr(group+'.translate',4,5,6); cmds.setAttr(group+'.rotate',0,45,0)
        before=self.points(self.obj); self.call(objects=[group]); self.near(before,self.points(self.obj)); cmds.undo(); self.near(before,self.points(self.obj))
        joint=cmds.createNode('joint',name='jointRoot'); child=cmds.createNode('joint',name='jointChild',parent=joint)
        cmds.setAttr(joint+'.ty',5); cmds.setAttr(joint+'.rotate',10,20,30); cmds.setAttr(joint+'.jointOrient',5,10,15); cmds.setAttr(child+'.ty',2)
        position=cmds.xform(child,query=True,translation=True,worldSpace=True)
        self.call(objects=[joint]); self.assertEqual((0,0,0),cmds.getAttr(joint+'.rotate')[0]); self.assertAlmostEqual(5,cmds.getAttr(joint+'.ty'))
        self.near([position],[cmds.xform(child,query=True,translation=True,worldSpace=True)])

    def test_full_preflight_wrong_last_drivers_alias_overlap_instances_and_shared_history(self):
        other=cmds.polyCube(name='badLast')[0]; cmds.lockNode(other,lock=True); before=self.state()
        self.assertFalse(TOOL.run(objects=[self.obj,other]).success); self.assertEqual(before,self.state()); cmds.lockNode(other,lock=False)
        self.assertFalse(TOOL.run(objects=[self.obj,'|sourceMesh']).success)
        cmds.select(self.obj); cmds.setKeyframe(self.obj,attribute='rx'); before=self.state(); self.assertFalse(TOOL.run().success); self.assertEqual(before,self.state()); cmds.cutKey(self.obj,attribute='rx',clear=True)
        group=cmds.group(self.obj,name='group'); self.assertFalse(TOOL.run(objects=[group,self.obj]).success)
        cmds.parent(self.obj,world=True); parent=cmds.createNode('transform',name='instanceParent'); cmds.parent(self.obj,parent,add=True)
        self.assertFalse(TOOL.run(objects=['|sourceMesh']).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
