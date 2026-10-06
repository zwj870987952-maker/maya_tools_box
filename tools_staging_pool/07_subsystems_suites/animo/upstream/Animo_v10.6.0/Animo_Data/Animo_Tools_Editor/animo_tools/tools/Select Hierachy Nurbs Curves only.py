import maya.cmds as cmds


def select_hierarchy_nurbs_curves():
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

    curves = []

    for node in hierarchy:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.nodeType(shape) == "nurbsCurve":
                curves.append(node)
                break

    if not curves:
        cmds.inViewMessage(
            msg="No NURBS curves found in the hierarchy",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.select(curves, replace=True)


select_hierarchy_nurbs_curves()