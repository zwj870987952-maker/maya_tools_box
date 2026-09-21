# -*- coding: utf-8 -*-
"""
工具基类规范模块：定义所有 Maya 自动化与大模型工具的标准抽象基类 (BaseMayaTool)。
"""
from __future__ import absolute_import, division, print_function

import time
import traceback
from .models import ToolResult
from ..core.context import UndoChunkContext


class BaseMayaTool(object):
    """
    所有 Maya 工具必须继承的统一基类。
    规范了：
      1. 元数据与 JSON Schema 参数描述（供大模型 Function Calling / MCP 识别）。
      2. 预检（validate）与无副作用 Dry-Run 机制。
      3. 统一原子化事务执行（execute）与 Undo 保护。
      4. 统一 UI 启动入口（show_ui）。
    """

    tool_id = "base_tool"
    tool_name = "基础工具"
    category = "General"
    description = "工具描述"
    version = "1.0.0"

    # 参数 JSON Schema 规范 (遵循 draft-07 标准)
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": True
    }

    def validate(self, **kwargs):
        """
        预检/参数校验方法（必须无副作用）。
        在大模型调用真正修改场景前执行，检查参数类型、节点是否存在、路径是否合法等。
        :return: ToolResult 对象（若参数合法则 success=True）
        """
        return ToolResult.ok(message="参数预检通过", dry_run=True)

    def execute(self, **kwargs):
        """
        执行核心业务逻辑方法。
        :return: ToolResult 对象
        """
        raise NotImplementedError("子类必须实现 execute 方法！")

    def run(self, dry_run=False, **kwargs):
        """
        对外调用的统一标准入口（支持 dry_run 预检模式与自动 Undo Chunk 保护）。
        :param dry_run: 若为 True，则仅执行校验并返回预检结果，绝不修改 Maya 场景。
        :param kwargs: 工具所需参数
        :return: ToolResult 结果对象
        """
        start_time = time.time()

        # 确保 Maya 运行环境（在 mayapy / 独立命令行下按需初始化）
        from ..core.maya_utils import ensure_maya_initialized
        ensure_maya_initialized()

        # 1. 首先执行参数预检
        val_res = self.validate(**kwargs)
        if not val_res.success:
            val_res.execution_time = round(time.time() - start_time, 4)
            return val_res

        # 2. 如果是 Dry-Run 模式，直接返回预检结果，零污染零修改
        if dry_run:
            val_res.dry_run = True
            val_res.message = "[Dry-Run 预检成功] " + val_res.message
            val_res.execution_time = round(time.time() - start_time, 4)
            return val_res

        # 3. 正式执行，包裹在统一 Undo Chunk 中
        chunk_name = "{}_{}".format(self.__class__.__name__, self.tool_id)
        with UndoChunkContext(chunk_name=chunk_name):
            try:
                result = self.execute(**kwargs)
                if not isinstance(result, ToolResult):
                    result = ToolResult.ok(
                        message="执行完成",
                        data=result if isinstance(result, dict) else {"result": result}
                    )
            except Exception as e:
                err_detail = traceback.format_exc()
                result = ToolResult.fail(
                    message="执行异常: {}".format(str(e)),
                    errors=[str(e), err_detail]
                )

        result.dry_run = False
        result.execution_time = round(time.time() - start_time, 4)
        return result

    def show_ui(self, parent=None):
        """
        打开图形化用户界面（由各工具在 UI 模块中重载）。
        """
        print("[{}] 该工具未提供图形界面或仅支持无界面 API 调用。".format(self.tool_name))

    def to_openai_tool(self):
        """导出为 OpenAI 标准 Function Calling 工具定义规范"""
        return {
            "type": "function",
            "function": {
                "name": self.tool_id,
                "description": "{}: {}".format(self.tool_name, self.description),
                "parameters": self.parameters_schema
            }
        }

    def to_mcp_tool(self):
        """导出为标准 Model Context Protocol (MCP) Tools 格式规范"""
        return {
            "name": self.tool_id,
            "description": "{}: {}".format(self.tool_name, self.description),
            "inputSchema": self.parameters_schema
        }
