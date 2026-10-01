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
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.a=cmds.polyCube(name='cubeA')[0]; self.b=cmds.polyCube(name='cubeB')[0]
        cmds.setAttr(self.b+'.translateX',4); cmds.select(self.a,self.b); cmds.currentTime(7); cmds.autoKeyframe(state=True)

    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r

    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.file(query=True,sceneName=True),cmds.file(query=True,modified=True),cmds.autoKeyframe(query=True,state=True))

    def test_actual_abc_with_spaces_animation_uv_and_no_overwrite(self):
        cmds.autoKeyframe(state=False); cmds.setKeyframe(self.a,attribute='translateX',time=1,value=0); cmds.setKeyframe(self.a,attribute='translateX',time=3,value=6); cmds.currentTime(7); cmds.autoKeyframe(state=True)
        with tempfile.TemporaryDirectory(prefix='abc space ') as directory:
            output=Path(directory)/'mesh cache.abc'; before=self.state(); queue=cmds.undoInfo(query=True,undoName=True)
            loaded=cmds.pluginInfo('AbcExport',query=True,loaded=True)
            self.call(action='export',output=str(output),start=1,end=3,dry_run=True); self.assertFalse(output.exists()); self.assertEqual(queue,cmds.undoInfo(query=True,undoName=True)); self.assertEqual(loaded,cmds.pluginInfo('AbcExport',query=True,loaded=True)); self.assertEqual(before,self.state())
            self.call(action='export',output=str(output),start=1,end=3); self.assertEqual(before,self.state()); data=output.read_bytes(); self.assertGreater(len(data),100)
            self.assertFalse(TOOL.run(action='export',output=str(output),start=1,end=3).success); self.assertEqual(data,output.read_bytes())
            cmds.file(new=True,force=True); cmds.loadPlugin('AbcImport',quiet=True); cmds.AbcImport(str(output),mode='import')
            self.assertEqual(2,len(cmds.ls(type='mesh'))); self.assertEqual(['map1'],cmds.polyUVSet('cubeA',query=True,allUVSets=True))
            cmds.currentTime(3); self.assertAlmostEqual(6,cmds.xform('cubeA',query=True,worldSpace=True,translation=True)[0],places=4)
            # Only fixture readers unloaded, releases Windows cache handle for temp cleanup.
            cmds.file(new=True,force=True); cmds.unloadPlugin('AbcImport')

    def test_set_missing_empty_namespace_collision_and_material_undo(self):
        self.assertFalse(TOOL.run(set_name='abc_export').success); cmds.sets(name='abc_export',empty=True); self.assertFalse(TOOL.run(set_name='abc_export').success)
        cmds.sets(self.a,self.b,edit=True,forceElement='abc_export'); self.assertEqual(2,len(self.call(set_name='abc_export').data['roots']))
        before=self.state(); sg=[cmds.listConnections(cmds.listRelatives(n,shapes=True)[0],type='shadingEngine') for n in (self.a,self.b)]
        self.call(action='materials',dry_run=True); self.assertEqual(before,self.state()); self.call(action='materials'); self.assertEqual(2,len(cmds.ls(type='lambert'))-1); cmds.undo(); self.assertEqual(before,self.state())
        self.assertEqual(sg,[cmds.listConnections(cmds.listRelatives(n,shapes=True)[0],type='shadingEngine') for n in (self.a,self.b)])
        cmds.namespace(add='first'); cmds.namespace(add='second'); a=cmds.polyCube(name='first:same')[0]; b=cmds.polyCube(name='second:same')[0]
        self.assertFalse(TOOL.run(objects=[a,b],options={'strip_namespaces':True}).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()

    def test_isolated_batch_two_sources_and_live_scene_preservation(self):
        with tempfile.TemporaryDirectory(prefix='batch abc ') as directory:
            folder=Path(directory)/'scenes'; output=Path(directory)/'out'; folder.mkdir(); output.mkdir()
            cmds.autoKeyframe(state=False); cmds.sets(self.a,name='abc_export'); cmds.file(rename=str(folder/'good.ma')); cmds.file(save=True,type='mayaAscii')
            cmds.file(new=True,force=True); cmds.polyCube(); cmds.file(rename=str(folder/'missing.mb')); cmds.file(save=True,type='mayaBinary')
            cmds.file(new=True,force=True); alive=cmds.polySphere(name='liveUnsaved')[0]; cmds.select(alive); cmds.currentTime(17); before=self.state()
            preview=self.call(action='batch',folder=str(folder),output_dir=str(output),dry_run=True); self.assertFalse(preview.data['scene_contents_checked']); self.assertEqual(before,self.state()); self.assertEqual([],list(output.iterdir()))
            result=TOOL.run(action='batch',folder=str(folder),output_dir=str(output),timeout=90)
            self.assertFalse(result.success); self.assertEqual(before,self.state()); self.assertTrue((output/'good.abc').exists()); self.assertFalse((output/'missing.abc').exists())
            self.assertEqual([True,False],[r['success'] for r in result.data['scenes']]); self.assertIn('Missing named objectSet',result.data['scenes'][1]['message'])
            # Collision preflight stops before starting any worker.
            self.assertFalse(TOOL.run(action='batch',folder=str(folder),output_dir=str(output),dry_run=True).success)
            (folder/'good.mb').write_bytes(b'not opened')
            second=Path(directory)/'another'; second.mkdir(); self.assertFalse(TOOL.run(action='batch',folder=str(folder),output_dir=str(second),dry_run=True).success)


if __name__=='__main__': unittest.main()
