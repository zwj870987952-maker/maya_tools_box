from pathlib import Path
import re

_WINDOW = None


def show():
    global _WINDOW
    from .native_ui import CgShake
    if _WINDOW is not None:
        try:
            _WINDOW.close()
        except RuntimeError:
            pass
    _WINDOW = CgShake()
    _WINDOW.show()
    return {'window': 'CgShake 1.5'}


def invoke(**kwargs):
    from maya import cmds
    from .tool import CgShakeTool
    result = CgShakeTool().run(**kwargs)
    if not result.success:
        cmds.warning(result.message)
    return result


def apply(ui):
    from maya import cmds
    from .contracts import CHANNELS
    start, end = cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)
    step = ui.byFrameSpinBox.value()
    frames = range(int(start), int(end + 1), step)
    weights = [cmds.gradientControlNoAttr(ui.range_ctr, query=True, valueAtPoint=(frame - start) / (end + 1 - start)) for frame in frames]
    amounts = {channel: getattr(ui, channel + 'AmountSpinBox').value() for channel in CHANNELS}
    return invoke(action='apply', start=start, end=end, step=step, amounts=amounts, falloff_samples=weights, overwrite=ui.overwriteCheckBox.isChecked(), use_cache=ui.useCacheCheckBox.isChecked())


def cache(ui):
    from maya import cmds
    from maya_toolkit.core.ui_base import QtWidgets
    from .files import default_data_root
    selected = cmds.ls(selection=True) or []
    overwrite = False
    if selected:
        target = default_data_root() / 'cache' / (cmds.ls(selected[0], uuid=True)[0] + '.anim')
        if target.exists() or Path(str(target) + '.json').exists():
            overwrite = QtWidgets.QMessageBox.question(ui, 'Overwrite cache file', str(target), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes
            if not overwrite:
                return
    return invoke(action='cache', overwrite_file=overwrite)


def restore(ui):
    return invoke(action='restore')


def clear(ui):
    return invoke(action='clear', overwrite=True)


def save_preset(ui):
    from maya import cmds
    from maya_toolkit.core.ui_base import QtWidgets
    from .contracts import CHANNELS
    name, accepted = QtWidgets.QInputDialog.getText(ui, 'Preset Name', 'Enter name (letters, digits, underscore)', text='Preset1')
    if not accepted:
        return
    if not re.fullmatch(r'[A-Za-z0-9_\-]+', name):
        cmds.warning('Invalid preset filename')
        return
    target = Path(ui.presetsPath) / (name + '.cgsk')
    overwrite = False
    if target.exists():
        overwrite = QtWidgets.QMessageBox.question(ui, 'Overwrite preset', str(target), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes
        if not overwrite:
            return
    preset = {'Frame': ui.byFrameSpinBox.value(), **{c.upper(): getattr(ui, c + 'AmountSpinBox').value() for c in CHANNELS}, 'Points': cmds.gradientControlNoAttr(ui.range_ctr, query=True, asString=True)}
    result = invoke(action='save_preset', file_path=str(target), preset=preset, overwrite_file=overwrite)
    if result.success:
        ui.populatePresets()


def load_preset(ui, name):
    from maya import cmds
    from .contracts import CHANNELS
    if not name:
        return
    if name == 'Default':
        data = {'Frame': 1, **{c.upper(): 5 for c in CHANNELS}, 'Points': '0,1,3,1,0,3'}
    else:
        result = invoke(action='load_preset', file_path=str(Path(ui.presetsPath) / Path(name).name))
        if not result.success:
            return
        data = result.data['preset']
    ui.byFrameSpinBox.setValue(data['Frame'])
    for channel in CHANNELS:
        getattr(ui, channel + 'AmountSpinBox').setValue(data[channel.upper()])
    cmds.gradientControlNoAttr(ui.range_ctr, edit=True, asString=data['Points'])
