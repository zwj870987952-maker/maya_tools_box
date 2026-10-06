import maya.cmds as cmds


def _force_show_locators_in_viewports():
    panels = cmds.getPanel(type="modelPanel") or []
    for panel in panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            try:
                cmds.modelEditor(panel, edit=True, locators=True)
            except Exception:
                pass


def create_locator_at_selection():
    selection = cmds.ls(selection=True, flatten=True)

    if not selection:
        cmds.warning("Nothing is selected. Select an object or components first.")
        return None

    positions = []

    for item in selection:
        pos = None

        if "." in item:
            try:
                pos = cmds.xform(item, query=True, worldSpace=True, translation=True)
            except Exception:
                pos = None
        else:
            try:
                bbox = cmds.exactWorldBoundingBox(item)
                pos = [
                    (bbox[0] + bbox[3]) * 0.5,
                    (bbox[1] + bbox[4]) * 0.5,
                    (bbox[2] + bbox[5]) * 0.5,
                ]
            except Exception:
                try:
                    pos = cmds.xform(item, query=True, worldSpace=True, rotatePivot=True)
                except Exception:
                    pos = None

        if pos and len(pos) >= 3:
            positions.append(pos[:3])

    if not positions:
        cmds.warning("Could not resolve a world position from the current selection.")
        return None

    count = len(positions)
    center_x = sum(p[0] for p in positions) / count
    center_y = sum(p[1] for p in positions) / count
    center_z = sum(p[2] for p in positions) / count

    cmds.undoInfo(openChunk=True)
    try:
        locator = cmds.spaceLocator(name="selection_locator#")[0]
        cmds.xform(locator, worldSpace=True, translation=(center_x, center_y, center_z))
        _force_show_locators_in_viewports()
        cmds.select(locator, replace=True)
    finally:
        cmds.undoInfo(closeChunk=True)

    return locator


def create_locator_at_selection_ui_command(*args):
    create_locator_at_selection()



create_locator_at_selection()