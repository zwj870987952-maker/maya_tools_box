# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.
import json
from maya import OpenMaya, OpenMayaUI, cmds, mel
try:
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *
    import shiboken6 as shiboken
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken

def mayaToQT(name):
    """
    Maya -> QWidget

    :param str name: Maya name of an ui object
    :return: QWidget of parsed Maya name
    :rtype: QWidget
    """
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        return shiboken.wrapInstance(int(ptr), QWidget)

def getMayaTimeline():
    """
    Get the object name of Maya's timeline.

    :return: Object name of Maya's timeline
    :rtype: str
    """
    return mel.eval('$tmpVar=$gPlayBackSlider')

def getTimeline():
    """
    Get the QWidget of Maya's timeline. For versions 2016.5 and later the
    first QWidget child of the timeline should be returned.

    :return: QWidget of Maya's timeline
    :rtype: QWidget
    """
    qtTimeline = mayaToQT(getMayaTimeline())
    for child in qtTimeline.children():
        if type(child) == QWidget:
            return child
    return qtTimeline

def getTimelineMenu():
    """
    Get the QWidget of Maya's timeline menu. An initialization mel function
    has to be called to create and populate the menu before adding
    functionality.

    :return: QWidget of Maya's timeline menu
    :rtype: QWidget
    """
    mel.eval('updateTimeSliderMenu TimeSliderMenu;')
    qtTimelineMenu = mayaToQT('TimeSliderMenu')
    return qtTimelineMenu

def getTimelineRange():
    r = cmds.timeControl(getMayaTimeline(), query=True, ra=True)
    start, end = (int(r[0]), int(r[1]))
    if end < start or end - start > 20000:
        raise ValueError('timeline selection范围超限')
    return list(range(start, end))

def remap(value, oMin, oMax, nMin, nMax):
    """
    Remap a value based on input minimin and maximum, the result is converted
    to an integer since markers can only live as a whole frame.

    :param float value: Value to remap
    :param float oMin: Original minimum
    :param float oMax: Original maximum
    :param float nMin: New minimum
    :param float nMax: New maximum
    :return: remapped value
    :rtype: int
    """
    return int((value - oMin) * (nMax - nMin) / (oMax - oMin) + nMin)
