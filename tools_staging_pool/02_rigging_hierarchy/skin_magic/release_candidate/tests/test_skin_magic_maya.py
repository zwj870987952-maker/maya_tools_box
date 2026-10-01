import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.skin_magic import runtime,ui_support


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        cmds.select(clear=True)
        self.j1=cmds.joint(name='j1')
        self.j2=cmds.joint(name='j2',position=(2,0,0))
        self.mesh=cmds.polyPlane(name='skinMesh',subdivisionsX=1,subdivisionsY=1)[0]
        self.skin=cmds.skinCluster(self.j1,self.j2,self.mesh,toSelectedBones=True,normalizeWeights=1)[0]
        cmds.skinPercent(self.skin,self.mesh+'.vtx[*]',transformValue=[(self.j1,0.8),(self.j2,0.2)],normalize=False)
        cmds.select(self.mesh)

    def call(self,**p):
        result=TOOL.run(**p)
        self.assertTrue(result.success,result.message)
        return result

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.getAttr(self.skin+'.weightDistribution'),cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True))

    def test_scope_dry_run_and_real_weights_one_undo(self):
        before=self.state()
        self.call(action='set_weights',objects=[self.mesh+'.vtx[0]'],weights={'j1':0.3,'j2':0.7},dry_run=True)
        self.assertEqual(before,self.state())
        self.call(action='set_weights',objects=[self.mesh+'.vtx[0]'],weights={'j1':0.3,'j2':0.7})
        values=cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)
        self.assertAlmostEqual(0.7,values[1],places=6)
        self.assertAlmostEqual(0.2,cmds.skinPercent(self.skin,self.mesh+'.vtx[1]',query=True,value=True)[1],places=6)
        cmds.undo()
        self.assertAlmostEqual(0.2,cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)[1],places=6)

    def test_json_export_remap_import_exclusive_and_undo(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'saved.VertexWeight')
            self.call(action='export_weights',objects=[self.mesh],path=path)
            original=Path(path).read_bytes()
            before=self.state()
            self.assertFalse(TOOL.run(action='export_weights',objects=[self.mesh],path=path).success)
            self.assertEqual(before,self.state())
            self.assertEqual(original,Path(path).read_bytes())
            self.call(action='set_weights',objects=[self.mesh],weights={'j1':0.1,'j2':0.9})
            self.call(action='import_weights',objects=[self.mesh],path=path)
            self.assertAlmostEqual(0.2,cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)[1],places=6)
            cmds.undo()
            self.assertAlmostEqual(0.9,cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)[1],places=6)
            self.assertTrue(Path(path).exists())

    def test_native_xml_import_replays_undo_and_no_holder_node(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'native.xml'
            cmds.deformerWeights(path.name,path=folder,export=True,deformer=self.skin,defaultValue=0.0)
            self.call(action='set_weights',objects=[self.mesh],weights={'j1':0.1,'j2':0.9})
            before_nodes=set(cmds.ls(long=True))
            cmds.undoInfo(openChunk=True,chunkName='candidateXmlImport')
            try:
                shape=cmds.listRelatives(self.mesh,shapes=True,fullPath=True)[0]
                ui_support.import_xml_weights(self.skin,shape,path)
            finally:
                cmds.undoInfo(closeChunk=True)
            self.assertAlmostEqual(0.2,cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)[1],places=6)
            self.assertEqual(before_nodes,set(cmds.ls(long=True)))
            cmds.undo()
            self.assertAlmostEqual(0.9,cmds.skinPercent(self.skin,self.mesh+'.vtx[0]',query=True,value=True)[1],places=6)

    def test_reject_locked_ambiguous_instance_wrong_scope_and_gui_dependencies(self):
        before=self.state()
        for params in ({'action':'set_weights','objects':[self.mesh],'weights':{'missing':1}},{'action':'inspect_skin','objects':[self.mesh+'.f[0]']},{'action':'set_weights','objects':[self.mesh,self.mesh+'.vtx[0]'],'weights':{'j1':1}}):
            self.assertFalse(TOOL.run(**params).success)
        self.assertEqual(before,self.state())
        cmds.setAttr(self.j1+'.liw',True)
        locked=self.state()
        self.assertFalse(TOOL.run(action='set_weights',objects=[self.mesh],weights={'j2':1}).success)
        self.assertEqual(locked,self.state())
        cmds.setAttr(self.j1+'.liw',False)
        parent=cmds.createNode('transform',name='instanceParent')
        cmds.parent(self.mesh,parent,add=True)
        self.assertFalse(TOOL.run(action='inspect_skin',objects=['|skinMesh']).success)
        result=TOOL.run(action='show_ui',dry_run=True)
        self.assertFalse(result.success)
        self.assertTrue('PyMel' in result.message or 'interactive' in result.message.lower())
        status=self.call(action='status')
        self.assertEqual(250,status.data['source_functions'])


if __name__=='__main__':
    unittest.main()
