"""Complete original UI routed to the same guarded API; no import-time UI."""
from maya import cmds, mel
from . import runtime
from .tool import ReParentProTool


def dispatch(action):
    flags = {key: cmds.checkBox('rppstg_' + key, query=True, value=True) for key in ('PinCheckBox', 'IKCheckBox', 'ManualCheckBox', 'FreezeCheckBox', 'RelativeCheckBox', 'IKCheckLocalBox')}
    if action == 'starter':
        modes = [mode for key, mode in (('PinCheckBox', 'reparent'), ('IKCheckBox', 'ik'), ('ManualCheckBox', 'manual_start'), ('FreezeCheckBox', 'freeze'), ('RelativeCheckBox', 'relative')) if flags[key]]
        if len(modes) > 1:
            cmds.warning('Choose one mode')
            return
        action = modes[0] if modes else 'reparent'
    p = {'action': action, 'delete_redundant': cmds.menuItem('rppstg_DelRed', query=True, checkBox=True), 'allow_clear_animation': cmds.checkBox('rppstg_allowClear', query=True, value=True)}
    if action in ('reparent', 'manual_go'):
        p['pin'] = flags['PinCheckBox']
    if action == 'ik':
        p['local'] = flags['IKCheckLocalBox']
    if action == 'bake_delete':
        p['bake_on_layer'] = cmds.menuItem('rppstg_onLayerMode', query=True, checkBox=True)
    result = ReParentProTool().run(**p)
    if not result.success:
        cmds.warning(result.message)
    return result


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for complete original panel')
    if cmds.window('rppstg_ReParentPanel', exists=True):
        cmds.showWindow('rppstg_ReParentPanel')
        return 'rppstg_ReParentPanel'
    runtime.resources()
    runtime.load_native()
    mel.eval((runtime.PKG / 'native_ui.mel').read_text(encoding='utf-8'))
    mel.eval('rppstg_showUI();')
    buttons = cmds.lsUI(type='button', long=True) or []
    for button in buttons:
        if button.startswith('rppstg_ReParentPanel|'):
            label = cmds.button(button, query=True, label=True)
            action = {'reParent': 'starter', 'Go': 'manual_go', 'Cancel': 'manual_cancel'}.get(label)
            if action:
                cmds.button(button, edit=True, command=lambda unused=False, value=action: dispatch(value))
    for menu in cmds.lsUI(type='menuItem', long=True) or []:
        if menu.startswith('rppstg_ReParentPanel|') and cmds.menuItem(menu, query=True, label=True) == 'BAKE AND DELETE':
            cmds.menuItem(menu, edit=True, command=lambda unused=False: dispatch('bake_delete'))
    cmds.setParent('rppstg_ReParentPanel')
    cmds.columnLayout(adjustableColumn=True)
    cmds.checkBox('rppstg_allowClear', label='Allow clearing ALL TR keys (backup scene)', value=False)
    cmds.text(label='Layer option applies to final bake only')
    cmds.window('rppstg_ReParentPanel', edit=True, widthHeight=(310, 220))
    return 'rppstg_ReParentPanel'
