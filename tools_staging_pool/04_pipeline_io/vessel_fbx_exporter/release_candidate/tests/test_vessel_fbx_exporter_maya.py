import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='vessel output '); self.rootdir=Path(self.temp.name); cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        cube=cmds.polyCube(name='assetMesh')[0]; cmds.sets(cube,name='AAA_body_FBXExport'); self.asset=self.rootdir/'asset.ma'; cmds.file(rename=str(self.asset)); cmds.file(save=True,type='mayaAscii')
        cmds.file(new=True,force=True); cmds.file(str(self.asset),reference=True,namespace='vessel')
        cmds.select(clear=True); self.joint=cmds.joint(name='root'); cmds.setKeyframe(self.joint,attribute='tx',time=1,value=0); cmds.setKeyframe(self.joint,attribute='tx',time=3,value=5); cmds.sets(self.joint,name='All_joints')
        self.reset=cmds.createNode('transform',name='resetControl'); cmds.setKeyframe(self.reset,attribute='tx',time=1,value=2); cmds.setKeyframe(self.reset,attribute='tx',time=3,value=7); cmds.addAttr(self.reset,longName='custom',attributeType='double',keyable=True); cmds.setKeyframe(self.reset,attribute='custom',time=2,value=8); cmds.sets(self.reset,name='Reset_Trans')
        cmds.select(self.reset); cmds.currentTime(8); cmds.playbackOptions(minTime=1,maxTime=3); cmds.autoKeyframe(state=True)
    def tearDown(self): cmds.file(new=True,force=True); self.temp.cleanup()
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.file(query=True,sceneName=True),cmds.file(query=True,modified=True),cmds.undoInfo(query=True,undoName=True),cmds.keyframe(self.reset+'.tx',query=True,valueChange=True),cmds.keyframe(self.reset+'.custom',query=True,timeChange=True),cmds.file(query=True,reference=True))
    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message+' '+str(r.errors)); return r
    def test_full_snapshot_reference_bake_reset_namespace_fbx_prepared_scene(self):
        output=self.rootdir/'exports'; p=dict(output_dir=str(output),keyword='ship',save_prepared_scene=True,embedded_textures=False)
        before=self.state(); dry=self.call(dry_run=True,**p); self.assertEqual(before,self.state()); self.assertFalse(output.exists()); self.assertTrue(dry.data['reset_cuts_all_keys_on_members']); self.assertEqual(1,len(dry.data['references']))
        result=self.call(action='process',**p); self.assertEqual(before,self.state()); self.assertTrue(cmds.objExists('vessel:assetMesh')); self.assertTrue(cmds.objExists('root')); fbx=Path(result.data['outputs'][0]['output']); self.assertTrue(fbx.is_file()); self.assertTrue(fbx.name.startswith('vessel_ship_body')); prepared=result.data['prepared_scene']['path']
        self.assertFalse(TOOL.run(action='process',**p).success); self.assertEqual(before,self.state())
        cmds.file(prepared,open=True,force=True,executeScriptNodes=False); self.assertTrue(cmds.objExists('assetMesh')); self.assertFalse(cmds.objExists('vessel:assetMesh')); self.assertTrue(cmds.objExists('root_001')); self.assertFalse(cmds.file(query=True,reference=True)); self.assertEqual([1],cmds.keyframe('resetControl.tx',query=True,timeChange=True)); self.assertEqual([1],cmds.keyframe('resetControl.custom',query=True,timeChange=True)); self.assertAlmostEqual(-90,cmds.getAttr('resetControl.rx')); self.assertEqual([1,2,3],cmds.keyframe('root_001.tx',query=True,timeChange=True))
        cmds.file(new=True,force=True); cmds.loadPlugin('fbxmaya',quiet=True); mel.eval('FBXImportMode -v "add"'); cmds.file(str(fbx),i=True,type='FBX'); self.assertEqual(1,len(cmds.ls(type='mesh',noIntermediate=True)))
    def test_bad_sets_reset_driver_and_locked_targets_no_output(self):
        output=self.rootdir/'bad'; cmds.setAttr(self.reset+'.tx',lock=True); before=self.state(); self.assertFalse(TOOL.run(action='process',output_dir=str(output),keyword='ship').success); self.assertEqual(before,self.state()); self.assertFalse(output.exists())
        cmds.setAttr(self.reset+'.tx',lock=False); cmds.sets(clear='vessel:AAA_body_FBXExport'); self.assertFalse(TOOL.run(output_dir=str(output),keyword='ship').success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()
if __name__=='__main__': unittest.main()
