CAMERAS = 'mtbSS_eb_labs_screenSpace_cameraList'
RIGS = 'mtbSS_eb_labs_screenSpace_rigList'
ORIENTATION = 'mtbSS_ebLabs_sc_orientationChkBox'


def refresh_rigs():
    from maya import cmds
    from . import scene
    if not cmds.textScrollList(RIGS, exists=True):
        return
    cmds.textScrollList(RIGS, edit=True, removeAll=True)
    for _, data in scene.records():
        control = scene.find(data['control_uuid']) if data['control_uuid'] else None
        if data['state'] == 'live' and control and scene.owned(control, data['token']):
            cmds.textScrollList(RIGS, edit=True, append=control)


def dispatch(action):
    from maya import cmds
    from . import scene
    from .tool import ScreenSpaceTool
    if action == 'create':
        cameras = cmds.textScrollList(CAMERAS, query=True, selectItem=True) or []
        result = ScreenSpaceTool().run(action=action, camera=cameras[0] if cameras else '', include_orientation=cmds.checkBox(ORIENTATION, query=True, value=True))
    else:
        controls = cmds.textScrollList(RIGS, query=True, selectItem=True) or []
        identities = {scene.identity(n) for n in controls if cmds.objExists(n)}
        ids = [data['record_uuid'] for _, data in scene.records() if data['control_uuid'] in identities]
        result = ScreenSpaceTool().run(action=action, record_ids=ids)
    if not result.success:
        cmds.warning(result.message + str(result.errors))
    refresh_rigs()
    return result


def quick_undo(action):
    from maya import cmds
    if action == 'undo':
        cmds.undo()
    elif action == 'redo':
        cmds.redo()
    else:
        raise ValueError('未知undo action')
    refresh_rigs()
