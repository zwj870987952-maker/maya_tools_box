import maya.cmds as cmds

def set_global_tangents():

    cmds.keyTangent(g=True, itt='linear', ott='linear')

set_global_tangents()