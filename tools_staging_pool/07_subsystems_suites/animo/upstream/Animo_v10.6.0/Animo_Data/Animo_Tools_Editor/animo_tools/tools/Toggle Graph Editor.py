import maya.cmds as cmds

def toggleGraphEditor():
    panel = "graphEditor1Window"
    if cmds.workspaceControl(panel, exists=True):
        isVisible = cmds.workspaceControl(panel, query=True, visible=True)
        cmds.workspaceControl(panel, edit=True, visible=not isVisible)
    else:
        cmds.GraphEditor()

toggleGraphEditor()