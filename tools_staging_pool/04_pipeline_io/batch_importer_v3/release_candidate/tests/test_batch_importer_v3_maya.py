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
        self.temp=tempfile.TemporaryDirectory(prefix='batch importer '); self.directory=Path(self.temp.name)
        cmds.file(new=True,force=True); cmds.polyCube(name='model'); self.ma=self.directory/'first.asset.ma'; cmds.file(rename=str(self.ma)); cmds.file(save=True,type='mayaAscii')
        self.mb=self.directory/'second.mb'; cmds.file(rename=str(self.mb)); cmds.file(save=True,type='mayaBinary')
        self.obj=self.directory/'triangle.obj'; self.obj.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n',encoding='ascii')
        cmds.file(new=True,force=True); cmds.undoInfo(state=True); self.alive=cmds.polySphere(name='existing')[0]; cmds.select(self.alive); cmds.currentTime(7); cmds.autoKeyframe(state=True)

    def tearDown(self): cmds.file(new=True,force=True); self.temp.cleanup()

    def call(self,**p):
        result=TOOL.run(**p); self.assertTrue(result.success,result.message); return result

    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.namespaceInfo(currentNamespace=True,absoluteName=True))

    def test_ma_mb_multiple_import_owned_undo_redo_without_source(self):
        before=self.state(); items=[{'path':str(self.ma),'count':2},{'path':str(self.mb),'namespace':'other'}]
        queue=cmds.undoInfo(query=True,undoName=True); self.call(items=items,dry_run=True); self.assertEqual(before,self.state()); self.assertEqual(queue,cmds.undoInfo(query=True,undoName=True))
        self.call(action='import',items=items); imported=self.state(); self.assertEqual(before[1:],imported[1:]); self.assertEqual(3,len(cmds.ls('first_asset*:*','other:*',type='mesh')))
        cmds.undo(); self.assertEqual(before,self.state()); self.assertTrue(cmds.namespace(exists=':first_asset')); self.ma.rename(self.ma.with_suffix('.ma.bak')); self.mb.rename(self.mb.with_suffix('.mb.bak'))
        cmds.redo(); self.assertEqual(imported,self.state()); self.assertTrue(cmds.objExists('|first_asset:model')); cmds.undo(); self.assertEqual(before,self.state())

    def test_references_repeated_undo_redo_and_removal_whole_scope(self):
        before=self.state(); items=[{'path':str(self.ma),'count':2,'namespace':'refModel'}]
        result=self.call(action='reference',items=items); self.assertEqual(2,len(result.data['imports'])); self.assertEqual(before[1:],self.state()[1:]); referenced=self.state()[0]
        cmds.undo(); self.assertEqual(before[0],self.state()[0]); cmds.redo(); self.assertEqual(referenced,self.state()[0])
        cmds.select('|refModel:model','|refModel:model|refModel:modelShape'); preview=self.call(action='remove_reference',dry_run=True)
        self.assertEqual(1,len(preview.data['references'])); self.assertTrue(preview.data['whole_file_reference_removal'])
        self.call(action='remove_reference'); self.assertFalse(cmds.objExists('|refModel:model')); self.assertTrue(cmds.objExists('|refModel1:model'))
        cmds.undo(); self.assertTrue(cmds.objExists('|refModel:model')); self.assertEqual(['|refModel:model','|refModel:model|refModel:modelShape'],cmds.ls(selection=True,long=True)); cmds.redo(); self.assertFalse(cmds.objExists('|refModel:model')); self.assertTrue(cmds.objExists('|refModel1:model'))

    def test_obj_actual_import_namespace_and_bad_last_row_no_writes(self):
        before=self.state(); self.assertFalse(TOOL.run(action='import',items=[{'path':str(self.ma)},{'path':str(self.directory/'missing.ma')}]).success); self.assertEqual(before,self.state())
        self.assertFalse(TOOL.run(action='reference',items=[{'path':str(self.ma)},{'path':str(self.ma)}]).success); self.assertEqual(before,self.state())
        self.call(action='import',items=[{'path':str(self.obj),'namespace':'objModel'}]); self.assertEqual(1,len(cmds.ls('objModel:*',type='mesh'))); cmds.undo(); self.assertEqual(before,self.state()); cmds.redo(); self.assertEqual(1,len(cmds.ls('objModel:*',type='mesh'))); cmds.undo()
        self.call(action='reference',items=[{'path':str(self.ma),'namespace':'edited'}]); cmds.setAttr('edited:model.translateX',3)
        before=self.state(); self.assertFalse(TOOL.run(action='remove_reference',objects=['edited:model']).success); self.assertEqual(before,self.state())
        self.assertFalse(TOOL.run(action='remove_reference',objects=[self.alive]).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()

    def test_unloaded_reference_state_and_nested_tree_removal_rejected(self):
        ref=self.call(action='reference',items=[{'path':str(self.ma),'namespace':'unloaded'}]).data['imports'][0]['reference_node']
        cmds.lockNode(ref,lock=False); ref=cmds.rename(ref,'customRN'); cmds.lockNode(ref,lock=True)
        cmds.file(unloadReference=ref); before=self.state(); preview=self.call(action='remove_reference',reference_nodes=[ref],dry_run=True)
        self.assertFalse(preview.data['references'][0]['loaded']); self.assertEqual([],preview.data['references'][0]['nodes']); self.assertEqual(before,self.state())
        self.call(action='remove_reference',reference_nodes=[ref]); cmds.undo(); self.assertTrue(cmds.objExists(ref)); self.assertTrue(cmds.lockNode(ref,query=True,lock=True)[0]); self.assertFalse(cmds.referenceQuery(ref,isLoaded=True)); cmds.redo(); self.assertFalse(cmds.objExists(ref))
        cmds.file(new=True,force=True); cmds.file(str(self.ma),reference=True,namespace='inner'); nested=self.directory/'nested.ma'; cmds.file(rename=str(nested)); cmds.file(save=True,type='mayaAscii'); cmds.file(new=True,force=True)
        self.call(action='reference',items=[{'path':str(nested),'namespace':'outer'}]); before=self.state()
        self.assertFalse(TOOL.run(action='remove_reference',objects=['outer:inner:model']).success); self.assertEqual(before,self.state())
        parent=[n for n in cmds.ls(type='reference') if n!='sharedReferenceNode' and not cmds.referenceQuery(n,parent=True,referenceNode=True)][0]
        self.assertFalse(TOOL.run(action='remove_reference',reference_nodes=[parent]).success); self.assertEqual(before,self.state())


if __name__=='__main__': unittest.main()
