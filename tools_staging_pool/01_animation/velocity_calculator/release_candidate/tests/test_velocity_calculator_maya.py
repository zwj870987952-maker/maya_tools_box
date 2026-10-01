import os
from pathlib import Path
import runpy
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()


def animate(node, attr, keys):
    for t, v in keys:
        cmds.setKeyframe(node, attribute=attr, time=t, value=v)
    cmds.keyTangent(node, attribute=attr, edit=True, inTangentType='linear', outTangentType='linear')


def scene(node):
    return (cmds.ls(long=True), cmds.ls(selection=True), cmds.currentTime(query=True), cmds.keyframe(node, query=True, timeChange=True), cmds.keyframe(node, query=True, valueChange=True), cmds.undoInfo(query=True, undoName=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.currentUnit(linear='cm', time='film')

    def test_true_endpoint_and_backward_context_preserve_scene(self):
        node = cmds.createNode('transform', name='velocityObject')
        animate(node, 'tx', ((1, 0), (5, 4), (9, 8)))
        cmds.currentTime(9)
        cmds.select(node)
        before = scene(node)
        dry = TOOL.run(dry_run=True, start_frame=1, end_frame=5)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, scene(node))
        result = TOOL.run(start_frame=1, end_frame=5)
        self.assertTrue(result.success, result.message)
        row = result.data['measurements'][0]
        self.assertAlmostEqual(4., row['distance'])
        self.assertAlmostEqual(24., row['speed'])
        self.assertAlmostEqual(0., row['start_position'][0])
        self.assertAlmostEqual(4., row['end_position'][0])
        instant = TOOL.run(mode='instant', frame=4.5, sample_step=.5)
        self.assertTrue(instant.success, instant.message)
        self.assertAlmostEqual(24., instant.data['measurements'][0]['speed'])
        self.assertEqual(before, scene(node))

    def test_general_time_linear_units_parent_world_and_instance_path(self):
        parent = cmds.createNode('transform', name='animatedParent')
        child = cmds.createNode('transform', name='child', parent=parent)
        animate(parent, 'tx', ((1, 0), (11, 10)))
        cmds.currentTime(7)
        for time_unit, linear_unit, expected in (('film', 'cm', 24), ('ntscf', 'cm', 60), ('120fps', 'm', 1.2), ('sec', 'cm', 1)):
            cmds.currentUnit(time=time_unit, updateAnimation=False, linear=linear_unit)
            result = TOOL.run(objects=[child], start_frame=1, end_frame=11)
            self.assertTrue(result.success, result.message)
            self.assertAlmostEqual(expected, result.data['measurements'][0]['speed'], places=5)
        cmds.currentUnit(time='film', updateAnimation=False, linear='cm')
        other = cmds.createNode('transform', name='otherParent')
        animate(other, 'ty', ((1, 0), (11, 20)))
        cmds.parent(child, other, add=True)
        paths = cmds.ls('child', long=True, allPaths=True)
        specific = next(p for p in paths if p.startswith('|' + other + '|'))
        result = TOOL.run(objects=[specific], start_frame=1, end_frame=11)
        self.assertTrue(result.success, result.message)
        self.assertAlmostEqual(48, result.data['measurements'][0]['speed'])

    def test_return_trip_zero_displacement_and_failures_readonly(self):
        node = cmds.createNode('transform', name='returnTrip')
        animate(node, 'tx', ((1, 0), (5, 10), (9, 0)))
        cmds.currentTime(3)
        before = scene(node)
        result = TOOL.run(objects=[node], start_frame=1, end_frame=9)
        self.assertTrue(result.success, result.message)
        self.assertEqual(0., result.data['measurements'][0]['speed'])
        for bad in ({'objects': [node], 'start_frame': 1, 'end_frame': 1}, {'objects': [node + '.tx']}, {'objects': [node], 'show_result': True}):
            self.assertFalse(TOOL.run(**bad).success)
        self.assertEqual(before, scene(node))
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()


if __name__ == '__main__':
    unittest.main(verbosity=2)
