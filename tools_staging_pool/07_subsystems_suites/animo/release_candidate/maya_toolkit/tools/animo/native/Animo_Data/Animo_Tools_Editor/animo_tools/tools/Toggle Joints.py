import maya.cmds as cmds


def toggle_joints():
    panel = cmds.getPanel(withFocus=True)

    if not panel or "modelPanel" not in panel:
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            return

    if "modelPanel" in panel:
        current_state = cmds.modelEditor(panel, query=True, joints=True)
        cmds.modelEditor(panel, edit=True, joints=(not current_state))


toggle_joints()
