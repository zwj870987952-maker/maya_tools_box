import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy harness may execute disposable tests')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.brs_smooth_mocap import runtime, algorithms
from maya_toolkit.tools.brs_smooth_mocap.backend import runtime as backend_runtime, scene


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.select(clear=True)
        self.root = cmds.joint(name='root')
        for time, value in [(1, 0), (3, 6), (5, 0)]:
            cmds.setKeyframe(self.root, attribute='tx', time=time, value=value)
        cmds.currentTime(1)
        cmds.select(self.root)
        self.curve = cmds.listConnections(self.root + '.tx', source=True, destination=False)[0]

    def test_selected_keys_actual_average_and_undo(self):
        cmds.selectKey(self.curve, time=(1, 5), replace=True)
        cmds.flushUndo()
        result = TOOL.run(action='smooth_keys')
        self.assertTrue(result.success, result.message)
        self.assertEqual(1, result.data['passes'])
        self.assertEqual([0, 2, 0], cmds.keyframe(self.curve, query=True, valueChange=True))
        self.assertEqual([0, 1, 2], cmds.keyframe(self.curve, query=True, selected=True, indexValue=True))
        cmds.undo()
        self.assertEqual([0, 6, 0], cmds.keyframe(self.curve, query=True, valueChange=True))

    def test_explicit_all_keys_endpoints_and_snapshot(self):
        for frame, value in [(1, 0), (2, 9), (3, 3), (4, 0)]:
            cmds.setKeyframe(self.curve, time=frame, value=value)
        # Existing fifth key remains 0; snapshot each neighbor before any commit.
        result = TOOL.run(action='smooth_keys', curves=[self.curve], selected_only=False)
        self.assertTrue(result.success, result.message)
        self.assertEqual([0, 4, 4, 1, 0], cmds.keyframe(self.curve, query=True, valueChange=True))

    def test_mocap_strength_minus_one_real_bake_cleanup_undo(self):
        cmds.flushUndo()
        result = TOOL.run(action='smooth_mocap', root_joint=self.root, strength=3, annotation=True)
        self.assertTrue(result.success, result.message)
        self.assertEqual(2, result.data['passes'])
        self.assertAlmostEqual(2 / 3, cmds.getAttr(self.root + '.tx', time=3), places=4)
        self.assertFalse(scene.by_role('locator'))
        self.assertFalse(cmds.listRelatives(self.root, type='constraint'))
        self.assertTrue(cmds.objExists(self.root))
        cmds.undo()
        self.assertEqual([0, 6, 0], cmds.keyframe(self.root, attribute='tx', query=True, valueChange=True))

    def test_leaf_joint_and_static_children_are_handled(self):
        child = cmds.joint(name='staticChild')
        result = TOOL.run(action='smooth_mocap', root_joint=self.root, strength=1, annotation=False)
        self.assertTrue(result.success, result.message)
        self.assertEqual(0, result.data['passes'])
        self.assertIn(cmds.ls(child, long=True)[0], result.data['skipped_joints'])
        self.assertFalse(scene.by_role('locator'))

    def test_readonly_missing_locked_curves_and_ui_refusal(self):
        before = cmds.ls(long=True)
        selection = cmds.ls(selection=True, long=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        result = TOOL.run(dry_run=True, action='smooth_mocap', root_joint=self.root)
        self.assertTrue(result.success, result.message)
        self.assertEqual(before, cmds.ls(long=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        cmds.setAttr(self.root + '.tx', lock=True)
        self.assertFalse(TOOL.run(action='smooth_mocap', root_joint=self.root).success)
        self.assertFalse(TOOL.run(action='smooth_keys', curves=[self.curve], selected_only=False).success)
        self.assertFalse(TOOL.run(action='open_ui').success)

    def test_failure_restores_state_and_both_guards(self):
        selection = cmds.ls(selection=True, long=True)
        with patch.object(algorithms, 'valueAverage', side_effect=RuntimeError('injected smooth failure')):
            result = TOOL.run(action='smooth_mocap', root_joint=self.root, annotation=False)
        self.assertFalse(result.success)
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(1, cmds.currentTime(query=True))
        self.assertFalse(cmds.refresh(query=True, suspend=True))
        self.assertFalse(runtime._ACTIVE)
        self.assertFalse(backend_runtime._ACTIVE)


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
