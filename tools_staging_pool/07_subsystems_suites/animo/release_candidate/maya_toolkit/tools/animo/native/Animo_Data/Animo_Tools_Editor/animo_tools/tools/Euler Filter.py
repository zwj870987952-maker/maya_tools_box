import maya.cmds as cmds

def apply_euler_filter():
    objs = cmds.ls(selection=True)
    curves = []
    if objs:
        for obj in objs:
            for axis in ('X', 'Y', 'Z'):
                anim = cmds.keyframe(obj + '.rotate' + axis, query=True, name=True)
                if anim:
                    curves.extend(anim)
    if not curves:
        curves = cmds.keyframe(query=True, name=True)

    selected_keys = cmds.keyframe(query=True, selected=True, name=True)
    key_times = {}
    if selected_keys:
        for curve in set(selected_keys):
            times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
            if times:
                key_times[curve] = times

    if curves:
        cmds.filterCurve(curves)

    try:
        cmds.selectKey(clear=True)
    except:
        pass

    if key_times:
        for curve, times in key_times.items():
            for t in times:
                cmds.selectKey(curve, add=True, time=(t, t))

apply_euler_filter()