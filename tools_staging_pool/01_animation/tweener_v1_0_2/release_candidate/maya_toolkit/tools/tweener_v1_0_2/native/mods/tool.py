# Modified complete source port, 2026-10-01. Morten Andersen / original GPL LICENSE preserved.
from maya_toolkit.tools.tweener_v1_0_2 import runtime
"""
Tool

- Allows Tweener to be used as a Maya tool using mouse drag.
- The tool can also be assigned a hotkey using the tweenerTool command.
"""

import maya.cmds as cmds

from . import globals as g
from . import options as options
from . import tween as tween
from . import utils as utils

tool = None


def reset():
    """
    Checks for existing tool contexts and initializes a new Tool object.
    """
    if cmds.draggerContext('stagingTweenerToolContext', q=True, exists=True):
        cmds.deleteUI('stagingTweenerToolContext')


def activate():
    """
    Activates the Tweener Tool in Maya.
    """
    global tool
    if tool is None:
        tool = Tool()

    cmds.setToolTo('stagingTweenerToolContext')


class Tool:
    """
    Creates a dragger context in Maya with the required functions.
    """

    def __init__(self):
        """
        Initializes the instance variables and sets up the dragger context.
        """
        self.press_position = [0, 0, 0]
        self.drag_position = [0, 0, 0]

        self.interpolation_mode = options.load_interpolation_mode()
        self.overshoot = options.load_overshoot()
        self.live_preview = options.load_live_preview()

        if not g.plugin_path:
            g.refresh_plug_in_path()

        icon_path = g.plugin_path + '/icons/tweener-icon.png'

        cmds.draggerContext('stagingTweenerToolContext',
                            name='tweenerTool',
                            pressCommand=self.press,
                            dragCommand=self.drag,
                            releaseCommand=self.release,
                            finalize=self.finalize,
                            space='screen',
                            image1=icon_path,
                            undoMode='step')

    def press(self):
        """
        Dragger context press event handler.

        Gets the initial position and reads in the available options. An
        initial interpolation is also performed.
        """
        self.press_position = cmds.draggerContext('stagingTweenerToolContext',
                                                  q=True,
                                                  anchorPoint=True)
        self.drag_position = list(self.press_position)
        self.interpolation_mode = options.load_interpolation_mode()
        self.overshoot = options.load_overshoot()
        self.live_preview = options.load_live_preview()

        # disable undo on first call, so we don't get 2 undos in queue
        # both press and release add to the same cache, so it should be safe
        if self.live_preview:

            runtime.begin_preview(0.0, self.interpolation_mode.idx)

            tween.interpolate(blend=0.0, mode=self.interpolation_mode)
            cmds.refresh()

    def drag(self):
        """
        Dragger context drag event handler.
        """
        self.drag_position = cmds.draggerContext('stagingTweenerToolContext',
                                                 q=True,
                                                 dragPoint=True)

        if self.live_preview:
            blend = self.get_blend()
            tween.interpolate(blend=blend, mode=self.interpolation_mode)
            cmds.refresh()

    def release(self):
        """
        Dragger context release event handler.
        """
        blend = self.get_blend()
        if self.live_preview:
            cmds.stagingTweener(t=blend, newCache=False, type=self.interpolation_mode.idx)
        else:
            cmds.stagingTweener(t=blend, newCache=True, type=self.interpolation_mode.idx)

        cmds.refresh()

    def finalize(self):
        """
        Dragger context finalize event handler.

        Its mere existence helps with returning to the previous tool when done.
        """
        runtime.cancel_preview()

    def get_blend(self):
        """
        Calculates the blend value based on the distance dragged.

        :return: Blend value
        :rtype: float
        """
        # calculate distance dragged
        x = self.drag_position[0] - self.press_position[0]

        blend = x / 150.0  # 150.0 is just a sensivity

        if not self.overshoot:
            blend = utils.clamp(blend, -1.0, 1.0)

        return blend

def _safe_tool_event(function):
    def invoke(instance, *args):
        try:
            return function(instance, *args)
        except Exception as exc:
            runtime.cancel_preview()
            cmds.warning('Mouse tween cancelled and rolled back: ' + str(exc))
    return invoke

Tool.press = _safe_tool_event(Tool.press)
Tool.drag = _safe_tool_event(Tool.drag)
Tool.release = _safe_tool_event(Tool.release)
