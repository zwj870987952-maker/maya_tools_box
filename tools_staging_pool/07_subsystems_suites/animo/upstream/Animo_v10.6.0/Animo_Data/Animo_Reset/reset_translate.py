import maya.cmds as cmds

def reset_translate():
    selection = cmds.ls(selection=True)
    for obj in selection:
        for axis in ('X', 'Y', 'Z'):
            attr = '{}.translate{}'.format(obj, axis)
            if cmds.getAttr(attr, lock=True):
                continue
            if cmds.getAttr(attr, settable=True):
                cmds.setAttr(attr, 0)

reset_translate()
