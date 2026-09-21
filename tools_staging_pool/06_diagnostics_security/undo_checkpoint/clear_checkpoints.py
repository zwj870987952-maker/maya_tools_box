# -*- coding: utf-8 -*-
"""
脚本 3: 清空记录点 (Clear Checkpoints)
=====================================
功能：
清空当前已保存的记录点标记（不影响场景中现有模型或操作）。

适合：绑定快捷键 (Hotkey) 或作为 Shelf 按钮一键点击执行。
"""

from __future__ import print_function, absolute_import
import os
import sys

# 将工具目录加入 sys.path
tool_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)

import maya_undo_checkpoint

def main():
    # 清空所有记录点
    maya_undo_checkpoint.clear_checkpoint_standalone()

if __name__ == "__main__":
    main()
