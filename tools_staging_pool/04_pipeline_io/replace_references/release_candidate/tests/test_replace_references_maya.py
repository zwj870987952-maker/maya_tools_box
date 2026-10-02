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
from maya_toolkit.tools.replace_references.tool import file_hash
class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='replace references '); self.root=Path(self.temp.name)
        cmds.file(new=True,force=True); cmds.polyCube(name='oldCube'); self.old=self.root/'old.ma'; cmds.file(rename=str(self.old)); cmds.file(save=True,type='mayaAscii')
        cmds.file(new=True,force=True); cmds.polySphere(name='newSphere'); self.new=self.root/'new.asset.mb'; cmds.file(rename=str(self.new)); cmds.file(save=True,type='mayaBinary')
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); cmds.file(str(self.old),reference=True,namespace='oldRNThing'); cmds.file(str(self.old),reference=True,namespace='secondOld')
        self.rn1=cmds.referenceQuery('oldRNThing:oldCube',referenceNode=True); self.rn2=cmds.referenceQuery('secondOld:oldCube',referenceNode=True)
        cmds.select('oldRNThing:oldCube'); cmds.currentTime(7); cmds.autoKeyframe(state=True)
    def tearDown(self): cmds.file(new=True,force=True); self.temp.cleanup()
    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message+' '+str(r.errors)); return r
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.namespaceInfo(currentNamespace=True,absoluteName=True),cmds.undoInfo(query=True,undoName=True))
    def test_two_references_exact_namespace_and_one_undo_redo(self):
        before=self.state(); p=dict(objects=['oldRNThing:oldCube','oldRNThing:oldCubeShape','secondOld:oldCube'],new_file=str(self.new)); dry=self.call(dry_run=True,**p); self.assertEqual(2,len(dry.data['references'])); self.assertEqual(before,self.state())
        result=self.call(action='replace',**p); self.assertEqual({'new_asset','new_asset1'},{r['new_namespace'] for r in result.data['references']}); self.assertTrue(cmds.objExists('new_asset:newSphere')); self.assertTrue(cmds.objExists('new_asset1:newSphere')); self.assertFalse(cmds.objExists('oldRNThing:oldCube')); self.assertEqual(before[2:5],self.state()[2:5])
        cmds.undo(); restored=self.state()[0]; self.assertTrue(before[0]<=restored); self.assertTrue(restored-before[0]<={'sharedReferenceNode'}); self.assertEqual(before[1],self.state()[1]); cmds.redo(); self.assertTrue(cmds.objExists('new_asset:newSphere')); self.assertEqual(self.new,Path(cmds.referenceQuery(self.rn1,filename=True,withoutCopyNumber=True))); cmds.undo()
    def test_unloaded_keep_namespace_and_edited_ref_all_table_refusal(self):
        cmds.file(unloadReference=self.rn1); before=self.state(); self.call(action='replace',reference_nodes=[self.rn1],new_file=str(self.new),rename_namespace=False)
        self.assertFalse(cmds.referenceQuery(self.rn1,isLoaded=True)); self.assertEqual(':oldRNThing',cmds.referenceQuery(self.rn1,namespace=True)); self.assertEqual(self.new,Path(cmds.referenceQuery(self.rn1,filename=True,withoutCopyNumber=True))); cmds.undo(); self.assertFalse(cmds.referenceQuery(self.rn1,isLoaded=True)); self.assertEqual(self.old,Path(cmds.referenceQuery(self.rn1,filename=True,withoutCopyNumber=True)))
        cmds.setAttr('secondOld:oldCube.tx',4); before=self.state(); self.assertFalse(TOOL.run(action='replace',reference_nodes=[self.rn1,self.rn2],new_file=str(self.new)).success); self.assertEqual(before,self.state()); self.assertEqual(self.old,Path(cmds.referenceQuery(self.rn1,filename=True,withoutCopyNumber=True)))
        with self.assertRaises(RuntimeError): TOOL.show_ui()
    def test_isolated_batch_saves_outputs_and_ambiguous_rules_no_output(self):
        source=self.root/'caller.ma'; cmds.file(rename=str(source)); cmds.file(save=True,type='mayaAscii'); digest=file_hash(source)
        cmds.file(new=True,force=True); cmds.polySphere(name='dirtyLive'); cmds.select('dirtyLive'); cmds.currentTime(9); cmds.autoKeyframe(state=True); before=self.state()
        output_dir=self.root/'results'; output_dir.mkdir(); rules=[{'source_contains':'old.ma','target':str(self.new)}]
        p=dict(files=[str(source)],rules=rules,output_dir=str(output_dir),rename_namespace=False)
        self.call(action='batch',dry_run=True,**p); self.assertEqual(before,self.state()); self.assertFalse(list(output_dir.iterdir()))
        result=self.call(action='batch',**p); self.assertEqual(before,self.state()); self.assertEqual(digest,file_hash(source)); row=result.data['scenes'][0]; self.assertEqual(2,row['replaced']); cmds.file(row['output']['path'],open=True,force=True,executeScriptNodes=False); self.assertTrue(cmds.objExists('oldRNThing:newSphere')); self.assertTrue(cmds.objExists('secondOld:newSphere')); self.assertFalse(cmds.objExists('oldRNThing:oldCube'))
        ambiguous=self.root/'ambiguous'; ambiguous.mkdir(); failed=TOOL.run(action='batch',files=[str(source)],rules=rules+[{'source_contains':'.ma','target':str(self.new)}],output_dir=str(ambiguous),rename_namespace=False)
        self.assertFalse(failed.success); self.assertIn('multiple rules',failed.data['scenes'][0]['message']); self.assertFalse(list(ambiguous.iterdir()))
if __name__=='__main__': unittest.main()
