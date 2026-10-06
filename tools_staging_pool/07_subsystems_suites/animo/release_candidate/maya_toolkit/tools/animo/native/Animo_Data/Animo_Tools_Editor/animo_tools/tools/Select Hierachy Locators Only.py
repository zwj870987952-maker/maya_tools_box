import maya.cmds as cmds


def select_hierarchy_locators():
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        cmds.inViewMessage(
            msg="Select an object first",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    hierarchy = []

    for obj in selection:
        hierarchy.append(obj)
        children = cmds.listRelatives(obj, allDescendents=True, fullPath=True) or []
        hierarchy.extend(children)

    locators = []

    for node in hierarchy:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.nodeType(shape) == "locator":
                locators.append(node)
                break

    if not locators:
        cmds.inViewMessage(
            msg="No locators found in the hierarchy",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.select(locators, replace=True)


select_hierarchy_locators()