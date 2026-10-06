import maya.cmds as cmds

def toggle_geometry():
    panel = cmds.getPanel(withFocus=True)
    
    if panel is None:
        panel = cmds.getPanel(withFocus=True)
        
    if "modelPanel" not in panel:
        panel = cmds.getPanel(withFocus=True)
        
    polygon_mode = cmds.modelEditor(panel, q=True, pm=True)
    
    if polygon_mode:
        cmds.modelEditor(panel, edit=True, pm=False)
        cmds.modelEditor(panel, edit=True, ns=False)
        cmds.modelEditor(panel, edit=True, subdivSurfaces=False)
    else:
        cmds.modelEditor(panel, edit=True, pm=True)
        cmds.modelEditor(panel, edit=True, ns=True)
        cmds.modelEditor(panel, edit=True, subdivSurfaces=True)

toggle_geometry()
