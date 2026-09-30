import os
from pathlib import Path
import random
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated mayapy harness may execute disposable-scene tests')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.cg_shake_py3 import runtime, files
from maya_toolkit.tools.cg_shake_py3.contracts import CHANNELS


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.node = cmds.createNode('transform', name='shakeCtrl')
        cmds.setKeyframe(self.node, attribute='tx', time=1, value=2)
        cmds.setKeyframe(self.node, attribute='tx', time=3, value=4)
        cmds.currentTime(1)
        cmds.select(self.node)

    def test_positive_uniform_six_draw_order_first_only_undo(self):
        other = cmds.createNode('transform', name='other')
        cmds.select([self.node, other])
        base = {frame: [cmds.getAttr(self.node + '.' + c, time=frame) for c in CHANNELS] for frame in (1, 2, 3)}
        cmds.flushUndo()
        result = TOOL.run(action='apply', start=1, end=3, falloff_samples=[1, .5, 0], seed=5)
        self.assertTrue(result.success, result.message)
        rng = random.Random(5)
        for row in result.data['samples']:
            frame, weight = row['frame'], row['falloff']
            for index, c in enumerate(CHANNELS):
                expected = base[frame][index] + weight * rng.uniform(0, 5)
                self.assertAlmostEqual(expected, cmds.getAttr(self.node + '.' + c, time=frame), places=5)
        self.assertFalse(cmds.keyframe(other, query=True))
        self.assertEqual(1, cmds.currentTime(query=True))
        cmds.undo()
        self.assertEqual([2, 4], cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True))

    def test_fractional_range_truncation_step_and_zero_channels(self):
        amounts = {c: 0 for c in CHANNELS}
        amounts['tx'] = 2
        result = TOOL.run(action='apply', start=1.5, end=5.5, step=2, amounts=amounts, falloff_samples=[1, 1, 1], seed=9)
        self.assertTrue(result.success, result.message)
        self.assertEqual([1, 3, 5], [r['frame'] for r in result.data['samples']])
        self.assertEqual(['tx'], result.data['keyed_channels'])
        self.assertFalse(cmds.keyframe(self.node, attribute='ty', query=True))

    def test_readonly_inputs_locks_and_gui_refusal(self):
        before, selection = cmds.ls(long=True), cmds.ls(selection=True, long=True)
        undo = cmds.undoInfo(query=True, undoName=True)
        self.assertTrue(TOOL.run(dry_run=True, action='apply', start=1, end=3, falloff_samples=[1, 1, 1]).success)
        self.assertEqual(before, cmds.ls(long=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        cmds.setAttr(self.node + '.rz', lock=True)
        self.assertFalse(TOOL.run(action='apply', start=1, end=3, falloff_samples=[1, 1, 1]).success)
        self.assertFalse(TOOL.run(action='open_ui').success)
        self.assertFalse(TOOL.run(action='apply', start=1, end=3, falloff_samples=[1]).success)

    def test_clear_overwrite_and_preset_files(self):
        self.assertFalse(TOOL.run(action='clear').success)
        self.assertTrue(TOOL.run(action='clear', overwrite=True).success)
        self.assertFalse(cmds.keyframe(self.node, query=True))
        preset = {'Frame': 1, **{c.upper(): 5 for c in CHANNELS}, 'Points': '0,1,3,1,0,3'}
        with tempfile.TemporaryDirectory() as scratch:
            target = str(Path(scratch) / 'new/preset.cgsk')
            self.assertTrue(TOOL.run(action='save_preset', file_path=target, preset=preset).success)
            self.assertFalse(TOOL.run(action='save_preset', file_path=target, preset=preset).success)
            self.assertTrue(TOOL.run(action='save_preset', file_path=target, preset=preset, overwrite_file=True).success)
            self.assertEqual(preset, TOOL.run(action='load_preset', file_path=target).data['preset'])

    def test_real_anim_export_import_cache_hash_and_undo_files_remain(self):
        if not files.plugin_loaded():
            cmds.loadPlugin('animImportExport')
        with tempfile.TemporaryDirectory() as scratch:
            target = str(Path(scratch) / 'cache.anim')
            result = TOOL.run(action='cache', file_path=target)
            self.assertTrue(result.success, result.message)
            self.assertTrue(Path(target).exists())
            self.assertTrue(Path(target + '.json').exists())
            self.assertFalse(TOOL.run(action='cache', file_path=target).success)
            cmds.keyframe(self.node, attribute='tx', edit=True, relative=True, valueChange=20)
            result = TOOL.run(action='restore')
            self.assertTrue(result.success, result.message)
            self.assertEqual([2, 4], cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True))
            with open(target, 'a', encoding='utf-8') as stream:
                stream.write('\n// changed\n')
            self.assertFalse(TOOL.run(action='restore').success)
            self.assertEqual([2, 4], cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True))

    def test_failure_restores_time_selection_ranges_guard_and_undo(self):
        selection = cmds.ls(selection=True, long=True)
        original = cmds.setKeyframe
        def fail(*args, **kwargs):
            if kwargs.get('at'):
                raise RuntimeError('injected key failure')
            return original(*args, **kwargs)
        cmds.flushUndo()
        with patch('maya.cmds.setKeyframe', side_effect=fail):
            result = TOOL.run(action='apply', start=1, end=3, falloff_samples=[1, 1, 1])
        self.assertFalse(result.success)
        self.assertEqual(1, cmds.currentTime(query=True))
        self.assertEqual(selection, cmds.ls(selection=True, long=True))
        self.assertFalse(runtime._ACTIVE)
        cmds.undo()
        self.assertEqual([2, 4], cmds.keyframe(self.node, attribute='tx', query=True, valueChange=True))


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    maya.standalone.uninitialize()
    sys.exit(0 if result.wasSuccessful() else 1)
