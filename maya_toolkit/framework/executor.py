# -*- coding: utf-8 -*-
"""
统一执行派发器与领域查询快捷函数
"""
from __future__ import absolute_import, division, print_function

from .registry import ToolRegistry
from .domains import (
    ToolDomain,
    TOOL_DOMAINS,
    get_domain_info,
    list_domains,
)


def execute_tool(tool_id, arguments=None, dry_run=False):
    """
    通过 tool_id 和字典参数调用任意已注册的 Maya 工具。
    专为大模型 Function Calling 与命令行脚本调用设计。
    """
    return ToolRegistry.execute(tool_id=tool_id, arguments=arguments, dry_run=dry_run)


def list_registered_tools(domain=None):
    """
    获取已注册工具列表，支持按业务领域过滤。
    :param domain: 可选领域键名，如 'animation', 'rigging' 等。
    """
    return ToolRegistry.list_tools(domain=domain)


def list_domains_summary():
    """获取所有业务领域的统计与旗下工具概览"""
    return ToolRegistry.list_domains_summary()


def export_tool_schemas(format_type="openai", domain=None):
    """
    导出工具 Schema，可选格式：'openai' 或 'mcp'，支持按领域分片导出。
    :param format_type: 'openai' 或 'mcp'
    :param domain: 可选领域键名，如 'animation'
    """
    if str(format_type).lower() == "mcp":
        return ToolRegistry.export_mcp_tools(domain=domain)
    return ToolRegistry.export_openai_tools(domain=domain)
