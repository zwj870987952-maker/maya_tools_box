# -*- coding: utf-8 -*-
"""
向后兼容层 (Compatibility Layer)
收纳历史单文件工具脚本，确保旧版本工作流、Shelf 按钮与流水线脚本无缝平滑运行。
推荐在新开发与大模型调用中直接使用 `maya_toolkit`。
"""
from __future__ import absolute_import, division, print_function

import os
import sys

_compat_dir = os.path.dirname(os.path.abspath(__file__))
if _compat_dir not in sys.path:
    sys.path.insert(0, _compat_dir)
