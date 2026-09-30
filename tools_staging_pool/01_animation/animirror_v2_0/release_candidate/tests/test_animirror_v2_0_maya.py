"""Actual disposable Maya scene algorithms; no GUI, no UI query replacements."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use isolated runner; tests replace the current scene')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.animirror_v2_0 import AnimirrorV2Tool
    load_tool = AnimirrorV2Tool
load_tool()
from maya_toolkit.tools.animirror_v2_0 import state, runtime


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.loadPlugin('lookdevKit', quiet=True)
        self.tool = load_tool()
        self.center = cmds.createNode('transform', name='center')
        self.reference = cmds.createNode('transform', name='reference')
        self.target = cmds.createNode('transform', name='mirrorTarget')
        cmds.setAttr(self.reference + '.translate', 3, 2, 1, type='double3')
        for frame, value in ((1, 3), (5, 5)):
            cmds.setKeyframe(self.reference, attribute='tx', time=frame, value=value)
        cmds.playbackOptions(min=1, max=5)
        cmds.currentTime(1)
        cmds.select([self.center, self.reference, self.target], replace=True)
        self.args = {'objects': [self.center, self.reference, self.target]}

    def ok(self, result):
        self.assertTrue(result.success, result.to_json())
        return result.data

    def test_readonly_dry_run_with_no_source_or_scene_mutation(self):
        name = 'mtbAV2_mirror_animation'
        origin = mel.eval('whatIs ' + name + ';')
        before, undo = cmds.ls(), cmds.undoInfo(query=True, undoName=True)
        selection = cmds.ls(selection=True, long=True)
        self.ok(self.tool.run(dry_run=True, **self.args))
        self.assertEqual(before, cmds.ls())
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(mel.eval('whatIs ' + name + ';'), origin)
        self.assertFalse(cmds.window('mtbAV2_AniMirror', exists=True))

    def test_live_x_mirror_ownership_cleanup_and_one_undo(self):
        data = self.ok(self.tool.run(**self.args))
        self.assertTrue(data['interactive'])
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx', time=1), -3)
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx', time=5), -5)
        self.assertEqual(len(state.records()), 1)
        self.assertTrue(cmds.ls(type='joint'))
        self.ok(self.tool.run(action='clear'))
        self.assertFalse(cmds.ls(type='joint'))
        self.assertFalse(cmds.ls(type='constraint'))
        self.assertFalse(cmds.ls(type='floatMath'))
        self.assertFalse(state.records())
        cmds.undo()
        self.assertEqual(len(state.records()), 1)
        self.ok(self.tool.run(action='clear'))
        self.assertFalse(state.records())

    def test_mirror_one_chunk_undo_then_new_mirror_has_no_stale_globals(self):
        self.ok(self.tool.run(**self.args))
        cmds.undo()
        self.assertFalse(state.records())
        self.assertFalse(cmds.ls(type='joint'))
        self.ok(self.tool.run(**self.args))
        self.assertEqual(len(state.records()), 1)
        self.assertEqual(cmds.getAttr(self.target + '.tx', time=5), -5)

    def test_three_translation_axes_original_actual_values(self):
        for axis, expected in (('X', (-3, 2, 1)), ('Y', (3, -2, 1)), ('Z', (3, 2, -1))):
            self.ok(self.tool.run(translation_axis=axis, rotations=False, **self.args))
            value = cmds.getAttr(self.target + '.translate')[0]
            for actual, wanted in zip(value, expected):
                self.assertAlmostEqual(actual, wanted, places=5)
            self.ok(self.tool.run(action='clear'))

    def test_rotation_only_and_disabled_translation(self):
        cmds.setAttr(self.reference + '.rotate', 10, 20, 30, type='double3')
        cmds.setAttr(self.target + '.translate', 9, 8, 7, type='double3')
        self.ok(self.tool.run(translations=False, invert_rotation=['Y', 'Z'], **self.args))
        self.assertEqual(cmds.getAttr(self.target + '.translate')[0], (9, 8, 7))
        rotation = cmds.getAttr(self.target + '.rotate')[0]
        for actual, wanted in zip(rotation, (10, -20, -30)):
            self.assertAlmostEqual(actual, wanted, places=4)

    def test_bake_accumulated_targets_filter_and_cleanup(self):
        self.ok(self.tool.run(**self.args))
        other = cmds.createNode('transform', name='otherTarget')
        self.ok(self.tool.run(objects=[self.center, self.reference, other]))
        data = self.ok(self.tool.run(action='bake', start=1, end=5))
        self.assertEqual(set(data['targets']), {'|' + self.target, '|' + other})
        self.assertFalse(state.records())
        self.assertFalse(cmds.ls(type='joint'))
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx', time=5), -5)
        self.assertTrue(cmds.keyframe(self.target, attribute='tx', query=True, timeChange=True))
        cmds.undo()
        self.assertEqual(len(state.records()), 2)
        self.ok(self.tool.run(action='clear'))

    def test_mirror_with_bake_actual_keys_and_single_undo(self):
        self.ok(self.tool.run(action='mirror_bake', start=1, end=5, **self.args))
        self.assertFalse(state.records())
        self.assertFalse(cmds.ls(type='constraint'))
        self.assertAlmostEqual(cmds.getAttr(self.target + '.tx', time=5), -5)
        cmds.undo()
        self.assertFalse(cmds.keyframe(self.target, query=True, timeChange=True))
        self.assertFalse(state.records())

    def test_uuid_rename_then_cleanup_preserves_same_name_foreign_node(self):
        self.ok(self.tool.run(**self.args))
        root = next(entry for entry in state.records()[0]['data']['owned'] if entry['role'] == 'root')
        original = state.find(root['uuid'])
        renamed = cmds.rename(original, 'renamedHelper')
        foreign = cmds.createNode('joint', name=original.rsplit('|', 1)[-1])
        self.ok(self.tool.run(action='clear'))
        self.assertTrue(cmds.objExists(foreign))
        self.assertFalse(cmds.objExists(renamed))

    def test_external_child_or_connection_refuses_delete(self):
        self.ok(self.tool.run(**self.args))
        root = next(entry for entry in state.records()[0]['data']['owned'] if entry['role'] == 'root')
        child = cmds.createNode('transform', name='externalChild', parent=state.find(root['uuid']))
        self.assertFalse(self.tool.run(action='clear', dry_run=True).success)
        self.assertTrue(cmds.objExists(child))

    def test_missing_plugin_locked_driver_reference_or_wrong_selection(self):
        cmds.setAttr(self.target + '.tx', lock=True)
        self.assertFalse(self.tool.run(dry_run=True, **self.args).success)
        cmds.setAttr(self.target + '.tx', lock=False)
        cmds.setKeyframe(self.target, attribute='tx', time=1, value=0)
        self.assertFalse(self.tool.run(dry_run=True, **self.args).success)
        self.assertFalse(self.tool.run(objects=['missing', self.reference, self.target], dry_run=True).success)
        with patch.object(cmds, 'allNodeTypes', return_value=[]):
            self.assertFalse(self.tool.run(dry_run=True, **self.args).success)

    def test_execution_error_restores_refresh_time_selection_and_captures_partial(self):
        selected = cmds.ls(selection=True, long=True)
        original_eval = mel.eval
        def fail(command):
            if command == 'mtbAV2_mirror_animation(0);':
                cmds.createNode('joint', name='partialHelper')
                cmds.currentTime(3)
                cmds.refresh(suspend=True)
                raise RuntimeError('intentional fixture failure')
            return original_eval(command)
        with patch.object(mel, 'eval', side_effect=fail):
            self.assertFalse(self.tool.run(**self.args).success)
        self.assertFalse(cmds.refresh(query=True, suspend=True))
        self.assertEqual(cmds.currentTime(query=True), 1)
        self.assertEqual(cmds.ls(selection=True, long=True), selected)
        self.assertTrue(state.records()[0]['data']['failed'])
        self.assertFalse(self.tool.run(dry_run=True, **self.args).success)
        self.ok(self.tool.run(action='clear'))
        self.assertFalse(cmds.objExists('partialHelper'))

    def test_all_original_procedure_origins_and_internal_guard(self):
        loaded = runtime.load_suite()
        self.assertEqual(len(loaded['procedures']), 11)
        for name in loaded['procedures']:
            self.assertTrue(str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(loaded['source'].casefold()))
        self.assertFalse(self.tool.run(action='open_ui', dry_run=True).success)
        with self.assertRaises(RuntimeError):
            mel.eval('mtbAV2_mirror_animation(0);')

    def test_foreign_output_connection_refuses_delete_and_component_selection_restored(self):
        mesh = cmds.polyCube()[0]
        cmds.select(mesh + '.vtx[0]')
        selection = cmds.ls(selection=True, long=True)
        self.ok(self.tool.run(**self.args))
        self.assertEqual(cmds.ls(selection=True, long=True), selection)
        operator = next(state.find(entry['uuid']) for entry in state.records()[0]['data']['owned'] if entry['role'] == 'translate_operator')
        outside = cmds.createNode('transform', name='foreignConsumer')
        cmds.connectAttr(operator + '.outFloat', outside + '.tx')
        self.assertFalse(self.tool.run(action='clear', dry_run=True).success)
        self.assertTrue(cmds.objExists(outside))
        cmds.disconnectAttr(operator + '.outFloat', outside + '.tx')
        self.ok(self.tool.run(action='clear'))
        self.assertTrue(cmds.objExists(self.target))

    def test_scene_save_reload_recovers_uuid_ownership_without_name_cache(self):
        import tempfile
        self.ok(self.tool.run(**self.args))
        with tempfile.TemporaryDirectory(prefix='animirror_scene_') as folder:
            path = str(Path(folder) / 'candidate.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, open=True, force=True)
            self.assertEqual(len(state.records()), 1)
            self.ok(self.tool.run(action='clear'))
            self.assertFalse(state.records())
            self.assertTrue(cmds.objExists(self.target))


if __name__ == '__main__':
    unittest.main(verbosity=2)
