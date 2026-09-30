def invoke(**kwargs):
    from maya import cmds
    from .tool import CopyAnimationTool
    result = CopyAnimationTool().run(**kwargs)
    if not result.success:
        cmds.warning(result.message)
    for warning in result.warnings:
        cmds.warning(warning)
    return result


def pairs(ui, all_items=False):
    from .native_ui import _parse_pair
    items = ui._items() if all_items else ui._items_to_process()
    result = []
    for item in items:
        source, target = _parse_pair(item.text())
        result.append({'source': source, 'target': target, 'modes': dict(item.modes)})
    return result


def dispatch(ui, action):
    return invoke(action=action, pairs=pairs(ui))


def save(ui):
    from maya import cmds
    from pathlib import Path
    names = cmds.fileDialog2(dialogStyle=2, fileMode=0, caption='保存动画复制配置', fileFilter='JSON Files (*.json)')
    if not names:
        return
    target = Path(names[0]).resolve()
    overwrite = False
    if target.exists():
        overwrite = cmds.confirmDialog(title='覆盖配置', message=str(target), button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No') == 'Yes'
        if not overwrite:
            return
    return invoke(action='save_config', file_path=str(target), pairs=pairs(ui, True), overwrite_file=overwrite)


def load(ui):
    from maya import cmds
    from .native_ui import CustomListWidgetItem
    names = cmds.fileDialog2(dialogStyle=2, fileMode=1, caption='读取动画复制配置', fileFilter='JSON Files (*.json)')
    if not names:
        return
    result = invoke(action='load_config', file_path=names[0])
    if not result.success:
        return
    ui.record_list.clear()
    for pair in result.data['pairs']:
        item = CustomListWidgetItem(pair['source'] + ' , ' + pair['target'])
        item.modes = dict(pair['modes'])
        ui.record_list.addItem(item)
    ui.record_list.viewport().update()
