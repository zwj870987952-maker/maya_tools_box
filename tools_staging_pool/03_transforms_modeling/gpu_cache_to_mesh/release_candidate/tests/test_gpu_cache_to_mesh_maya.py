import os
from pathlib import Path
import runpy
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1': raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
for plugin in ('AbcExport','AbcImport','gpuCache'): cmds.loadPlugin(plugin,quiet=True)
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True); cmds.undoInfo(state=True)
        self.temp=tempfile.TemporaryDirectory(); self.path=(Path(self.temp.name)/'fixture.abc').as_posix()
        src=cmds.polyCube(name='abcCube')[0]
        cmds.setKeyframe(src,attribute='tx',time=1,value=2); cmds.setKeyframe(src,attribute='tx',time=3,value=6)
        cmds.AbcExport(j='-frameRange 1 3 -root |abcCube -file "'+self.path+'"')
        cmds.delete(src)
        self.parent=cmds.group(empty=True,name='cacheParent'); self.cache=cmds.createNode('gpuCache',parent=self.parent,name='cacheShape')
        cmds.setAttr(self.cache+'.cacheFileName',self.path,type='string'); cmds.setAttr(self.parent+'.ty',10)
        cmds.currentTime(1); cmds.select(self.parent)
    def tearDown(self):
        cmds.file(new=True,force=True); cmds.flushUndo()
        # Native cache libraries may retain Windows read handles. In this
        # isolated process only, release plugins before cleaning scratch files.
        for plugin in ('gpuCache','AbcImport'): cmds.unloadPlugin(plugin)
        self.temp.cleanup()
        for plugin in ('AbcImport','gpuCache'): cmds.loadPlugin(plugin,quiet=True)
    def state(self): return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),cmds.getAttr(self.cache+'.visibility'),cmds.namespaceInfo(currentNamespace=True))
    def test_real_Alembic_import_parent_animation_and_Undo(self):
        before=self.state(); result=TOOL.run(objects=[self.parent],dry_run=True)
        self.assertTrue(result.success,result.message); self.assertEqual(before,self.state())
        result=TOOL.run(objects=[self.parent]); self.assertTrue(result.success,result.message+' '+str(result.errors))
        roots=result.data['imports'][0]['roots']; self.assertEqual(1,len(roots))
        root=roots[0]; mesh=cmds.listRelatives(root,shapes=True,fullPath=True)[0]
        self.assertEqual(8,cmds.polyEvaluate(mesh,vertex=True)); self.assertAlmostEqual(2,cmds.getAttr(root+'.tx'))
        self.assertAlmostEqual(10,cmds.xform(root,query=True,worldSpace=True,translation=True)[1])
        cmds.currentTime(3); self.assertAlmostEqual(6,cmds.getAttr(root+'.tx')); cmds.currentTime(1)
        self.assertEqual(0,cmds.getAttr(self.cache+'.visibility'))
    def test_one_chunk_removes_imported_mesh_and_restores_cache(self):
        before=self.state(); result=TOOL.run(objects=[self.cache]); self.assertTrue(result.success,result.message)
        cmds.undo()
        self.assertEqual(before[0],set(cmds.ls(long=True)))
        self.assertEqual(1,cmds.getAttr(self.cache+'.visibility'))
        self.assertEqual(before[3],cmds.undoInfo(query=True,undoName=True))
        cmds.redo()
        root=result.data['imports'][0]['roots'][0]
        self.assertTrue(cmds.objExists(root)); self.assertEqual(0,cmds.getAttr(self.cache+'.visibility'))
        self.assertAlmostEqual(6,cmds.getAttr(root+'.tx',time=3))
        cmds.undo(); self.assertEqual(before[0],set(cmds.ls(long=True)))
        cmds.redo(); self.assertTrue(cmds.objExists(root))
    def test_all_rows_preflight_hide_option_and_guards(self):
        bad=cmds.createNode('gpuCache',parent=self.parent,name='badCache')
        cmds.setAttr(bad+'.cacheFileName',str(Path(self.temp.name)/'missing.abc'),type='string')
        before=self.state(); result=TOOL.run(objects=[self.parent]); self.assertFalse(result.success); self.assertEqual(before,self.state())
        cmds.delete(bad)
        result=TOOL.run(objects=[self.cache],hide_original=False); self.assertTrue(result.success,result.message)
        self.assertEqual(1,cmds.getAttr(self.cache+'.visibility')); cmds.undo()
        self.assertFalse(TOOL.run(objects=[self.parent,self.cache],dry_run=True).success)
        cmds.setAttr(self.cache+'.visibility',lock=True); self.assertFalse(TOOL.run(objects=[self.cache],dry_run=True).success)
        with self.assertRaises(RuntimeError): TOOL.show_ui()


if __name__=='__main__': unittest.main()
