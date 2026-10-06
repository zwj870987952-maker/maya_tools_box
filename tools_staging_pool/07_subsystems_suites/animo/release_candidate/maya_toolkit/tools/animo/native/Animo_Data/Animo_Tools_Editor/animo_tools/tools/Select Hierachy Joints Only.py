import maya.cmds as cmds


def select_hierarchy_joints():
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

    joints = cmds.ls(hierarchy, type="joint", long=True)

    if not joints:
        cmds.inViewMessage(
            msg="No joints found in the hierarchy",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.select(joints, replace=True)


select_hierarchy_joints()