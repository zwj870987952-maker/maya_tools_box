import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('必须通过隔离 runner 运行')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / 'launch_candidate.py').exists():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.bh_speedlines import SpeedLinesTool
    load_tool = SpeedLinesTool
tool = load_tool()
from maya_toolkit.tools.bh_speedlines import runtime, scene


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        runtime._DRAW = None
        runtime._ACTIVE = False
        cmds.currentTime(3.5)
        cmds.select(clear=True)
        cmds.flushUndo()

    def ok(self, result):
        self.assertTrue(result.success, result.to_dict())
        return result.data

    def curves(self):
        return [cmds.curve(degree=3, point=[(i, math.sin(i), z) for i in range(11)]) for z in (0, 2)]

    def snapshot(self):
        return (sorted(cmds.ls(long=True)), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), runtime.preferences(), cmds.undoInfo(query=True, undoName=True))

    def test_complete_source_origins_no_ui_prefs_and_guard(self):
        before = self.snapshot()
        data = runtime.load_suite()
        self.assertEqual(len(data['procedures']), 22)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(cmds.window('mtbSL_bh_speedLinesUI', exists=True))
        self.assertFalse(tool.run(action='open_ui', dry_run=True).success)
        self.assertFalse(tool.run(action='start_draw', dry_run=True).success)
        with self.assertRaises(RuntimeError):
            mel.eval('mtbSL_bh_setUpConvertPrefs();')

    def test_geometry_actual_mesh_consumes_curves_prefs_restore_and_undo(self):
        curves = self.curves()
        cmds.select(curves)
        preferences = runtime.preferences()
        data = self.ok(tool.run(action='geometry', objects=curves))
        self.assertTrue(data['warnings'])
        mesh = cmds.ls(selection=True, long=True)[0]
        self.assertEqual(cmds.nodeType(scene.shape(mesh)), 'mesh')
        self.assertGreater(cmds.polyEvaluate(mesh, face=True), 0)
        self.assertTrue(all(not cmds.objExists(curve) for curve in curves))
        self.assertEqual(preferences, runtime.preferences())
        cmds.undo()
        self.assertTrue(all(cmds.objExists(curve) for curve in curves))
        self.assertFalse(cmds.objExists(mesh))
        self.assertEqual(preferences, runtime.preferences())

    def test_geometry_preserve_curves_owned_layer_and_foreign_collision(self):
        curves = self.curves()
        self.ok(tool.run(action='geometry', objects=curves, high_detail=True, on_layer=True, consume_curves=False))
        self.assertTrue(all(cmds.objExists(curve) for curve in curves))
        self.assertTrue(scene.owned(scene.LAYER))
        self.assertTrue(cmds.editDisplayLayerMembers(scene.LAYER, query=True))
        cmds.undo()
        self.assertFalse(cmds.objExists(scene.LAYER))
        cmds.createDisplayLayer(name=scene.LAYER, empty=True)
        self.assertFalse(tool.run(action='geometry', objects=curves, on_layer=True, dry_run=True).success)

    def test_flip_and_mesh_simplify_real_topology_undo(self):
        mesh = cmds.polyPlane(subdivisionsX=1, subdivisionsY=1)[0]
        def normal():
            return tuple(float(value) for value in cmds.polyInfo(mesh + '.f[0]', faceNormals=True)[0].split(':', 1)[1].split())
        before = normal()
        self.ok(tool.run(action='flip', objects=[mesh]))
        self.assertEqual(normal(), tuple(-value for value in before))
        cmds.undo()
        self.assertEqual(normal(), before)
        sphere = cmds.polySphere(subdivisionsX=16, subdivisionsY=12)[0]
        count = cmds.polyEvaluate(sphere, face=True)
        self.ok(tool.run(action='simplify', objects=[sphere]))
        self.assertLess(cmds.polyEvaluate(sphere, face=True), count)
        cmds.undo()
        self.assertEqual(cmds.polyEvaluate(sphere, face=True), count)

    def test_curve_simplify_and_stock_smooth_actual(self):
        curve = self.curves()[0]
        shape = scene.shape(curve)
        spans = cmds.getAttr(shape + '.spans')
        self.ok(tool.run(action='simplify', objects=[curve]))
        self.assertEqual(cmds.getAttr(scene.shape(curve) + '.spans'), spans // 2)
        self.assertEqual(cmds.getAttr(scene.shape(curve) + '.degree'), 2)
        cmds.undo()
        self.assertEqual(cmds.getAttr(scene.shape(curve) + '.spans'), spans)
        points = [cmds.pointPosition(curve + '.cv[' + str(i) + ']', local=True) for i in range(11)]
        self.ok(tool.run(action='smooth', objects=[curve]))
        after = [cmds.pointPosition(curve + '.cv[' + str(i) + ']', local=True) for i in range(11)]
        self.assertNotEqual(points, after)
        cmds.undo()
        self.assertEqual(points, [cmds.pointPosition(curve + '.cv[' + str(i) + ']', local=True) for i in range(11)])

    def test_visibility_one_two_frames_integer_cast_no_shape_keys_undo(self):
        mesh = cmds.polyCube()[0]
        for hold, times, values in ((False, [2, 3, 4], [0, 1, 0]), (True, [2, 3, 4, 5], [0, 1, 1, 0])):
            self.ok(tool.run(action='key_visibility', objects=[mesh], hold_two=hold))
            self.assertEqual(cmds.currentTime(query=True), 3.5)
            self.assertEqual(cmds.keyframe(mesh, attribute='visibility', query=True, timeChange=True), times)
            self.assertEqual(cmds.keyframe(mesh, attribute='visibility', query=True, valueChange=True), values)
            self.assertFalse(cmds.keyframe(scene.shape(mesh), attribute='visibility', query=True, timeChange=True))
            cmds.undo()
            self.assertFalse(cmds.keyframe(mesh, attribute='visibility', query=True, timeChange=True))

    def test_readonly_preflight_and_geometry_failure_restore_prefs_selection_time(self):
        curves = self.curves()
        cmds.select(curves)
        before = self.snapshot()
        self.ok(tool.run(action='geometry', objects=curves, dry_run=True))
        self.assertEqual(before, self.snapshot())
        original = mel.eval
        def fail(command):
            if command == 'mtbSL_bh_geoFrom2Curves();':
                cmds.nurbsToPolygonsPref(pc=777)
                cmds.currentTime(7)
                cmds.select(clear=True)
                raise RuntimeError('intentional fixture failure')
            return original(command)
        with patch.object(mel, 'eval', side_effect=fail):
            self.assertFalse(tool.run(action='geometry', objects=curves).success)
        after = self.snapshot()
        self.assertEqual(before[:4], after[:4])
        self.assertFalse(runtime._ACTIVE)

    def test_plane_fixed_name_refusal_owned_cleanup_external_child_and_no_gui(self):
        foreign = cmds.createNode('transform', name=scene.PLANE)
        self.assertFalse(tool.run(action='stop_draw', dry_run=True).success)
        self.assertTrue(cmds.objExists(foreign))
        cmds.delete(foreign)
        plane = cmds.nurbsPlane(name=scene.PLANE)[0]
        scene.write_draw(plane, {'context': cmds.currentCtx(), 'live': []})
        child = cmds.createNode('transform', name='externalChild', parent=plane)
        self.assertFalse(tool.run(action='stop_draw', dry_run=True).success)
        cmds.parent(child, world=True)
        plane = cmds.rename(plane, 'renamedOwnedPlane')
        self.ok(tool.run(action='stop_draw'))
        self.assertFalse(cmds.objExists(plane))
        self.assertTrue(cmds.objExists(child))
        self.ok(tool.run(action='stop_draw'))

    def test_restore_error_does_not_leave_internal_write_guard_active(self):
        curves = self.curves()
        original = cmds.nurbsToPolygonsPref
        def fail_restore(**kwargs):
            if not kwargs.get('query'):
                raise RuntimeError('intentional restore fixture failure')
            return original(**kwargs)
        with patch.object(cmds, 'nurbsToPolygonsPref', side_effect=fail_restore):
            self.assertFalse(tool.run(action='geometry', objects=curves).success)
        self.assertFalse(runtime._ACTIVE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
