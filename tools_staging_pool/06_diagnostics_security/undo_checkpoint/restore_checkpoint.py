# -*- coding: utf-8 -*-
"""
脚本 2: 恢复记录点 (Restore Checkpoint)
=====================================
功能：
批量自动执行 Maya Undo，精确回退到上一次生成的记录点位置。

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
    # 恢复回退到当前有效的记录点
    maya_undo_checkpoint.restore_checkpoint_standalone()

if __name__ == "__main__":
    main()
