# Complete original three proxy functions, explicit actual-name/bake fixes.
import maya.cmds as cmds

def create_joint_and_parent_constraint(selected_transforms, skinning_enabled=False, frame_range=None):
    created_objects = []
    constraints = []
    for i, transform_node in enumerate(selected_transforms):
        cmds.select(clear=True)
        joint_name = '{}_joint'.format(transform_node.split('|')[-1])
        suffix = 1
        while cmds.objExists(joint_name):
            joint_name = '{}_joint{}'.format(transform_node.split('|')[-1], suffix)
            suffix += 1
        joint_name = cmds.joint(name=joint_name, position=(0, 0, 0))
        parent_constraint = cmds.parentConstraint(transform_node, joint_name, maintainOffset=False)[0]
        created_objects.append(joint_name)
        constraints.append(parent_constraint)
        print('Created a joint named {} for the transform node {} and applied a parent constraint without maintaining offset.'.format(joint_name, transform_node))
    if skinning_enabled:
        for transform_node, joint_name, parent_constraint in zip(selected_transforms, created_objects, constraints):
            cmds.select(clear=True)
            cmds.bakeResults(joint_name, simulation=True, time=frame_range)
            cmds.delete(parent_constraint)
            cmds.currentTime(frame_range[0])
            cmds.cutKey(transform_node, clear=True)
            cmds.select([transform_node, joint_name])
            cmds.skinCluster(joint_name, transform_node, toSelectedBones=True, bindMethod=0)
    cmds.select(selected_transforms, replace=True)
    selection_set_name = 'ISS_joint'
    cmds.sets(selected_transforms, name=selection_set_name)
    cmds.select(created_objects, replace=True)
    created_set_name = 'GOS_joint'
    cmds.sets(created_objects, name=created_set_name)
    cmds.select(selected_transforms, replace=True)
    return created_objects

def create_locator_and_parent_constraint(selected_transforms):
    created_objects = []
    for transform_node in selected_transforms:
        locator_name = transform_node.split('|')[-1] + '_locator'
        suffix = 1
        while cmds.objExists(locator_name):
            locator_name = '{}_{}'.format(transform_node.split('|')[-1] + '_locator', suffix)
            suffix += 1
        locator = cmds.spaceLocator(name=locator_name)[0]
        parent_constraint = cmds.parentConstraint(transform_node, locator, maintainOffset=False)[0]
        created_objects.append(locator)
        print('Created a locator named {} for the transform node {} and applied a parent constraint without maintaining offset.'.format(locator, transform_node))
    cmds.select(selected_transforms, replace=True)
    selection_set_name = 'ISS_cube'
    cmds.sets(selected_transforms, name=selection_set_name)
    cmds.select(created_objects, replace=True)
    created_set_name = 'GOS_cube'
    cmds.sets(created_objects, name=created_set_name)
    cmds.select(selected_transforms, replace=True)
    return created_objects

def create_cube_and_parent_constraint(selected_transforms):
    created_objects = []
    for transform_node in selected_transforms:
        cube_name = transform_node.split('|')[-1] + '_cube'
        suffix = 1
        while cmds.objExists(cube_name):
            cube_name = '{}_{}'.format(transform_node.split('|')[-1] + '_cube', suffix)
            suffix += 1
        cube = cmds.polyCube(name=cube_name)[0]
        parent_constraint = cmds.parentConstraint(transform_node, cube, maintainOffset=False)[0]
        created_objects.append(cube)
        print('Created a cube named {} for the transform node {} and applied a parent constraint without maintaining offset.'.format(cube, transform_node))
    cmds.select(selected_transforms, replace=True)
    selection_set_name = 'ISS_cube'
    cmds.sets(selected_transforms, name=selection_set_name)
    cmds.select(created_objects, replace=True)
    created_set_name = 'GOS_cube'
    cmds.sets(created_objects, name=created_set_name)
    cmds.select(selected_transforms, replace=True)
    return created_objects
