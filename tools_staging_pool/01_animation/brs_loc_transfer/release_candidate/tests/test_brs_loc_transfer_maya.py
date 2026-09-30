import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy harness may execute disposable-scene tests')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.brs_loc_transfer import scene, runtime, legacy


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.node = cmds.createNode('transform', name='ctrl')
        for frame, value in [(1, 0), (3, 2), (5, 4)]:
            cmds.setKeyframe(self.node, attribute='tx', time=frame, value=value)
        cmds.keyframe(self.node, attribute='tx', edit=True, time=(3, 3), breakdown=True)
        cmds.currentTime(1)
        cmds.playbackOptions(minTime=1, maxTime=5)
        cmds.select(self.node)

    def create(self, **kwargs):
        result = TOOL.run(action='create', objects=[self.node], **kwargs)
        self.assertTrue(result.success, result.message)
        return scene.locator_for(self.node, required=True)

    def test_create_sparse_annotation_no_source_write_and_undo(self):
        keys = cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True)
        cmds.flushUndo()
        loc = self.create(constrain=False)
        self.assertEqual([1, 3, 5], cmds.keyframe(loc, attribute='tx', query=True, timeChange=True))
        self.assertEqual([3], cmds.keyframe(loc, attribute='tx', query=True, breakdown=True))
        self.assertEqual(keys, cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True))
        self.assertTrue(scene.owned(scene.group(), 'group'))
        self.assertTrue(any(scene.owned(n, 'annotation') for n in cmds.listRelatives(loc, allDescendents=True, fullPath=True)))
        cmds.undo()
        self.assertFalse(scene.by_role('locator'))
        self.assertTrue(cmds.objExists(self.node))

    def test_apply_edited_locator_constraints_undo(self):
        loc = self.create(constrain=True, annotation=False, bake_all=True)
        self.assertTrue(cmds.listRelatives(self.node, type='constraint'))
        cmds.keyframe(loc, attribute='tx', edit=True, relative=True, valueChange=10)
        cmds.flushUndo()
        result = TOOL.run(action='apply', objects=[self.node], bake_all=True)
        self.assertTrue(result.success, result.message)
        self.assertFalse(scene.by_role('locator'))
        self.assertFalse(scene.group())
        self.assertTrue(cmds.objExists(self.node))
        self.assertFalse(cmds.listRelatives(self.node, type='constraint'))
        self.assertAlmostEqual(10, cmds.getAttr(self.node + '.tx', time=1), places=4)
        cmds.undo()
        self.assertTrue(scene.locator_for(self.node, required=True))

    def test_timeline_dense_sparse_skip_and_guard(self):
        cmds.playbackOptions(minTime=0, maxTime=6)
        static = cmds.createNode('transform', name='static')
        result = TOOL.run(action='create', objects=[self.node, static], in_timeline=True, bake_all=True, constrain=False, annotation=False)
        self.assertTrue(result.success, result.message)
        self.assertEqual([cmds.ls(static, long=True)[0]], result.data['skipped'])
        loc = scene.locator_for(self.node, required=True)
        self.assertEqual(list(range(7)), cmds.keyframe(loc, attribute='tx', query=True, timeChange=True))
        with self.assertRaises(RuntimeError):
            legacy.objectToLocatorSnap()
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_readonly_preflight_foreign_nodes_and_connections(self):
        before = cmds.ls(long=True)
        selection = cmds.ls(selection=True, long=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        self.assertTrue(TOOL.run(dry_run=True, action='create', objects=[self.node]).success)
        self.assertEqual(before, cmds.ls(long=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        foreign = cmds.createNode('transform', name=scene.GROUP)
        self.assertFalse(TOOL.run(action='create', objects=[self.node]).success)
        cmds.delete(foreign)
        loc = self.create(constrain=False, annotation=False)
        child = cmds.createNode('transform', name='foreignChild', parent=loc)
        self.assertFalse(TOOL.run(action='apply', objects=[self.node]).success)
        self.assertTrue(cmds.objExists(child))

    def test_rename_save_reload_identity_and_apply(self):
        self.create(constrain=False, annotation=False)
        node = cmds.rename(self.node, 'renamedCtrl')
        loc = scene.locator_for(node, required=True)
        cmds.rename(loc, 'renamedLocator')
        cmds.rename(scene.group(), 'renamedGroup')
        import tempfile
        with tempfile.TemporaryDirectory() as scratch:
            file = str(Path(scratch) / 'owned.ma')
            cmds.file(rename=file)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(file, open=True, force=True)
            result = TOOL.run(action='apply', objects=[node])
        self.assertTrue(result.success, result.message)
        self.assertTrue(cmds.objExists(node))

    def test_guide_full_redirect_path(self):
        loc = self.create(constrain=False, annotation=False)
        before_world = cmds.getAttr(loc + '.worldMatrix[0]', time=1)[12]
        self.assertTrue(TOOL.run(action='create_guide').success)
        guide = scene.guide()
        cmds.setAttr(guide + '.tx', 10)
        result = TOOL.run(action='redirect', annotation=False, bake_all=True)
        self.assertTrue(result.success, result.message)
        self.assertFalse(scene.guide())
        self.assertEqual(1, len(scene.by_role('locator')))
        self.assertTrue(scene.locator_for(self.node, required=True))
        self.assertTrue(cmds.getAttr(scene.group() + '.tx', lock=True))
        current = scene.locator_for(self.node, required=True)
        after_world = cmds.getAttr(current + '.worldMatrix[0]', time=1)[12]
        self.assertAlmostEqual(10, cmds.getAttr(scene.group() + '.tx'))
        print('Original redirection world observation:', before_world, after_world, 'group tx', cmds.getAttr(scene.group() + '.tx'))
        self.assertAlmostEqual(before_world, after_world, places=4)

    def test_failure_restores_refresh_time_selection_locks_guard(self):
        selection = cmds.ls(selection=True, long=True)
        with patch.object(legacy, 'bakeKey', side_effect=RuntimeError('injected bake failure')):
            result = TOOL.run(action='create', objects=[self.node])
        self.assertFalse(result.success)
        self.assertEqual(1, cmds.currentTime(query=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertFalse(cmds.refresh(query=True, suspend=True))
        self.assertFalse(runtime._ACTIVE)

    def test_extra_animation_external_constraint_and_rewired_message_refused(self):
        loc = self.create(constrain=False, annotation=False)
        cmds.addAttr(self.node, longName='customAnimated', attributeType='double', keyable=True)
        cmds.setKeyframe(self.node, attribute='customAnimated', time=1, value=1)
        self.assertFalse(TOOL.run(action='apply', objects=[self.node]).success)
        cmds.cutKey(self.node, attribute='customAnimated', clear=True)
        foreign = cmds.createNode('transform', name='foreignDriver')
        con = cmds.pointConstraint(foreign, self.node)[0]
        self.assertFalse(TOOL.run(action='apply', objects=[self.node]).success)
        self.assertTrue(cmds.objExists(con))
        cmds.delete(con)
        cmds.disconnectAttr(self.node + '.message', loc + '.' + scene.TARGET)
        cmds.connectAttr(foreign + '.message', loc + '.' + scene.TARGET)
        self.assertFalse(TOOL.run(action='apply', objects=[self.node]).success)


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
