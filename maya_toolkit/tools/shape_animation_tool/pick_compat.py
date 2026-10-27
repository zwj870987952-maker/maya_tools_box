"""The two actual PyMel operations in the full original ray picker, using cmds."""
import maya.cmds as cmds


class PyNode(str):
    def isIntermediate(self):
        return bool(cmds.getAttr(self+'.intermediateObject'))

    def isVisible(self):
        path = (cmds.ls(self, long=True) or [self])[0]
        while path:
            for attr in ('visibility', 'lodVisibility'):
                if cmds.attributeQuery(attr, node=path, exists=True) and not cmds.getAttr(path+'.'+attr):
                    return False
            parents = cmds.listRelatives(path, parent=True, fullPath=True) or []
            path = parents[0] if parents else ''
        return True


def select(node):
    cmds.select(str(node), replace=True)
