import maya.cmds as cmds

def set_global_tangents():

    cmds.keyTangent(g=True, itt='auto', ott='auto')

set_global_tangents()