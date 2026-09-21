############骨骼蒙皮模式下，模型之间不能带父子关系，不然会因为maya默认的蒙皮逻辑，破坏父子模型的运动状态###############

import maya.cmds as cmds

def create_joint_and_parent_constraint(selected_transforms, skinning_enabled=False):
    created_objects = []
    for i, transform_node in enumerate(selected_transforms):
        cmds.select(clear=True)
        joint_name = "{}_joint".format(transform_node.split("|")[-1])

        suffix = 1
        while cmds.objExists(joint_name):
            joint_name = "{}_joint{}".format(transform_node.split("|")[-1], suffix)
            suffix += 1

        joint_name = cmds.joint(name=joint_name, position=(0, 0, 0))
        parent_constraint = cmds.parentConstraint(transform_node, joint_name, maintainOffset=False)[0]

        created_objects.append(joint_name)

        print("Created a joint named {} for the transform node {} and applied a parent constraint without maintaining offset.".format(joint_name, transform_node))

    if skinning_enabled:
        for transform_node in selected_transforms:
            cmds.select(clear=True)
            joint_name = "{}_joint".format(transform_node.split("|")[-1])
            # Bake animation on the created joints
            cmds.bakeResults(joint_name, simulation=True, time=(cmds.playbackOptions(query=True, min=True), cmds.playbackOptions(query=True, max=True)))            
            cmds.cutKey(transform_node, clear=True)  # 删除物体的所有动画
            cmds.select([transform_node, joint_name])
            cmds.skinCluster(toSelectedBones=True, bindMethod=0)
                        
    # 修改部分：在选择集名称后添加_类型后缀
    cmds.select(selected_transforms, replace=True)
    selection_set_name = "ISS_joint"
    cmds.sets(selected_transforms, name=selection_set_name)

    cmds.select(created_objects, replace=True)
    created_set_name = "GOS_joint"
    cmds.sets(created_objects, name=created_set_name)
    cmds.select(selected_transforms, replace=True)

def create_locator_and_parent_constraint(selected_transforms):
    created_objects = []
    for transform_node in selected_transforms:
        locator_name = transform_node.split("|")[-1] + "_locator"

        suffix = 1
        while cmds.objExists(locator_name):
            locator_name = "{}_{}".format(transform_node.split("|")[-1] + "_locator", suffix)
            suffix += 1

        locator = cmds.spaceLocator(name=locator_name)[0]
        parent_constraint = cmds.parentConstraint(transform_node, locator, maintainOffset=False)[0]

        created_objects.append(locator)

        print("Created a locator named {} for the transform node {} and applied a parent constraint without maintaining offset.".format(locator, transform_node))

    # 修改部分：在选择集名称后添加_类型后缀
    cmds.select(selected_transforms, replace=True)
    selection_set_name = "ISS_cube"
    cmds.sets(selected_transforms, name=selection_set_name)

    cmds.select(created_objects, replace=True)
    created_set_name = "GOS_cube"
    cmds.sets(created_objects, name=created_set_name)


    cmds.select(selected_transforms, replace=True)

def create_cube_and_parent_constraint(selected_transforms):
    created_objects = []
    for transform_node in selected_transforms:
        cube_name = transform_node.split("|")[-1] + "_cube"

        suffix = 1
        while cmds.objExists(cube_name):
            cube_name = "{}_{}".format(transform_node.split("|")[-1] + "_cube", suffix)
            suffix += 1

        cube = cmds.polyCube(name=cube_name)[0]
        parent_constraint = cmds.parentConstraint(transform_node, cube, maintainOffset=False)[0]

        created_objects.append(cube)

        print("Created a cube named {} for the transform node {} and applied a parent constraint without maintaining offset.".format(cube, transform_node))

    # 修改部分：在选择集名称后添加_类型后缀
    cmds.select(selected_transforms, replace=True)
    selection_set_name = "ISS_cube"
    cmds.sets(selected_transforms, name=selection_set_name)

    cmds.select(created_objects, replace=True)
    created_set_name = "GOS_cube"
    cmds.sets(created_objects, name=created_set_name)

    cmds.select(selected_transforms, replace=True)

class CreateObjectsUI:
    def __init__(self):
        self.window_name = "CreateObjectsWindow"
    
    def create_window(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        cmds.window(self.window_name, title="Create Objects", widthHeight=(300, 150), toolbox=True)
        cmds.columnLayout(adjustableColumn=True, columnAlign="center")
        
        cmds.text(label="Select an object type to create:")
        self.object_type_option_menu = cmds.optionMenu()
        cmds.menuItem(label="Joint")
        cmds.menuItem(label="Locator")
        cmds.menuItem(label="Cube")
        
        cmds.checkBox("SkinningCheckBox", label="Skinning")
        
        cmds.button(label="Create", command=self.create_objects)
        
        cmds.showWindow(self.window_name)
    
    def create_objects(self, *args):
        selected_index = cmds.optionMenu(self.object_type_option_menu, query=True, select=True)
        selected_transforms = cmds.ls(selection=True, dag=True, long=True, type='transform')
        
        if not selected_transforms:
            cmds.warning("Please select at least one transform node.")
            return
        
        skinning_enabled = cmds.checkBox("SkinningCheckBox", query=True, value=True)
        
        if selected_index == 1:
            create_joint_and_parent_constraint(selected_transforms, skinning_enabled)
        elif selected_index == 2:
            create_locator_and_parent_constraint(selected_transforms)
        elif selected_index == 3:
            create_cube_and_parent_constraint(selected_transforms)



# Create UI and show window
ui = CreateObjectsUI()
ui.create_window()