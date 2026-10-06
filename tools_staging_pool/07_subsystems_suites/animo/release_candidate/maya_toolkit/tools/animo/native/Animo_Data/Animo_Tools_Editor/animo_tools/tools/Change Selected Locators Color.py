import maya.cmds as cmds


def show_nurbs_curves_in_all_viewports():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            editor = cmds.modelPanel(panel, query=True, modelEditor=True)
            cmds.modelEditor(editor, edit=True, nurbsCurves=True)
            cmds.modelEditor(panel, edit=True, controllers=True)


def turn_off_selection_highlighting():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            cmds.modelEditor(panel, edit=True, selectionHiliteDisplay=False)


def turn_on_selection_highlighting():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            cmds.modelEditor(panel, edit=True, selectionHiliteDisplay=True)


def toggle_selected_color():
    colors = [13, 17, 18, 31, 28, 6, 9, 14, 20, 25]
    selection = cmds.ls(selection=True, type='transform')

    if not selection:
        cmds.warning("Nothing is selected. Select NURBS curves or locators first.")
        return

    valid_objects = []

    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        has_valid_shape = any(cmds.nodeType(shape) in ["nurbsCurve", "locator"] for shape in shapes)
        if has_valid_shape:
            valid_objects.append(obj)

    if not valid_objects:
        cmds.warning("No NURBS curves or locators found in the current selection.")
        return

    show_nurbs_curves_in_all_viewports()
    turn_off_selection_highlighting()

    for obj in valid_objects:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []

        for shape in shapes:
            try:
                use_object_color = cmds.getAttr(shape + ".useObjectColor")
                if use_object_color == 2:
                    cmds.setAttr(shape + ".useObjectColor", 0)
                    cmds.setAttr(shape + ".wireColorRGB", 0, 0, 0, type="double3")
            except Exception:
                pass

        current_color = 0
        try:
            if cmds.getAttr(obj + ".overrideEnabled"):
                current_color = cmds.getAttr(obj + ".overrideColor")
        except Exception:
            pass

        if current_color in colors:
            next_index = (colors.index(current_color) + 1) % len(colors)
        else:
            next_index = 0

        next_color = colors[next_index]

        try:
            cmds.setAttr(obj + ".overrideEnabled", 1)
            cmds.setAttr(obj + ".overrideColor", next_color)
        except Exception:
            pass

    cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", "turn_on_selection_highlighting()"])


toggle_selected_color()