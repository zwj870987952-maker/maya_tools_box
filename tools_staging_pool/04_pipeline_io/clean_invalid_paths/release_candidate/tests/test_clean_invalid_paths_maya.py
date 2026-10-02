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
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.bad=cmds.shadingNode('file',asTexture=True,name='badTexture'); cmds.setAttr(self.bad+'.fileTextureName','D:/中文/texture.png',type='string')
        self.accent=cmds.shadingNode('file',asTexture=True,name='accentTexture'); cmds.setAttr(self.accent+'.fileTextureName','D:/é.png',type='string')
        self.good=cmds.shadingNode('file',asTexture=True,name='asciiMissing'); cmds.setAttr(self.good+'.fileTextureName','D:/not-existing.png',type='string')
        self.container=cmds.shadingNode('layeredTexture',asTexture=True,name='layeredOwner'); cmds.connectAttr(self.good+'.outColor',self.container+'.inputs[0].color'); cmds.connectAttr(self.bad+'.outColor',self.container+'.inputs[1].color')
        self.cube=cmds.polyCube(name='alive')[0]; cmds.select(self.cube); cmds.currentTime(6); cmds.autoKeyframe(state=True)
    def tearDown(self): cmds.file(new=True,force=True); self.temp.cleanup()
    def call(self,**p):
        r=TOOL.run(**p); self.assertTrue(r.success,r.message); return r
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.autoKeyframe(query=True,state=True),cmds.undoInfo(query=True,undoName=True))
    def test_scan_all_actual_owners_dry_no_writes_and_undo_connections(self):
        before=self.state(); preview=self.call(dry_run=True,action='delete',nodes=[self.bad]); self.assertEqual(before,self.state())
        result=self.call(nodes=[self.container]); self.assertEqual([self.bad],[r['node'] for r in result.data['issues']]); self.assertFalse(result.data['containers'][0]['delete_container'])
        self.assertFalse(TOOL.run(action='delete',nodes=[self.container]).success); self.assertEqual(before,self.state())
        all_scan=self.call(); self.assertEqual({self.bad,self.accent},{r['node'] for r in all_scan.data['issues']}); self.assertNotIn(self.good,{r['node'] for r in all_scan.data['issues']})
        self.call(action='delete',nodes=[self.bad]); self.assertFalse(cmds.objExists(self.bad)); self.assertTrue(cmds.objExists(self.container)); self.assertTrue(cmds.objExists(self.good)); self.assertEqual(before[1:4],self.state()[1:4])
        cmds.undo(); self.assertEqual(before[0],self.state()[0]); self.assertTrue(cmds.isConnected(self.bad+'.outColor',self.container+'.inputs[1].color')); cmds.redo(); self.assertFalse(cmds.objExists(self.bad)); cmds.undo()
    def test_path_attrs_dag_shape_parent_and_locked_all_or_none(self):
        cmds.loadPlugin('gpuCache',quiet=True); parent=cmds.createNode('transform',name='cacheParent'); shape=cmds.createNode('gpuCache',parent=parent,name='cacheShape'); cmds.setAttr(shape+'.cacheFileName','D:/坏/cache.abc',type='string')
        before=self.state(); self.call(action='delete',nodes=[shape]); self.assertFalse(cmds.objExists(shape)); self.assertTrue(cmds.objExists(parent)); cmds.undo(); self.assertEqual(before[0],self.state()[0]); cmds.redo(); self.assertFalse(cmds.objExists(shape)); cmds.undo()
        cmds.lockNode(self.accent,lock=True); before=self.state(); self.assertFalse(TOOL.run(action='delete',nodes=[self.bad,self.accent]).success); self.assertEqual(before,self.state()); cmds.lockNode(self.accent,lock=False)
        plane=cmds.imagePlane(name='imagePlane',fileName='D:/坏/image.png')[1]; r=self.call(nodes=[plane]); self.assertEqual('imageName',r.data['issues'][0]['attribute'])
        self.call(action='delete',nodes=[plane]); self.assertFalse(cmds.objExists(plane)); cmds.undo(); self.assertTrue(cmds.objExists(plane))
    def test_whole_reference_scope_undo_and_edited_reference_refusal(self):
        path=self.root/'中文.ma'; cmds.file(new=True,force=True); cmds.polyCube(name='model'); cmds.file(rename=str(path)); cmds.file(save=True,type='mayaAscii'); cmds.file(new=True,force=True)
        cmds.file(str(path),reference=True,namespace='ref'); rn=cmds.referenceQuery('ref:model',referenceNode=True); cmds.select('ref:model')
        before=self.state(); self.assertFalse(TOOL.run(action='delete',nodes=[rn]).success); self.assertEqual(before,self.state())
        dry=self.call(action='delete',nodes=[rn],allow_reference_removal=True,dry_run=True); self.assertTrue(dry.data['whole_reference_removal']); self.assertGreater(len(dry.data['references'][0]['nodes']),0); self.assertEqual(before,self.state())
        self.call(action='delete',nodes=[rn],allow_reference_removal=True); self.assertFalse(cmds.objExists('ref:model')); cmds.undo(); self.assertTrue(cmds.objExists('ref:model')); self.assertEqual(before[1],self.state()[1]); cmds.redo(); self.assertFalse(cmds.objExists('ref:model')); cmds.undo()
        cmds.setAttr('ref:model.tx',2); before=self.state(); self.assertFalse(TOOL.run(action='delete',nodes=[rn],allow_reference_removal=True).success); self.assertEqual(before,self.state())
        with self.assertRaises(RuntimeError): TOOL.show_ui()
if __name__=='__main__': unittest.main()
