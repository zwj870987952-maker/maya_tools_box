import maya.cmds as cmds

# 查询选择集中的骨骼个数
selection = cmds.ls(selection=True, type='joint')
selection_size = len(selection)

# 检查是否选中了一个或多个骨骼
if selection_size > 0:
    # 如果选中了骨骼，则将它们的 segmentScaleCompensate 属性改为 0
    for selected_joint in selection:
        cmds.setAttr(selected_joint + ".segmentScaleCompensate", 0)
else:
    # 如果没有选中骨骼，则提示用户选择骨骼
    cmds.warning("Please select at least one joint.")