import maya.cmds as cmds


def select_by_selected_keys():
    curves = cmds.keyframe(query=True, selected=True, name=True)

    if not curves:
        cmds.inViewMessage(
            msg="Select keys in the Graph Editor first",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    objects = []

    for curve in curves:
        connections = cmds.listConnections(curve, source=False, destination=True) or []
        objects.extend(connections)

    objects = list(set(objects))

    if not objects:
        cmds.inViewMessage(
            msg="No objects found for the selected keys",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.select(objects, replace=True)


select_by_selected_keys()