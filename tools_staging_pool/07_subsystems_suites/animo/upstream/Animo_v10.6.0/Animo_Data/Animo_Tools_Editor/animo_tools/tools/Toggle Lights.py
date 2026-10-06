import maya.cmds as cmds


def toggle_lights():
    panel = cmds.getPanel(withFocus=True)

    if not panel or "modelPanel" not in panel:
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            return

    if "modelPanel" in panel:
        current_state = cmds.modelEditor(panel, query=True, lights=True)
        cmds.modelEditor(panel, edit=True, lights=(not current_state))


toggle_lights()
