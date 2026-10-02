from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore,QtGui,QtWidgets
import importlib

import ks_nodeOutliner

_ICON_OBJ_DICT_ = {}

def processIconPath(iconPath):
    if not iconPath:
        return None

    if QtCore.QFile.exists(iconPath):
        return iconPath

    if iconPath.startswith(':/'):
        iconPath = iconPath.replace(':/', ks_nodeOutliner._ICON_DIR_)
        if QtCore.QFile.exists(iconPath):
            return iconPath

    return None


def getIconObject(iconPath):
    iconObject = _ICON_OBJ_DICT_.get(iconPath, None)
    if not iconObject:
        iconObject = QtGui.QIcon(processIconPath(iconPath) or '')
        _ICON_OBJ_DICT_[iconPath] = iconObject
    return iconObject


def makeIconBtn(iconPath=None, statusTip=None, command=None, iconFallBackLetter=None, iconSize=20):
    button = QtWidgets.QToolButton()
    button.setFixedSize(iconSize,iconSize)
    button.setIconSize(QtCore.QSize(iconSize,iconSize))

    if statusTip:
        button.setStatusTip(statusTip)
    if command:
        button.clicked.connect(command)

    iconObject = getIconObject(iconPath)
    if iconObject:
        button.setIcon(iconObject)
    else:
        button.setText(iconFallBackLetter)

    return button


def setIcon_listItem(item, iconPath=None):
    iconObject = getIconObject(iconPath)
    if type(item) == QtWidgets.QTreeWidgetItem:
        item.setIcon(0, iconObject)
    else:
        item.setIcon(iconObject)


def getModule(moduleName,reloadModule=False):
    from maya_toolkit.tools.ks_node_outliner_v2_2.session import script_module
    return script_module(moduleName,reloadModule)

def getModuleFunction(module, functionName):
    try:
        function = getattr(module, functionName)
    except:
        print('\n------------\nKS_NodeOutliner ScriptFilter - Could not find script functon:', functionName, module, '\n------------')
        function = None

    return function
