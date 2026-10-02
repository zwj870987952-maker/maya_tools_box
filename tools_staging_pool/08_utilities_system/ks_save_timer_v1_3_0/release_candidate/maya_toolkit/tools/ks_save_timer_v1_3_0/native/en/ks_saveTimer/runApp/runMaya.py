from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2


from ks_saveTimer.libApp import getLibApp as libApp
__LIB_APP__ = libApp.__LIB_APP__

from ks_saveTimer.lib import GUI_saveTimer


def checkExistingSaveTimer():
    for widget in QtWidgets.QApplication.allWidgets():
        if type(widget) == GUI_saveTimer.GUI_SaveTimer:
            return True
    return False

def openSaveTimer_maya_embed(target='statusLine'):
    from maya import cmds

    if cmds.about(batch=True):
        return

    if checkExistingSaveTimer():
        print('KS_SaveTimer - Already one instance of KS_SaveTimer found! Preventing making another...')
        return

    saveTimerWidget = GUI_saveTimer.GUI_SaveTimer()
    saveTimerWidget.setFixedHeight(22)
    saveTimerWidget.setFixedWidth(60)
    __LIB_APP__.QT_embedUItoInterface('ks_saveTimer', saveTimerWidget, target)
