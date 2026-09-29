from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds as mc
import maya.mel as mel
import json
from .Qt import QtWidgets, QtCore, QtCompat

import os
import maya.cmds as cmds
from maya import OpenMayaUI as omui
import importlib

# Special cases for different Maya versions
try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

try:
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QWidget
except ImportError:
    from PySide.QtGui import QIcon, QWidget



#PATHS
USERAPPDIR = mc.internalVar(userAppDir=True)
VERSION = mc.about(v=True)


from . import AssetIt_Global
importlib.reload(AssetIt_Global)

from . import AssetIt_CSS
importlib.reload(AssetIt_CSS)

##THEME_SET
IconPath = AssetIt_Global.IconsPathThemeClassic
PreferencePath = AssetIt_Global.PreferencePath
ToolsPath = AssetIt_Global.ToolPath

##GLOBAL VAR
WindowsTitle = "Welcome to AssetIt"
ASSET_LIBRARY_PATH = AssetIt_Global.USER_LIB_PATH


#________________//
#___________________________________________
#________________//
class Launcher_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Launcher_UI, self).__init__()
        self.setMinimumSize(1620, 875)

        self.buildUI()


    def buildUI(self):
        LAUNCHERLayout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_CSS.AssetIt_CSS)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize

        #############################################

        ## SCATTER TAB Banner
        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(IconPath + "AssetIt_Launch_01.jpg")
        label.setPixmap(pixmap)
        label.setAlignment(QtCore.Qt.AlignTop)
        LAUNCHERLayout.addWidget(label)



        LibraryPathLabel = QtWidgets.QLabel(self)
        #LibraryPathLabel.setFont(QtGui.QFont('Candara', 10))
        #LauncherTitle.setStyleSheet("QLabel { background-color : #1e1e1e; color : #65BEF1; }")
        LibraryPathLabel.setText("Library Path :")
        LAUNCHERLayout.addWidget(LibraryPathLabel)
        #LibraryPathLabel.setAlignment(QtCore.Qt.AlignTop)

        ## LIBRARY PATH
        LibPathHlyt = QtWidgets.QHBoxLayout()
        LAUNCHERLayout.addLayout(LibPathHlyt)
        LibPathHlyt.setAlignment(QtCore.Qt.AlignCenter)

        spacer = QtWidgets.QLabel(self)
        spacer.setText("       ")
        LibPathHlyt.addWidget(spacer)

        self.saveNameField = QtWidgets.QLineEdit()
        self.saveNameField.setPlaceholderText(ASSET_LIBRARY_PATH)
        LibPathHlyt.addWidget(self.saveNameField)



        ## LIBRARY PATH BTN
        LibPathBTN = QtWidgets.QPushButton()
        LibPathBTN.setFixedSize(iconButtonSize,iconButtonSize)
        LibPathBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        LibPathBTN.setIcon(QtGui.QIcon(IconPath + "Folder2.png"))
        LibPathBTN.clicked.connect(self.SET_LibPath)
        LibPathBTN.setToolTip("  Set Your Library Path  ")
        LibPathBTN.setShortcut(QtGui.QKeySequence("Return"))
        LibPathHlyt.addWidget(LibPathBTN)





        LAUNCHERLayout.addStretch()


        return self.saveNameField




    def SET_LibPath(self):
        #//TODO - If Asset_Library folder already exist just pass   ELSE    Copy or Create a structure
        LIBFOLDEREXIST = 0
        print (ASSET_LIBRARY_PATH)

        # //TODO - Faire une verif de la bonne prise du dossier

        #from shutil import copyfile

        Path = mc.fileDialog2(ds=1, cap="Select a file", fm=3)
        SelectPath = Path[0]
        print ("Select PATH : " + SelectPath)

        infoToSave = {"USER_LIB_PATH": SelectPath}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'UserLibPath.json', "w").write(s)


        mc.deleteUI(WindowsTitle)

        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()




def Dock(Widget, width=200, height=200, hp="free", show=True):
    label = getattr(Widget, "label", WindowsTitle)

    try:
        cmds.deleteUI(WindowsTitle)
    except RuntimeError:
        pass

    dockControl = cmds.workspaceControl(
        WindowsTitle,
        initialWidth=width,
        minimumWidth=False,
        widthProperty=hp,
        heightProperty=hp,
        label=label
    )

    dockPtr = omui.MQtUtil.findControl(dockControl)
    dockWidget = QtCompat.wrapInstance(int(dockPtr), QtWidgets.QWidget)
    dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    child = Widget(dockWidget)
    dockWidget.layout().addWidget(child)

    if show:
        cmds.evalDeferred(
            lambda *args: cmds.workspaceControl(
                dockControl,
                edit=True,
                widthProperty="free",
                restore=True
            )
        )
    return child

def showUI():
    ui = Dock(Launcher_UI)
    ui.show()

    # Get a pointer and convert it to Qt Widget object
    qw = omui.MQtUtil.findWindow(WindowsTitle)
    widget = wrapInstance(int(qw), QWidget)
    # Create a QIcon object
    icon = QIcon(IconPath + "Windows_Ico2.png")
    # Assign the icon
    widget.setWindowIcon(icon)


    return ui

