import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('必须通过隔离 runner 运行')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.bh_local_nudge import LocalNudgeTool
    load_tool = LocalNudgeTool
tool = load_tool()
from maya_toolkit.tools.bh_local_nudge import runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        self.node = cmds.createNode('transform', name='control')
        cmds.select(self.node)
        cmds.flushUndo()

    def ok(self, result):
        self.assertTrue(result.success, result.to_dict())
        return result.data

    def snapshot(self):
        return (sorted(cmds.ls(long=True)), cmds.getAttr(self.node + '.translate')[0], cmds.currentTime(query=True),
                cmds.ls(selection=True, long=True), cmds.undoInfo(query=True, undoName=True), mel.eval('whatIs mtbLN_bh_localNudgeIt;'))

    def test_source_all_five_and_internal_guard_batch_ui(self):
        nodes = sorted(cmds.ls(long=True))
        data = runtime.load_suite()
        self.assertEqual(len(data['procedures']), 5)
        self.assertEqual(nodes, sorted(cmds.ls(long=True)))
        self.assertFalse(cmds.window('mtbLN_localNudgeUI', exists=True))
        with self.assertRaises(RuntimeError):
            mel.eval('mtbLN_bh_localNudgeIt("X","positive");')
        self.assertFalse(tool.run(action='open_ui', dry_run=True).success)

    def test_translate_rotate_actual_original_modifiers_and_undo(self):
        for channel in ('translate', 'rotate'):
            for ctrl, alt, value in ((False, False, 8), (True, False, 4), (False, True, 2), (True, True, 1)):
                data = self.ok(tool.run(objects=[self.node], channel=channel, axis='X', direction='negative', amount=8, ctrl=ctrl, alt=alt))
                self.assertAlmostEqual(cmds.getAttr(self.node + '.' + channel + 'X'), -value)
                self.assertAlmostEqual(data['changes'][0]['after'], -value)
                cmds.undo()
                self.assertAlmostEqual(cmds.getAttr(self.node + '.' + channel + 'X'), 0)

    def test_bulk_parent_transformed_local_attribute_not_world_vector(self):
        parent = cmds.createNode('transform', name='parent')
        cmds.setAttr(parent + '.ry', 90)
        cmds.setAttr(parent + '.scale', 2, 2, 2, type='double3')
        child = cmds.parent(self.node, parent)[0]
        second = cmds.createNode('transform', name='other')
        cmds.setAttr(child + '.tx', 1)
        before = cmds.xform(child, query=True, worldSpace=True, translation=True)
        self.ok(tool.run(objects=[child, second], axis='X', amount=.25))
        after = cmds.xform(child, query=True, worldSpace=True, translation=True)
        self.assertAlmostEqual(cmds.getAttr(child + '.tx'), 1.25)
        self.assertAlmostEqual(after[2] - before[2], -.5)
        self.assertAlmostEqual(cmds.getAttr(second + '.tx'), .25)
        cmds.undo()
        self.assertAlmostEqual(cmds.getAttr(child + '.tx'), 1)
        self.assertAlmostEqual(cmds.getAttr(second + '.tx'), 0)

    def test_dry_run_readonly_and_component_selection_restored(self):
        before = self.snapshot()
        self.ok(tool.run(objects=[self.node], dry_run=True))
        self.assertEqual(before, self.snapshot())
        mesh = cmds.polyCube()[0]
        cmds.select(mesh + '.vtx[0]')
        selection = cmds.ls(selection=True, long=True)
        self.ok(tool.run(objects=[self.node], axis='Z', amount=.2))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))

    def test_animated_value_does_not_create_or_change_keys_with_autokey_off(self):
        cmds.setKeyframe(self.node, attribute='tx', time=1, value=1)
        cmds.setKeyframe(self.node, attribute='tx', time=5, value=5)
        cmds.currentTime(3)
        keys = cmds.keyframe(self.node, query=True, timeChange=True), cmds.keyframe(self.node, query=True, valueChange=True)
        data = self.ok(tool.run(objects=[self.node], axis='X', amount=.5))
        self.assertAlmostEqual(cmds.getAttr(self.node + '.tx'), 3.5)
        self.assertEqual(keys, (cmds.keyframe(self.node, query=True, timeChange=True), cmds.keyframe(self.node, query=True, valueChange=True)))
        self.assertTrue(data['changes'][0]['animated'])
        cmds.currentTime(5)
        self.assertAlmostEqual(cmds.getAttr(self.node + '.tx'), 5)

    def test_preflight_lock_nonanim_driver_duplicates_and_missing(self):
        cmds.setAttr(self.node + '.tx', lock=True)
        self.assertFalse(tool.run(objects=[self.node], axis='X', dry_run=True).success)
        cmds.setAttr(self.node + '.tx', lock=False)
        source = cmds.createNode('addDoubleLinear')
        cmds.connectAttr(source + '.output', self.node + '.tx')
        self.assertFalse(tool.run(objects=[self.node], axis='X', dry_run=True).success)
        self.assertFalse(tool.run(objects=[self.node, self.node], dry_run=True).success)
        self.assertFalse(tool.run(objects=['missing'], dry_run=True).success)

    def test_failure_restores_selection_and_undo_partial_write(self):
        other = cmds.createNode('transform', name='other')
        cmds.select(other)
        selection = cmds.ls(selection=True, long=True)
        original = mel.eval
        def fail(command):
            if command.startswith('mtbLN_bh_localNudgeIt('):
                cmds.setAttr(self.node + '.ty', 3)
                cmds.select(clear=True)
                raise RuntimeError('intentional fixture failure')
            return original(command)
        with patch.object(mel, 'eval', side_effect=fail):
            self.assertFalse(tool.run(objects=[self.node]).success)
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        cmds.undo()
        self.assertAlmostEqual(cmds.getAttr(self.node + '.ty'), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
