import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy harness may execute disposable-scene tests')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.copy_animation import scene, runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.source = cmds.createNode('transform', name='source')
        self.target = cmds.createNode('transform', name='target')
        for time, value in [(1, 0), (3, 4), (5, 8)]:
            cmds.setKeyframe(self.source, attribute='tx', time=time, value=value)
        cmds.currentTime(1)
        cmds.setAttr(self.target + '.tx', 10)
        cmds.select(self.source)

    def run_pair(self, action='execute', **modes):
        pair = {'source': self.source, 'target': self.target, 'modes': {'translate': 'none', 'rotate': 'none', 'scale': 'none', 'other': 'none'}}
        pair['modes'].update(modes)
        result = TOOL.run(action=action, pairs=[pair], start=1, end=5)
        self.assertTrue(result.success, result.message + str(result.errors))
        return result

    def test_frame_key_gating_offset_undo_and_cleanup(self):
        cmds.flushUndo()
        self.run_pair(translate='frame')
        self.assertEqual([1, 3, 5], cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        self.assertEqual([10, 14, 18], cmds.keyframe(self.target, attribute='tx', query=True, valueChange=True))
        self.assertTrue(scene.group())
        cmds.undo()
        self.assertFalse(scene.records())
        self.assertFalse(cmds.keyframe(self.target, query=True))
        self.assertTrue(cmds.objExists(self.target))

    def test_numeric_every_integer_and_matching_custom_scalar(self):
        for node in (self.source, self.target):
            cmds.addAttr(node, longName='custom', attributeType='double', keyable=True)
        cmds.setKeyframe(self.source, attribute='custom', time=1, value=2)
        cmds.setKeyframe(self.source, attribute='custom', time=5, value=6)
        self.run_pair(translate='numeric', other='numeric')
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        self.assertAlmostEqual(8, cmds.getAttr(self.target + '.tx', time=5))
        self.assertAlmostEqual(6, cmds.getAttr(self.target + '.custom', time=5))
        self.assertFalse(scene.nodes('locator'))

    def test_constraints_maintain_offset_repeat_cleanup_empty_target(self):
        self.run_pair(translate='constraint')
        self.assertAlmostEqual(18, cmds.getAttr(self.target + '.tx', time=5))
        self.run_pair(translate='constraint')
        self.assertEqual(1, len(scene.records()[0][1]['constraints']))
        result = TOOL.run(action='cleanup')
        self.assertTrue(result.success, result.message)
        self.assertTrue(cmds.objExists(self.target))
        self.assertFalse(cmds.listRelatives(self.target, type='constraint'))
        self.assertFalse(scene.records())

    def test_readonly_lock_foreign_group_set_and_child_protection(self):
        pair = {'source': self.source, 'target': self.target, 'modes': {'translate': 'frame', 'rotate': 'none', 'scale': 'none'}}
        before, selection = cmds.ls(long=True), cmds.ls(selection=True, long=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        self.assertTrue(TOOL.run(dry_run=True, action='execute', pairs=[pair], start=1, end=5).success)
        self.assertEqual(before, cmds.ls(long=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        foreign = cmds.group(empty=True, name=scene.GROUP)
        self.assertFalse(TOOL.run(action='execute', pairs=[pair]).success)
        cmds.delete(foreign)
        self.run_pair(action='create_locators')
        node, data = scene.records()[0]
        child = cmds.createNode('transform', name='foreignChild', parent=scene.find(data['source_locator']))
        self.assertFalse(TOOL.run(action='cleanup').success)
        self.assertTrue(cmds.objExists(child))

    def test_rename_save_reload_record_and_rebuild(self):
        self.run_pair(action='create_locators')
        self.source = cmds.rename(self.source, 'renamedSource')
        self.target = cmds.rename(self.target, 'renamedTarget')
        node, data = scene.records()[0]
        cmds.rename(scene.find(data['source_locator']), 'renamedHelper')
        with tempfile.TemporaryDirectory() as scratch:
            file = str(Path(scratch) / 'owned.ma')
            cmds.file(rename=file)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(file, open=True, force=True)
            self.run_pair(translate='frame')
        self.assertAlmostEqual(18, cmds.getAttr(self.target + '.tx', time=5))
        self.assertEqual(1, len(scene.records()))

    def test_config_roundtrip_overwrite_and_gui_refusal(self):
        pair = {'source': self.source, 'target': self.target}
        with tempfile.TemporaryDirectory() as scratch:
            file = str(Path(scratch) / 'config.json')
            self.assertTrue(TOOL.run(action='save_config', file_path=file, pairs=[pair]).success)
            self.assertFalse(TOOL.run(action='save_config', file_path=file, pairs=[pair]).success)
            result = TOOL.run(action='load_config', file_path=file)
            self.assertTrue(result.success, result.message)
            self.assertEqual(self.source, result.data['pairs'][0]['source'])
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_error_recorded_failed_and_state_guard_undo(self):
        from maya_toolkit.tools.copy_animation.algorithms import ChannelAlgorithms
        cmds.flushUndo()
        selection = cmds.ls(selection=True, long=True)
        with patch.object(ChannelAlgorithms, '_match_and_key', side_effect=RuntimeError('injected match failure')):
            pair = {'source': self.source, 'target': self.target, 'modes': {'translate': 'frame', 'rotate': 'none', 'scale': 'none'}}
            result = TOOL.run(action='execute', pairs=[pair], start=1, end=5)
        self.assertFalse(result.success)
        self.assertTrue(result.errors)
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(1, cmds.currentTime(query=True))
        self.assertFalse(runtime._ACTIVE)
        cmds.undo()
        self.assertFalse(scene.records())

    def test_frame_constraint_numeric_mode_transition(self):
        self.run_pair(translate='frame')
        self.run_pair(translate='constraint')
        self.run_pair(translate='numeric')
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        self.assertAlmostEqual(8, cmds.getAttr(self.target + '.tx', time=5), places=4)

    def test_batch_duplicate_leaf_constraint_identity_and_cleanup(self):
        pairs = []
        for index in range(2):
            root = cmds.createNode('transform', name='pairParent' + str(index))
            source = cmds.createNode('transform', name='duplicateSource', parent=root)
            target = cmds.createNode('transform', name='duplicateTarget', parent=root)
            source = cmds.ls(source, long=True)[0]
            target = cmds.ls(target, long=True)[0]
            pairs.append({'source': source, 'target': target, 'modes': {'translate': 'constraint', 'rotate': 'none', 'scale': 'none'}})
        result = TOOL.run(action='execute', pairs=pairs, start=1, end=5)
        self.assertTrue(result.success, result.message)
        self.assertEqual(2, len(scene.records()))
        result = TOOL.run(action='cleanup')
        self.assertTrue(result.success, result.message)
        for pair in pairs:
            self.assertTrue(cmds.objExists(pair['target']))


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
