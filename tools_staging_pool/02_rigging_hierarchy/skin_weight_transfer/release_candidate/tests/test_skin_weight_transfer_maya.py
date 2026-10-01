import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.skin_weight_transfer.operations import read_weights


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        cmds.select(clear=True)
        self.a=cmds.joint(name='a')
        self.b=cmds.joint(name='b',position=(1,0,0))
        self.c=cmds.joint(name='c',position=(2,0,0))
        self.mesh=cmds.polyPlane(name='mesh',subdivisionsX=1,subdivisionsY=1)[0]
        self.skin=cmds.skinCluster([self.a,self.b,self.c],self.mesh,toSelectedBones=True,normalizeWeights=1)[0]
        cmds.setAttr(self.skin+'.maintainMaxInfluences',False)
        cmds.skinPercent(self.skin,self.mesh+'.vtx[*]',transformValue=[(self.a,0.2),(self.b,0.3),(self.c,0.5)],normalize=False)
        self.shape=cmds.listRelatives(self.mesh,shapes=True,fullPath=True)[0]
        cmds.select(self.mesh)

    def call(self,**p):
        result=TOOL.run(**p)
        self.assertTrue(result.success,result.message)
        return result

    def weights(self):
        return cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),self.weights(),cmds.skinCluster(self.skin,query=True,influence=True))

    def test_real_full_mesh_merge_readonly_and_one_undo(self):
        before=self.state()
        result=self.call(task_text='a => b => mesh',dry_run=True)
        self.assertEqual(4,result.data['tasks'][0]['meshes'][0]['vertex_count'])
        self.assertEqual(before,self.state())
        self.call(task_text='a => b => mesh')
        for vertex in cmds.ls(self.mesh+'.vtx[*]',flatten=True):
            actual=cmds.skinPercent(self.skin,vertex,query=True,value=True)
            for a,b in zip(actual,[0,0.5,0.5]):
                self.assertAlmostEqual(a,b,places=6)
        self.assertEqual(before[1],cmds.ls(selection=True,long=True))
        cmds.undo()
        self.assertEqual(before[0],set(cmds.ls(long=True)))
        for actual,w in zip(self.weights(),[0.2,0.3,0.5]):
            self.assertAlmostEqual(actual,w,places=6)

    def test_discovery_ordered_chain_remove_source_and_single_undo(self):
        before=self.state()
        self.call(task_text='a => b => => DelSkin\nb => c')
        influences=cmds.skinCluster(self.skin,query=True,influence=True)
        self.assertNotIn('a',influences)
        self.assertTrue(cmds.objExists('a'))
        actual=dict(zip(influences,self.weights()))
        self.assertAlmostEqual(0,actual['b'],places=6)
        self.assertAlmostEqual(1,actual['c'],places=6)
        cmds.undo()
        self.assertEqual(before[5],cmds.skinCluster(self.skin,query=True,influence=True))
        for actual,w in zip(self.weights(),[0.2,0.3,0.5]):
            self.assertAlmostEqual(actual,w,places=6)

    def test_non_normalized_weights_all_influences_and_undo(self):
        cmds.setAttr(self.skin+'.normalizeWeights',0)
        cmds.skinPercent(self.skin,self.mesh+'.vtx[*]',transformValue=[(self.a,0.8),(self.b,0.4),(self.c,0.8)],normalize=False)
        self.call(tasks=[{'source_joint':'a','target_joint':'b','meshes':[self.shape]}])
        for actual,w in zip(self.weights(),[0,0.6,0.4]):
            self.assertAlmostEqual(actual,w,places=6)
        cmds.undo()
        for actual,w in zip(self.weights(),[0.8,0.4,0.8]):
            self.assertAlmostEqual(actual,w,places=6)

    def test_all_task_rejection_no_partial_write_locks_aliases_instance(self):
        before=self.state()
        for task in ('a=>b=>mesh\na=>missing=>mesh','a=>b=>mesh=>DelSkin\na=>c=>mesh','a=>a=>mesh','a=>b=>mesh,meshShape'):
            self.assertFalse(TOOL.run(task_text=task).success)
        self.assertEqual(before,self.state())
        cmds.setAttr(self.c+'.liw',True)
        locked=self.state()
        self.assertFalse(TOOL.run(task_text='a=>b=>mesh').success)
        self.assertEqual(locked,self.state())
        cmds.setAttr(self.c+'.liw',False)
        parent=cmds.createNode('transform',name='instanceParent')
        cmds.parent(self.mesh,parent,add=True)
        self.assertFalse(TOOL.run(task_text='a=>b=>|mesh').success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__=='__main__':
    unittest.main()
