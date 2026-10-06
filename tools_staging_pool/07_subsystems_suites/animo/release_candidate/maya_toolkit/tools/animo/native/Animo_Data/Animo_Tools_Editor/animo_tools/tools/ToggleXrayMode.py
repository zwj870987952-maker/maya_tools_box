import maya.cmds as cmds

def toggle_xray_mode():
    panel = cmds.getPanel(withFocus=True)
    
    if panel is None:
        panel = cmds.getPanel(withFocus=True)
        
    if "modelPanel" not in panel:
        panel = cmds.getPanel(withFocus=True)
    
    xray_mode = cmds.modelEditor(panel, q=True, xray=True)
    
    if xray_mode:
        cmds.modelEditor(panel, e=True, xray=False)
    else:
        cmds.modelEditor(panel, e=True, xray=True)

toggle_xray_mode()
