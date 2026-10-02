import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
from maya.api import OpenMaya as om
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.per_frame_bs_fbx.tool import dag_path
class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='frame bs '); self.rootdir=Path(self.temp.name); cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.root=cmds.createNode('transform',name='sourceGroup'); cube=cmds.polyCube(name='sourceCube')[0]; cmds.parent(cube,self.root); self.mesh=cmds.listRelatives(cube,shapes=True,fullPath=True)[0]
        cmds.setKeyframe(self.root,attribute='tx',time=1,value=0); cmds.setKeyframe(self.root,attribute='tx',time=3,value=8)
        target=cmds.duplicate(cube,name='deformedTarget')[0]; cmds.move(0,3,0,target+'.vtx[0]',relative=True,objectSpace=True)
        self.bs=cmds.blendShape(target,cube,name='source_bs')[0]; cmds.setKeyframe(self.bs+'.weight[0]',time=1,value=0); cmds.setKeyframe(self.bs+'.weight[0]',time=3,value=1); cmds.delete(target)
        self.second=cmds.polyCube(name='secondCube')[0]; cmds.parent(self.second,self.root); cmds.setAttr(self.second+'.tz',4)
        cmds.currentTime(2); cmds.currentTime(1); self.samples={}
        for frame in (1,2,3): cmds.currentTime(frame); self.samples[frame]=self.points(self.mesh)
        cmds.namespace(add='userScope'); cmds.namespace(set=':userScope'); cmds.currentTime(8); cmds.select(self.root); cmds.autoKeyframe(state=True)
    def tearDown(self): cmds.namespace(set=':'); cmds.file(new=True,force=True); self.temp.cleanup()
    def points(self,mesh): return [(p.x,p.y,p.z) for p in om.MFnMesh(dag_path(mesh)).getPoints(om.MSpace.kWorld)]
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.namespaceInfo(currentNamespace=True,absoluteName=True),cmds.undoInfo(query=True,undoName=True))
    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message+' '+str(r.errors)); return r
    def assert_points(self,a,b):
        self.assertEqual(len(a),len(b))
        for p,q in zip(a,b):
            for x,y in zip(p,q): self.assertAlmostEqual(x,y,places=4)
    def test_world_deform_two_meshes_native_pulse_skin_one_undo_redo(self):
        before=self.state(); self.call(root=self.root,start=1,end=3,dry_run=True); self.assertEqual(before,self.state())
        result=self.call(action='build',root=self.root,start=1,end=3); self.assertEqual(2,len(result.data['meshes'])); self.assertEqual(6,result.data['targets']); self.assertEqual(before[1:5],self.state()[1:5])
        row=[r for r in result.data['meshes'] if r['source']==self.mesh][0]; shape=cmds.listRelatives(row['base'],shapes=True,noIntermediate=True,fullPath=True)[0]
        cmds.undoInfo(stateWithoutFlush=False)
        for frame in (1,2,3):
            cmds.currentTime(frame); self.assert_points(self.samples[frame],self.points(shape)); self.assertEqual(3,len(cmds.listAttr(row['blend_shape']+'.weight',multi=True))); self.assertEqual([result.data['joint'].rsplit('|',1)[-1]],cmds.skinCluster(row['skin_cluster'],query=True,influence=True))
        # Evaluation shouldn't add commands after the operation before one Undo.
        cmds.currentTime(8); cmds.undoInfo(stateWithoutFlush=True)
        cmds.undo(); self.assertEqual(before[0],self.state()[0]); cmds.redo(); self.assertTrue(cmds.objExists(result.data['group']))
        cmds.undoInfo(stateWithoutFlush=False); cmds.currentTime(3); self.assert_points(self.samples[3],self.points(shape)); cmds.currentTime(8); cmds.undoInfo(stateWithoutFlush=True)
        self.assertFalse(TOOL.run(action='build',root=self.root,start=1,end=3).success)
    def test_actual_fbx_shapes_skin_reimport_readback_and_dry_refusals(self):
        output=self.rootdir/'shapes.fbx'; result=self.call(action='build_export',root=self.root,start=1,end=3,output=str(output),ascii=True); self.assertGreater(output.stat().st_size,1000)
        expected_base=[r['base'].rsplit('|',1)[-1] for r in result.data['meshes'] if r['source']==self.mesh][0]
        cmds.undo(); self.assertFalse(cmds.objExists(result.data['group'])); self.assertTrue(output.exists())
        before=self.state(); self.assertFalse(TOOL.run(action='build_export',root=self.root,start=1,end=3,output=str(output)).success); self.assertEqual(before,self.state())
        cmds.namespace(set=':'); cmds.file(new=True,force=True); mel.eval('FBXImportMode -v "add"'); cmds.file(str(output),i=True,type='FBX')
        # FBX importer materializes BS target helper meshes separately. Assert
        # actual skin output geometry, rather than mistaking targets for models.
        skins=cmds.ls(type='skinCluster'); self.assertEqual(2,len(skins)); self.assertEqual(2,len(cmds.ls(type='blendShape')))
        meshes=sorted({m for skin in skins for m in cmds.listConnections(skin+'.outputGeometry',source=False,destination=True,type='mesh',shapes=True) or []}); self.assertEqual(2,len(meshes),str(cmds.ls(type='mesh',long=True)))
        meshes=[cmds.ls(m,long=True)[0] for m in meshes]
        matches=[m for m in meshes if m.rsplit('|',2)[-2].split(':')[-1]==expected_base]; self.assertEqual(1,len(matches),str(meshes)); shape=matches[0]
        for frame in (1,3): cmds.currentTime(frame); self.assert_points(self.samples[frame],self.points(shape))
    def test_instance_empty_bad_grid_and_locked_source_readonly(self):
        before=self.state(); self.assertFalse(TOOL.run(root=self.root,start=1,end=2,step=.3).success); self.assertEqual(before,self.state())
        cmds.instance(self.root,name='instance'); before=self.state(); self.assertFalse(TOOL.run(root=self.root,start=1,end=3).success); self.assertEqual(before,self.state())
        with self.assertRaises(RuntimeError): TOOL.show_ui()
if __name__=='__main__': unittest.main()
