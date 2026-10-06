import maya.cmds as cmds


def select_hierarchy():
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        return

    hierarchy = []

    for obj in selection:
        hierarchy.append(obj)
        children = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
        hierarchy.extend(children)

    cmds.select(hierarchy, replace=True)


select_hierarchy()