import maya.cmds as cmds
import maya.mel as mel
import os
import sys

SAMPLE_BY = 4
MARK_COLOR = "#32CD32"
MARK_OPACITY = 0.25


def load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(folder)
        marker_folder = os.path.join(parent_folder, "Animo_Keys_Tangent")
    except NameError:
        marker_folder = os.path.join(
            cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent"
        )

    if marker_folder not in sys.path:
        sys.path.insert(0, marker_folder)

    mod_name = "mark_frame"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    try:
        import importlib
        return importlib.import_module(mod_name)
    except Exception:
        return None


def get_bake_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    range_visible = cmds.timeControl(playback_slider, query=True, rangeVisible=True)
    if range_visible:
        time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        start = int(time_range[0])
        end = int(time_range[1] - 1)
        if end > start:
            return start, end

    start = int(cmds.playbackOptions(q=True, min=True))
    end = int(cmds.playbackOptions(q=True, max=True))
    return start, end


def clear_marker(marker_module):
    if marker_module:
        try:
            marker_module.trigger_fade(delay=0)
        except Exception:
            pass


def run():
    selection = cmds.ls(sl=True)
    if not selection:
        cmds.inViewMessage(amg='Please select something!', pos='midCenter', fade=True)
        return

    marker_module = load_marker_module()

    start, end = get_bake_range()

    if marker_module:
        try:
            marker_module.mark_range(start, end, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
            cmds.refresh(force=True)
        except Exception:
            pass

    eval_mode = cmds.evaluationManager(q=True, mode=True)

    try:
        cmds.waitCursor(state=True)
        cmds.refresh(suspend=True)
        cmds.evaluationManager(mode="off")

        cb_attrs = cmds.channelBox("mainChannelBox", q=True, sma=True)

        if cb_attrs:
            cmds.bakeResults(
                selection,
                t=(start, end),
                at=cb_attrs,
                sm=True,
                pok=True,
                sb=str(SAMPLE_BY)
            )
        else:
            cmds.bakeResults(
                selection,
                t=(start, end),
                sm=True,
                pok=True,
                sb=str(SAMPLE_BY)
            )

    finally:
        cmds.waitCursor(state=False)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode=eval_mode[0])
        # Only force the main pane back to managed if it actually ended up
        # unmanaged -- unconditionally re-managing it forces a full relayout
        # of Maya's main window, which was pulling other floating Animo/
        # Spacify windows closed along with it even though they have
        # nothing to do with this bake.
        try:
            main_pane = mel.eval('$tmpVar=$gMainPane')
            is_managed = cmds.paneLayout(main_pane, query=True, manage=True)
        except Exception:
            is_managed = True

        if not is_managed:
            mel.eval("paneLayout -e -manage true $gMainPane")
        clear_marker(marker_module)


run()
