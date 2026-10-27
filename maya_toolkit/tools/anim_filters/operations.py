# -*- coding: utf-8 -*-
# Derived from animFilters 1.0, Copyright 2018 Michal Mach; GPL-2.0-or-later.
from __future__ import absolute_import, division, print_function


def commands():
    import maya.cmds as cmds
    return cmds


def sample_curves(cmds, curves, start, end):
    result = {}
    for curve in curves:
        values = {}
        for frame in range(start, end + 1):
            evaluated = cmds.keyframe(curve, query=True, time=(frame, frame), eval=True)
            if not evaluated:
                raise ValueError("Cannot evaluate {} at {}".format(curve, frame))
            values[frame] = float(evaluated[0])
        result[curve] = values
    return result


def apply_curves(cmds, raw, processed):
    completed = []
    for curve, original in raw.items():
        start, end = min(original), max(original)
        # Match upstream open interior deletion. Endpoint writes replace values.
        if end - start > 0.002:
            cmds.cutKey(curve, time=(start + 0.001, end - 0.001), option="keys", clear=True)
        for time, value in sorted(processed[curve].items()):
            cmds.setKeyframe(curve, time=float(time), value=float(value), inTangentType="auto", outTangentType="auto")
        completed.append(curve)
    return completed
