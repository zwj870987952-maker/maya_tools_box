import maya.cmds as cmds

def toggle_imageplanes():
    panel = cmds.getPanel(withFocus=True)
    
    if panel is None:
        panel = cmds.getPanel(withFocus=True)
        
    if "modelPanel" not in panel:
        panel = cmds.getPanel(withFocus=True)
    
    imageplane_mode = cmds.modelEditor(panel, q=True, imagePlane=True)
    
    if imageplane_mode:
        cmds.modelEditor(panel, e=True, imagePlane=False)
    else:
        cmds.modelEditor(panel, e=True, imagePlane=True)

toggle_imageplanes()
