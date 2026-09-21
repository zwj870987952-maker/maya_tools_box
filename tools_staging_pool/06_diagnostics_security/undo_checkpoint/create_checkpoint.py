# -*- coding: utf-8 -*-
"""
脚本 1: 生成记录点 (Create Checkpoint)
=====================================
功能：
在当前 Maya 场景操作流中插入一个唯一命名的记录点。
若之前已有记录点，则直接覆盖为当前新的记录点。

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
    # 生成唯一命名的记录点，overwrite=True 表示已有记录点直接覆盖
    maya_undo_checkpoint.create_checkpoint_standalone(name="唯一记录点", overwrite=True)

if __name__ == "__main__":
    main()
