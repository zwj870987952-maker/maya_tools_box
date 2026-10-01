import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.mirror_tool.native import MirrorTool


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.autoKeyframe(state=False)
        self.left=cmds.createNode('transform',name='hand_L'); self.right=cmds.createNode('transform',name='hand_R')
        cmds.setAttr(self.left+'.translate',2,4,6); cmds.setAttr(self.left+'.rotate',10,20,30); cmds.setAttr(self.left+'.scale',2,3,4)
        cmds.select(self.left)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.xform(self.left,query=True,matrix=True,worldSpace=True),cmds.xform(self.right,query=True,matrix=True,worldSpace=True),cmds.autoKeyframe(query=True,state=True))

    def assertMatrix(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=7)

    def test_all_nine_modes_original_formula_matrix_equivalence_dry_and_undo(self):
        original=MirrorTool.__new__(MirrorTool)
        for plane in ('XY','YZ','XZ'):
            for mode in ('orientation','behavior','copy'):
                before=self.state(); self.call(plane=plane,mode=mode,dry_run=True); self.assertEqual(before,self.state())
                self.call(plane=plane,mode=mode); result=self.state()
                self.assertEqual(before[1],result[1]); self.assertEqual(before[2],result[2]); self.assertEqual(before[4],result[4])
                cmds.undo(); self.assertMatrix(before[5],self.state()[5]); self.assertEqual(before[3],self.state()[3])
                self.assertTrue(original.mirror_transform(self.left,self.right,plane,mode))
                self.assertMatrix(result[5],self.state()[5])
                cmds.xform(self.right,matrix=before[5],worldSpace=True)

    def test_both_sides_snapshot_hierarchy_transform_only_and_parent_order(self):
        cmds.setAttr(self.left+'.scale',1,1,1); cmds.setAttr(self.left+'.rotate',0,0,0)
        cmds.setAttr(self.left+'.translate',3,0,0); cmds.setAttr(self.right+'.translate',-7,0,0)
        self.call(objects=[self.left,self.right],plane='YZ')
        self.assertAlmostEqual(7,cmds.getAttr(self.left+'.tx')); self.assertAlmostEqual(-3,cmds.getAttr(self.right+'.tx'))
        cmds.undo()
        childL=cmds.polyCube(name='child_L')[0]; childR=cmds.polyCube(name='child_R')[0]
        cmds.parent(childL,self.left); cmds.parent(childR,self.right)
        cmds.setAttr(childL+'.translate',2,0,0); cmds.setAttr(childR+'.translate',4,0,0)
        before=cmds.xform(childR,query=True,worldSpace=True,translation=True)
        r=self.call(objects=[self.left],include_hierarchy=True,plane='YZ')
        self.assertEqual(2,len(r.data['rows'])); self.assertEqual('|hand_R',r.data['rows'][0]['target'])
        self.assertAlmostEqual(-5,cmds.xform(childR,query=True,worldSpace=True,translation=True)[0])
        self.assertTrue(cmds.objExists('child_RShape'))
        cmds.undo(); self.assertEqual(before,cmds.xform(childR,query=True,worldSpace=True,translation=True))

    def test_all_rows_locked_ambiguity_instance_namespace_and_animated_rejection(self):
        target=cmds.createNode('transform',name='badTarget'); cmds.setAttr(target+'.ry',lock=True)
        before=self.state()
        self.assertFalse(TOOL.run(pairs=[{'source':self.left,'target':self.right},{'source':self.left,'target':target}]).success); self.assertEqual(before,self.state())
        cmds.setKeyframe(self.right,attribute='tx'); before=self.state()
        self.assertFalse(TOOL.run().success); self.assertEqual(before,self.state()); cmds.cutKey(self.right,attribute='tx',clear=True)
        parent=cmds.createNode('transform',name='parent'); cmds.parent(self.right,parent,add=True)
        self.assertFalse(TOOL.run().success); cmds.parent('|parent|hand_R',removeObject=True)
        cmds.namespace(add='character_L'); a=cmds.createNode('transform',name='character_L:wrist_L'); b=cmds.createNode('transform',name='character_L:wrist_R')
        cmds.setAttr(a+'.tx',9); self.call(objects=[a],plane='YZ'); self.assertEqual(-9,cmds.getAttr(b+'.tx'))
        cmds.delete(self.right)
        one=cmds.createNode('transform',name='one'); two=cmds.createNode('transform',name='two')
        cmds.createNode('transform',name='hand_R',parent=one); cmds.createNode('transform',name='hand_R',parent=two)
        before=(set(cmds.ls(long=True)),cmds.undoInfo(query=True,undoName=True))
        self.assertFalse(TOOL.run(objects=[self.left]).success)
        self.assertEqual(before,(set(cmds.ls(long=True)),cmds.undoInfo(query=True,undoName=True)))
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
