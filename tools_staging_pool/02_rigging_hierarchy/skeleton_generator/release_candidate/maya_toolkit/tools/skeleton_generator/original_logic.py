import maya.cmds as cmds

def duplicate_skeleton_hierarchy(suffix='_copy'):
    """
    复制选中的骨骼链和定位器，创建位置、旋转完全相同的新骨骼链
    新骨骼名称为原骨骼名称或定位器名称加上指定后缀
    保持原有的层级结构
    直接匹配原骨骼或定位器的位置和旋转
    """
    selected_joints = cmds.ls(selection=True, type='joint')
    selected_locator_transforms = []
    selected_items = cmds.ls(selection=True)
    for item in selected_items:
        shapes = cmds.listRelatives(item, shapes=True, type='locator')
        if shapes:
            selected_locator_transforms.append(item)
    selected_objects = selected_joints + selected_locator_transforms
    if not selected_objects:
        cmds.warning('请先选择至少一个骨骼或定位器')
        return
    object_mapping = {}
    root_objects = []
    for obj in selected_objects:
        parent = cmds.listRelatives(obj, parent=True)
        if not parent or parent[0] not in selected_objects:
            root_objects.append(obj)

    def create_joint_hierarchy(obj, parent=None):
        if parent:
            cmds.select(parent)
        else:
            cmds.select(clear=True)
        new_joint = cmds.joint(name=f'{obj}{suffix}')
        object_mapping[obj] = new_joint
        children = cmds.listRelatives(obj, children=True)
        if children:
            for child in children:
                child_shapes = cmds.listRelatives(child, shapes=True)
                is_locator = child_shapes and any((cmds.objectType(shape) == 'locator' for shape in child_shapes))
                if cmds.objectType(child) == 'joint' or is_locator:
                    if child in selected_objects:
                        create_joint_hierarchy(child, new_joint)
        return new_joint
    for root in root_objects:
        create_joint_hierarchy(root)
    for original_obj, new_joint in object_mapping.items():
        cmds.matchTransform(new_joint, original_obj, position=True, rotation=True, scale=False)
        if cmds.objectType(original_obj) == 'joint':
            cmds.setAttr(f'{new_joint}.radius', cmds.getAttr(f'{original_obj}.radius'))
            cmds.setAttr(f'{new_joint}.drawStyle', cmds.getAttr(f'{original_obj}.drawStyle'))
    cmds.select(list(object_mapping.values()))
    print('骨骼复制完成。共复制了 {} 个对象。'.format(len(object_mapping)))
    return object_mapping
