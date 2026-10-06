import maya.cmds as cmds


def toggle_ctrls():
    panel = cmds.getPanel(withFocus=True)

    if not panel or "modelPanel" not in panel:
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            return

    if "modelPanel" in panel:
        nurbs_visible = cmds.modelEditor(panel, query=True, nurbsCurves=True)

        if nurbs_visible:
            cmds.modelEditor(panel, edit=True, nurbsCurves=False)
            cmds.modelEditor(panel, edit=True, controlVertices=True)
            cmds.modelEditor(panel, edit=True, controllers=False)
        else:
            cmds.modelEditor(panel, edit=True, nurbsCurves=True)
            cmds.modelEditor(panel, edit=True, controlVertices=True)
            cmds.modelEditor(panel, edit=True, controllers=True)


toggle_ctrls()
