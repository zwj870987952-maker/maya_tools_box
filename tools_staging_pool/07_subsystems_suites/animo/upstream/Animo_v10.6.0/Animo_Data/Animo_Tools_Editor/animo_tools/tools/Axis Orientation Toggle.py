import maya.cmds as cmds


def manip_toggle():
    current_ctx = cmds.currentCtx()

    if current_ctx == 'moveSuperContext':
        current_mode = cmds.manipMoveContext('Move', query=True, mode=True)
        if current_mode == 1:
            new_mode = 0
            label = 'Local'
        else:
            new_mode = 1
            label = 'World'
        cmds.manipMoveContext('Move', edit=True, mode=new_mode)
        cmds.inViewMessage(
            msg=label,
            pos='midCenter',
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    if current_ctx == 'RotateSuperContext':
        current_mode = cmds.manipRotateContext('Rotate', query=True, mode=True)
        if current_mode == 0:
            new_mode = 1
            label = 'World'
        elif current_mode == 1:
            new_mode = 2
            label = 'Gimbal'
        else:
            new_mode = 0
            label = 'Local'
        cmds.manipRotateContext('Rotate', edit=True, mode=new_mode)
        cmds.inViewMessage(
            msg=label,
            pos='midCenter',
            fade=True,
            fontSize=14,
            textColor=(0.6, 0.6, 0.6),
            fadeStayTime=800
        )
        return

    cmds.inViewMessage(
        msg='Switch to Move or Rotate tool',
        pos='midCenter',
        fade=True,
        fontSize=14,
        textColor=(0.6, 0.6, 0.6),
        fadeStayTime=800
    )


manip_toggle()