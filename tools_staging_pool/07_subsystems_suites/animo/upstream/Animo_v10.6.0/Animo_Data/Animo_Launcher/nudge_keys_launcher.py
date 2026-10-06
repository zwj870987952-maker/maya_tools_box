import json
import os

import maya.cmds as cmds
import maya.OpenMayaUI as omui

try:
    from PySide2 import QtGui, QtWidgets
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtGui, QtWidgets
    from shiboken6 import wrapInstance


WINDOW_NAME = "keyShiftToolUI"
PREFS_FILE_NAME = "nudge_keys_prefs.json"
DEFAULT_AMOUNT = 1.0
CURSOR_OFFSET_X = 0
CURSOR_OFFSET_Y = 0


def get_animo_data_path():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(script_dir, ".."))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data")


def get_prefs_path():
    animo_data = get_animo_data_path()
    prefs_dir = os.path.join(animo_data, "Animo_Prefs")
    if not os.path.exists(prefs_dir):
        try:
            os.makedirs(prefs_dir)
        except:
            pass
    return prefs_dir


def get_prefs_file():
    return os.path.join(get_prefs_path(), PREFS_FILE_NAME)


def load_last_amount():
    prefs_file = get_prefs_file()
    try:
        with open(prefs_file, "r") as f:
            data = json.load(f)
        amount = float(data.get("amount", DEFAULT_AMOUNT))
        if amount <= 0:
            return DEFAULT_AMOUNT
        return amount
    except:
        return DEFAULT_AMOUNT


def save_last_amount(amount):
    prefs_file = get_prefs_file()
    try:
        with open(prefs_file, "w") as f:
            json.dump({"amount": amount}, f)
    except:
        pass


def save_current_amount():
    try:
        amount = cmds.floatField(
            "keyShiftAmountField",
            q=True,
            value=True
        )
    except:
        return
    save_last_amount(amount)


def get_channelbox_attributes():
    channel_box = "mainChannelBox"
    attrs = []

    for flag in ("sma", "ssa", "sha", "soa"):
        try:
            result = cmds.channelBox(
                channel_box,
                q=True,
                **{flag: True}
            )
            if result:
                attrs.extend(result)
        except:
            pass

    return list(set(attrs))


def get_graph_editor_selected_keys():
    curves = cmds.keyframe(
        q=True,
        selected=True,
        name=True
    ) or []

    result = []

    for curve in set(curves):
        times = cmds.keyframe(
            curve,
            q=True,
            selected=True,
            timeChange=True
        ) or []

        for time in times:
            result.append((curve, time))

    return result


def show_message(message):
    try:
        cmds.inViewMessage(
            amg=message,
            pos="midCenter",
            fade=True,
            fadeStayTime=2000,
            fadeOutTime=500
        )
    except:
        pass


def has_collision(curve, source_time, target_time, moving_times):
    tolerance = 0.0001

    existing_times = cmds.keyframe(
        curve,
        q=True,
        time=(target_time, target_time),
        timeChange=True
    ) or []

    for existing_time in existing_times:
        if abs(existing_time - target_time) < tolerance:
            if not any(
                abs(existing_time - moving_time) < tolerance
                for moving_time in moving_times
            ):
                return True

    return False


def get_safe_move_order(times, amount):
    if amount > 0:
        return sorted(times, reverse=True)
    return sorted(times)


def shift_graph_editor_keys(amount):
    selected_keys = get_graph_editor_selected_keys()

    if not selected_keys:
        return False

    curve_keys = {}

    for curve, time in selected_keys:
        curve_keys.setdefault(curve, []).append(time)

    for curve, times in curve_keys.items():
        for time in times:
            target_time = time + amount

            if has_collision(
                curve,
                time,
                target_time,
                times
            ):
                show_message(
                    "Cannot shift keys: another key is in the way."
                )
                return False

    for curve, times in curve_keys.items():
        move_order = get_safe_move_order(times, amount)
        for time in move_order:
            try:
                cmds.keyframe(
                    curve,
                    e=True,
                    time=(time, time),
                    timeChange=time + amount
                )
            except:
                show_message(
                    "Cannot move keys: blocked by another keyframe."
                )
                return False

    return True


def get_timeline_range():
    try:
        slider = cmds.timeControl(
            "timeControl1",
            q=True,
            rangeArray=True
        )

        if slider and slider[1] > slider[0]:
            return slider[0], slider[1] - 1

    except:
        pass

    return (
        cmds.playbackOptions(q=True, min=True),
        cmds.playbackOptions(q=True, max=True)
    )


def get_animation_curves():
    curves = []
    objects = cmds.ls(selection=True) or []

    if not objects:
        return []

    attrs = get_channelbox_attributes()

    if attrs:
        for obj in objects:
            for attr in attrs:
                plug = "{}.{}".format(obj, attr)

                if not cmds.objExists(plug):
                    continue

                connected = cmds.listConnections(
                    plug,
                    type="animCurve"
                ) or []

                curves.extend(connected)

    else:
        connected = cmds.listConnections(
            objects,
            type="animCurve"
        ) or []

        curves.extend(connected)

    return list(set(curves))


def get_timeline_keys():
    start, end = get_timeline_range()
    curves = get_animation_curves()

    result = {}

    for curve in curves:
        times = cmds.keyframe(
            curve,
            q=True,
            time=(start, end),
            timeChange=True
        ) or []

        if times:
            result[curve] = times

    return result


def shift_timeline_keys(amount):
    curve_keys = get_timeline_keys()

    if not curve_keys:
        show_message("No keys found in the selected range.")
        return False

    for curve, times in curve_keys.items():
        for time in times:
            target_time = time + amount

            if has_collision(
                curve,
                time,
                target_time,
                times
            ):
                show_message(
                    "Cannot shift keys: another key is in the way."
                )
                return False

    for curve, times in curve_keys.items():
        move_order = get_safe_move_order(times, amount)
        for time in move_order:
            try:
                cmds.keyframe(
                    curve,
                    e=True,
                    time=(time, time),
                    timeChange=time + amount
                )
            except:
                show_message(
                    "Cannot move keys: blocked by another keyframe."
                )
                return False

    return True


def shift_keys(direction):
    try:
        amount = cmds.floatField(
            "keyShiftAmountField",
            q=True,
            value=True
        )
    except:
        show_message("Enter a valid number.")
        return

    if amount == 0:
        return

    amount *= direction

    cmds.waitCursor(state=True)

    try:
        current_time = cmds.currentTime(q=True)

        graph_keys = get_graph_editor_selected_keys()

        if graph_keys:
            shift_graph_editor_keys(amount)
            cmds.refresh()
            return

        curves = get_animation_curves()

        if not curves:
            show_message("No animation curves found.")
            return

        current_time_is_key = False

        for curve in curves:
            keys = cmds.keyframe(
                curve,
                q=True,
                time=(current_time, current_time),
                timeChange=True
            ) or []

            if keys:
                current_time_is_key = True
                break

        moved = shift_timeline_keys(amount)

        if moved and current_time_is_key:
            cmds.currentTime(
                current_time + amount,
                edit=True
            )

        cmds.refresh()
    finally:
        cmds.waitCursor(state=False)


def create_key_shift_ui():
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(
        WINDOW_NAME,
        title="Key Shift",
        sizeable=False,
        minimizeButton=False,
        maximizeButton=False,
        retain=False,
        closeCommand=lambda: save_current_amount()
    )

    cmds.columnLayout(
        adjustableColumn=True,
        rowSpacing=3
    )

    cmds.rowLayout(
        numberOfColumns=3,
        columnWidth3=(70, 45, 45),
        columnAttach3=(
            "both",
            "both",
            "both"
        ),
        columnOffset3=(
            3,
            2,
            3
        )
    )

    cmds.floatField(
        "keyShiftAmountField",
        value=load_last_amount(),
        precision=2,
        minValue=0.001,
        changeCommand=lambda *_: save_current_amount()
    )

    cmds.button(
        label="<--",
        height=26,
        command=lambda *_: shift_keys(-1)
    )

    cmds.button(
        label="-->",
        height=26,
        command=lambda *_: shift_keys(1)
    )

    cmds.setParent("..")

    cmds.showWindow(WINDOW_NAME)

    try:
        cursor_pos = QtGui.QCursor.pos()
        ptr = omui.MQtUtil.findWindow(WINDOW_NAME)
        if ptr is not None:
            widget = wrapInstance(int(ptr), QtWidgets.QWidget)
            target_x = cursor_pos.x() - (widget.width() // 2) - CURSOR_OFFSET_X
            target_y = cursor_pos.y() - (widget.height() // 2) - CURSOR_OFFSET_Y
            widget.move(target_x, target_y)
    except:
        pass


create_key_shift_ui()