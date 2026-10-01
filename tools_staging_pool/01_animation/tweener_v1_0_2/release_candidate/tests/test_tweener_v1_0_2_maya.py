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


def animated(name='a', attribute='tx', keys=((1, 0), (5, 20), (9, 10))):
    if not cmds.objExists(name):
        cmds.createNode('transform', name=name)
    for frame, value in keys:
        cmds.setKeyframe(name, attribute=attribute, time=frame, value=value)
    cmds.keyTangent(name, attribute=attribute, edit=True, inTangentType='linear', outTangentType='linear')
    return cmds.listConnections(name + '.' + attribute, source=True, destination=False, type='animCurve')[0]


def data(curve):
    return (cmds.keyframe(curve, query=True, timeChange=True), cmds.keyframe(curve, query=True, valueChange=True))


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)

    def test_all_five_complete_modes_actual_api2_and_undo_redo(self):
        for mode, blend, expected in (('between', 0, 5), ('towards', .5, 15), ('average', .5, 12.5), ('default', .5, 10), ('curve', .5, 15)):
            curve = animated()
            cmds.currentTime(5)
            before = data(curve)
            result = TOOL.run(curves=[curve], mode=mode, blend=blend)
            self.assertTrue(result.success, result.message)
            self.assertAlmostEqual(expected, data(curve)[1][1], places=5)
            after = data(curve)
            cmds.undo()
            self.assertEqual(before, data(curve))
            cmds.redo()
            self.assertEqual(after, data(curve))
            cmds.delete('a')

    def test_insert_range_selected_groups_and_preview_readonly(self):
        curve = animated()
        cmds.currentTime(3)
        before = data(curve)
        undo = cmds.undoInfo(query=True, undoName=True)
        dry = TOOL.run(dry_run=True, curves=[curve], mode='curve', blend=.5)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, data(curve))
        self.assertEqual(undo, cmds.undoInfo(query=True, undoName=True))
        result = TOOL.run(curves=[curve], mode='between', blend=0)
        self.assertTrue(result.success, result.message)
        self.assertEqual([1., 3., 5., 9.], data(curve)[0])
        cmds.undo()
        self.assertEqual(before, data(curve))
        cmds.delete('a')
        curve = animated(keys=((1, 0), (3, 10), (5, 20), (7, 30), (9, 40)))
        result = TOOL.run(curves=[curve], time_range=[3, 7], blend=0)
        self.assertTrue(result.success, result.message)
        self.assertEqual([0., 20., 20., 20., 40.], data(curve)[1])
        cmds.undo()
        result = TOOL.run(curves=[curve], key_indices={curve: [1, 2]}, blend=0)
        self.assertTrue(result.success, result.message)
        self.assertEqual([0., 15., 15., 30., 40.], data(curve)[1])

    def test_keyhammer_union_and_inclusive_endpoint_no_outside_selection(self):
        x = animated(attribute='tx', keys=((1, 0), (5, 10)))
        y = animated(attribute='ty', keys=((3, 6), (7, 14)))
        outsider = animated('outside', keys=((100, 5), (200, 10)))
        cmds.selectKey(outsider, time=(100, 100))
        before = (data(x), data(y), data(outsider))
        result = TOOL.run(action='keyhammer', curves=[x, y], time_range=[1, 7])
        self.assertTrue(result.success, result.message)
        self.assertEqual([1., 3., 5., 7.], data(x)[0])
        self.assertEqual([1., 3., 5., 7.], data(y)[0])
        self.assertEqual(before[2], data(outsider))
        cmds.undo()
        self.assertEqual(before, (data(x), data(y), data(outsider)))

    def test_whole_object_resolution_locked_shared_scope_and_batch_ui(self):
        curve = animated()
        cmds.currentTime(5)
        result = TOOL.run(objects=['a'], blend=0)
        self.assertTrue(result.success, result.message)
        cmds.undo()
        before = data(curve)
        cmds.setAttr('a.tx', lock=True)
        self.assertFalse(TOOL.run(curves=[curve]).success)
        self.assertEqual(before, data(curve))
        cmds.setAttr('a.tx', lock=False)
        shared = cmds.createNode('transform', name='shared')
        cmds.connectAttr(curve + '.output', shared + '.tx')
        self.assertFalse(TOOL.run(objects=['a']).success)
        self.assertEqual(before, data(curve))
        self.assertFalse(TOOL.run(action='activate_tool').success)
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()

    def test_actual_preview_cancel_commit_and_keyhammer_failure_rollback(self):
        from unittest.mock import patch
        from maya_toolkit.tools.tweener_v1_0_2 import runtime
        from maya_toolkit.tools.tweener_v1_0_2.tool import normalize
        curve = animated()
        cmds.currentTime(5)
        before = data(curve)
        params = normalize(curves=[curve])
        prepared = runtime.plan(params)
        _, animdata, tween, options, _ = runtime.libraries()
        # Actual original API engine and change cache, only GUI scope acquisition
        # is fixed to this real curve; no Qt or fake animation implementation.
        with patch.object(runtime, 'plan', return_value=prepared):
            runtime.begin_preview(.5, 0)
        tween.interpolate(-.5, options.BlendingMode.between)
        self.assertNotEqual(before, data(curve))
        runtime.cancel_preview()
        self.assertEqual(before, data(curve))
        with patch.object(runtime, 'plan', return_value=prepared):
            runtime.begin_preview(.5, 0)
        runtime.load_plugin()
        with runtime.scope(prepared):
            cmds.stagingTweener(t=.5, newCache=False, type=0)
        self.assertFalse(runtime.PREVIEW)
        after = data(curve)
        cmds.undo()
        self.assertEqual(before, data(curve))
        cmds.redo()
        self.assertEqual(after, data(curve))
        cmds.delete('a')
        x = animated(attribute='tx', keys=((1, 0), (5, 10)))
        y = animated(attribute='ty', keys=((3, 6), (7, 14)))
        before = (data(x), data(y))
        with patch.object(runtime, 'progress', side_effect=lambda control, **kw: bool(kw.get('isCancelled'))):
            result = TOOL.run(action='keyhammer', curves=[x, y])
        self.assertFalse(result.success)
        self.assertEqual(before, (data(x), data(y)))

    def test_original_animation_layer_choice_and_angular_units(self):
        animated(attribute='rx', keys=((1, 0), (5, 40), (9, 20)))
        cmds.currentTime(5)
        result = TOOL.run(objects=['a'], mode='default', blend=.5)
        self.assertTrue(result.success, result.message)
        self.assertAlmostEqual(20., cmds.getAttr('a.rx'), places=5)
        cmds.undo()
        self.assertAlmostEqual(40., cmds.getAttr('a.rx'), places=5)
        cmds.delete('a')
        base = animated()
        layer = cmds.animLayer('testTweenLayer', attribute='a.tx')
        root = cmds.animLayer(query=True, root=True)
        cmds.setAttr(root + '.selected', False)
        cmds.setAttr(layer + '.selected', True)
        cmds.setAttr(layer + '.preferred', True)
        for frame, value in ((1, 2), (5, 30), (9, 12)):
            cmds.setKeyframe('a', attribute='tx', time=frame, value=value, animLayer=layer)
        curve = cmds.animLayer(layer, query=True, findCurveForPlug='a.tx')[0]
        cmds.currentTime(5)
        before, base_before = data(curve), data(base)
        dry = TOOL.run(dry_run=True, objects=['a'], blend=0)
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(curve, dry.data['curves'][0]['curve'])
        result = TOOL.run(objects=['a'], blend=0)
        self.assertTrue(result.success, result.message)
        self.assertAlmostEqual((before[1][0] + before[1][-1]) * .5, data(curve)[1][1])
        self.assertEqual(base_before, data(base))
        cmds.undo()
        self.assertEqual(before, data(curve))
        cmds.setAttr(layer + '.lock', True)
        self.assertFalse(TOOL.run(curves=[curve]).success)


if __name__ == '__main__':
    unittest.main(verbosity=2)
