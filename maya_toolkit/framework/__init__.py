# -*- coding: utf-8 -*-
"""
Framework 架构层：包含统一大模型与自动化返回模型、抽象基类、工具注册表与派发器。
"""
from __future__ import absolute_import, division, print_function

from .models import ToolResult
from .base_tool import BaseMayaTool
from .domains import (
    ToolDomain,
    TOOL_DOMAINS,
    get_domain_info,
    list_domains,
)
from .registry import ToolRegistry
from .executor import (
    execute_tool,
    list_registered_tools,
    list_domains_summary,
    export_tool_schemas,
)

__all__ = [
    "ToolResult",
    "BaseMayaTool",
    "ToolDomain",
    "TOOL_DOMAINS",
    "get_domain_info",
    "list_domains",
    "ToolRegistry",
    "execute_tool",
    "list_registered_tools",
    "list_domains_summary",
    "export_tool_schemas",
]
