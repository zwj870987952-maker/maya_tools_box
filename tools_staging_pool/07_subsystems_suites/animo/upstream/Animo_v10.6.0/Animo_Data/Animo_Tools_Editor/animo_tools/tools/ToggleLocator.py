import maya.cmds as cmds

def toggle_locator():
    panel = cmds.getPanel(withFocus=True)
    
    if panel is None:
        panel = cmds.getPanel(withFocus=True)
        
    if "modelPanel" not in panel:
        panel = cmds.getPanel(withFocus=True)
        
    locator_mode = cmds.modelEditor(panel, q=True, locators=True)
    
    if locator_mode:
        cmds.modelEditor(panel, e=True, locators=False)
    else:
        cmds.modelEditor(panel, e=True, locators=True)

toggle_locator()
