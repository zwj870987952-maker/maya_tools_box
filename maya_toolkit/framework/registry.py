# -*- coding: utf-8 -*-
"""
工具注册中心与大模型 Schema 导出中心 (ToolRegistry)
"""
from __future__ import absolute_import, division, print_function

import json
from .models import ToolResult
from .base_tool import BaseMayaTool


class ToolRegistry(object):
    """
    全局单例工具注册中心：
    统一负责工具的注册、查找、元数据汇总、大模型 Function Schema 导出与统一调度派发。
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
    def list_tools(cls):
        """获取所有已注册工具的简要信息列表"""
        tool_list = []
        for tid, tool in cls._registry.items():
            tool_list.append({
                "tool_id": tid,
                "tool_name": tool.tool_name,
                "category": tool.category,
                "version": tool.version,
                "description": tool.description
            })
        tool_list.sort(key=lambda x: (x["category"], x["tool_id"]))
        return tool_list

    @classmethod
    def export_openai_tools(cls):
        """导出所有工具为 OpenAI Function Calling 规范的 tools 数组"""
        return [tool.to_openai_tool() for tool in cls._registry.values()]

    @classmethod
    def export_mcp_tools(cls):
        """导出所有工具为标准 MCP (Model Context Protocol) Tools 规范"""
        return [tool.to_mcp_tool() for tool in cls._registry.values()]

    @classmethod
    def export_schemas_json(cls, indent=2):
        """将当前工具箱所有 Schema 导出为美化后的 JSON 字符串"""
        return json.dumps(cls.export_openai_tools(), indent=indent, ensure_ascii=False)

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
                message="未找到 ID 为 [{}] 的工具！当前可用工具: {}".format(tool_id, available),
                errors=["ToolNotFound: {}".format(tool_id)]
            )

        args = arguments or {}
        if not isinstance(args, dict):
            return ToolResult.fail(
                message="arguments 参数必须为字典格式，实际传入: {}".format(type(args).__name__),
                errors=["InvalidArgumentsType"]
            )

        return tool.run(dry_run=dry_run, **args)
