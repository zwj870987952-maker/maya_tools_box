# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from functools import partial
from .operations import maya_commands


def show(tool):
    cmds = maya_commands()
    name = "resetPivotCandidateWindow"
    if cmds.window(name, exists=True):
        cmds.deleteUI(name)
    window = cmds.window(name, title="重置坐标中心轴", widthHeight=(280, 370))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="选择物体后执行；支持先预检", height=30)
    preview = cmds.checkBox(label="仅预检（不修改场景）", value=False)

    def invoke(action, *unused):
        result = tool.run(action=action, dry_run=cmds.checkBox(preview, query=True, value=True))
        print(result.to_json())
        if not result.success:
            cmds.warning(result.message)

    for label, actions in (
        ("轴心点位置", (("中心", "center"), ("世界原点", "origin"), ("父物体轴心", "parent"))),
        ("轴向方向", (("重置旋转轴", "reset_axes"), ("对齐世界", "world"), ("匹配骨骼方向（源、目标顺序）", "joint"))),
        ("综合操作", (("完全重置物体", "complete"),))
    ):
        cmds.frameLayout(label=label, collapsable=False, marginWidth=5, marginHeight=5)
        cmds.columnLayout(adjustableColumn=True)
        for text, action in actions:
            cmds.button(label=text, command=partial(invoke, action), height=30)
        cmds.setParent("..")
        cmds.setParent("..")
    cmds.button(label="关闭", command=lambda *unused: cmds.deleteUI(name))
    cmds.showWindow(window)
    return window
