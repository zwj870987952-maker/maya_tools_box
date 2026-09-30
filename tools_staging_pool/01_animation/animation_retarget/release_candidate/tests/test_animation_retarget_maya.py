"""Disposable scenes only. Does not instantiate Qt or claim GUI acceptance."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use plans/staging_run/run_mayapy_check.py; tests replace the scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').is_file():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.animation_retarget import AnimationRetargetTool
    load_tool = AnimationRetargetTool


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.source = cmds.createNode('transform', name='source')
        self.target = cmds.createNode('transform', name='target')
        cmds.setAttr(self.target + '.tx', 10)
        cmds.setKeyframe(self.source, attribute='tx', time=1, value=1)
        cmds.setKeyframe(self.source, attribute='tx', time=2.5, value=3)
        cmds.setKeyframe(self.source, attribute='tx', time=5, value=5)
        cmds.playbackOptions(min=1, max=5)
        cmds.currentTime(1)
        self.tool = load_tool()
        self.ops = sys.modules[self.tool.__class__.__module__.rsplit('.', 1)[0] + '.operations']
        self.pair = {'source': self.source, 'target': self.target}

    def ok(self, result):
        self.assertTrue(result.success, result.to_json())
        return result.data

    def numeric(self, **modes):
        return dict(self.pair, modes={'translate': 'numeric', 'rotate': 'none', 'scale': 'none', 'other': 'none', **modes})

    def test_dry_run_no_scene_time_selection_or_undo_changes(self):
        cmds.select(self.source)
        nodes, time, undo = cmds.ls(), cmds.currentTime(query=True), cmds.undoInfo(query=True, undoName=True)
        self.ok(self.tool.run(dry_run=True, pairs=[self.pair]))
        self.assertEqual(nodes, cmds.ls())
        self.assertEqual(time, cmds.currentTime(query=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        self.assertEqual(cmds.ls(selection=True), [self.source])

    def test_all_constraint_modes_offsets_and_one_step_undo(self):
        cmds.select(self.source)
        data = self.ok(self.tool.run(pairs=[self.pair]))
        self.assertEqual(len(data['constraints']), 3)
        self.assertEqual(len(data['info_nodes']), 1)
        cmds.currentTime(5)
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx'), 14)
        cmds.currentTime(1)
        # Time edits after run create separate undo entries; undo them then the tool.
        cmds.undo()
        cmds.undo()
        cmds.undo()
        self.assertFalse(cmds.ls(type='pointConstraint'))
        self.assertFalse(cmds.ls(type='network'))
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx'), 10)

    def test_numeric_union_fractional_frames_custom_vector_children(self):
        for node in (self.source, self.target):
            cmds.addAttr(node, longName='custom', attributeType='double', keyable=True)
            cmds.addAttr(node, longName='vector', attributeType='double3')
            for axis in 'XYZ':
                cmds.addAttr(node, longName='vector' + axis, attributeType='double', parent='vector', keyable=True)
        cmds.setKeyframe(self.source, attribute='custom', time=2.5, value=7)
        cmds.setKeyframe(self.source, attribute='vectorX', time=2.5, value=9)
        cmds.currentTime(12)
        cmds.select(self.source)
        data = self.ok(self.tool.run(action='numeric_copy', pairs=[self.numeric(other='numeric')]))
        self.assertEqual(data['frames'], [1, 2.5, 5])
        self.assertEqual(cmds.keyframe(self.target, attribute='tx', query=True, valueChange=True), [1, 3, 5])
        self.assertEqual(cmds.getAttr(self.target + '.custom', time=2.5), 7)
        self.assertEqual(cmds.getAttr(self.target + '.vectorX', time=2.5), 9)
        self.assertEqual(cmds.currentTime(query=True), 12)
        self.assertEqual(cmds.ls(selection=True), [self.source])
        cmds.undo()
        self.assertFalse(cmds.keyframe(self.target, query=True, timeChange=True))

    def test_bake_only_selected_owned_constraints_foreign_set_untouched(self):
        foreign_target = cmds.createNode('transform', name='foreignTarget')
        foreign_constraint = cmds.pointConstraint(self.source, foreign_target)[0]
        foreign_set = cmds.sets(foreign_constraint, name='Constraint_SelectionSet')
        data = self.ok(self.tool.run(pairs=[self.pair]))
        other = cmds.createNode('transform', name='other')
        other_data = self.ok(self.tool.run(pairs=[{'source': self.source, 'target': other}]))
        baked = self.ok(self.tool.run(action='bake', pairs=[self.pair]))
        self.assertEqual(len(baked['deleted_owned_constraints']), 3)
        self.assertTrue(cmds.objExists(foreign_constraint))
        self.assertTrue(cmds.objExists(foreign_set))
        self.assertTrue(all(cmds.objExists(node) for node in other_data['constraints']))
        self.assertFalse(any(cmds.objExists(node) for node in data['constraints']))
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx', time=5), 14)
        cmds.undo()
        self.assertTrue(all(cmds.objExists(node) for node in data['constraints']))

    def test_smart_bake_real_command(self):
        self.ok(self.tool.run(pairs=[self.pair]))
        data = self.ok(self.tool.run(action='bake', pairs=[self.pair], smart=True, start=1, end=5))
        self.assertTrue(data['smart'])
        self.assertTrue(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))

    def test_json_pose_strings_and_rename_uuid(self):
        for node in (self.source, self.target):
            cmds.addAttr(node, longName='label', dataType='string')
            cmds.setAttr(node + '.label', 'x,y:z"\\value', type='string')
        pair = dict(self.pair, modes={'translate': 'none', 'rotate': 'none', 'scale': 'none'})
        self.ok(self.tool.run(pairs=[pair]))
        renamed = cmds.rename(self.target, 'renamed')
        cmds.setAttr(renamed + '.tx', 20)
        cmds.setAttr(renamed + '.label', 'changed', type='string')
        scene = self.ok(self.tool.run(action='load_scene'))
        self.assertEqual(scene['pairs'][0]['target'], '|renamed')
        result = self.ok(self.tool.run(action='restore_pose'))
        self.assertIn('|renamed.label', result['restored'])
        self.assertEqual(cmds.getAttr(renamed + '.label'), 'x,y:z"\\value')
        self.assertEqual(cmds.getAttr(renamed + '.tx'), 10)
        cmds.undo()
        self.assertEqual(cmds.getAttr(renamed + '.tx'), 20)

    def test_preflight_locked_driven_ambiguous_cycle_rejected(self):
        cmds.setAttr(self.target + '.tx', lock=True)
        self.assertFalse(self.tool.run(dry_run=True, pairs=[self.pair]).success)
        cmds.setAttr(self.target + '.tx', lock=False)
        cmds.pointConstraint(self.source, self.target)
        self.assertFalse(self.tool.run(dry_run=True, pairs=[self.pair]).success)
        self.assertFalse(self.tool.run(dry_run=True, pairs=[self.pair, {'source': self.target, 'target': self.source}]).success)
        self.assertFalse(self.tool.run(dry_run=True, pairs=[{'source': 'missing', 'target': self.target}]).success)

    def test_legacy_scene_info_and_pose(self):
        group = cmds.group(empty=True, name='Rematch')
        node = cmds.createNode('transform', name='RematchInfo', parent=group)
        for suffix, value in (('_pairInfo', self.source + ' , ' + self.target), ('_modes', json.dumps({'translate': 'none'})),
                              ('_sourcePose', json.dumps({'translateX': 1, 'otherAttributes': ''})),
                              ('_targetPose', json.dumps({'translateX': 10, 'otherAttributes': ''}))):
            cmds.addAttr(node, longName='legacy' + suffix, dataType='string')
            cmds.setAttr(node + '.legacy' + suffix, value, type='string')
        data = self.ok(self.tool.run(action='load_scene'))
        self.assertEqual(data['legacy_records'], 1)
        cmds.setAttr(self.target + '.tx', 20)
        self.ok(self.tool.run(action='restore_pose'))
        self.assertEqual(cmds.getAttr(self.target + '.tx'), 10)

    def test_save_load_exclusive_file_dry_run(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'pairs.json')
            self.ok(self.tool.run(action='save_config', pairs=[self.pair], path=path, dry_run=True))
            self.assertFalse(Path(path).exists())
            self.ok(self.tool.run(action='save_config', pairs=[self.pair], path=path))
            before = Path(path).read_bytes()
            self.assertFalse(self.tool.run(action='save_config', pairs=[self.pair], path=path).success)
            self.assertEqual(Path(path).read_bytes(), before)
            loaded = self.ok(self.tool.run(action='load_config', path=path))
            self.assertEqual(loaded['pairs'][0]['target'], 'target')

    def test_execution_exception_restores_time_and_selection(self):
        cmds.currentTime(12)
        cmds.select(self.source)
        original = self.ops.numeric_copy
        def failure(*args):
            cmds.currentTime(3)
            cmds.select(self.target)
            raise RuntimeError('intentional fixture failure')
        with patch.object(self.ops, 'numeric_copy', failure):
            self.assertFalse(self.tool.run(action='numeric_copy', pairs=[self.numeric()]).success)
        self.assertEqual(cmds.currentTime(query=True), 12)
        self.assertEqual(cmds.ls(selection=True), [self.source])

    def test_owned_constraint_rename_and_deleted_name_reuse_guard(self):
        data = self.ok(self.tool.run(pairs=[self.pair]))
        original = data['constraints'][0]
        renamed = cmds.rename(original, 'renamedConstraint')
        self.assertFalse(self.tool.run(pairs=[self.pair], dry_run=True).success)
        self.ok(self.tool.run(action='bake', pairs=[self.pair]))
        self.assertFalse(cmds.objExists(renamed))
        # A later foreign constraint with the same old name has a different UUID.
        foreign = cmds.pointConstraint(self.source, self.target, name=original)[0]
        self.ok(self.tool.run(action='bake', pairs=[self.pair]))
        self.assertTrue(cmds.objExists(foreign))

    def test_scene_and_restore_preflight_no_mutation_and_undo_required(self):
        self.ok(self.tool.run(pairs=[dict(self.pair, modes={'translate': 'none', 'rotate': 'none', 'scale': 'none'})]))
        undo = cmds.undoInfo(query=True, undoName=True)
        before = cmds.getAttr(self.target + '.tx')
        self.ok(self.tool.run(action='restore_pose', dry_run=True))
        self.assertEqual(cmds.getAttr(self.target + '.tx'), before)
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo)
        cmds.undoInfo(state=False)
        self.assertFalse(self.tool.run(action='restore_pose', dry_run=True).success)
        cmds.undoInfo(state=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
