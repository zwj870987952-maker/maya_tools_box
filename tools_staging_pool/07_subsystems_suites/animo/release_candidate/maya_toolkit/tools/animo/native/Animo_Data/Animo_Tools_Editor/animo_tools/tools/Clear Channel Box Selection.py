from functools import partial
import maya.cmds as cmds
import maya.mel as mel


def get_channel_box_selection():
    if not cmds.ls(selection=True):
        return

    channel_box = mel.eval("$temp=$gChannelBoxName")

    main_attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True)
    shape_attrs = cmds.channelBox(channel_box, query=True, selectedShapeAttributes=True)
    history_attrs = cmds.channelBox(channel_box, query=True, selectedHistoryAttributes=True)

    channels = []

    if main_attrs:
        channels.extend(main_attrs)
    if shape_attrs:
        channels.extend(shape_attrs)
    if history_attrs:
        channels.extend(history_attrs)

    return channels


def clear_channel_box_selection():
    if not get_channel_box_selection():
        return

    selection = cmds.ls(selection=True)
    cmds.select(clear=True)
    cmds.evalDeferred(partial(cmds.select, selection))


clear_channel_box_selection()