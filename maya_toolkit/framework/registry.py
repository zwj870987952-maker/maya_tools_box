# -*- coding: utf-8 -*-
"""
工具注册中心与大模型 Schema 导出中心 (ToolRegistry)
支持按工业级业务领域 (Domain Taxonomy) 检索、分片与导出。
"""
from __future__ import absolute_import, division, print_function

import json
from .models import ToolResult
from .base_tool import BaseMayaTool
from .domains import (
    ToolDomain,
    TOOL_DOMAINS,
    get_domain_info,
    list_domains,
)


class ToolRegistry(object):
    """
    全局单例工具注册中心：
    统一负责工具的注册、查找、业务领域归类、大模型 Function Schema 导出与统一调度派发。
    """

    _registry = {}

    @classmethod
    def register(cls, tool_instance_or_class):
        """注册一个工具类或实例"""
        if isinstance(tool_instance_or_class, type) and issubclass(tool_instance_or_class, BaseMayaTool):
            instance = tool_instance_or_class()
        elif isinstance(tool_instance_or_class, BaseMayaTool):
            instance = tool_instance_or_class
        else:
            raise TypeError("注册对象必须是 BaseMayaTool 的子类或其实例！")

        tool_id = instance.tool_id
        cls._registry[tool_id] = instance
        return instance

    @classmethod
    def get(cls, tool_id):
        """根据 tool_id 获取对应工具实例"""
        return cls._registry.get(str(tool_id))

    @classmethod
    def list_tools(cls, domain=None):
        """
        获取已注册工具的信息列表，支持按 domain (大业务领域) 过滤。
        :param domain: 可选领域键名，如 'animation', 'rigging' 等。为 None 时返回全部。
        """
        tool_list = []
        norm_domain = str(domain).lower().strip() if domain else None

        for tid, tool in cls._registry.items():
            tool_cat = str(tool.category).lower().strip()
            if norm_domain and tool_cat != norm_domain:
                continue

            dom_info = get_domain_info(tool.category)
            tool_list.append({
                "tool_id": tid,
                "tool_name": tool.tool_name,
                "category": tool.category,
                "domain_name": dom_info["name"],
                "badge_color": dom_info["badge_color"],
                "version": tool.version,
                "description": tool.description
            })

        tool_list.sort(key=lambda x: (x["category"], x["tool_id"]))
        return tool_list

    @classmethod
    def list_domains_summary(cls):
        """
        返回 6 大领域的完整元数据列表，并附带各自旗下已注册工具的数量与精简清单。
        便于大模型在决策前进行全局领域概览。
        """
        summaries = []
        for domain in list_domains():
            tools = cls.list_tools(domain=domain["id"])
            d_copy = dict(domain)
            d_copy["tool_count"] = len(tools)
            d_copy["tools"] = tools
            summaries.append(d_copy)
        return summaries

    @classmethod
    def export_openai_tools(cls, domain=None):
        """
        导出工具为 OpenAI Function Calling 规范的 tools 数组，支持按领域分片导出。
        :param domain: 领域过滤键名
        """
        norm_domain = str(domain).lower().strip() if domain else None
        tools = []
        for tool in cls._registry.values():
            if norm_domain and str(tool.category).lower().strip() != norm_domain:
                continue
            tools.append(tool.to_openai_tool())
        return tools

    @classmethod
    def export_mcp_tools(cls, domain=None):
        """
        导出工具为标准 MCP (Model Context Protocol) Tools 规范，支持按领域分片导出。
        :param domain: 领域过滤键名
        """
        norm_domain = str(domain).lower().strip() if domain else None
        tools = []
        for tool in cls._registry.values():
            if norm_domain and str(tool.category).lower().strip() != norm_domain:
                continue
            tools.append(tool.to_mcp_tool())
        return tools

    @classmethod
    def export_schemas_json(cls, domain=None, indent=2):
        """将指定领域或全部工具 Schema 导出为美化后的 JSON 字符串"""
        return json.dumps(cls.export_openai_tools(domain=domain), indent=indent, ensure_ascii=False)

    @classmethod
    def execute(cls, tool_id, arguments=None, dry_run=False):
        """
        统一大模型/外部脚本调用派发入口。
        :param tool_id: 工具标识 ID
        :param arguments: 字典参数（支持从大模型 JSON 解析后直接传入）
        :param dry_run: 是否为预检模式
        :return: ToolResult 对象
        """
        tool = cls.get(tool_id)
        if not tool:
            available = list(cls._registry.keys())
            return ToolResult.fail(
                tool_id=str(tool_id),
                message="未找到 ID 为 [{}] 的工具！当前可用工具: {}".format(tool_id, available),
                errors=["ToolNotFound: {}".format(tool_id)]
            )

        args = {} if arguments is None else arguments
        if not isinstance(args, dict):
            return ToolResult.fail(
                tool_id=str(tool_id),
                message="arguments 参数必须为字典格式，实际传入: {}".format(type(args).__name__),
                errors=["InvalidArgumentsType"]
            )

        return tool.run(dry_run=dry_run, **args)
