import maya.cmds as cmds
import os
import json

# 全局变量，用于存储约束信息
g_constraint_info = []

# 获取默认文件路径（Windows 临时路径）
def get_default_file_path():
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", ""))
    if not temp_dir:
        cmds.warning("无法获取 Windows 临时路径。")
        return ""
    return os.path.join(temp_dir, "constraint_info.json")

# 创建UI窗口
def create_constraint_ui():
    # 如果窗口已存在，则删除
    if cmds.window("constraintWindow", exists=True):
        cmds.deleteUI("constraintWindow")

    # 创建窗口
    window = cmds.window("constraintWindow", title="约束工具", widthHeight=(300, 200))

    # 创建布局
    cmds.columnLayout(adjustableColumn=True)

    # 按钮：查找约束物体
    cmds.button(label="查找约束物体", command="find_constraint_objects()")

    # 按钮：断开约束
    cmds.button(label="断开约束", command="break_constraints()")

    # 按钮：恢复约束
    cmds.button(label="恢复约束", command="restore_constraints()")

    # 按钮：反向约束
    cmds.button(label="反向约束", command="reverse_constraints()")

    # 显示窗口
    cmds.showWindow(window)

# 查找约束物体
def find_constraint_objects():
    global g_constraint_info
    g_constraint_info = []

    # 获取当前选中的节点
    selected_nodes = cmds.ls(selection=True)

    # 检查是否有选中的节点
    if not selected_nodes:
        cmds.warning("请先选中一个约束节点。")
    else:
        for node in selected_nodes:
            # 检查选中的节点是否是约束节点（通过检查节点类型是否包含 "Constraint"）
            node_type = cmds.nodeType(node)
            if "Constraint" in node_type:
                # 获取约束的目标物体（被约束的物体）
                constrained_objects = cmds.listConnections(node + ".constraintParentInverseMatrix", source=True, destination=False)
                if not constrained_objects:
                    constrained_objects = cmds.listConnections(node + ".constraintTranslate", source=True, destination=False)
                if not constrained_objects:
                    constrained_objects = cmds.listConnections(node + ".constraintRotate", source=True, destination=False)

                # 获取约束的驱动物体（约束的物体）
                driver_objects = cmds.listConnections(node + ".target[0].targetParentMatrix", source=True, destination=False)
                if not driver_objects:
                    driver_objects = cmds.listConnections(node + ".target[0].targetTranslate", source=True, destination=False)
                if not driver_objects:
                    driver_objects = cmds.listConnections(node + ".target[0].targetRotate", source=True, destination=False)

                # 如果找到被约束的物体和驱动物体，记录约束信息
                if constrained_objects and driver_objects:
                    constraint_info = {
                        "node": node,
                        "type": node_type,
                        "constrained": constrained_objects[0],  # 假设只有一个被约束物体
                        "drivers": driver_objects  # 可能有多个驱动物体
                    }
                    g_constraint_info.append(constraint_info)

                    # 打印信息
                    print(f"约束节点: {node}")
                    print(f"约束类型: {node_type}")
                    print(f"被约束的物体: {constrained_objects[0]}")
                    print(f"驱动物体: {', '.join(driver_objects)}")
                else:
                    cmds.warning(f"无法找到与约束节点 {node} 相关的物体。")
            else:
                # 忽略非约束节点
                continue

        # 将约束信息保存到文件
        save_constraint_info()

# 保存约束信息到文件
def save_constraint_info():
    global g_constraint_info
    file_path = get_default_file_path()
    if not file_path:
        return

    try:
        with open(file_path, "w") as f:
            json.dump(g_constraint_info, f, indent=4)
        print(f"约束信息已保存到文件: {file_path}")
    except Exception as e:
        cmds.warning(f"保存约束信息失败: {str(e)}")

# 从文件读取约束信息
def load_constraint_info():
    global g_constraint_info
    file_path = get_default_file_path()
    if not file_path:
        return

    try:
        with open(file_path, "r") as f:
            g_constraint_info = json.load(f)
        print(f"约束信息已从文件加载: {file_path}")
    except Exception as e:
        cmds.warning(f"加载约束信息失败: {str(e)}")

# 断开约束
def break_constraints():
    global g_constraint_info
    if not g_constraint_info:
        cmds.warning("请先查找约束物体。")
    else:
        for constraint in g_constraint_info:
            # 删除约束节点
            cmds.delete(constraint["node"])
            print(f"已删除约束节点: {constraint['node']}")

# 恢复约束
def restore_constraints():
    global g_constraint_info
    # 从文件加载约束信息
    load_constraint_info()

    if not g_constraint_info:
        cmds.warning("请先查找约束物体。")
    else:
        for constraint in g_constraint_info:
            # 获取约束信息
            constraint_type = constraint["type"]
            constrained_object = constraint["constrained"]
            driver_objects = constraint["drivers"]

            # 根据约束类型重新创建约束
            if constraint_type == "parentConstraint":
                new_constraint = cmds.parentConstraint(driver_objects, constrained_object, maintainOffset=True)
            elif constraint_type == "pointConstraint":
                new_constraint = cmds.pointConstraint(driver_objects, constrained_object, maintainOffset=True)
            elif constraint_type == "orientConstraint":
                new_constraint = cmds.orientConstraint(driver_objects, constrained_object, maintainOffset=True)
            elif constraint_type == "scaleConstraint":
                new_constraint = cmds.scaleConstraint(driver_objects, constrained_object, maintainOffset=True)
            elif constraint_type == "aimConstraint":
                new_constraint = cmds.aimConstraint(driver_objects, constrained_object, maintainOffset=True)
            else:
                cmds.warning(f"不支持的约束类型: {constraint_type}")
                continue

            print(f"已恢复约束: {new_constraint[0]} (类型: {constraint_type})")

# 反向约束
def reverse_constraints():
    global g_constraint_info
    # 从文件加载约束信息
    load_constraint_info()

    if not g_constraint_info:
        cmds.warning("请先查找约束物体。")
    else:
        for constraint in g_constraint_info:
            # 获取约束信息
            constraint_type = constraint["type"]
            constrained_object = constraint["constrained"]
            driver_objects = constraint["drivers"]

            # 将驱动物体和被约束物体角色互换
            if constraint_type == "parentConstraint":
                new_constraint = cmds.parentConstraint(constrained_object, driver_objects, maintainOffset=True)
            elif constraint_type == "pointConstraint":
                new_constraint = cmds.pointConstraint(constrained_object, driver_objects, maintainOffset=True)
            elif constraint_type == "orientConstraint":
                new_constraint = cmds.orientConstraint(constrained_object, driver_objects, maintainOffset=True)
            elif constraint_type == "scaleConstraint":
                new_constraint = cmds.scaleConstraint(constrained_object, driver_objects, maintainOffset=True)
            elif constraint_type == "aimConstraint":
                new_constraint = cmds.aimConstraint(constrained_object, driver_objects, maintainOffset=True)
            else:
                cmds.warning(f"不支持的约束类型: {constraint_type}")
                continue

            print(f"已创建反向约束: {new_constraint[0]} (类型: {constraint_type})")

# 创建UI窗口
create_constraint_ui()
