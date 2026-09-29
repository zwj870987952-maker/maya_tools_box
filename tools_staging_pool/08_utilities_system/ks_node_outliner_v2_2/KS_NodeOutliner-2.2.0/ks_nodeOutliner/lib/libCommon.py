from __future__ import absolute_import
from __future__ import print_function
from PySide2 import QtCore, QtGui, QtWidgets
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
        iconObject = QtGui.QIcon(processIconPath(iconPath))
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


def getModule(moduleName, reloadModule=False):
    if moduleName.startswith('.'):
        modulePath = ks_nodeOutliner._SF_ROOTPACKAGE_ + moduleName
    else:
        modulePath = moduleName

    try:
        module = importlib.import_module(modulePath)
    except:
        print('\n------------\nKS_NodeOutliner ScriptFilter - Could not find script module:', moduleName, '\n------------')
        return None

    if reloadModule:
        reload(module)

    return module

def getModuleFunction(module, functionName):
    try:
        function = getattr(module, functionName)
    except:
        print('\n------------\nKS_NodeOutliner ScriptFilter - Could not find script functon:', functionName, module, '\n------------')
        function = None

    return function
