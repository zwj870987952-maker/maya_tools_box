import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.lock_to_world import runtime, native


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.currentUnit(angle='deg', linear='cm')
        cmds.autoKeyframe(state=False)
        self.parent = cmds.createNode('transform', name='movingSpace')
        self.node = cmds.circle(name='control', constructionHistory=False)[0]
        cmds.parent(self.node, self.parent)
        for frame in (1, 3, 5):
            cmds.setKeyframe(self.parent, attribute='tx', time=frame, value=frame * 3)
            for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                cmds.setKeyframe(self.node, attribute=attr, time=frame, value=frame * (5 if attr.startswith('r') else 1))
        cmds.currentTime(3)
        cmds.select(self.node)

    def lock(self, **kwargs):
        result = TOOL.run(objects=[self.node], start=1, end=5, **kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result

    def test_full_lock_all_orders_parent_motion_and_undo(self):
        for order in range(6):
            cmds.setAttr(self.node + '.rotateOrder', order)
            matrix = runtime.world_matrix(self.node, 1)
            before = cmds.keyframe(self.node, query=True, valueChange=True)
            self.lock()
            for frame in range(1, 6):
                for x, y in zip(matrix, runtime.world_matrix(self.node, frame)):
                    self.assertAlmostEqual(x, y, places=6)
            self.assertFalse(cmds.ls('mtbLock_*'))
            cmds.undo()
            self.assertEqual(before, cmds.keyframe(self.node, query=True, valueChange=True))

    def test_frozen_multi_mask_dry_and_channel_scope(self):
        cmds.setAttr(self.node + '.rotatePivot', 2, -3, 1)
        before = (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True))
        self.assertTrue(TOOL.run(dry_run=True, objects=[self.node], start=1, end=5).success)
        self.assertEqual(before, (cmds.ls(long=True), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True)))
        start = runtime.world_matrix(self.node, 1)
        self.lock()
        for frame in range(1, 6):
            for x, y in zip(start, runtime.world_matrix(self.node, frame)):
                self.assertAlmostEqual(x, y, places=6)
        cmds.undo()
        rotation_curves = [cmds.listConnections(self.node + '.' + attr, source=True, destination=False)[0] for attr in ('rx', 'ry', 'rz')]
        original_rot = {curve: cmds.keyframe(curve, query=True, valueChange=True) for curve in rotation_curves}
        cmds.setAttr(self.node + '.ry', lock=True)
        self.lock(attributes=['tx'])
        self.assertEqual(original_rot, {curve: cmds.keyframe(curve, query=True, valueChange=True) for curve in rotation_curves})
        cmds.undo()
        cmds.setAttr(self.node + '.ry', lock=False)
        other = cmds.createNode('transform', name='other')
        result = TOOL.run(objects=[self.node, other], start=1, end=5)
        self.assertTrue(result.success, result.message)
        self.assertEqual([1, 2, 3, 4, 5], cmds.keyframe(other, attribute='tx', query=True))
        cmds.undo()

    def test_guards_failure_cleanup_and_finally(self):
        other = cmds.createNode('transform', name='foreign')
        curve = cmds.listConnections(self.node + '.tx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', other + '.tx')
        self.assertFalse(TOOL.validate(objects=[self.node], start=1, end=5).success)
        cmds.disconnectAttr(curve + '.output', other + '.tx')
        cmds.setKeyframe(self.node, attribute='rotatePivotX', time=1, value=2)
        self.assertFalse(TOOL.validate(objects=[self.node]).success)
        cmds.undo()
        self.assertFalse(TOOL.validate(action='open_ui').success)
        self.assertFalse(TOOL.validate(objects=[self.node], use_channel_box=True).success)
        with self.assertRaises(RuntimeError):
            native.snapCtlFromMatrixList([], [], 1, 5, [])
        before = cmds.keyframe(self.node, query=True, valueChange=True)
        real = cmds.setKeyframe
        count = []
        def fail(*args, **kwargs):
            count.append(args)
            if len(count) == 2:
                raise RuntimeError('injected second key failure')
            return real(*args, **kwargs)
        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'setKeyframe', side_effect=fail):
            result = TOOL.run(objects=[self.node], start=1, end=5)
        self.assertFalse(result.success)
        self.assertIn('injected second key failure', str(result.errors))
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertEqual(3, cmds.currentTime(query=True))
        self.assertFalse(runtime._ACTIVE)
        self.assertFalse(cmds.ls('mtbLock_*'))
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(self.node, query=True, valueChange=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
