"""Actual disposable Maya frame-loop, key/Undo and preflight tests; no native GUI."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('必须通过隔离 mayapy runner 运行')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.back2origin_v05_gaiv3 import Back2OriginTool
    load_tool = Back2OriginTool
tool = load_tool()
from maya_toolkit.tools.back2origin_v05_gaiv3 import engine, algorithms


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.refresh(suspend=False)
        self.global_node = cmds.createNode('transform', name='Main')
        self.root = cmds.createNode('transform', name='RootX_M', parent=self.global_node)
        self.ik = cmds.createNode('transform', name='IKLeg_R', parent=self.root)
        self.pv = cmds.createNode('transform', name='PoleLeg_R', parent=self.root)
        self.other = cmds.createNode('transform', name='prop', parent=self.root)
        for node, offset in ((self.ik, 10), (self.pv, 20), (self.other, 30)):
            cmds.setAttr(node + '.tx', offset)
        for frame in range(1, 6):
            cmds.setKeyframe(self.root, attribute='tx', time=frame, value=frame)
        cmds.playbackOptions(min=1, max=5, animationStartTime=0, animationEndTime=10)
        cmds.currentTime(3)
        cmds.select(self.ik)
        cmds.flushUndo()
        self.args = {'root_control': self.root, 'global_control': self.global_node, 'ik_controls': [self.ik],
                     'pv_controls': [self.pv], 'other_controls': [self.other], 'channels': ['X'], 'start': 1, 'end': 5}

    def tearDown(self):
        cmds.refresh(suspend=False)

    def ok(self, result):
        self.assertTrue(result.success, result.to_dict())
        return result.data

    def snapshot(self):
        return {'nodes': sorted(cmds.ls(long=True)), 'time': cmds.currentTime(query=True),
                'selection': cmds.ls(selection=True, long=True), 'eval': cmds.evaluationManager(query=True, mode=True),
                'refresh': cmds.refresh(query=True, suspend=True),
                'range': [cmds.playbackOptions(query=True, **{flag: True}) for flag in ('min', 'max', 'animationStartTime', 'animationEndTime')],
                'keys': [(node, cmds.keyframe(node, query=True, timeChange=True), cmds.keyframe(node, query=True, valueChange=True)) for node in (self.root, self.global_node, self.ik)],
                'undo': cmds.undoInfo(query=True, undoName=True)}

    def world(self, node, frame):
        # Sample without adding time changes above the tool's Undo chunk.
        matrix = cmds.getAttr(node + '.worldMatrix[0]', time=frame)
        return tuple(matrix[12:15])

    def test_forward_real_world_positions_root_keys_and_single_undo(self):
        before = {node: [self.world(node, frame) for frame in range(1, 6)] for node in (self.ik, self.pv, self.other)}
        cmds.currentTime(3)
        self.ok(tool.run(**self.args))
        self.assertEqual(cmds.currentTime(query=True), 3)
        for frame in range(1, 6):
            self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=frame), 0)
            self.assertAlmostEqual(cmds.getAttr(self.global_node + '.tx', time=frame), frame)
            for node in before:
                self.assertEqual(self.world(node, frame), before[node][frame - 1])
        cmds.undo()
        self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=3), 3)
        self.assertFalse(cmds.keyframe(self.global_node, query=True, timeChange=True))
        self.assertFalse(cmds.keyframe(self.ik, query=True, timeChange=True))

    def test_reverse_overwrites_root_and_preserves_control_world_positions(self):
        for frame in range(1, 6):
            cmds.setKeyframe(self.global_node, attribute='tx', time=frame, value=frame + 5)
        positions = [self.world(self.ik, frame) for frame in range(1, 6)]
        cmds.currentTime(3)
        self.ok(tool.run(action='reverse', **self.args))
        for frame in range(1, 6):
            self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=frame), frame + 5)
            self.assertAlmostEqual(cmds.getAttr(self.global_node + '.tx', time=frame), 0)
            self.assertEqual(self.world(self.ik, frame), positions[frame - 1])
        cmds.undo()
        self.assertAlmostEqual(cmds.getAttr(self.global_node + '.tx', time=3), 8)
        self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=3), 3)

    def test_thinning_absolute_modulus_also_cuts_unselected_translate_axis(self):
        for frame in range(0, 7):
            cmds.setKeyframe(self.root, attribute='tz', time=frame, value=frame + 10)
        data = self.ok(tool.run(frame_step=2, **self.args))
        self.assertTrue(data['warnings'])
        self.assertEqual(cmds.keyframe(self.root, attribute='tx', query=True, timeChange=True), [1, 2, 4, 5])
        self.assertEqual(cmds.keyframe(self.root, attribute='tz', query=True, timeChange=True), [0, 1, 2, 4, 5, 6])
        cmds.undo()
        self.assertEqual(cmds.keyframe(self.root, attribute='tz', query=True, timeChange=True), list(range(7)))

    def test_optional_global_in_place_and_playback_range_default(self):
        args = dict(self.args, global_control='')
        args.pop('start')
        args.pop('end')
        data = self.ok(tool.run(**args))
        self.assertEqual(data['range'], [1, 5])
        self.assertTrue(data['warnings'])
        self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=3), 0)
        self.assertFalse(cmds.keyframe(self.global_node, query=True, timeChange=True))

    def test_dry_run_scene_and_runtime_unchanged(self):
        before = self.snapshot()
        self.ok(tool.run(dry_run=True, **self.args))
        self.assertEqual(before, self.snapshot())

    def test_preflight_lock_driver_duplicates_invalid_and_batch_gui(self):
        cmds.setAttr(self.ik + '.tz', lock=True)
        self.assertFalse(tool.run(dry_run=True, **self.args).success)
        cmds.setAttr(self.ik + '.tz', lock=False)
        driver = cmds.createNode('addDoubleLinear')
        cmds.connectAttr(driver + '.output', self.global_node + '.tx')
        self.assertFalse(tool.run(dry_run=True, **self.args).success)
        cmds.disconnectAttr(driver + '.output', self.global_node + '.tx')
        self.assertFalse(tool.run(dry_run=True, **dict(self.args, other_controls=[self.ik])).success)
        self.assertFalse(tool.run(dry_run=True, **dict(self.args, root_control='missing')).success)
        self.assertFalse(tool.run(action='reverse', dry_run=True, **dict(self.args, global_control='')).success)
        self.assertFalse(tool.run(action='open_ui', dry_run=True).success)

    def test_reference_target_actual_file_preflight(self):
        with tempfile.TemporaryDirectory(prefix='back2origin_ref_') as directory:
            path = str(Path(directory) / 'fixture.ma')
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii', force=True)
            cmds.file(new=True, force=True)
            cmds.file(path, reference=True, namespace='ref')
            self.assertFalse(tool.run(root_control='ref:RootX_M', channels=['X'], dry_run=True).success)

    def test_exception_runtime_restore_and_undo_partial_keys(self):
        cmds.refresh(suspend=True)
        before = self.snapshot()
        def fail(*unused):
            cmds.currentTime(5)
            cmds.setKeyframe(self.root, attribute='tx', value=99)
            cmds.select(clear=True)
            cmds.playbackOptions(min=2, max=4)
            raise RuntimeError('intentional fixture failure')
        with patch.object(algorithms, 'zero_out_root_control', side_effect=fail):
            self.assertFalse(tool.run(**self.args).success)
        after = self.snapshot()
        for key in ('time', 'selection', 'eval', 'refresh', 'range', 'nodes'):
            self.assertEqual(before[key], after[key], key)
        cmds.undo()
        self.assertAlmostEqual(cmds.getAttr(self.root + '.tx', time=5), 5)

    def test_discovery_uses_long_paths_nested_namespaces_and_reports_ambiguity(self):
        cmds.namespace(add='char')
        cmds.namespace(add='char:nested')
        root = cmds.createNode('transform', name='char:nested:RootX_M')
        global_node = cmds.createNode('transform', name='char:nested:Main')
        before = self.snapshot()
        all_data = self.ok(tool.run(action='discover'))
        self.assertIn('root_control', all_data['ambiguous'])
        data = self.ok(tool.run(action='discover', namespace='char:nested'))
        self.assertEqual(data['matches']['root_control'], ['|' + root])
        self.assertEqual(data['matches']['global_control'], ['|' + global_node])
        self.assertFalse(data['ambiguous'])
        # run() uses a framework Undo wrapper even for readonly execution; validate
        # and dry_run themselves are the strict no-Undo-write preflight path.
        self.assertEqual(before['nodes'], self.snapshot()['nodes'])

    def test_native_module_import_complete_no_window_and_installer_refused(self):
        from maya_toolkit.tools.back2origin_v05_gaiv3 import native_ui
        import json
        catalog = json.loads((Path(native_ui.__file__).parent / 'catalog.json').read_text(encoding='utf-8'))
        self.assertTrue(all(callable(getattr(native_ui, name)) for name in catalog['original_functions']))
        self.assertFalse(cmds.window('mtbB2O_back2OriginWindow', exists=True))
        before = self.snapshot()
        with self.assertRaises(RuntimeError):
            native_ui.save_script_to_maya_default()
        self.assertEqual(before, self.snapshot())


if __name__ == '__main__':
    unittest.main(verbosity=2)
