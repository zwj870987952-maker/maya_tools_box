from pathlib import Path
import importlib.util
import sys
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.undo_checkpoint import manager
class Tests(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True,infinity=True);manager.manager.clear()
    def test_true_marker_restore_two_points_undo_redo_and_name_injection(self):
        cube=cmds.polyCube(name='checkpointCube')[0];cmds.setAttr(cube+'.tx',1)
        old_queue=manager.queue_snapshot();before_nodes=cmds.ls();dry=tool.run(dry_run=True,action='create',name='a"; deleteAll;')
        self.assertTrue(dry.success,dry);self.assertEqual(manager.queue_snapshot(),old_queue);self.assertEqual(cmds.ls(),before_nodes)
        first=tool.run(action='create',name='a"; deleteAll;');self.assertTrue(first.success,first)
        cmds.setAttr(cube+'.tx',2);second=tool.run(action='create',name='second');self.assertTrue(second.success,second);cmds.setAttr(cube+'.tx',3)
        queue=manager.queue_snapshot();preview=tool.run(dry_run=True,action='restore',target_id=first.data['id']);self.assertTrue(preview.success,preview);self.assertEqual(manager.queue_snapshot(),queue);self.assertEqual(cmds.getAttr(cube+'.tx'),3)
        refused=tool.run(action='restore',target_id=first.data['id'],max_steps=1);self.assertFalse(refused.success);self.assertEqual(cmds.getAttr(cube+'.tx'),3);self.assertEqual(manager.queue_snapshot(),queue)
        result=tool.run(action='restore',target_id=second.data['id']);self.assertTrue(result.success,result);self.assertEqual(cmds.getAttr(cube+'.tx'),2)
        cmds.redo();self.assertTrue(manager.applied[second.data['id']]);cmds.redo();self.assertEqual(cmds.getAttr(cube+'.tx'),3)
        result=tool.run(action='restore',target_id=first.data['id']);self.assertTrue(result.success,result);self.assertEqual(cmds.getAttr(cube+'.tx'),1);self.assertTrue(cmds.objExists(cube))
    def test_flushed_queue_or_foreign_id_never_undo_unrelated_actions(self):
        cube=cmds.polyCube()[0];created=tool.run(action='create');self.assertTrue(created.success,created);cmds.flushUndo();cmds.setAttr(cube+'.tx',9);queue=manager.queue_snapshot()
        self.assertFalse(tool.run(action='restore',target_id=created.data['id']).success);self.assertEqual(cmds.getAttr(cube+'.tx'),9);self.assertEqual(manager.queue_snapshot(),queue)
        self.assertFalse(tool.run(action='restore',target_id='foreign').success);self.assertEqual(cmds.getAttr(cube+'.tx'),9)
    def test_clear_overwrite_queue_preserved_and_disabled_undo(self):
        cmds.polyCube();first=tool.run(action='create');second=tool.run(action='create',overwrite=True);self.assertTrue(first.success);self.assertTrue(second.success);self.assertEqual(len(manager.items),1)
        queue=manager.queue_snapshot();self.assertTrue(tool.run(action='clear').success);self.assertEqual(manager.items,[]);self.assertEqual(manager.queue_snapshot(),queue)
        cmds.undoInfo(stateWithoutFlush=False);self.assertFalse(tool.run(action='create').success);self.assertFalse(tool.run(action='restore').success);cmds.undoInfo(stateWithoutFlush=True)
if __name__=='__main__':unittest.main()
