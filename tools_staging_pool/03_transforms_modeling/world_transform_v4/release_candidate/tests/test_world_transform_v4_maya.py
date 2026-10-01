import json
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


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.currentUnit(linear='cm',angle='deg')
        self.parent=cmds.createNode('transform',name='parent'); self.child=cmds.createNode('transform',name='child',parent=self.parent)
        cmds.setAttr(self.parent+'.translate',2,4,6); cmds.setAttr(self.parent+'.rotate',20,30,40)
        cmds.setAttr(self.child+'.translate',1,2,3); cmds.setAttr(self.child+'.rotate',12,25,35)
        cmds.select(self.child,self.parent); cmds.currentTime(2.5); cmds.autoKeyframe(state=False)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def pose(self,n): return cmds.xform(n,query=True,worldSpace=True,matrix=True)

    def close(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=5)

    def test_hierarchy_current_uuid_and_undo(self):
        poses=[self.pose(n) for n in (self.parent,self.child)]
        before=(cmds.ls(long=True),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True))
        self.call(dry_run=True); self.assertEqual(before,(cmds.ls(long=True),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True)))
        s=self.call(action='copy').data['snapshot']
        self.parent=cmds.rename(self.parent,'renamedParent'); self.child=cmds.listRelatives(self.parent,children=True,fullPath=True)[0]
        cmds.setAttr(self.parent+'.translate',8,9,10); cmds.setAttr(self.parent+'.rotate',1,2,3); cmds.setAttr(self.child+'.translate',7,8,9)
        changed=[self.pose(n) for n in (self.parent,self.child)]; selection=cmds.ls(selection=True,long=True)
        cmds.autoKeyframe(state=True); queue=cmds.undoInfo(query=True,undoName=True)
        self.call(action='paste',snapshot=s,dry_run=True); self.assertEqual(queue,cmds.undoInfo(query=True,undoName=True)); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        self.call(action='paste',snapshot=s)
        for n,expected in zip((self.parent,self.child),poses): self.close(self.pose(n),expected); self.assertEqual([2.5],cmds.keyframe(n,attribute='translateX',query=True,timeChange=True))
        self.assertEqual(selection,cmds.ls(selection=True,long=True)); self.assertEqual(2.5,cmds.currentTime(query=True)); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        cmds.undo()
        for n,expected in zip((self.parent,self.child),changed): self.close(self.pose(n),expected); self.assertFalse(cmds.keyframe(n,query=True,timeChange=True))

    def test_existing_fractional_keys_channels_outside_range_and_undo(self):
        cmds.select(self.parent); s=self.call(action='copy').data['snapshot']
        for t,v in ((0.,9.),(1.5,4.),(3.25,8.),(10.,12.)): cmds.setKeyframe(self.parent,attribute='translateX',time=t,value=v)
        cmds.currentTime(1); cmds.currentTime(2.5)
        keys=cmds.keyframe(self.parent,attribute='translateX',query=True,valueChange=True); pose=self.pose(self.parent)
        r=self.call(action='paste',snapshot=s,channels='translate',start=1,end=4,only_keyframes=True)
        self.assertEqual([1.5,3.25],r.data['frames']); self.assertFalse(cmds.keyframe(self.parent,attribute='rotateX',query=True,timeChange=True))
        values=cmds.keyframe(self.parent,attribute='translateX',query=True,valueChange=True); self.assertEqual(keys[0],values[0]); self.assertEqual(keys[-1],values[-1]); self.assertEqual([2.,2.],values[1:3])
        cmds.undo(); self.assertEqual(keys,cmds.keyframe(self.parent,attribute='translateX',query=True,valueChange=True)); self.close(pose,self.pose(self.parent)); self.assertEqual(2.5,cmds.currentTime(query=True))

    def test_joint_rotation_order_pivots_units_and_range(self):
        cmds.select(clear=True); joint=cmds.joint(name='joint'); cmds.setAttr(joint+'.jointOrient',10,20,30); cmds.setAttr(joint+'.rotateOrder',3); cmds.setAttr(joint+'.rotate',15,25,35)
        cmds.select(joint); s=self.call(action='copy').data['snapshot']; expected=self.pose(joint)
        cmds.setAttr(joint+'.rotate',1,2,3); self.call(action='paste',snapshot=s,start=1,end=3); self.close(expected,self.pose(joint)); self.assertEqual([1.,2.,3.],cmds.keyframe(joint,attribute='rotateX',query=True,timeChange=True)); cmds.undo()
        cmds.select(self.parent); cmds.setAttr(self.parent+'.rotatePivot',.3,.6,.9); cmds.setAttr(self.parent+'.scalePivot',.1,.2,.3)
        cmds.currentUnit(angle='rad',linear='m'); s=self.call(action='copy').data['snapshot']; expected=self.pose(self.parent)
        cmds.setAttr(self.parent+'.translate',7,8,9); cmds.setAttr(self.parent+'.rotate',.1,.2,.3)
        self.call(action='paste',snapshot=s); self.close(expected,self.pose(self.parent)); cmds.undo()
        cmds.currentUnit(angle='deg'); self.assertFalse(TOOL.run(action='paste',snapshot=s).success)

    def test_file_exclusive_dry_load_and_clipboard_no_side_effect(self):
        s=self.call(action='copy').data['snapshot']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'snapshot.json'; self.call(action='save',path=str(path),snapshot=s,dry_run=True); self.assertFalse(path.exists())
            self.call(action='save',path=str(path),snapshot=s); content=path.read_bytes(); self.assertFalse(TOOL.run(action='save',path=str(path),snapshot=s).success); self.assertEqual(content,path.read_bytes())
            self.assertEqual(s,self.call(action='load',path=str(path)).data['snapshot'])
            path.write_text('{"bad":true}',encoding='utf8'); self.assertFalse(TOOL.run(action='load',path=str(path)).success)
            cmds.select(self.parent); current=self.pose(self.parent); self.call(action='copy',dry_run=True); cmds.select(clear=True)
            result=self.call(action='paste',dry_run=True); self.assertEqual(2,len(result.data['objects'])); self.close(current,self.pose(self.parent))

    def test_all_rows_guards_shared_curve_and_instances(self):
        s=self.call(action='copy').data['snapshot']; cmds.setAttr(self.child+'.translateX',lock=True)
        before=self.pose(self.parent); self.assertFalse(TOOL.run(action='paste',snapshot=s).success); self.close(before,self.pose(self.parent)); cmds.setAttr(self.child+'.translateX',lock=False)
        cmds.setKeyframe(self.parent,attribute='translateX',time=1,value=5)
        curve=cmds.listConnections(self.parent+'.translateX',source=True,destination=False)[0]; cmds.connectAttr(curve+'.output',self.child+'.translateX',force=True)
        self.assertFalse(TOOL.run(action='paste',snapshot=s).success)
        cmds.file(new=True,force=True); first=cmds.createNode('transform',name='first'); parent=cmds.createNode('transform',name='p'); cmds.parent(first,parent,add=True)
        self.assertFalse(TOOL.run(action='copy',objects=[first]).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
