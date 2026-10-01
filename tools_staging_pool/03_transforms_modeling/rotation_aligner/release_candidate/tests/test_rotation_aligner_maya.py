import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.rotation_aligner import native


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.currentUnit(angle='deg'); cmds.autoKeyframe(state=False)
        self.source=cmds.createNode('transform',name='source'); self.target=cmds.createNode('transform',name='reference')
        cmds.setAttr(self.target+'.rz',45); cmds.select(self.source,self.target)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.xform(self.source,query=True,matrix=True,worldSpace=True),cmds.xform(self.target,query=True,matrix=True,worldSpace=True),cmds.autoKeyframe(query=True,state=True))

    def dot(self,a,b): return sum(x*y for x,y in zip(a,b))

    def test_single_primary_and_full_axes_original_equivalence_undo_and_rad(self):
        cmds.autoKeyframe(state=True); before=self.state()
        self.call(time_mode='single',dry_run=True); self.assertEqual(before,self.state())
        self.call(time_mode='single'); result=self.state()
        self.assertAlmostEqual(1,self.dot(native.get_object_axes(self.source)[1],native.get_object_axes(self.target)[1]),places=6)
        self.assertEqual(before[1:3],result[1:3]); self.assertEqual(before[5],result[5]); self.assertTrue(result[6])
        cmds.undo(); self.assertEqual(before[4],self.state()[4]); self.assertEqual(before[3],self.state()[3])
        cmds.autoKeyframe(state=False)
        settings=dict(full_alignment=False,rotate_axes={'x':True,'y':True,'z':True},source_axis='+Y',target_axis='+Y')
        for _ in range(5): native.align_object_to_target(self.source,self.target,settings=settings)
        for a,b in zip(result[4],self.state()[4]): self.assertAlmostEqual(a,b,places=7)
        cmds.setAttr(self.source+'.rotate',5,10,15); cmds.setAttr(self.target+'.rotate',20,30,40)
        self.call(time_mode='single',full_alignment=True)
        for a,b in zip(native.get_object_axes(self.source),native.get_object_axes(self.target)): self.assertAlmostEqual(1,self.dot(a,b),places=6)
        cmds.undo(); cmds.currentUnit(angle='rad'); self.call(time_mode='single',full_alignment=True)
        for a,b in zip(native.get_object_axes(self.source),native.get_object_axes(self.target)): self.assertAlmostEqual(1,self.dot(a,b),places=6)
        self.assertEqual('rad',cmds.currentUnit(query=True,angle=True))

    def test_actual_bake_keyed_reference_subset_fractional_keys_and_undo(self):
        cmds.setKeyframe(self.target,attribute='rz',time=1,value=0); cmds.setKeyframe(self.target,attribute='rz',time=3,value=90)
        before=self.state(); r=self.call(time_mode='custom',custom_start=1,custom_end=3)
        self.assertEqual([1,2,3],r.data['rows'][0]['frames'])
        self.assertEqual([1,2,3],cmds.keyframe(self.source,attribute='rz',query=True,timeChange=True))
        for t in (1,2,3):
            matrixA=cmds.getAttr(self.source+'.worldMatrix[0]',time=t); matrixB=cmds.getAttr(self.target+'.worldMatrix[0]',time=t)
            self.assertAlmostEqual(1,self.dot(matrixA[4:7],matrixB[4:7]),places=6)
        self.assertEqual(before[2],cmds.currentTime(query=True)); cmds.undo()
        self.assertEqual([],cmds.keyframe(self.source,query=True,timeChange=True) or []); self.assertEqual(before[4],self.state()[4])
        cmds.setKeyframe(self.target,attribute='rz',time=2.5,value=70)
        self.call(time_mode='custom',custom_start=1,custom_end=3,bake_all_frames=False)
        self.assertEqual([1,2.5,3],cmds.keyframe(self.source,attribute='rz',query=True,timeChange=True))

    def test_locked_axis_one_axis_joint_orient_parent_rotation_and_all_table_errors(self):
        cmds.setAttr(self.source+'.rx',lock=True); cmds.setAttr(self.source+'.ry',lock=True)
        self.call(time_mode='single',rotate_axes={'x':True,'y':True,'z':True})
        self.assertEqual(0,cmds.getAttr(self.source+'.rx')); self.assertEqual(0,cmds.getAttr(self.source+'.ry')); self.assertAlmostEqual(45,cmds.getAttr(self.source+'.rz'),places=6)
        parent=cmds.createNode('transform',name='rotatedParent'); cmds.setAttr(parent+'.rz',20)
        joint=cmds.createNode('joint',name='jointSource',parent=parent); cmds.setAttr(joint+'.jointOrient',10,15,20); cmds.setAttr(joint+'.rotateOrder',4)
        self.call(pairs=[{'source':joint,'target':self.target}],time_mode='single',full_alignment=True)
        for a,b in zip(native.get_object_axes(joint),native.get_object_axes(self.target)): self.assertAlmostEqual(1,self.dot(a,b),places=6)
        bad=cmds.createNode('transform',name='bad'); cmds.setAttr(bad+'.rotate',lock=True)
        before=self.state(); self.assertFalse(TOOL.run(pairs=[{'source':self.source,'target':self.target},{'source':bad,'target':self.target}],time_mode='single').success); self.assertEqual(before,self.state())
        self.assertFalse(TOOL.run(pairs=[{'source':self.source,'target':self.source}],time_mode='single').success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()

    def test_existing_curve_rad_keys_outside_range_and_shared_curve_refusal(self):
        cmds.setKeyframe(self.source,attribute='rz',time=-1,value=5); cmds.setKeyframe(self.source,attribute='rz',time=5,value=10)
        cmds.setKeyframe(self.target,attribute='rz',time=1,value=20); cmds.setKeyframe(self.target,attribute='rz',time=3,value=70)
        cmds.currentUnit(angle='rad')
        # Evaluate the freshly authored curve at the fixture current frame.
        # setKeyframe(value=...) does not necessarily dirty cached transforms
        # until the time changes in standalone Maya.
        cmds.currentTime(2,edit=True); cmds.currentTime(1,edit=True); before=self.state()
        key_values=cmds.keyframe(self.source,attribute='rz',query=True,valueChange=True)
        self.call(time_mode='custom',custom_start=1,custom_end=3)
        self.assertEqual([-1,1,2,3,5],cmds.keyframe(self.source,attribute='rz',query=True,timeChange=True))
        for t in (1,2,3):
            matrixA=cmds.getAttr(self.source+'.worldMatrix[0]',time=t); matrixB=cmds.getAttr(self.target+'.worldMatrix[0]',time=t)
            self.assertAlmostEqual(1,self.dot(matrixA[4:7],matrixB[4:7]),places=6)
        cmds.undo(); self.assertEqual([-1,5],cmds.keyframe(self.source,attribute='rz',query=True,timeChange=True)); self.assertEqual(key_values,cmds.keyframe(self.source,attribute='rz',query=True,valueChange=True)); self.assertEqual(before[4],self.state()[4])
        other=cmds.createNode('transform',name='sharedConsumer')
        curve=cmds.listConnections(self.source+'.rz',source=True,destination=False)[0]
        cmds.connectAttr(curve+'.output',other+'.rz'); before=self.state()
        self.assertFalse(TOOL.run(time_mode='custom',custom_start=1,custom_end=3).success); self.assertEqual(before,self.state())


if __name__=='__main__': unittest.main()
