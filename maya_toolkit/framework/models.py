# -*- coding: utf-8 -*-
"""
大模型与自动化调用统一返回协议模型 (ToolResult)
"""
from __future__ import absolute_import, division, print_function

import json


class ToolResult(object):
    """
    所有 Maya 工具 API 与大模型调用的统一返回值对象。
    具备标准化的 JSON 序列化能力，使 LLM / Agent 能够精准理解执行结果。
    """

    def __init__(
        self,
        success=True,
        message="",
        data=None,
        errors=None,
        warnings=None,
        dry_run=False,
        execution_time=0.0
    ):
        self.success = bool(success)
        self.message = str(message)
        self.data = data if data is not None else {}
        self.errors = list(errors) if errors else []
        self.warnings = list(warnings) if warnings else []
        self.dry_run = bool(dry_run)
        self.execution_time = float(execution_time)

    def to_dict(self):
        """转为标准 Python 原生字典（保证可 JSON 序列化）"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "dry_run": self.dry_run,
            "execution_time": self.execution_time
        }

    def to_json(self, indent=2, ensure_ascii=False):
        """转为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def ok(cls, message="操作执行成功", data=None, warnings=None, dry_run=False, execution_time=0.0):
        """快速构建成功响应"""
        return cls(
            success=True,
            message=message,
            data=data or {},
            warnings=warnings or [],
            dry_run=dry_run,
            execution_time=execution_time
        )

    @classmethod
    def fail(cls, message="操作执行失败", errors=None, data=None, dry_run=False, execution_time=0.0):
        """快速构建失败响应"""
        err_list = errors if isinstance(errors, list) else ([str(errors)] if errors else [])
        return cls(
            success=False,
            message=message,
            errors=err_list,
            data=data or {},
            dry_run=dry_run,
            execution_time=execution_time
        )

    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        mode = " [DRY-RUN]" if self.dry_run else ""
        return "<ToolResult [{status}{mode}] {msg}>".format(status=status, mode=mode, msg=self.message)
