"""Isolated tests; numerical dependencies are reported, never replaced by fake math."""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / "maya_toolkit/framework/base_tool.py").is_file())
sys.path.insert(0, str(ROOT))
from maya_toolkit.framework import ToolRegistry
BEFORE = ToolRegistry.get("anim_filters")
PACKAGE = HERE.parents[1] / "maya_toolkit/tools/anim_filters"
NAME = "offline_anim_filters"
spec = importlib.util.spec_from_file_location(NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
sys.modules[NAME] = module
spec.loader.exec_module(module)
algorithms = sys.modules[NAME + ".algorithms"]
operations = sys.modules[NAME + ".operations"]


class Scene:
    def __init__(self):
        self.writes = []
        self.evaluations = 0
        self.locked = False

    def undoInfo(self, **kwargs):
        return True

    def ls(self, name, **kwargs):
        return [name] if name == "curve" else []

    def nodeType(self, node):
        return "animCurveTL"

    def referenceQuery(self, node, **kwargs):
        return False

    def lockNode(self, node, **kwargs):
        return [self.locked]

    def getAttr(self, plug, **kwargs):
        return False

    def listConnections(self, plug, **kwargs):
        return ["cube.translateX"]

    def keyframe(self, node=None, **kwargs):
        if kwargs.get("name"):
            return ["curve"]
        if kwargs.get("timeChange"):
            return [1.0, 5.0]
        if kwargs.get("keyframeCount"):
            return 5
        self.evaluations += 1
        return [float(kwargs["time"][0])]

    def cutKey(self, *args, **kwargs):
        self.writes.append(("cut", args, kwargs))

    def setKeyframe(self, *args, **kwargs):
        self.writes.append(("set", args, kwargs))


class AlgorithmTests(unittest.TestCase):
    def test_adaptive_matches_original_on_valid_segments(self):
        source = PACKAGE / "upstream/scripts/animFilters/animFilters.py"
        tree = ast.parse(source.read_bytes())
        names = ("resample_keys", "rejoin_keys", "decimate")
        subset = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names], type_ignores=[])
        original = {}
        exec(compile(subset, str(source), "exec"), original)
        for keys in ({1: 0, 2: 1, 3: 4, 4: 2, 5: 8}, {-2: 2, -1: 3, 0: 4, 1: 5}, {1: 2, 2: 2, 3: 2, 4: 3}):
            for tolerance in (0.01, 0.5, 2.0, 100.0):
                self.assertEqual(algorithms.decimate(keys, tolerance), original["decimate"](keys, tolerance))

    def test_zero_tolerance_linear_segment_terminates_and_keeps_endpoints(self):
        self.assertEqual(algorithms.decimate({1: 1, 2: 2, 3: 3}, 0), {1.0: 1.0, 3.0: 3.0})

    def test_large_nonrecursive_adaptive_segment(self):
        keys = {time: time % 2 for time in range(1500)}
        result = algorithms.decimate(keys, 0)
        self.assertEqual(result, keys)

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "SciPy unavailable in offline interpreter")
    def test_scientific_modes_are_finite_at_pad_boundary(self):
        import math
        raw = {"curve": {time: math.sin(time) for time in range(19)}}
        for mode in ("butterworth", "median"):
            processed, warnings = algorithms.filter_samples(raw, mode=mode, window_size=3)
            self.assertTrue(all(math.isfinite(value) for value in processed["curve"].values()))


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()
        self.tool = module.AnimFiltersTool()
        patch = mock.patch.object(operations, "commands", return_value=self.scene)
        patch.start()
        self.addCleanup(patch.stop)

    def test_dry_run_computes_results_without_writes(self):
        result = self.tool.run(dry_run=True, mode="adaptive")
        self.assertTrue(result.success, result.message)
        self.assertEqual(self.scene.writes, [])
        self.assertEqual(result.data["output_sample_count"], 2)

    def test_rejects_invalid_inputs_and_explicit_empty_arrays(self):
        for kwargs in ({"anim_curves": []}, {"time_range": [1, 1]}, {"time_range": [1.2, 4]}, {"tolerance": float("nan")}, {"unexpected": True}, {"mode": "butterworth", "cutoff": 15}, {"window_size": True}, {"anim_curves": ["curve"]}):
            self.assertFalse(self.tool.run(**kwargs).success, str(kwargs))
        self.assertEqual(self.scene.writes, [])

    def test_sample_limit_rejects_before_sampling_or_writing(self):
        result = self.tool.run(time_range=[1, 10000], max_samples=10)
        self.assertFalse(result.success)
        self.assertEqual(self.scene.evaluations, 0)
        self.assertEqual(self.scene.writes, [])

    def test_locked_curve_prevents_all_writes(self):
        self.scene.locked = True
        self.assertFalse(self.tool.run().success)
        self.assertEqual(self.scene.writes, [])

    def test_scientific_dependency_failure_is_explicit_and_read_only(self):
        with mock.patch.dict(sys.modules, {"scipy": None}):
            result = self.tool.run(mode="median")
        self.assertFalse(result.success)
        self.assertIn("scipy", " ".join(result.errors).lower())
        self.assertEqual(self.scene.writes, [])

    def test_result_is_json_and_writes_use_undoable_commands(self):
        result = self.tool.run(anim_curves=["curve"], time_range=[1, 5])
        self.assertTrue(result.success, result.message)
        data = json.loads(result.to_json())["data"]
        self.assertEqual(data["processed_samples"]["curve"], [{"time": 1.0, "value": 1.0}, {"time": 5.0, "value": 5.0}])
        self.assertEqual([row[0] for row in self.scene.writes], ["cut", "set", "set"])

    def test_candidate_does_not_register_itself(self):
        self.assertIs(ToolRegistry.get("anim_filters"), BEFORE)


if __name__ == "__main__":
    unittest.main()
