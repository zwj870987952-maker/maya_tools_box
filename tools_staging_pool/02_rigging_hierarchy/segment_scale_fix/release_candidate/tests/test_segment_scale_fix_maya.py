import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
TOOL = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'launch_candidate.py'))['load_tool']()


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_scaled_parent_real_world_matrix_selection_scope_and_undo(self):
        root = cmds.joint(name='rootJoint')
        child = cmds.joint(name='childJoint', position=(3, 0, 0))
        tip = cmds.joint(name='tipJoint', position=(6, 0, 0))
        cmds.setAttr(root + '.sx', 2)
        cmds.select(child)
        before = cmds.xform(child, query=True, worldSpace=True, matrix=True)
        snapshot = (cmds.ls(selection=True, long=True), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True), cmds.ls(long=True))
        dry = TOOL.run(dry_run=True)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(1, len(dry.data['changes']))
        self.assertEqual(snapshot, (cmds.ls(selection=True, long=True), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True), cmds.ls(long=True)))
        result = TOOL.run()
        self.assertTrue(result.success, result.message)
        self.assertFalse(cmds.getAttr(child + '.segmentScaleCompensate'))
        self.assertTrue(cmds.getAttr(root + '.segmentScaleCompensate'))
        self.assertTrue(cmds.getAttr(tip + '.segmentScaleCompensate'))
        after = cmds.xform(child, query=True, worldSpace=True, matrix=True)
        self.assertAlmostEqual(before[0] * 2, after[0])
        cmds.undo()
        self.assertTrue(cmds.getAttr(child + '.segmentScaleCompensate'))
        for a, b in zip(before, cmds.xform(child, query=True, worldSpace=True, matrix=True)):
            self.assertAlmostEqual(a, b)

    def test_locked_driven_alias_instance_and_empty_protection(self):
        j = cmds.joint(name='joint')
        cmds.setAttr(j + '.segmentScaleCompensate', lock=True)
        self.assertFalse(TOOL.run(objects=[j]).success)
        cmds.setAttr(j + '.segmentScaleCompensate', lock=False)
        driver = cmds.createNode('multiplyDivide')
        cmds.connectAttr(driver + '.outputX', j + '.segmentScaleCompensate')
        self.assertFalse(TOOL.run(objects=[j]).success)
        cmds.disconnectAttr(driver + '.outputX', j + '.segmentScaleCompensate')
        self.assertFalse(TOOL.run(objects=[j, '|joint']).success)
        parent = cmds.createNode('transform', name='instanceParent')
        cmds.parent(j, parent, add=True)
        self.assertFalse(TOOL.run(objects=['|joint']).success)
        cmds.select(clear=True)
        self.assertFalse(TOOL.run().success)

    def test_noop_and_mixed_selection_matches_original_joint_filter(self):
        j = cmds.joint(name='selectedJoint')
        other = cmds.createNode('transform', name='nonjoint')
        cmds.select([j, other])
        self.assertTrue(TOOL.run().success)
        result = TOOL.run(dry_run=True)
        self.assertTrue(result.success, result.message)
        self.assertFalse(result.data['scene_write'])
        self.assertEqual([], result.data['changes'])
        self.assertEqual(1, result.data['unchanged_count'])
        self.assertFalse(TOOL.run(objects=[other]).success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
