import maya.cmds as cmds


def select_all_anim_curves():
    anim_curves = cmds.ls(type=[
        "animCurveTL",
        "animCurveTA",
        "animCurveTT",
        "animCurveTU",
        "animCurveUL",
        "animCurveUA",
        "animCurveUT",
        "animCurveUU"
    ])

    if not anim_curves:
        cmds.inViewMessage(
            msg="No animated objects found in the scene",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    objects = []

    for curve in anim_curves:
        connections = cmds.listConnections(curve, source=False, destination=True) or []
        objects.extend(connections)

    objects = list(set(objects))

    if not objects:
        cmds.inViewMessage(
            msg="No animated objects found in the scene",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.select(objects, replace=True)


select_all_anim_curves()