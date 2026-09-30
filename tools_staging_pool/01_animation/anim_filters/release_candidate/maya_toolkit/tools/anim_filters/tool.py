# -*- coding: utf-8 -*-
# animFilters adaptation: Copyright 2018 Michal Mach, GPL-2.0-or-later.
from __future__ import absolute_import, division, print_function

import math
from numbers import Real, Integral
from maya_toolkit.framework import BaseMayaTool, ToolResult
from . import algorithms, operations


def number(value, name, minimum=0, strict=False):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or (value <= minimum if strict else value < minimum):
        raise ValueError("Invalid " + name)


class AnimFiltersTool(BaseMayaTool):
    tool_id = "anim_filters"
    tool_name = "动画曲线过滤器"
    category = "animation"
    version = "1.1.0"
    description = "Adaptive/Butterworth/Median 曲线过滤；实时预览保留 Undo；科学滤波需要目标 Maya 的 NumPy/SciPy。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["adaptive", "butterworth", "median"], "default": "adaptive"},
            "anim_curves": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "省略时读取 Graph Editor 所选关键帧所属曲线；显式调用需给 time_range"},
            "time_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "description": "含端点的整数帧区间；省略时所选关键帧的全局起止帧"},
            "tolerance": {"type": "number", "minimum": 0, "default": 0.25},
            "window_size": {"type": "integer", "minimum": 1, "maximum": 10001, "default": 35},
            "sample_frequency": {"type": "number", "exclusiveMinimum": 0, "default": 30.0},
            "cutoff": {"type": "number", "exclusiveMinimum": 0, "default": 7.0},
            "order": {"type": "integer", "minimum": 1, "maximum": 32, "default": 5},
            "max_samples": {"type": "integer", "minimum": 2, "maximum": 2000000, "default": 100000}
        },
        "additionalProperties": False
    }

    def _prepare(self, mode="adaptive", anim_curves=None, time_range=None, tolerance=0.25, window_size=35, sample_frequency=30.0, cutoff=7.0, order=5, max_samples=100000, **kwargs):
        if kwargs:
            raise ValueError("Unknown parameters: " + ", ".join(sorted(kwargs)))
        if mode not in ("adaptive", "butterworth", "median"):
            raise ValueError("Invalid mode")
        number(tolerance, "tolerance")
        number(sample_frequency, "sample_frequency", strict=True)
        number(cutoff, "cutoff", strict=True)
        for value, name, low, high in ((window_size, "window_size", 1, 10001), (order, "order", 1, 32), (max_samples, "max_samples", 2, 2000000)):
            if isinstance(value, bool) or not isinstance(value, Integral) or not low <= value <= high:
                raise ValueError("Invalid " + name)
        if mode == "butterworth" and cutoff >= sample_frequency / 2.0:
            raise ValueError("cutoff must be less than Nyquist (sample_frequency / 2)")
        cmds = operations.commands()
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError("Enable Maya Undo before filtering")
        explicit_curves = anim_curves is not None
        if explicit_curves and (not isinstance(anim_curves, (list, tuple)) or not anim_curves or any(not isinstance(node, str) or not node for node in anim_curves)):
            raise ValueError("anim_curves must contain nonempty node names")
        if not explicit_curves:
            anim_curves = cmds.keyframe(query=True, selected=True, name=True) or []
        if not anim_curves:
            raise ValueError("Select animation keys in Graph Editor or provide anim_curves")
        if time_range is None:
            if explicit_curves:
                raise ValueError("Explicit anim_curves require time_range")
            times = cmds.keyframe(query=True, selected=True, timeChange=True) or []
            if not times:
                raise ValueError("No selected key times")
            start, end = int(min(times)), int(max(times))
        elif isinstance(time_range, (list, tuple)) and len(time_range) == 2 and all(isinstance(value, Integral) and not isinstance(value, bool) for value in time_range):
            start, end = time_range
        else:
            raise ValueError("time_range requires two integer frames")
        if start >= end:
            raise ValueError("time_range must span at least one frame")
        unique = []
        for name in anim_curves:
            resolved = cmds.ls(name, long=True) or []
            if len(resolved) != 1 or cmds.nodeType(resolved[0]) not in ("animCurveTA", "animCurveTL", "animCurveTU"):
                raise ValueError("Only unique time-input angle/linear/unitless curves supported: " + name)
            curve = resolved[0]
            if cmds.referenceQuery(curve, isNodeReferenced=True) or any(cmds.lockNode(curve, query=True, lock=True) or []):
                raise ValueError("Referenced/locked curve: " + curve)
            if cmds.getAttr(curve + ".ktv", lock=True):
                raise ValueError("Locked key array: " + curve)
            outputs = cmds.listConnections(curve + ".output", source=False, destination=True, plugs=True) or []
            if len(outputs) != 1:
                raise ValueError("Curve needs one destination as in upstream: " + curve)
            if cmds.getAttr(outputs[0], lock=True):
                raise ValueError("Locked destination: " + outputs[0])
            if cmds.referenceQuery(outputs[0].split(".")[0], isNodeReferenced=True):
                raise ValueError("Referenced destination is not supported: " + outputs[0])
            if not cmds.keyframe(curve, query=True, keyframeCount=True):
                raise ValueError("Empty curve: " + curve)
            if curve not in unique:
                unique.append(curve)
        raw_count = (end - start + 1) * len(unique)
        filtered_count = max(2, int(sample_frequency * (end - start) / 30.0 + 1)) * len(unique) if mode == "butterworth" else raw_count
        if max(raw_count, filtered_count) > max_samples:
            raise ValueError("Sample count exceeds max_samples; narrow range or raise explicit limit")
        raw = operations.sample_curves(cmds, unique, start, end)
        if any(not math.isfinite(value) for keys in raw.values() for value in keys.values()):
            raise ValueError("Nonfinite evaluated values")
        processed, warnings = algorithms.filter_samples(raw, mode, tolerance, window_size, sample_frequency, cutoff, order)
        return cmds, raw, processed, warnings, [start, end]

    def validate(self, **kwargs):
        try:
            unused_cmds, raw, processed, warnings, time_range = self._prepare(**kwargs)
            return ToolResult.ok("过滤预检通过（尚未写入曲线）", data={"mode": kwargs.get("mode", "adaptive"), "anim_curves": list(raw), "time_range": time_range, "input_sample_count": sum(len(keys) for keys in raw.values()), "output_sample_count": sum(len(keys) for keys in processed.values())}, warnings=warnings)
        except Exception as error:
            return ToolResult.fail("过滤预检失败: {}".format(error), errors=[str(error)])

    def execute(self, **kwargs):
        cmds, raw, processed, warnings, time_range = self._prepare(**kwargs)
        try:
            completed = operations.apply_curves(cmds, raw, processed)
        except Exception as error:
            return ToolResult(success=False, message="曲线写入失败；可能已有部分修改，请撤销", data={"partial_changes_possible": True, "anim_curves": list(raw)}, errors=[str(error)], warnings=warnings)
        return ToolResult.ok("过滤完成", data={"mode": kwargs.get("mode", "adaptive"), "anim_curves": completed, "time_range": time_range, "processed_samples": {curve: [{"time": float(time), "value": float(value)} for time, value in sorted(keys.items())] for curve, keys in processed.items()}}, warnings=warnings)

    def show_ui(self, parent=None):
        from .ui import show
        return show(self, parent=parent)
