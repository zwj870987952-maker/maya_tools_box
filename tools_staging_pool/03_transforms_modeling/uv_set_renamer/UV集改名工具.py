import maya.cmds as cmds

def create_uv_set_renamer():
    # 创建一个窗口
    if cmds.window("renameUVSetsWindow", exists=True):
        cmds.deleteUI("renameUVSetsWindow")

    window = cmds.window("renameUVSetsWindow", title="UV Set Renamer", widthHeight=(300, 200), sizeable=True)

    # 创建一个布局
    main_layout = cmds.columnLayout(adjustableColumn=True)
    
    # 获取当前选中的对象
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("请先选择模型对象。")
        cmds.deleteUI(window, window=True)
        return

    uv_sets = {}  # 使用字典来存储UV集名称和对应的模型列表
    uv_set_inputs = {}

    for obj in selected_objects:
        for uv_set in cmds.polyUVSet(obj, query=True, allUVSets=True):
            if uv_set not in uv_sets:
                uv_sets[uv_set] = [obj]
            else:
                uv_sets[uv_set].append(obj)
        
    for uv_set, obj_list in uv_sets.items():
        # 创建水平布局
        horizontal_layout = cmds.rowLayout(numberOfColumns=2, columnAttach=[(1, 'left', 0), (2, 'both', 0)], columnWidth2=(150, 150))
        # 添加UV集名称，背景颜色填充整个框
        cmds.text(label=uv_set, align="left", backgroundColor=[0.1, 0.1, 0.1], width=150, height=30)
        # 添加新名称输入框
        uv_set_input = cmds.textField()
        
        # 输入框按钮样式
        cmds.textField(uv_set_input, edit=True, backgroundColor=[1, 1, 1], height=30)  # 通过edit参数设置背景颜色
        uv_set_inputs[uv_set] = uv_set_input
        cmds.setParent(main_layout)

    # 执行按钮样式
    cmds.button(label="重命名", height=40, backgroundColor=[0.9, 0.4, 0.4], command=lambda *args: rename_uv_sets(uv_set_inputs, uv_sets))
    # 添加水印文本
    watermark_label = cmds.text(label="<font size='4'>by ZWJ</font>",  height=30, align="right")

    cmds.showWindow(window)

def rename_uv_sets(uv_set_inputs, uv_sets):
    rename_info = []  # 用于存储重命名信息的列表
    for uv_set, input_field in uv_set_inputs.items():
        new_name = cmds.textField(input_field, query=True, text=True)
        if new_name:  # 仅在有输入新名称时才执行重命名
            for obj in uv_sets[uv_set]:
                rename_info.append((obj, uv_set, new_name))  # 添加到重命名信息列表

    # 打印重命名信息
    for obj, uv_set, new_name in rename_info:
        try:
            cmds.polyUVSet(obj, rename=True, uvSet=uv_set, newUVSet=new_name)
            print("模型: {}, 旧UV集: {}, 新名称: {}".format(obj, uv_set, new_name))
        except Exception as e:
            print("重命名失败 - 模型: {}, 旧UV集: {}, 新名称: {}".format(obj, uv_set, new_name))

if __name__ == "__main__":
    create_uv_set_renamer()
