# -*- coding: utf-8 -*-
"""
一键将【Maya 场景记录点工具】及 3 个独立操作按钮安装到当前工具架 (Shelf)
在 Maya 的 Script Editor (Python) 中运行此脚本即可。
"""

from __future__ import print_function
import os
import sys
import maya.cmds as cmds
import maya.mel as mel

def install_to_shelf():
    script_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    
    # 查找当前激活的 Shelf
    current_shelf = mel.eval("tabLayout -q -st $gShelfTopLevel;")
    if not current_shelf:
        cmds.warning("未找到当前活动的 Shelf。")
        return

    # 1. 主面板按钮
    cmd_ui = (
        "import sys\\n"
        "tool_dir = r'{dir}'\\n"
        "if tool_dir not in sys.path: sys.path.insert(0, tool_dir)\\n"
        "import maya_undo_checkpoint\\n"
        "maya_undo_checkpoint.show()\\n"
    ).format(dir=script_dir)

    cmds.shelfButton(
        parent=current_shelf,
        label="UndoCP_UI",
        annotation="打开【Maya 场景记录点管理面板】",
        image1="history.png",
        command=cmd_ui,
        sourceType="python",
        imageOverlayLabel="CP面板",
        overlayLabelColor=(1, 1, 1),
        overlayLabelBackColor=(0.15, 0.4, 0.75, 0.8)
    )

    # 2. 生成记录点 (独立执行)
    cmd_create = (
        "import sys\\n"
        "tool_dir = r'{dir}'\\n"
        "if tool_dir not in sys.path: sys.path.insert(0, tool_dir)\\n"
        "import create_checkpoint\\n"
        "create_checkpoint.main()\\n"
    ).format(dir=script_dir)

    cmds.shelfButton(
        parent=current_shelf,
        label="SetCP",
        annotation="生成记录点 (已有则覆盖)",
        image1="setKeyframe.png",
        command=cmd_create,
        sourceType="python",
        imageOverlayLabel="设记录",
        overlayLabelColor=(1, 1, 1),
        overlayLabelBackColor=(0.18, 0.65, 0.35, 0.8)
    )

    # 3. 恢复记录点 (独立执行)
    cmd_restore = (
        "import sys\\n"
        "tool_dir = r'{dir}'\\n"
        "if tool_dir not in sys.path: sys.path.insert(0, tool_dir)\\n"
        "import restore_checkpoint\\n"
        "restore_checkpoint.main()\\n"
    ).format(dir=script_dir)

    cmds.shelfButton(
        parent=current_shelf,
        label="UndoToCP",
        annotation="恢复回退到记录点",
        image1="undo.png",
        command=cmd_restore,
        sourceType="python",
        imageOverlayLabel="回记录",
        overlayLabelColor=(1, 1, 1),
        overlayLabelBackColor=(0.85, 0.45, 0.15, 0.8)
    )

    # 4. 清空记录点 (独立执行)
    cmd_clear = (
        "import sys\\n"
        "tool_dir = r'{dir}'\\n"
        "if tool_dir not in sys.path: sys.path.insert(0, tool_dir)\\n"
        "import clear_checkpoints\\n"
        "clear_checkpoints.main()\\n"
    ).format(dir=script_dir)

    cmds.shelfButton(
        parent=current_shelf,
        label="ClearCP",
        annotation="清空记录点",
        image1="delete.png",
        command=cmd_clear,
        sourceType="python",
        imageOverlayLabel="清记录",
        overlayLabelColor=(1, 1, 1),
        overlayLabelBackColor=(0.4, 0.4, 0.4, 0.8)
    )

    print("==================================================")
    print("【成功】已将 4 个记录点快捷按钮添加到当前工具架 [{}]！".format(current_shelf))
    print("  1. [CP面板] 打开图形管理界面")
    print("  2. [设记录] 一键生成记录点 (覆盖旧点)")
    print("  3. [回记录] 一键批量 Undo 回退到记录点")
    print("  4. [清记录] 一键清空记录点")
    print("==================================================")

if __name__ == "__main__":
    install_to_shelf()
