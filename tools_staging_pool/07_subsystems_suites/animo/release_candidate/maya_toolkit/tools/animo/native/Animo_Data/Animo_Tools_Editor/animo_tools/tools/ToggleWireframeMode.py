import maya.cmds as cmds

def toggle_wireframe_mode():
    panel = cmds.getPanel(withFocus=True)
    if not cmds.modelEditor(panel, query=True, exists=True):
        return

    polys_on = cmds.modelEditor(panel, query=True, polymeshes=True)

    if not polys_on:
        cmds.modelEditor(panel, edit=True, polymeshes=True)
        cmds.modelEditor(panel, edit=True, nurbsSurfaces=True)
        return

    is_wireframe = cmds.modelEditor(panel, query=True, displayAppearance=True) == 'wireframe'

    if is_wireframe:
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', wireframeOnShaded=False)
        cmds.modelEditor(panel, edit=True, displayTextures=True)
    else:
        cmds.modelEditor(panel, edit=True, displayAppearance='wireframe')

toggle_wireframe_mode()
