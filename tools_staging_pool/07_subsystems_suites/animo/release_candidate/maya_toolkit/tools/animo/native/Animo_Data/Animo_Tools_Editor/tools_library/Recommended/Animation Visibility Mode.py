import maya.cmds as cmds
import maya.mel as mel


def toggle_animation_visibility():
    model_panels = cmds.getPanel(type="modelPanel")
    visibility_on = None

    for panel in model_panels:
        if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
            continue

        nurbs_curves_visible = cmds.modelEditor(panel, q=True, nurbsCurves=True)

        if nurbs_curves_visible:
            visibility_on = False
            cmds.modelEditor(panel, e=True, allObjects=False)
            cmds.modelEditor(panel, e=True, polymeshes=True)
            cmds.modelEditor(panel, e=True, nurbsSurfaces=True)
            cmds.modelEditor(panel, e=True, subdivSurfaces=True)
        else:
            visibility_on = True
            cmds.modelEditor(panel, e=True, allObjects=False)
            cmds.modelEditor(panel, e=True, polymeshes=True)
            cmds.modelEditor(panel, e=True, nurbsSurfaces=True)
            cmds.modelEditor(panel, e=True, nurbsCurves=True)
            cmds.modelEditor(panel, e=True, subdivSurfaces=True)
            cmds.modelEditor(panel, e=True, manipulators=True)
            cmds.modelEditor(panel, e=True, textures=True)
            cmds.modelEditor(panel, e=True, motionTrails=True)
            mel.eval('modelEditor -e -controllers true {0};'.format(panel))

    if visibility_on is not None:
        status = "ON" if visibility_on else "OFF"
        cmds.inViewMessage(
            amg='Animation Visibility <span style="color:#FFFF00;">{0}</span>'.format(status),
            pos='midCenter',
            fade=True,
            fadeStayTime=1200,
            dragKill=True
        )


toggle_animation_visibility()