import maya.cmds as cmds

def toggleGraphEditorMinimize():
    panel = "graphEditor1Window"
    if cmds.window(panel, exists=True):
        isIconified = cmds.window(panel, query=True, iconify=True)
        cmds.window(panel, edit=True, iconify=not isIconified)
    else:
        cmds.GraphEditor()

toggleGraphEditorMinimize()