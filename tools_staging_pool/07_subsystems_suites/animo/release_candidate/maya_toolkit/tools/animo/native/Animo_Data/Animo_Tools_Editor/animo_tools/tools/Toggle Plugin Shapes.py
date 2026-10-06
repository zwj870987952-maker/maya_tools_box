import maya.cmds as cmds


def toggle_plugin_shapes():
    panel = cmds.getPanel(withFocus=True)

    if not panel or "modelPanel" not in panel:
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            return

    if "modelPanel" in panel:
        if cmds.optionVar(exists="togglePluginShapesState"):
            current_state = cmds.optionVar(query="togglePluginShapesState")
        else:
            current_state = 1

        new_state = 0 if current_state else 1
        cmds.optionVar(intValue=("togglePluginShapesState", new_state))
        cmds.modelEditor(panel, edit=True, pluginShapes=bool(new_state))


toggle_plugin_shapes()
