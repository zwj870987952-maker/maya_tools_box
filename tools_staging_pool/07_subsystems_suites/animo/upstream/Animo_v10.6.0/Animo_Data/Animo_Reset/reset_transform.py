import maya.cmds as cmds

def reset_transform():
    selection = cmds.ls(selection=True)
    for obj in selection:
        for attr_name, default in [
            ('translateX', 0), ('translateY', 0), ('translateZ', 0),
            ('rotateX', 0), ('rotateY', 0), ('rotateZ', 0),
            ('scaleX', 1), ('scaleY', 1), ('scaleZ', 1),
        ]:
            attr = '{}.{}'.format(obj, attr_name)
            if cmds.getAttr(attr, lock=True):
                continue
            if cmds.getAttr(attr, settable=True):
                cmds.setAttr(attr, default)

reset_transform()
