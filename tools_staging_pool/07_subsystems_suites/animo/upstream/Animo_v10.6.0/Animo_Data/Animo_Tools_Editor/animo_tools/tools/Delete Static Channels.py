import maya.cmds as cmds

def delete_static_channels():
    sel = cmds.ls(selection=True)
    if not sel:
        return

    cmds.waitCursor(state=True)

    try:
        anim_curves = cmds.keyframe(sel, query=True, name=True)
        if not anim_curves:
            cmds.waitCursor(state=False)
            return

        for curve in anim_curves:
            if not cmds.objExists(curve):
                continue

            key_values = cmds.keyframe(curve, query=True, valueChange=True)

            if not key_values:
                continue

            if len(key_values) == 1:
                cmds.delete(curve)
                continue

            all_same = all(abs(v - key_values[0]) < 0.0001 for v in key_values)
            if all_same:
                cmds.delete(curve)

    finally:
        cmds.waitCursor(state=False)

delete_static_channels()