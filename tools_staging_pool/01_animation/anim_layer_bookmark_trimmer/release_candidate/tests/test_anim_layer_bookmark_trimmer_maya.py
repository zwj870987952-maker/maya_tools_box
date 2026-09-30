"""Destructive fixture tests are restricted to the disposable mayapy runner."""
import os
from pathlib import Path
import sys
import unittest

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use the isolated mayapy runner; these tests create new scenes')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.anim_layer_bookmark_trimmer import AnimLayerBookmarkTrimmerTool
    load_tool = AnimLayerBookmarkTrimmerTool


def snapshot(curve):
    return dict(times=cmds.keyframe(curve, query=True, timeChange=True),
                values=cmds.keyframe(curve, query=True, valueChange=True),
                incoming=cmds.keyTangent(curve, query=True, inTangentType=True),
                outgoing=cmds.keyTangent(curve, query=True, outTangentType=True),
                weighted=cmds.keyTangent(curve, query=True, weightedTangents=True))


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.loadPlugin('timeSliderBookmark', quiet=True)
        self.cube = cmds.polyCube()[0]
        cmds.addAttr(self.cube, longName='customFloat', attributeType='double', keyable=True)
        for t, value in ((0, -2), (1, 0), (2, 8), (3, 2), (4, 9), (5, 10), (6, 12)):
            for attr in ('translateX', 'rotateY', 'scaleX', 'customFloat'):
                cmds.setKeyframe(self.cube, attribute=attr, time=t, value=value, inTangentType='linear', outTangentType='linear')
            cmds.setKeyframe(self.cube, attribute='visibility', time=t, value=t % 2)
        self.curve = cmds.listConnections(self.cube + '.translateX', source=True, destination=False)[0]
        self.bookmark = self.add_bookmark(1, 5)
        self.tool = load_tool()
        self.args = dict(objects=[self.cube], channel_box_priority=False, include_rotate=False)

    @staticmethod
    def add_bookmark(start, stop):
        node = cmds.createNode('timeSliderBookmark')
        cmds.setAttr(node + '.timeRangeStart', start)
        cmds.setAttr(node + '.timeRangeStop', stop)
        cmds.setAttr(node + '.name', 'fixture', type='string')
        return node

    def assert_success(self, result):
        self.assertTrue(result.success, result.to_json())

    def test_trim_preview_read_only_and_apply_undo(self):
        before = snapshot(self.curve)
        undo = cmds.undoInfo(query=True, undoName=True)
        cmds.select(self.cube)
        undo = cmds.undoInfo(query=True, undoName=True)
        result = self.tool.run(dry_run=True, **self.args)
        self.assert_success(result)
        self.assertEqual(snapshot(self.curve), before)
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), undo)
        self.assertEqual(cmds.ls(selection=True), [self.cube])
        self.assert_success(self.tool.run(**self.args))
        self.assertEqual(cmds.keyframe(self.curve, query=True, timeChange=True), [1, 5])
        cmds.undo()
        self.assertEqual(snapshot(self.curve), before)

    def test_playback_matches_entire_bookmark_and_keeps_outside_keys(self):
        cmds.playbackOptions(minTime=2, maxTime=4)
        self.assert_success(self.tool.run(scope='playback', **self.args))
        self.assertEqual(cmds.keyframe(self.curve, query=True, timeChange=True), [0, 1, 5, 6])

    def test_selected_cursor_outside_uses_nearest_bookmark(self):
        cmds.currentTime(100)
        self.assert_success(self.tool.run(dry_run=True, scope='selected', **self.args))

    def test_six_modes_keep_endpoints_outside_key_values_and_undo(self):
        for mode in ('smooth', 'simplify', 'multikey_ease', 'ease', 'tangents', 'smart'):
            with self.subTest(mode=mode):
                before = snapshot(self.curve)
                self.assert_success(self.tool.run(action='optimize', mode=mode, **self.args))
                for time, value in ((0, -2), (1, 0), (5, 10), (6, 12)):
                    self.assertAlmostEqual(cmds.keyframe(self.curve, time=(time, time), query=True, valueChange=True)[0], value)
                cmds.undo()
                self.assertEqual(snapshot(self.curve), before)

    def test_missing_endpoints_preflight_evaluates_without_adding(self):
        cmds.setAttr(self.bookmark + '.timeRangeStart', 1.5)
        cmds.setAttr(self.bookmark + '.timeRangeStop', 4.5)
        before = snapshot(self.curve)
        result = self.tool.run(dry_run=True, action='optimize', **self.args)
        self.assert_success(result)
        self.assertEqual(snapshot(self.curve), before)
        values = [cmds.keyframe(self.curve, query=True, eval=True, time=(t, t))[0] for t in (1.5, 4.5)]
        self.assert_success(self.tool.run(action='optimize', **self.args))
        for time, value in zip((1.5, 4.5), values):
            self.assertAlmostEqual(cmds.keyframe(self.curve, time=(time, time), query=True, valueChange=True)[0], value)

    def test_other_floats_included_discrete_scale_excluded(self):
        excluded = {a: snapshot(cmds.listConnections(self.cube + '.' + a, source=True, destination=False)[0])
                    for a in ('visibility', 'scaleX', 'rotateY')}
        self.assert_success(self.tool.run(include_others=True, **self.args))
        custom_curve = cmds.listConnections(self.cube + '.customFloat', source=True, destination=False)[0]
        self.assertEqual(cmds.keyframe(custom_curve, query=True, timeChange=True), [1, 5])
        for attr, before in excluded.items():
            self.assertEqual(snapshot(cmds.listConnections(self.cube + '.' + attr, source=True, destination=False)[0]), before)

    def test_explicit_layer_does_not_modify_base_animation(self):
        before = snapshot(self.curve)
        cmds.select(self.cube)
        layer = cmds.animLayer('fixtureLayer', addSelectedObjects=True)
        for time in (0, 1, 2, 3, 4, 5, 6):
            cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=time, value=time * 3)
        result = self.tool.run(layer=layer, **self.args)
        self.assert_success(result)
        self.assertEqual(snapshot(self.curve), before)
        self.assertEqual(cmds.keyframe(result.data['curves'][0], query=True, timeChange=True), [1, 5])

    def test_locked_curve_and_overlap_reject_without_writes(self):
        before = snapshot(self.curve)
        cmds.lockNode(self.curve, lock=True)
        self.assertFalse(self.tool.run(dry_run=True, **self.args).success)
        cmds.lockNode(self.curve, lock=False)
        self.add_bookmark(2, 4)
        self.assertFalse(self.tool.run(action='optimize', **self.args).success)
        self.assertEqual(snapshot(self.curve), before)

    def test_base_with_other_layer_present_remains_isolated(self):
        cmds.select(self.cube)
        layer = cmds.animLayer('fixtureLayer', addSelectedObjects=True)
        for time in (1, 2, 3, 4, 5):
            cmds.setKeyframe(self.cube, attribute='translateX', animLayer=layer, time=time, value=time * 3)
        layered_curve = cmds.animLayer(layer, query=True, findCurveForPlug=self.cube + '.translateX')
        if isinstance(layered_curve, list):
            layered_curve = layered_curve[0]
        before = snapshot(layered_curve)
        result = self.tool.run(layer='BaseAnimation', **self.args)
        self.assert_success(result)
        self.assertEqual(snapshot(layered_curve), before)
        self.assertEqual(cmds.keyframe(self.curve, query=True, timeChange=True), [1, 5])

    def test_trim_can_insert_missing_endpoints_and_undo(self):
        before = snapshot(self.curve)
        cmds.setAttr(self.bookmark + '.timeRangeStart', 1.5)
        cmds.setAttr(self.bookmark + '.timeRangeStop', 4.5)
        values = [cmds.keyframe(self.curve, query=True, eval=True, time=(t, t))[0] for t in (1.5, 4.5)]
        self.assert_success(self.tool.run(ensure_keys_at_bounds=True, **self.args))
        self.assertEqual(cmds.keyframe(self.curve, query=True, timeChange=True), [1.5, 4.5])
        self.assertEqual(cmds.keyframe(self.curve, query=True, valueChange=True), values)
        cmds.undo()
        self.assertEqual(snapshot(self.curve), before)


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False)
    # Maya standalone shutdown occasionally exits with unrelated errors; preserve test status.
    sys.exit(0 if result.result.wasSuccessful() else 1)
