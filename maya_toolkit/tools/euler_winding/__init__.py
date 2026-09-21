# -*- coding: utf-8 -*-
"""
动画欧拉角 360 度异常跳变修正工具 (Euler Winding Fixer)
"""
from __future__ import absolute_import, division, print_function

from .tool import EulerWindingTool
from .algorithms import (
    RotationJumpEvent,
    detect_and_unwind_sequence,
    normalize_sequence_baseline,
)

__all__ = [
    "EulerWindingTool",
    "RotationJumpEvent",
    "detect_and_unwind_sequence",
    "normalize_sequence_baseline",
]
