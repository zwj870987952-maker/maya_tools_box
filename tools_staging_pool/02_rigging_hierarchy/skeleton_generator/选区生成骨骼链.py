import maya.cmds as cmds

def duplicate_skeleton_hierarchy(suffix="_copy"):
    """
    复制选中的骨骼链和定位器，创建位置、旋转完全相同的新骨骼链
    新骨骼名称为原骨骼名称或定位器名称加上指定后缀
    保持原有的层级结构
    直接匹配原骨骼或定位器的位置和旋转
    """
    # 获取选中的骨骼和定位器
    selected_joints = cmds.ls(selection=True, type="joint")
    
    # 正确获取定位器的transform节点
    selected_locator_transforms = []
    selected_items = cmds.ls(selection=True)
    
    for item in selected_items:
        shapes = cmds.listRelatives(item, shapes=True, type="locator")
        if shapes:
            selected_locator_transforms.append(item)
    
    # 合并所有选中的对象
    selected_objects = selected_joints + selected_locator_transforms
    
    if not selected_objects:
        cmds.warning("请先选择至少一个骨骼或定位器")
        return
    
    # 创建骨骼映射表 {原对象: 新骨骼}
    object_mapping = {}
    
    # 找出所有选中对象的根对象(没有选中的父级对象)
    root_objects = []
    for obj in selected_objects:
        parent = cmds.listRelatives(obj, parent=True)
        if not parent or parent[0] not in selected_objects:
            root_objects.append(obj)
    
    # 创建所有新骨骼并保持层级关系，但不设置变换
    def create_joint_hierarchy(obj, parent=None):
        # 创建新骨骼
        if parent:
            cmds.select(parent)
        else:
            cmds.select(clear=True)
        
        new_joint = cmds.joint(name=f"{obj}{suffix}")
        
        # 添加到映射表
        object_mapping[obj] = new_joint
        
        # 创建子骨骼
        children = cmds.listRelatives(obj, children=True)
        if children:
            for child in children:
                # 只处理骨骼和定位器的transform节点
                child_shapes = cmds.listRelatives(child, shapes=True)
                is_locator = child_shapes and any(cmds.objectType(shape) == "locator" for shape in child_shapes)
                
                if cmds.objectType(child) == "joint" or is_locator:
                    if child in selected_objects:
                        create_joint_hierarchy(child, new_joint)
        
        return new_joint
    
    # 首先创建骨骼层级结构
    for root in root_objects:
        create_joint_hierarchy(root)
    
    # 然后匹配每个骨骼的位置和旋转
    for original_obj, new_joint in object_mapping.items():
        # 只匹配位置和旋转，不匹配缩放
        cmds.matchTransform(new_joint, original_obj, position=True, rotation=True, scale=False)
        
        # 复制其他属性
        if cmds.objectType(original_obj) == "joint":
            cmds.setAttr(f"{new_joint}.radius", cmds.getAttr(f"{original_obj}.radius"))
            cmds.setAttr(f"{new_joint}.drawStyle", cmds.getAttr(f"{original_obj}.drawStyle"))
    
    # 选择所有新创建的骨骼
    cmds.select(list(object_mapping.values()))
    
    print("骨骼复制完成。共复制了 {} 个对象。".format(len(object_mapping)))
    return object_mapping

# 执行函数
duplicate_skeleton_hierarchy(suffix="_copy")
