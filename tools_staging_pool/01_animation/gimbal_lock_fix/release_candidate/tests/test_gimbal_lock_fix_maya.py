import math
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy may run disposable scenes')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds, OpenMaya as om
from maya.api import OpenMaya as om2
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.gimbal_lock_fix import runtime, native


def matrix(angles, order):
    return list(om2.MEulerRotation(*(math.radians(x) for x in angles), order).asMatrix())


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.currentUnit(angle='deg')
        cmds.autoKeyframe(state=False)
        self.node = cmds.createNode('transform', name='animatedRotation')
        for frame, rotation in ((1, (10, 20, 30)), (3, (100, 95, 240)), (5, (190, -75, 400))):
            for attr, value in zip(('rx', 'ry', 'rz'), rotation):
                cmds.setKeyframe(self.node, attribute=attr, time=frame, value=value)
        cmds.currentTime(3)
        cmds.select(self.node)

    def test_all_six_orders_preserve_key_orientations_and_undo(self):
        for order in range(6):
            cmds.setAttr(self.node + '.rotateOrder', order)
            before = {frame: cmds.getAttr(self.node + '.rotate', time=frame)[0] for frame in (1, 3, 5)}
            result = TOOL.run(action='fix', objects=[self.node])
            self.assertTrue(result.success, result.message + str(result.errors))
            for frame, angles in before.items():
                actual = cmds.getAttr(self.node + '.rotate', time=frame)[0]
                for a, b in zip(matrix(angles, order), matrix(actual, order)):
                    self.assertAlmostEqual(a, b, places=7, msg=str((order, frame, angles, actual)))
            cmds.undo()
            self.assertEqual(before, {frame: cmds.getAttr(self.node + '.rotate', time=frame)[0] for frame in (1, 3, 5)})

    def test_readonly_detect_and_dry_and_real_angle_threshold(self):
        before = (cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True), cmds.keyframe(self.node, query=True, valueChange=True))
        dry = TOOL.run(dry_run=True, action='fix', objects=[self.node], samples_per_frame=2)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, (cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True), cmds.keyframe(self.node, query=True, valueChange=True)))
        result = TOOL.run(action='detect', objects=[self.node], threshold=0.1)
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual([(1, 5)], result.data['results'][0]['problem_ranges'])
        self.assertEqual(before, (cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True), cmds.keyframe(self.node, query=True, valueChange=True)))

    def test_density_subframe_range_and_native_gui_bridge(self):
        result = TOOL.run(action='fix', objects=[self.node], start=1, end=3, samples_per_frame=2)
        self.assertTrue(result.success, result.message + str(result.errors))
        self.assertEqual([1, 1.5, 2, 2.5, 3, 5], cmds.keyframe(self.node, attribute='rx', query=True))
        self.assertEqual(5, result.data['results'][0]['sample_count'])
        cmds.undo()
        self.assertTrue(native.GimbalLockFixer().fix_animation_curves(self.node, 1, 5, 1))
        cmds.undo()
        self.assertEqual([1, 3, 5], cmds.keyframe(self.node, attribute='rx', query=True))
        self.assertFalse(TOOL.validate(action='fix', objects=[self.node], start=1.1, end=2.9).success)
        self.assertFalse(TOOL.validate(action='open_ui').success)

    def test_slerp_does_not_mutate_cached_quaternion_and_scope_guards(self):
        q1, q2 = om.MQuaternion(0, 0, 0, 1), om.MQuaternion(0, 0, 0, -1)
        native._Algorithm().quaternion_slerp(q1, q2, 0.25)
        self.assertEqual(-1, q2.w)
        cmds.setAttr(self.node + '.rx', lock=True)
        self.assertFalse(TOOL.validate(action='fix', objects=[self.node]).success)
        self.assertTrue(TOOL.validate(action='detect', objects=[self.node]).success)
        cmds.setAttr(self.node + '.rx', lock=False)
        foreign = cmds.createNode('transform', name='foreign')
        curve = cmds.listConnections(self.node + '.rx', source=True, destination=False)[0]
        cmds.connectAttr(curve + '.output', foreign + '.rx')
        self.assertFalse(TOOL.validate(action='fix', objects=[self.node]).success)
        cmds.disconnectAttr(curve + '.output', foreign + '.rx')
        cmds.setKeyframe(self.node, attribute='rotateOrder', time=1, value=0)
        self.assertFalse(TOOL.validate(action='fix', objects=[self.node]).success)
        with self.assertRaises(RuntimeError):
            native._Algorithm()._apply_fixed_rotations(self.node, {}, 'xyz')
        cmds.currentUnit(angle='rad')
        self.assertFalse(TOOL.validate(action='detect', objects=[self.node]).success)
        cmds.currentUnit(angle='deg')

    def test_partial_failure_undo_and_finally(self):
        before = cmds.keyframe(self.node, query=True, valueChange=True)
        real = cmds.setKeyframe
        calls = []

        def injected(*args, **kwargs):
            calls.append(args)
            if len(calls) == 2:
                raise RuntimeError('injected second key write failure')
            return real(*args, **kwargs)

        cmds.autoKeyframe(state=True)
        with patch.object(cmds, 'setKeyframe', side_effect=injected):
            result = TOOL.run(action='fix', objects=[self.node])
        self.assertFalse(result.success)
        self.assertFalse(runtime._ACTIVE)
        self.assertTrue(cmds.autoKeyframe(query=True, state=True))
        self.assertEqual(3, cmds.currentTime(query=True))
        self.assertEqual([self.node], cmds.ls(selection=True))
        cmds.undo()
        self.assertEqual(before, cmds.keyframe(self.node, query=True, valueChange=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
