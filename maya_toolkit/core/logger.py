# -*- coding: utf-8 -*-
"""
结构化日志模块：
统一控制终端输出、Maya 视口提示与大模型结构化执行日志收集。
"""
from __future__ import absolute_import, division, print_function

import sys
import time

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False


class ToolkitLogger(object):
    """兼顾用户交互与自动化/大模型记录的日志收集器"""

    def __init__(self, tool_name="MayaToolkit"):
        self.tool_name = tool_name
        self.entries = []

    def _log(self, level, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            "level": level,
            "time": timestamp,
            "message": str(message)
        }
        self.entries.append(entry)

        prefix = "[{}][{}]".format(self.tool_name, level.upper())
        formatted = "{} {}".format(prefix, message)

        if level == "error":
            if MAYA_AVAILABLE and cmds:
                cmds.error(formatted)
            else:
                sys.stderr.write(formatted + "\n")
        elif level == "warning":
            if MAYA_AVAILABLE and cmds:
                cmds.warning(formatted)
            else:
                sys.stderr.write(formatted + "\n")
        else:
            print(formatted)

    def info(self, message):
        self._log("info", message)

    def warning(self, message):
        self._log("warning", message)

    def error(self, message):
        self._log("error", message)

    def clear(self):
        self.entries = []

    def get_entries(self):
        return list(self.entries)
