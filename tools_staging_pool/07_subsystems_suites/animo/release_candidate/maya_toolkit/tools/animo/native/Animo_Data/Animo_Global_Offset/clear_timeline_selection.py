from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2 import QtCore, QtGui, QtWidgets


def clear_time_slider_selection():
    
    app = QtWidgets.QApplication.instance()
    
    widgetStr = mel.eval('$gPlayBackSlider=$gPlayBackSlider')
    ptr = omui.MQtUtil.findControl(widgetStr)
    slider = wrapInstance(int(ptr), QtWidgets.QWidget)
    
    slider_height = slider.size().height()
    
    current_frame = cmds.currentTime(query=True)
    
    click_pos = QtCore.QPoint(-10, slider_height / 2.0)
    
    event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                              click_pos,
                              QtCore.Qt.MouseButton.LeftButton,
                              QtCore.Qt.MouseButton.LeftButton,
                              QtCore.Qt.NoModifier)
    app.sendEvent(slider, event)
    
    event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                              click_pos,
                              QtCore.Qt.MouseButton.LeftButton,
                              QtCore.Qt.MouseButton.LeftButton,
                              QtCore.Qt.NoModifier)
    app.sendEvent(slider, event)
    
    app.processEvents()
    
    cmds.currentTime(current_frame)


clear_time_slider_selection()