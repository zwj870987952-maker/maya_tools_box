import math
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
from maya_toolkit.tools.quaternion_tool.native import Quaternion


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.currentUnit(angle='deg')
        self.obj=cmds.polyCube(name='target')[0]; cmds.setAttr(self.obj+'.rotate',15,25,35); cmds.select(self.obj)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def near(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=7)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.xform(self.obj,query=True,matrix=True,worldSpace=True),cmds.autoKeyframe(query=True,state=True),cmds.currentUnit(query=True,angle=True))

    def test_real_maya_quaternion_geometry_and_all_pure_actions_no_scene_write(self):
        before=self.state()
        q=self.call(action='from_euler',euler=[10,20,30]).data['quaternion']
        self.near([10,20,30],self.call(action='to_euler',quaternion=q).data['euler_degrees'])
        expected=om.MEulerRotation(*[math.radians(v) for v in (10,20,30)]).asQuaternion()
        self.near(q,[expected.x,expected.y,expected.z,expected.w])
        self.near([0,1,0],self.call(action='rotate_vector',quaternion=self.call(action='from_axis_angle',axis=[0,0,1],angle=90).data['quaternion'],vector=[1,0,0]).data['rotated_vector'])
        for direction in ([0,1,0],[-1,0,0],[1,0,0]):
            value=self.call(action='from_to',from_direction=[1,0,0],to_direction=direction).data['quaternion']
            self.near(direction,self.call(action='rotate_vector',quaternion=value,vector=[1,0,0]).data['rotated_vector'])
        identity=self.call(action='multiply',quaternion=q,second=self.call(action='inverse',quaternion=q).data['quaternion']).data['quaternion']
        self.near([0,0,0,1],identity)
        self.near(q,self.call(action='normalize',quaternion=[2*v for v in q]).data['quaternion'])
        self.near(q,self.call(action='from_components',quaternion=q).data['quaternion'])
        self.near(q,self.call(action='slerp',quaternion=q,second=[-v for v in q],t=.5).data['quaternion'])
        half=self.call(action='slerp',quaternion=[0,0,0,1],second=self.call(action='from_axis_angle',axis=[0,0,1],angle=90).data['quaternion'],t=.5).data['euler_degrees']
        self.near([0,0,45],half)
        self.near([0,0,0,1],self.call(action='normalize',quaternion=[0,0,0,0]).data['quaternion'])
        self.assertEqual(before,self.state())
        source=om.MVector(2,0,0); target=om.MVector(0,3,0); axis=om.MVector(0,0,2)
        Quaternion.FromToRotation(source,target); Quaternion.FromAxisAngle(axis,90)
        self.near([2,0,0],source); self.near([0,3,0],target); self.near([0,0,2],axis)

    def test_apply_original_cmd_rotation_single_undo_autokey_and_radian_unit(self):
        q=self.call(action='from_euler',euler=[10,20,30]).data['quaternion']; cmds.autoKeyframe(state=True)
        before=self.state(); self.call(action='apply',quaternion=q,dry_run=True); self.assertEqual(before,self.state())
        self.call(action='apply',quaternion=q); result=self.state(); self.assertEqual(before[1],result[1]); self.assertTrue(result[5])
        cmds.undo(); self.near(before[4],self.state()[4]); self.assertEqual(before[3],self.state()[3])
        cmds.autoKeyframe(state=False); euler=Quaternion(q).Euler(); cmds.rotate(*euler,self.obj,absolute=True)
        self.near(result[4],self.state()[4])
        cmds.currentUnit(angle='rad'); before=self.state(); self.call(action='apply',quaternion=q)
        self.near(result[4],self.state()[4]); self.assertEqual('rad',cmds.currentUnit(query=True,angle=True))
        cmds.undo(); self.near(before[4],self.state()[4])

    def test_all_target_preflight_rotation_order_locked_driven_alias_instance(self):
        other=cmds.createNode('transform',name='other'); cmds.setAttr(other+'.rx',lock=True); before=self.state()
        self.assertFalse(TOOL.run(action='apply',objects=[self.obj,other]).success); self.assertEqual(before,self.state())
        cmds.setAttr(self.obj+'.rotateOrder',2); self.assertFalse(TOOL.run(action='apply').success); cmds.setAttr(self.obj+'.rotateOrder',0)
        cmds.setKeyframe(self.obj,attribute='ry'); before=self.state(); self.assertFalse(TOOL.run(action='apply').success); self.assertEqual(before,self.state())
        cmds.cutKey(self.obj,attribute='ry',clear=True)
        self.assertFalse(TOOL.run(action='apply',objects=[self.obj,'|target']).success)
        self.assertFalse(TOOL.run(action='apply',objects=['target.f[0]']).success)
        parent=cmds.createNode('transform',name='parent'); cmds.parent(self.obj,parent,add=True)
        self.assertFalse(TOOL.run(action='apply',objects=['|target']).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
