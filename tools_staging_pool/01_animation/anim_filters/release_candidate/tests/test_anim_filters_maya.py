"""Isolated Maya tests, including an explicit unmet scientific dependency check."""
import ast
import importlib.util
import os
from pathlib import Path
import sys
import unittest

if not os.environ.get("STAGING_ISOLATED_MAYAPY"):
    raise RuntimeError("Requires isolated mayapy runner")
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

RC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RC))
if (RC / "launch_candidate.py").is_file():
    from launch_candidate import load_tool
else:
    from maya_toolkit.tools.anim_filters import AnimFiltersTool
    load_tool = AnimFiltersTool


def curve_snapshot(curve):
    return {"times": cmds.keyframe(curve, query=True, timeChange=True), "values": cmds.keyframe(curve, query=True, valueChange=True), "in": cmds.keyTangent(curve, query=True, inTangentType=True), "out": cmds.keyTangent(curve, query=True, outTangentType=True), "undo_state": cmds.undoInfo(query=True, state=True)}


class AnimFiltersMayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.cube = cmds.polyCube()[0]
        for time, value in ((0, -3), (1, 1), (2, 9), (3, 2), (4, 7)):
            cmds.setKeyframe(self.cube, attribute="translateX", time=time, value=value, inTangentType="linear", outTangentType="linear")
        self.curve = cmds.listConnections(self.cube + ".translateX", source=True, destination=False)[0]
        cmds.selectKey(self.curve, time=(1, 3), replace=True)
        self.tool = load_tool()

    def test_adaptive_dry_run_preserves_full_curve_and_undo_queue(self):
        before = curve_snapshot(self.curve)
        name = cmds.undoInfo(query=True, undoName=True)
        selection = cmds.keyframe(query=True, selected=True, timeChange=True)
        result = self.tool.run(dry_run=True)
        self.assertTrue(result.success, result.to_json())
        self.assertEqual(curve_snapshot(self.curve), before)
        self.assertEqual(cmds.undoInfo(query=True, undoName=True), name)
        self.assertEqual(cmds.keyframe(query=True, selected=True, timeChange=True), selection)

    def test_adaptive_apply_preserves_outside_keys_and_one_step_undo(self):
        before = curve_snapshot(self.curve)
        result = self.tool.run(anim_curves=[self.curve], time_range=[1, 3], tolerance=100)
        self.assertTrue(result.success, result.to_json())
        self.assertEqual(cmds.keyframe(self.curve, query=True, timeChange=True), [0, 1, 3, 4])
        self.assertEqual(cmds.keyframe(self.curve, query=True, valueChange=True), [-3, 1, 2, 7])
        cmds.undo()
        self.assertEqual(curve_snapshot(self.curve), before)

    def test_endpoint_write_matches_upstream_for_translation_and_rotation(self):
        package = sys.modules[self.tool.__class__.__module__].__package__
        ops = sys.modules[package + ".operations"]
        path = Path(ops.__file__).parent / "upstream/scripts/animFilters/animFilters.py"
        tree = ast.parse(path.read_bytes())
        subset = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ("add_keys", "apply_curves")], type_ignores=[])
        original = {"cmds": cmds, "om": om, "oma": oma}
        exec(compile(subset, str(path), "exec"), original)
        for attribute in ("translateX", "rotateX"):
            if attribute == "rotateX":
                for time, value in ((0, -3), (1, 1), (2, 9), (3, 2), (4, 7)):
                    cmds.setKeyframe(self.cube, attribute=attribute, time=time, value=value)
            curve = cmds.listConnections(self.cube + "." + attribute, source=True, destination=False)[0]
            raw = {curve: {1: 1, 2: 9, 3: 2}}
            processed = {curve: {1: 100, 2: 5, 3: 200}}
            original["apply_curves"](raw, processed)
            expected = cmds.keyframe(curve, query=True, valueChange=True)
            # Reset values with commands, then apply the candidate on the same sample data.
            for time, value in ((1, 1), (2, 9), (3, 2)):
                cmds.setKeyframe(curve, time=time, value=value)
            ops.apply_curves(cmds, raw, processed)
            actual = cmds.keyframe(curve, query=True, valueChange=True)
            for first, second in zip(actual, expected):
                self.assertAlmostEqual(first, second, places=6)

    def test_preview_refresh_cancel_and_apply_remain_undoable(self):
        package = self.tool.__class__.__module__.rsplit(".", 1)[0]
        from importlib import import_module
        PreviewSession = import_module(package + ".preview").PreviewSession
        before = curve_snapshot(self.curve)
        session = PreviewSession(self.tool, cmds)
        result = session.update({"tolerance": 100}, buffer=True)
        self.assertTrue(result.success, result.to_json())
        self.assertTrue(session.active)
        self.assertTrue(cmds.undoInfo(query=True, state=True))
        session.update({"tolerance": 0, "anim_curves": [self.curve], "time_range": [1, 3]})
        session.cancel()
        self.assertEqual(curve_snapshot(self.curve), before)
        session.update({"tolerance": 100, "anim_curves": [self.curve], "time_range": [1, 3]})
        session.apply()
        cmds.undo()
        self.assertEqual(curve_snapshot(self.curve), before)

    def test_preview_refuses_to_undo_unrelated_edits(self):
        from importlib import import_module
        package = self.tool.__class__.__module__.rsplit(".", 1)[0]
        session = import_module(package + ".preview").PreviewSession(self.tool, cmds)
        session.update({"tolerance": 100})
        cmds.setAttr(self.cube + ".translateY", 23)
        with self.assertRaises(RuntimeError):
            session.cancel()
        self.assertEqual(cmds.getAttr(self.cube + ".translateY"), 23)
        cmds.undo()
        session.cancel()

    @unittest.skipUnless(os.environ.get("STAGING_QT_SMOKE") == "1", "Qt smoke requires its own explicitly enabled process; this standalone runtime crashed creating Qt widgets")
    def test_qt_resource_loads_and_sliders_cancel_without_settings_writes(self):
        from PySide6 import QtWidgets
        application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        package = self.tool.__class__.__module__.rsplit(".", 1)[0]
        from importlib import import_module
        ui = import_module(package + ".ui")

        class MemorySettings:
            def value(self, name, default):
                return False
            def setValue(self, name, value):
                pass

        before = curve_snapshot(self.curve)
        window = ui.show(self.tool, settings=MemorySettings())
        controller = ui._controllers[-1]
        controller.controls["thresholdSpinBox"].setValue(10)
        controller.start()
        self.assertTrue(controller.preview.active)
        controller.controls["thresholdSlider"].setValue(500)
        self.assertTrue(controller.preview.active)
        window.close()
        application.processEvents()
        self.assertEqual(curve_snapshot(self.curve), before)

    def test_scientific_dependencies_in_target_maya(self):
        self.assertIsNotNone(importlib.util.find_spec("scipy"), "SciPy is absent from this Maya interpreter; Butterworth/Median require a compatible installation and retest")
        for mode in ("butterworth", "median"):
            result = self.tool.run(mode=mode, window_size=3)
            self.assertTrue(result.success, result.to_json())
            cmds.undo()


if __name__ == "__main__":
    try:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(AnimFiltersMayaTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        status = 0 if result.wasSuccessful() else 1
    finally:
        maya.standalone.uninitialize()
    sys.exit(status)
