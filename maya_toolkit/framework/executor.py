# -*- coding: utf-8 -*-
"""
统一执行派发器快捷函数
"""
from __future__ import absolute_import, division, print_function

from .registry import ToolRegistry


def execute_tool(tool_id, arguments=None, dry_run=False):
    """
    通过 tool_id 和字典参数调用任意已注册的 Maya 工具。
    专为大模型 Function Calling 与命令行脚本调用设计。
    """
    return ToolRegistry.execute(tool_id=tool_id, arguments=arguments, dry_run=dry_run)


def list_registered_tools():
    """获取所有已注册工具列表"""
    return ToolRegistry.list_tools()


def export_tool_schemas(format_type="openai"):
    """
    导出工具 Schema，可选格式：'openai' 或 'mcp'
    """
    if str(format_type).lower() == "mcp":
        return ToolRegistry.export_mcp_tools()
    return ToolRegistry.export_openai_tools()
