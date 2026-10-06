import maya.cmds as cmds


def reverse_animation():
    curves = cmds.keyframe(query=True, selected=True, name=True)

    if not curves:
        selection = cmds.ls(selection=True) or []
        curves = []
        for item in selection:
            if cmds.nodeType(item) in ('animCurveTL', 'animCurveTA', 'animCurveTT', 'animCurveTU'):
                curves.append(item)
            else:
                connected = cmds.listConnections(item, type='animCurve') or []
                curves.extend(connected)
        curves = list(set(curves))

    if not curves:
        cmds.inViewMessage(
            msg='Select curves or keys in the Graph Editor',
            pos='midCenter',
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    for curve in curves:
        selected_times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
        all_times = cmds.keyframe(curve, query=True, timeChange=True)

        if not all_times:
            continue

        times = selected_times if selected_times else all_times
        first_time = min(times)
        last_time = max(times)
        pivot = (first_time + last_time) / 2.0

        cmds.scaleKey(
            curve,
            time=(first_time, last_time),
            timePivot=pivot,
            timeScale=-1,
            valuePivot=0,
            valueScale=1
        )

    cmds.inViewMessage(
        msg='Animation Reversed',
        pos='midCenter',
        fade=True,
        fontSize=14,
        textColor=(0.6, 0.6, 0.6),
        fadeStayTime=800
    )


reverse_animation()