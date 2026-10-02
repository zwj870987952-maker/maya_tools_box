from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2

import os

from maya import cmds, mel
from maya import OpenMaya
from maya import OpenMayaUI as omui
# from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

from ks_saveTimer.lib import Singleton


##
## ------------------ FUNCTIONALITY ------------------
##


# def getUserConfigLocation():
#     return os.environ['MAYA_APP_DIR']

def displayStatusMessage(message):
    return OpenMaya.MGlobal.displayInfo(message)

def displayWarningMessage(message):
    cmds.warning(message)
    return

def get_filePath():
    filePath = cmds.file(q=1, sn=1)
    if filePath == '':
        return None
    return filePath

def get_projectDir():
    return cmds.workspace(q=True, rootDirectory=True)

##
## ------------------ UI / QT COMMANDS ------------------
##


def QT_getMainWindow():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)


def findLayout_statusLine():
    layerEditorBtn = mel.eval('$tmpVar=$gLayerEditorButton')
    buttonLayout = cmds.iconTextCheckBox(layerEditorBtn, q=1, p=1)
    maya_parentLayout = cmds.formLayout(buttonLayout, q=1, p=1)
    return maya_parentLayout

def deleteLayoutFromUI(uiName):
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import close
    return close()


def QT_embedUItoInterface(uiName,widget,target="statusLine"):
    if target!="statusLine":raise ValueError("Only statusLine supported")
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import embed_maya
    return embed_maya(widget)
    # widget.setParent(rootLayout_Qt)



##
## ------------------ Callbacks ------------------
##



class _appCallbacks(QtCore.QObject):
    fileSaved = Signal()
    fileOpened = Signal()
    SCRIPTJOB_IDS = []

    def __init__(self,parent=None):
        super().__init__(parent)
        from maya_toolkit.tools.ks_save_timer_v1_3_0.session import init_callbacks
        init_callbacks(self)



_INSTANCE=None
def appCallbacks(*args,**kwargs):
    import sys
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton
    return singleton(sys.modules[__name__],"appCallbacks",*args,**kwargs)
