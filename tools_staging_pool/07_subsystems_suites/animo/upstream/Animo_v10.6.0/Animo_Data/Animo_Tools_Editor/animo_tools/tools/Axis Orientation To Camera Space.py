import maya.cmds as cmds


def manip_camera_mode():
    current_ctx = cmds.currentCtx()

    if current_ctx not in ("moveSuperContext", "RotateSuperContext"):
        cmds.inViewMessage(
            msg="Switch to Move or Rotate tool",
            pos="midCenter",
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    panel = cmds.getPanel(underPointer=True)

    if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
        panel = cmds.getPanel(withFocus=True)

    if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            cmds.inViewMessage(
                msg="No viewport found",
                pos="midCenter",
                fade=True,
                fontSize=14,
                textColor=(0.6, 0.6, 0.6),
                fadeStayTime=800
            )
            return

    camera = cmds.modelPanel(panel, query=True, camera=True)

    if cmds.nodeType(camera) == "camera":
        camera = cmds.listRelatives(camera, parent=True, fullPath=True)[0]

    if current_ctx == "moveSuperContext":
        cmds.manipMoveContext("Move", edit=True, mode=6, orientObject=camera)
    else:
        cmds.manipRotateContext("Rotate", edit=True, mode=3, orientObject=camera)

    cmds.inViewMessage(
        msg="Camera",
        pos="midCenter",
        fade=True,
        fontSize=14,
        textColor=(0.6, 0.6, 0.6),
        fadeStayTime=800
    )


manip_camera_mode()