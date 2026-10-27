"""Original whole Qt UI connected to the same checked API as non-GUI callers."""
import time
from pathlib import Path
import maya.cmds as cmds
import maya.mel as mel
from maya_toolkit.framework.models import ToolResult
from . import runtime
from .settings import validate_preset

VAR = 'mtkOverslapperCandidateGradient'
WINDOW = 'mtkOverslapperCandidateGradientWindow'


def read_preset(path):
    return runtime.read_preset(path)


def import_error(widget, error):
    return report(widget, ToolResult.fail('预设导入失败', errors=str(error)))


def report(widget, result):
    widget.error_label.setText(result.message + ('\n' + '\n'.join(result.errors) if result.errors else ''))
    widget.error_label.setVisible(True)
    widget.error_height = int(60 * widget.height_scale)
    widget.stiffness_type_changed()
    return result


def action(widget, action, **kwargs):
    return report(widget, runtime.run_api(action=action, **kwargs))


def write_preset(widget, data):
    from .native.overslapper_tool import qt_w
    try:
        validate_preset(data)
    except Exception as error:
        return report(widget, ToolResult.fail('预设导出输入失败', errors=str(error)))
    path, _ = qt_w.QFileDialog.getSaveFileName(widget, 'Save Preset', str(Path.home()), 'JSON Files (*.json)')
    if not path:
        return None
    # Qt save dialog has confirmed replacement if path exists.
    return report(widget, runtime.run_api(action='write_preset', preset_path=path, preset_data=data, overwrite=Path(path).exists()))


def options(widget):
    mode = 'rotation' if widget.overlap_type.currentIndex() == 0 else 'translation'
    time_type = widget.timeline_combo_box.currentIndex()
    if time_type == 0:
        r = [float(widget.timeline_start.text()), float(widget.timeline_end.text())]
    elif time_type == 1:
        r = [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
    else:
        slider = mel.eval('$tmpVar=$gPlayBackSlider')
        sel = cmds.timeControl(slider, q=True, rangeArray=True)
        r = [sel[0], sel[1] - 1]
    if any(v != int(v) for v in r):
        raise ValueError('Integer frame boundaries required')
    axes = ''.join(a for a in 'xyz' if getattr(widget, 'axis_' + a + '_checkbox').isChecked()) if widget.axes_option.isChecked() else 'xyz'
    values = dict(mode=mode, frame_range=[int(v) for v in r], order=widget.selection_combo_box.currentText(), axes=axes,
                  main_axis=widget.main_axis_combo_box.currentText(), up_axis=widget.up_axis_combo_box.currentText(),
                  stiffness=float(widget.stiffness_value.text()), strength=float(widget.strength_value.text()),
                  frame_lag=float(widget.translation_strength_value.text()), cycle=widget.cycle_option.isChecked(),
                  ignore_translation=widget.rotation_translation_option.isChecked(),
                  remove_parent=widget.parent_result.text() if widget.parent_option.isChecked() else None,
                  distance=float(widget.distance_value.text()) if widget.default_distance_option.isChecked() else None,
                  distance_only=widget.default_distance_only_option.isChecked() if widget.default_distance_option.isChecked() else False,
                  animation_type=widget.animation_combo_box.currentText(), new_layer=widget.create_layer_option.isChecked(),
                  override=widget.override_layer.isChecked(), overshoot=widget.overshoot_option.isChecked(),
                  overshoot_first=widget.overshoot_first_option.isChecked(), overshoot_between=widget.overshoot_between_option.isChecked(),
                  overshoot_end=widget.overshoot_end_option.isChecked(), overshoot_strength=float(widget.overshoot_strength_value.text()),
                  overshoot_frequency=int(widget.overshoot_frequency_value.text()), wind=widget.wind_option.isChecked(),
                  wind_strength=float(widget.wind_strength_value.text()), wind_absolute=widget.wind_absolute_option.isChecked())
    if widget.add_to_layer_option.isChecked() and not values['new_layer']:
        layers = [l for l in cmds.ls(type='animLayer') or [] if cmds.animLayer(l, q=True, selected=True) and l != cmds.animLayer(q=True, root=True)]
        if not layers:
            raise ValueError('Select one non-base destination animation layer')
        values['target_layer'] = layers[-1]
    if widget.stiffness_option.isChecked():
        targets = [runtime.node(n) for n in cmds.ls(sl=True, long=True) or []]
        groups = runtime.ordered(targets, values['order'])
        values['stiffness_values'] = [[cmds.gradientControlNoAttr(widget.falloff_curve, q=True, vap=i / float(len(g))) for i in range(len(g))] for g in groups]
    return values


def overlap(widget):
    from .native.overslapper_tool import qt_w, qt_g, qt_c
    if runtime._PROGRESS is not None:
        raise ValueError('Overlap already running')
    owns_cursor = False
    start = time.time()
    try:
        values = options(widget)
        # Original workers are synchronous; no unsafe Qt thread may issue Maya commands.
        widget.progress_bar.setVisible(True)
        widget.progress_bar.setMinimum(0)
        widget.progress_bar.setMaximum(len(cmds.ls(sl=True) or []))
        runtime._PROGRESS = widget.progress_bar_update
        qt_w.QApplication.setOverrideCursor(qt_g.QCursor(qt_c.Qt.BusyCursor))
        owns_cursor = True
        result = runtime.run_api(**values)
        result.message += ' (%.3f s)' % (time.time() - start)
        return report(widget, result)
    except Exception as error:
        return report(widget, ToolResult.fail('Overslapper UI 输入/执行失败', errors=str(error)))
    finally:
        runtime._PROGRESS = None
        widget.progress_bar.setVisible(False)
        if owns_cursor:
            qt_w.QApplication.restoreOverrideCursor()


def cleanup(widget):
    if runtime._WIDGET is not widget:
        return
    runtime._WIDGET = None
    if cmds.optionVar(exists=VAR):
        cmds.optionVar(remove=VAR)
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW, window=True)


def open_close(action, plan):
    if action == 'close_ui':
        if runtime._WIDGET is not None:
            runtime._WIDGET.close()
        return ToolResult.ok('候选窗口已关闭', data=plan, warnings=plan['warnings'])
    if runtime._WIDGET is not None:
        runtime._WIDGET.show()
        runtime._WIDGET.raise_()
        return ToolResult.ok('候选窗口已显示', data=plan, warnings=plan['warnings'])
    if cmds.optionVar(exists=VAR) or cmds.window(WINDOW, exists=True):
        raise ValueError('Private candidate gradient name already exists; close its owner before opening')
    from .native.overslapper_tool import overslapper_UI, qt_c
    try:
        widget = overslapper_UI()
        widget.setObjectName('mtkOverslapperCandidate')
        widget.setAttribute(qt_c.Qt.WA_DeleteOnClose, True)
        runtime._WIDGET = widget
        widget.show()
    except Exception:
        runtime._WIDGET = None
        if cmds.optionVar(exists=VAR):
            cmds.optionVar(remove=VAR)
        if cmds.window(WINDOW, exists=True):
            cmds.deleteUI(WINDOW, window=True)
        raise
    return ToolResult.ok('完整原生 Overslapper 窗口已打开', data=plan, warnings=plan['warnings'])
