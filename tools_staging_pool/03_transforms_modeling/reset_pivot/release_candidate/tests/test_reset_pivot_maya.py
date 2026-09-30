"""Run only in an isolated mayapy process, never in an existing GUI scene."""
import os
import sys
import unittest

if not os.environ.get("STAGING_ISOLATED_MAYAPY"):
    raise RuntimeError("This test requires the isolated runner")

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds

RC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RC)
if os.path.isfile(os.path.join(RC, "launch_candidate.py")):
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.reset_pivot import ResetPivotTool
    load_tool = ResetPivotTool


def snapshot(node):
    return {"matrix": cmds.xform(node, query=True, worldSpace=True, matrix=True), "pivot": cmds.xform(node, query=True, worldSpace=True, pivots=True), "parent": cmds.listRelatives(node, parent=True, fullPath=True) or [], "selection": cmds.ls(selection=True, long=True) or []}


class MayaPivotTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.parent = cmds.group(empty=True, name="parentGroup")
        cube = cmds.polyCube(name="pivotCube")[0]
        self.node = cmds.parent(cube, self.parent)[0]
        self.node = cmds.ls(self.node, long=True)[0]
        cmds.xform(self.node, translation=[4, 3, 2], rotation=[10, 20, 30])
        cmds.select(clear=True)
        self.joint = cmds.joint(name="sourceJoint", orientation=[12, 23, 34])
        cmds.select(self.node, replace=True)
        self.tool = load_tool()

    def test_every_action_dry_run_is_read_only(self):
        before = snapshot(self.node)
        undo_name = cmds.undoInfo(query=True, undoName=True)
        for action in ("center", "origin", "parent", "reset_axes", "world", "joint", "complete"):
            args = {"action": action, "target_nodes": [self.node]}
            if action == "joint":
                args["source_joint"] = self.joint
            result = self.tool.run(dry_run=True, **args)
            self.assertTrue(result.success, result.to_json())
            self.assertEqual(snapshot(self.node), before)
            self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo_name)

    def test_origin_pivot_and_one_step_undo(self):
        before = snapshot(self.node)
        result = self.tool.run(action="origin", target_nodes=[self.node])
        self.assertTrue(result.success, result.to_json())
        for value in cmds.xform(self.node, query=True, worldSpace=True, pivots=True):
            self.assertAlmostEqual(value, 0, places=5)
        cmds.undo()
        self.assertEqual(snapshot(self.node), before)

    def test_every_action_keeps_parent_and_undo_restores_transform(self):
        for action in ("center", "parent", "reset_axes", "world", "joint", "complete"):
            before = snapshot(self.node)
            args = {"action": action, "target_nodes": [self.node]}
            if action == "joint":
                args["source_joint"] = self.joint
            result = self.tool.run(**args)
            self.assertTrue(result.success, result.to_json())
            node = result.data["processed_nodes"][0]
            self.assertEqual(cmds.listRelatives(node, parent=True, fullPath=True), ["|parentGroup"])
            cmds.undo()
            after = snapshot(self.node)
            self.assertEqual(after["parent"], before["parent"])
            self.assertEqual(after["selection"], before["selection"])
            for field in ("matrix", "pivot"):
                for actual, expected in zip(after[field], before[field]):
                    self.assertAlmostEqual(actual, expected, places=5)

    def test_animated_target_is_rejected_without_scene_change(self):
        cmds.setKeyframe(self.node, attribute="rotateX", time=1, value=5)
        before = snapshot(self.node)
        result = self.tool.run(action="complete", target_nodes=[self.node])
        self.assertFalse(result.success)
        self.assertEqual(snapshot(self.node), before)


if __name__ == "__main__":
    try:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(MayaPivotTests)
        result = unittest.TextTestRunner().run(suite)
        status = 0 if result.wasSuccessful() else 1
    finally:
        maya.standalone.uninitialize()
    sys.exit(status)
