import json
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
from maya_toolkit.tools.fbx_batch_exporter_v7.tool import FLAGS,configuration
class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='fbx output '); self.root=Path(self.temp.name); cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.cube=cmds.polyCube(name='model')[0]; cmds.setKeyframe(self.cube,attribute='tx',time=1,value=0); cmds.setKeyframe(self.cube,attribute='tx',time=3,value=6)
        cmds.currentTime(2); cmds.currentTime(1); cmds.select(self.cube); cmds.currentTime(8); cmds.playbackOptions(animationStartTime=0,animationEndTime=10,minTime=2,maxTime=7); cmds.autoKeyframe(state=True)
    def tearDown(self): cmds.file(new=True,force=True); self.temp.cleanup()
    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message+' '+str(r.errors)); return r
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),tuple(cmds.playbackOptions(query=True,**{k:True}) for k in ('animationStartTime','animationEndTime','minTime','maxTime')),cmds.file(query=True,modified=True),cmds.undoInfo(query=True,undoName=True))
    def settings(self):
        cmds.loadPlugin('fbxmaya',quiet=True)
        return [mel.eval(command+' -q') for command in list(FLAGS.values())+['FBXExportBakeComplexAnimation','FBXExportBakeComplexStep','FBXExportBakeComplexStart','FBXExportBakeComplexEnd','FBXExportUpAxis','FBXExportFileVersion']]+[mel.eval('FBXProperty "Export|IncludeGrp|Animation" -q')]
    def test_real_ascii_export_import_animation_and_restore(self):
        jobs=[{'objects':[self.cube],'start':1,'end':3}]; p=dict(jobs=jobs,output_dir=str(self.root),prefix='keep prefix',options={'ascii':True,'embedded_textures':False})
        before=self.state(); dry=self.call(dry_run=True,**p); self.assertEqual(before,self.state()); self.assertEqual([],list(self.root.iterdir()))
        settings=self.settings(); before=self.state(); result=self.call(action='export',**p); self.assertEqual(before,self.state()); self.assertEqual(settings,self.settings())
        path=Path(result.data['outputs'][0]['output']); self.assertTrue(path.read_bytes().startswith(b'; FBX')); self.assertGreater(path.stat().st_size,1000)
        result2=self.call(action='export',**p); second=Path(result2.data['outputs'][0]['output']); self.assertTrue(second.name.startswith('keep prefix_')); self.assertNotEqual(path,second)
        cmds.file(new=True,force=True); mel.eval('FBXImportMode -v "add"'); cmds.file(str(path),i=True,type='FBX',namespace='back'); models=cmds.ls(type='mesh'); self.assertEqual(1,len(models),str(cmds.ls(long=True))); parent=cmds.listRelatives(models[0],parent=True,fullPath=True)[0]; cmds.currentTime(3); self.assertAlmostEqual(6,cmds.getAttr(parent+'.tx'),places=4)
    def test_scene_ssc_and_hierarchy_bake_real_one_undo(self):
        cmds.select(clear=True); joint=cmds.joint(name='rootJoint'); cmds.select(self.cube); before=self.state(); self.call(action='disable_ssc',objects=[joint],dry_run=True); self.assertEqual(before,self.state())
        self.call(action='disable_ssc',objects=[joint]); self.assertFalse(cmds.getAttr(joint+'.segmentScaleCompensate')); cmds.undo(); self.assertTrue(cmds.getAttr(joint+'.segmentScaleCompensate')); cmds.redo(); self.assertFalse(cmds.getAttr(joint+'.segmentScaleCompensate')); cmds.undo()
        target=cmds.createNode('transform',name='driven'); constraint=cmds.pointConstraint(self.cube,target,maintainOffset=False)[0]; cmds.select(self.cube)
        before=self.state(); self.call(action='bake',objects=[target],start=1,end=3); self.assertEqual(before[1:5],self.state()[1:5]); self.assertEqual([1,2,3],cmds.keyframe(target,attribute='tx',query=True,timeChange=True)); self.assertAlmostEqual(6,cmds.getAttr(target+'.tx',time=3),places=4)
        cmds.undo(); self.assertTrue(cmds.isConnected(constraint+'.constraintTranslateX',target+'.tx'))
        cmds.setAttr(joint+'.segmentScaleCompensate',lock=True); before=self.state(); self.assertFalse(TOOL.run(action='disable_ssc',objects=[joint]).success); self.assertEqual(before,self.state())
    def test_settings_roundtrip_and_bad_last_row_dry_no_effects(self):
        config=configuration({'version':1,'jobs':[{'objects':[self.cube],'start':1,'end':3}],'prefix':'p','options':{'ascii':False}}); path=self.root/'config.json'
        self.call(action='save_settings',settings_path=str(path),configuration=config,dry_run=True); self.assertFalse(path.exists()); self.call(action='save_settings',settings_path=str(path),configuration=config)
        result=self.call(action='load_settings',settings_path=str(path)); self.assertEqual(config,result.data['configuration']); original=path.read_bytes(); self.assertFalse(TOOL.run(action='save_settings',settings_path=str(path),configuration=config).success); self.assertEqual(original,path.read_bytes())
        before=self.state(); self.assertFalse(TOOL.run(action='export',jobs=[{'objects':[self.cube],'start':1,'end':3},{'objects':['missing'],'start':1,'end':3}],output_dir=str(self.root)).success); self.assertEqual(before,self.state()); self.assertFalse(list(self.root.glob('*.fbx')))
        with self.assertRaises(RuntimeError): TOOL.show_ui()
if __name__=='__main__': unittest.main()
