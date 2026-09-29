
##                                         ADD ASSET
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds as mc
import maya.mel as mel
import json
from .Qt import QtWidgets, QtCore, QtCompat
import os
import maya.cmds as cmds
from maya import OpenMayaUI as omui
import shutil

import maya.app.general.createImageFormats as createImageFormats
from mtoa.cmds.arnoldRender import arnoldRender

import maya.app.renderSetup.model.override as override
import maya.app.renderSetup.model.selector as selector
import maya.app.renderSetup.model.collection as collection
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.typeIDs as typeIDs



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

import importlib

from . import AssetIt_Global
importlib.reload(AssetIt_Global)

from . import AssetIt_CSS
importlib.reload(AssetIt_CSS)




##PATH_SET
IconPath = AssetIt_Global.IconsPathThemeClassic
PreferencePath = AssetIt_Global.PreferencePath
ToolsPath = AssetIt_Global.ToolPath
AssetCreationPath = AssetIt_Global.AssetCreationPath

##GLOBAL VAR
WindowsTitle = "Info Panel"
ASSET_LIBRARY_PATH = AssetIt_Global.ASSET_LIBRARY_PATH
ASSET_FAVOURITES_PATH = AssetIt_Global.ASSET_FAVOURITES_PATH
ASSET_CREATION_PATH = AssetIt_Global.AssetCreationPath
ASSET_PATH = ""
ASSET_NAME = ""
RENDER_CHOICE = ""
TEXTURE_SAVED = ""
TEXTURES_CHOICE = ""
TEXTURE_NBR = ""
USER_NOTE = ""

def SEND_INFO(AssetPath, AssetName):
    global ASSET_PATH
    ASSET_PATH = AssetPath
    global ASSET_NAME
    ASSET_NAME = AssetName

    ##JSON ASSET METADATA
    JSON_FILE = ASSET_PATH.replace("png", "json")
    JSON_OPEN = open(JSON_FILE, "r")
    JSON_LOAD = json.load(JSON_OPEN)

    global RENDER_CHOICE
    RENDER_CHOICE = (JSON_LOAD['RenderChoice'])

    global TEXTURE_SAVED
    TEXTURE_SAVED = (JSON_LOAD['TextureSaved'])

    global TEXTURES_CHOICE
    TEXTURES_CHOICE = (JSON_LOAD['TextureChoice'])

    global TEXTURE_NBR
    TEXTURE_NBR = (JSON_LOAD['TextureNbr'])

    global USER_NOTE
    USER_NOTE = (JSON_LOAD['UserInfo'])


    return ASSET_NAME + str(RENDER_CHOICE) + ASSET_PATH + str(TEXTURE_SAVED) + TEXTURES_CHOICE + str(TEXTURE_NBR) + USER_NOTE




class AssetMetadata_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AssetMetadata_UI, self).__init__()
        self.setMinimumSize(420, 700)
        self.buildUI()



    def buildUI(self):
        INFO_MAIN_Layout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_Global.Theme)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize

        #######_______________________________________________// ASSET IMAGE
        IMAGELayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(IMAGELayout)

        self.AssetImage = QtWidgets.QLabel()
        self.AssetImage.setObjectName("ThumbAsset")
        self.AssetImage.setPixmap(QtGui.QPixmap(ASSET_PATH))
        self.AssetImage.setAlignment(QtCore.Qt.AlignCenter)
        self.AssetImage.setFixedSize(400, 400)
        IMAGELayout.addWidget(self.AssetImage)



        #######_______________________________________________// NAME
        NAMELayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(NAMELayout)

        self.AssetName_title = QtWidgets.QLabel()
        self.AssetName_title.setText("NAME :")
        self.AssetName_title.setFixedHeight(30)
        NAMELayout.addWidget(self.AssetName_title)

        self.AssetName = QtWidgets.QLabel()
        self.AssetName.setObjectName("AssetTitle")
        #self.AssetName.setWordWrap(True)
        self.AssetName.setText(ASSET_NAME)
        self.AssetName.setFixedHeight(30)
        NAMELayout.addWidget(self.AssetName)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)


        #######_______________________________________________// PATH
        PATHLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(PATHLayout)

        self.AssetPath_title = QtWidgets.QLabel()
        self.AssetPath_title.setText("PATH :")
        self.AssetPath_title.setFixedHeight(30)
        PATHLayout.addWidget(self.AssetPath_title)

        self.AssetPath = QtWidgets.QLabel()
        self.AssetPath.setObjectName("AssetTitle")
        #self.AssetPath.setWordWrap(True)
        self.AssetPath.setText(ASSET_PATH)
        self.AssetPath.setFixedHeight(30)
        PATHLayout.addWidget(self.AssetPath)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)

        #######_______________________________________________// RENDERER
        RENDERERLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(RENDERERLayout)

        self.Renderer_title = QtWidgets.QLabel()
        self.Renderer_title.setText("RENDERER :")
        self.Renderer_title.setFixedHeight(30)
        RENDERERLayout.addWidget(self.Renderer_title)

        self.Renderer = QtWidgets.QLabel()
        self.Renderer.setObjectName("AssetTitle")
        #self.Renderer.setWordWrap(True)
        self.Renderer.setText(RENDER_CHOICE)
        self.Renderer.setFixedHeight(30)
        RENDERERLayout.addWidget(self.Renderer)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)

        #######_______________________________________________// SAVE MATERIAL
        MATERIALLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(MATERIALLayout)

        self.Material_title = QtWidgets.QLabel()
        self.Material_title.setText("SAVED MATERIAL :")
        self.Material_title.setFixedHeight(30)
        MATERIALLayout.addWidget(self.Material_title)

        self.SaveMaterial = QtWidgets.QLabel()
        self.SaveMaterial.setObjectName("AssetTitle")
        #self.SaveMaterial.setWordWrap(True)
        self.SaveMaterial.setText(str(TEXTURE_SAVED))
        self.SaveMaterial.setFixedHeight(30)
        MATERIALLayout.addWidget(self.SaveMaterial)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)

        #######_______________________________________________// TEXTURE NBR
        TEXTURELayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(TEXTURELayout)

        self.Texture_title = QtWidgets.QLabel()
        self.Texture_title.setText("TEXTURE :")
        self.Texture_title.setFixedHeight(30)
        TEXTURELayout.addWidget(self.Texture_title)

        self.TextureNbr = QtWidgets.QLabel()
        self.TextureNbr.setObjectName("AssetTitle")
        self.TextureNbr.setText(str(TEXTURE_NBR))
        self.TextureNbr.setFixedHeight(30)
        TEXTURELayout.addWidget(self.TextureNbr)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)

        #######_______________________________________________// TEXTURE LOCATION
        TEXTURELOCATIONLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(TEXTURELOCATIONLayout)

        self.TextureLocation_title = QtWidgets.QLabel()
        self.TextureLocation_title.setText("TEXTURE LOCATION :")
        self.TextureLocation_title.setFixedHeight(30)
        TEXTURELOCATIONLayout.addWidget(self.TextureLocation_title)

        self.TextureLocation = QtWidgets.QLabel()
        self.TextureLocation.setObjectName("AssetTitle")
        self.TextureLocation.setText(str(TEXTURES_CHOICE))
        self.TextureLocation.setFixedHeight(30)
        TEXTURELOCATIONLayout.addWidget(self.TextureLocation)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)

        #######_______________________________________________// USER NOTE
        USERNOTELayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(USERNOTELayout)

        self.Usernote_title = QtWidgets.QLabel()
        self.Usernote_title.setText("USER NOTE :")
        self.Usernote_title.setFixedHeight(30)
        USERNOTELayout.addWidget(self.Usernote_title)

        self.Usernote = QtWidgets.QLabel()
        self.Usernote.setObjectName("AssetTitle")
        self.Usernote.setText(str(USER_NOTE))
        self.Usernote.setFixedHeight(30)
        USERNOTELayout.addWidget(self.Usernote)

        INFOLayout = QtWidgets.QHBoxLayout(self)
        INFO_MAIN_Layout.addLayout(INFOLayout)





        INFO_MAIN_Layout.addStretch()
        NAMELayout.addStretch()
        RENDERERLayout.addStretch()
        PATHLayout.addStretch()
        MATERIALLayout.addStretch()
        TEXTURELayout.addStretch()
        TEXTURELOCATIONLayout.addStretch()
        USERNOTELayout.addStretch()






    def Apply(self):
        print (ASSET_PATH)
        print (ASSET_NAME)




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
    ui = Dock(AssetMetadata_UI)
    ui.show()

    # Get a pointer and convert it to Qt Widget object
    qw = omui.MQtUtil.findWindow(WindowsTitle)
    widget = wrapInstance(int(qw), QWidget)
    # Create a QIcon object
    icon = QIcon(IconPath + "Windows_Ico2.png")
    # Assign the icon
    widget.setWindowIcon(icon)

    return ui

