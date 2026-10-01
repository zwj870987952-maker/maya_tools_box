import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya.api import OpenMaya as om
TOOL = runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)

    def call(self,**p):
        result = TOOL.run(**p)
        self.assertTrue(result.success,result.message)
        return result

    def test_mixed_selected_forest_world_pose_radius_scope_and_one_undo(self):
        root = cmds.joint(name='rootJoint',position=(3,2,1))
        child = cmds.joint(name='childJoint',position=(5,3,2))
        tip = cmds.joint(name='unselectedTip',position=(7,5,2))
        loc = cmds.spaceLocator(name='locatorSource')[0]
        cmds.parent(loc,child)
        cmds.setAttr(root+'.rz',37)
        cmds.setAttr(child+'.ry',21)
        cmds.setAttr(root+'.radius',2.5)
        cmds.setAttr(child+'.drawStyle',2)
        cmds.setAttr(loc+'.translate',1,4,2)
        cmds.setAttr(loc+'.rotate',10,20,30)
        cmds.select([root,child,loc])
        before = set(cmds.ls(long=True))
        state = (cmds.currentTime(query=True),cmds.ls(selection=True,long=True),cmds.undoInfo(query=True,undoName=True))
        self.call(dry_run=True)
        self.assertEqual(before,set(cmds.ls(long=True)))
        self.assertEqual(state,(cmds.currentTime(query=True),cmds.ls(selection=True,long=True),cmds.undoInfo(query=True,undoName=True)))
        result = self.call()
        mapping = result.data['mapping']
        self.assertEqual(3,len(mapping))
        self.assertFalse(cmds.objExists('unselectedTip_copy'))
        for source,target in mapping.items():
            for a,b in zip(cmds.xform(source,query=True,worldSpace=True,translation=True),cmds.xform(target,query=True,worldSpace=True,translation=True)):
                self.assertAlmostEqual(a,b,places=5)
            qs = om.MTransformationMatrix(om.MMatrix(cmds.xform(source,query=True,worldSpace=True,matrix=True))).rotation(asQuaternion=True)
            qt = om.MTransformationMatrix(om.MMatrix(cmds.xform(target,query=True,worldSpace=True,matrix=True))).rotation(asQuaternion=True)
            self.assertAlmostEqual(1,abs(qs.x*qt.x+qs.y*qt.y+qs.z*qt.z+qs.w*qt.w),places=5)
            self.assertEqual((1,1,1),cmds.getAttr(target+'.scale')[0])
        source_child = cmds.ls(child,long=True)[0]
        self.assertEqual([mapping[source_child]],cmds.listRelatives(mapping[cmds.ls(loc,long=True)[0]],parent=True,fullPath=True))
        self.assertEqual(2.5,cmds.getAttr(mapping[cmds.ls(root,long=True)[0]]+'.radius'))
        self.assertEqual(2,cmds.getAttr(mapping[source_child]+'.drawStyle'))
        self.assertEqual(set(mapping.values()),set(cmds.ls(selection=True,long=True)))
        cmds.undo()
        self.assertEqual(before,set(cmds.ls(long=True)))

    def test_unselected_parent_disconnect_namespace_no_scale_and_context(self):
        cmds.namespace(add='rig')
        root = cmds.joint(name='rig:a')
        middle = cmds.joint(name='rig:unselected',position=(2,0,0))
        child = cmds.joint(name='rig:c',position=(4,0,0))
        cmds.setAttr(root+'.sx',2)
        cmds.namespace(add='caller')
        cmds.namespace(setNamespace='caller')
        caller_namespace = cmds.namespaceInfo(currentNamespace=True)
        cmds.autoKeyframe(state=True)
        cmds.select(root)
        original_selection = cmds.ls(selection=True,long=True)
        result = self.call(objects=[root,child],select_result=False,suffix='_new')
        self.assertEqual(2,len(result.data['roots']))
        for target in result.data['mapping'].values():
            self.assertFalse(cmds.listRelatives(target,parent=True))
            self.assertEqual((1,1,1),cmds.getAttr(target+'.scale')[0])
        self.assertEqual(caller_namespace,cmds.namespaceInfo(currentNamespace=True))
        self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        self.assertEqual(original_selection,cmds.ls(selection=True,long=True))
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')

    def test_collision_alias_instance_empty_and_component_rejection(self):
        j = cmds.joint(name='joint')
        cmds.createNode('transform',name='joint_copy')
        self.assertFalse(TOOL.run(objects=[j]).success)
        cmds.delete('joint_copy')
        self.assertFalse(TOOL.run(objects=[j,'|joint']).success)
        parent = cmds.createNode('transform',name='instanceParent')
        cmds.parent(j,parent,add=True)
        self.assertFalse(TOOL.run(objects=['|joint']).success)
        cmds.select(clear=True)
        self.assertFalse(TOOL.run().success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__=='__main__':
    unittest.main(verbosity=2)
