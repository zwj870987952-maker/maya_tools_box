import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.autoKeyframe(state=False)
        self.a=cmds.polyCube(name='partA')[0]; self.b=cmds.polyCube(name='partB')[0]; cmds.setAttr(self.b+'.tx',3)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.autoKeyframe(query=True,state=True))

    def test_combine_group_destination_unrelated_materials_and_single_undo(self):
        group=cmds.group(self.a,self.b,name='assembly'); spare=cmds.createNode('transform',name='keepMe',parent=group)
        shader=cmds.shadingNode('lambert',asShader=True,name='redMaterial'); sg=cmds.sets(renderable=True,noSurfaceShader=True,empty=True,name='redSG'); cmds.connectAttr(shader+'.outColor',sg+'.surfaceShader'); cmds.sets(self.a,edit=True,forceElement=sg)
        cmds.select(group); cmds.autoKeyframe(state=True); before=self.state()
        self.call(dry_run=True); self.assertEqual(before,self.state())
        out=self.call().data['outputs'][0]
        self.assertEqual(12,cmds.polyEvaluate(out,face=True)); self.assertEqual(16,cmds.polyEvaluate(out,vertex=True))
        self.assertEqual(['|assembly'],cmds.listRelatives(out,parent=True,fullPath=True))
        self.assertTrue(cmds.objExists(spare)); self.assertFalse(cmds.objExists(self.a)); self.assertFalse(cmds.objExists(self.b))
        self.assertTrue(cmds.sets(sg,query=True)); self.assertTrue(cmds.autoKeyframe(query=True,state=True))
        cmds.undo(); self.assertEqual(before[0],self.state()[0]); self.assertEqual(before[1],self.state()[1]); self.assertEqual(before[3],self.state()[3])
        self.assertTrue(cmds.objExists(self.a)); self.assertTrue(cmds.objExists(self.b)); self.assertTrue(cmds.objExists(spare))

    def test_separate_shells_parent_pivots_and_undo(self):
        source=cmds.polyUnite(self.a,self.b,constructionHistory=False,name='twoShells')[0]; cmds.delete(source,constructionHistory=True)
        group=cmds.group(source,name='container'); cmds.xform(source,worldSpace=True,rotatePivot=[1,2,3],scalePivot=[4,5,6])
        pivots=cmds.xform(source,query=True,worldSpace=True,pivots=True); cmds.select(source); before=self.state()
        out=self.call(action='separate').data['outputs']; self.assertEqual(2,len(out))
        for node in out:
            self.assertEqual(6,cmds.polyEvaluate(node,face=True)); self.assertEqual(['|container'],cmds.listRelatives(node,parent=True,fullPath=True))
            self.assertEqual(pivots,cmds.xform(node,query=True,worldSpace=True,pivots=True))
        cmds.undo(); self.assertEqual(before[0],self.state()[0]); self.assertEqual(12,cmds.polyEvaluate(source,face=True))

    def test_duplicate_rigged_readonly_faces_all_faces_and_extract_undo(self):
        joint=cmds.createNode('joint',name='bindJoint'); skin=cmds.skinCluster(joint,self.a,toSelectedBones=True)[0]
        shape=cmds.listRelatives(self.a,shapes=True,noIntermediate=True,fullPath=True)[0]
        original=cmds.getAttr(shape+'.worldMesh[0]')
        cmds.select(self.a+'.f[0:1]'); before=self.state()
        out=self.call(action='duplicate').data['outputs'][0]; self.assertEqual(2,cmds.polyEvaluate(out,face=True))
        self.assertEqual(6,cmds.polyEvaluate(self.a,face=True)); self.assertTrue(cmds.objExists(skin)); self.assertEqual(original,cmds.getAttr(shape+'.worldMesh[0]'))
        cmds.undo(); self.assertEqual(before[0],self.state()[0])
        out=self.call(action='duplicate',components=[self.b+'.f[0:5]']).data['outputs'][0]; self.assertEqual(6,cmds.polyEvaluate(out,face=True))
        cmds.undo(); before=self.state()
        out=self.call(action='extract',components=[self.b+'.f[0:1]']).data['outputs'][0]
        self.assertEqual(2,cmds.polyEvaluate(out,face=True)); self.assertEqual(4,cmds.polyEvaluate(self.b,face=True))
        cmds.undo(); self.assertEqual(6,cmds.polyEvaluate(self.b,face=True)); self.assertEqual(before[0],self.state()[0])

    def test_full_preflight_locked_instance_external_history_all_faces_and_batch_install(self):
        cmds.lockNode(self.b,lock=True); before=self.state()
        self.assertFalse(TOOL.run(objects=[self.a,self.b]).success); self.assertEqual(before,self.state()); cmds.lockNode(self.b,lock=False)
        self.assertFalse(TOOL.run(action='separate',objects=[self.a]).success)
        self.assertFalse(TOOL.run(action='extract',components=[self.a+'.f[0:5]']).success)
        self.assertFalse(TOOL.run(action='duplicate',components=[self.a+'.f[0]',self.b+'.f[0]']).success)
        foreign=cmds.createNode('transform',name='externalHistoryConsumer'); foreign_shape=cmds.createNode('mesh',name='externalShape',parent=foreign)
        shape=cmds.listRelatives(self.a,shapes=True,fullPath=True)[0]; creator=cmds.listConnections(shape+'.inMesh',source=True,destination=False)[0]
        cmds.connectAttr(creator+'.output',foreign_shape+'.inMesh'); before=self.state()
        self.assertFalse(TOOL.run(objects=[self.a,self.b]).success); self.assertEqual(before,self.state())
        cmds.disconnectAttr(creator+'.output',foreign_shape+'.inMesh')
        parent=cmds.createNode('transform',name='instanceParent'); cmds.parent(self.b,parent,add=True)
        self.assertFalse(TOOL.run(objects=[self.a,'|partB']).success)
        before=self.state()
        for p in ({'action':'shelf'},{'action':'hotkey','key':'C'}): self.assertFalse(TOOL.run(**p).success)
        self.assertEqual(before,self.state())
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
