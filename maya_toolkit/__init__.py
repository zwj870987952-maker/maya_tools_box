# -*- coding: utf-8 -*-
"""
Maya Toolkit - 统一规范的 Maya 生产力工具箱与自动化/大模型调度框架
"""
from __future__ import absolute_import, division, print_function

__version__ = "2.0.0"
import os
import sys

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_compat_dir = os.path.join(_root_dir, "compat")
if os.path.isdir(_compat_dir) and _compat_dir not in sys.path:
    sys.path.insert(0, _compat_dir)

# 导出核心层与框架层公共 API
from .core import (
    ensure_maya_initialized,
    UndoChunkContext,
    SuspendRefreshContext,
    undo_chunk,
    natural_sort_key,
    get_mesh_shape,
    get_mesh_dag,
    get_skin_cluster,
    resolve_selected_meshes,
    get_all_user_selection_sets,
    get_maya_main_window,
    apply_dark_theme,
    ToolkitLogger,
)

from .framework import (
    ToolResult,
    BaseMayaTool,
    ToolRegistry,
    execute_tool,
    list_registered_tools,
    export_tool_schemas,
)

# 导入 tools 自动完成所有工具的注册
from . import tools

# 导出统一启动面板 UI
from .ui import show_launcher, install_shelf_button
show_ui = show_launcher

__all__ = [
    "UndoChunkContext",
    "SuspendRefreshContext",
    "undo_chunk",
    "natural_sort_key",
    "get_mesh_shape",
    "get_mesh_dag",
    "get_skin_cluster",
    "resolve_selected_meshes",
    "get_all_user_selection_sets",
    "get_maya_main_window",
    "apply_dark_theme",
    "ToolkitLogger",
    "ToolResult",
    "BaseMayaTool",
    "ToolRegistry",
    "execute_tool",
    "list_registered_tools",
    "export_tool_schemas",
    "tools",
]
