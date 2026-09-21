# -*- coding: utf-8 -*-
"""
业务工具层：自动注册所有 6 大内置工具到统一工具注册中心 (ToolRegistry)
"""
from __future__ import absolute_import, division, print_function

from ..framework.registry import ToolRegistry

from .namespace_clean import NamespaceCleanTool
from .euler_winding import EulerWindingTool
from .weights_copy import WeightsCopyTool
from .fbx_export import FBXExportTool
from .material_transfer import MaterialTransferTool
from .fbx_diff import FBXDiffSyncTool

# 统一自动注册内置工具
ALL_TOOL_CLASSES = [
    NamespaceCleanTool,
    EulerWindingTool,
    WeightsCopyTool,
    FBXExportTool,
    MaterialTransferTool,
    FBXDiffSyncTool,
]


def register_all_builtin_tools():
    """注册所有内置工具"""
    registered = []
    for cls in ALL_TOOL_CLASSES:
        tool_instance = ToolRegistry.register(cls)
        registered.append(tool_instance)
    return registered


# 导入时自动完成注册
register_all_builtin_tools()

__all__ = [
    "NamespaceCleanTool",
    "EulerWindingTool",
    "WeightsCopyTool",
    "FBXExportTool",
    "MaterialTransferTool",
    "FBXDiffSyncTool",
    "register_all_builtin_tools",
]
