import maya.cmds as cmds


def get_namespace_from_object(obj):
    short_name = obj.split("|")[-1]
    if ":" in short_name:
        return short_name.rsplit(":", 1)[0]
    return ""


def get_selected_namespaces():
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        return []

    namespaces = set()
    for obj in selection:
        if ":" in obj:
            ns = obj.split("|")[-1].rsplit(":", 1)[0]
            namespaces.add(ns)
        else:
            namespaces.add("")

    return list(namespaces)


def find_all_nurbs_curves_in_namespace(namespace):
    all_transforms = cmds.ls(type="transform", long=True)
    nurbs_curves = []

    for transform in all_transforms:
        obj_namespace = get_namespace_from_object(transform)

        if obj_namespace == namespace:
            shapes = cmds.listRelatives(transform, shapes=True, fullPath=True)
            if shapes:
                for shape in shapes:
                    if cmds.nodeType(shape) == "nurbsCurve":
                        nurbs_curves.append(transform)
                        break

    return nurbs_curves


def select_all_ctrls():
    cmds.waitCursor(state=True)

    try:
        original_selection = cmds.ls(selection=True, long=True)

        if not original_selection:
            cmds.inViewMessage(
                msg="Select at least one object first",
                pos="midCenter",
                fade=True,
                fontSize=14,
                textColor=(0.6, 0.6, 0.6),
                fadeStayTime=800
            )
            return

        selected_namespaces = get_selected_namespaces()

        all_curves = []
        for ns in selected_namespaces:
            curves_in_ns = find_all_nurbs_curves_in_namespace(ns)
            all_curves.extend(curves_in_ns)

        if all_curves:
            cmds.select(all_curves, replace=True)
            cmds.select(original_selection, add=True)
        else:
            cmds.inViewMessage(
                msg="No NURBS curves found in the selected namespace(s)",
                pos="midCenter",
                fade=True,
                fontSize=14,
                textColor=(0.6, 0.6, 0.6),
                fadeStayTime=800
            )

    finally:
        cmds.waitCursor(state=False)


select_all_ctrls()