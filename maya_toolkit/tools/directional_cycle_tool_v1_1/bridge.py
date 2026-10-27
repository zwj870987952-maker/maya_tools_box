_WINDOW = None


def dispatch(window, direction):
    from maya import cmds
    from .tool import DirectionalCycleTool
    result = DirectionalCycleTool().run(action='run', direction=direction, controllers=window.SavedController or [], feet_number=window.SpinBox_FeetNumber.value(), angle=window.SpinBox_RotationValue.value(), bake=window.Check_Bake.isChecked(), correction_locators=True, counter_rotation=window.Check_CounterRotation.isChecked())
    if not result.success:
        cmds.warning(result.message + str(result.errors))
    elif result.data:
        print(result.data)
    return result


def show_window():
    global _WINDOW
    from maya_toolkit.core.ui_base import get_maya_main_window
    from .native_ui import UISetup_DirCycleTool
    if _WINDOW is not None:
        try:
            _WINDOW.close()
            _WINDOW.deleteLater()
        except RuntimeError:
            pass
    _WINDOW = UISetup_DirCycleTool(parent=get_maya_main_window())
    _WINDOW.show(dockable=True)
    return _WINDOW
