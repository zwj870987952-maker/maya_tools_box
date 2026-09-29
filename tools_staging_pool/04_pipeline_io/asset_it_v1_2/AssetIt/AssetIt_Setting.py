
##                                         SETTING
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds as mc
import maya.mel as mel
import json
from .Qt import QtWidgets, QtCore, QtCompat
import os
import maya.cmds as cmds
from maya import OpenMayaUI as omui

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

##GLOBAL VAR
WindowsTitle = "Settings"
ASSET_LIBRARY_PATH = AssetIt_Global.ASSET_LIBRARY_PATH
ASSET_FAVOURITES_PATH = AssetIt_Global.ASSET_FAVOURITES_PATH



##UI INFO
Theme_pref = json.load(open(PreferencePath + 'Pref_Theme.json', "r"))
PREF_THEME = (Theme_pref['THEME'])
if PREF_THEME == 0:
    ThemeIndex = 0
if PREF_THEME == 1:
    ThemeIndex = 1
if PREF_THEME == 2:
    ThemeIndex = 2

Icon_pref = json.load(open(PreferencePath + 'Pref_IconSize.json', "r"))
PREF_ICON = (Icon_pref['ICONSIZE'])
if PREF_ICON == 18:
    IconIndex = 0
if PREF_ICON == 26:
    IconIndex = 1
if PREF_ICON == 32:
    IconIndex = 2


Click_pref = json.load(open(PreferencePath + 'Pref_Click.json', "r"))
PREF_CLICK = (Click_pref['CLICK'])
if PREF_CLICK == 0:
    ClickIndex = 0
if PREF_CLICK == 1:
    ClickIndex = 1

# ________________//
# ___________________________________________
# ________________//


class Setting_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Setting_UI, self).__init__()
        self.setMinimumSize(650, 410)

        self.buildUI()


    def buildUI(self):
        SETTINGLayout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_Global.Theme)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize

        #############################################
        LibraryPathLabel = QtWidgets.QLabel(self)
        LibraryPathLabel.setText("Library Path :")
        SETTINGLayout.addWidget(LibraryPathLabel)


        ## LIBRARY PATH
        LibPathHlyt = QtWidgets.QHBoxLayout()
        SETTINGLayout.addLayout(LibPathHlyt)
        LibPathHlyt.setAlignment(QtCore.Qt.AlignCenter)

        spacer = QtWidgets.QLabel(self)
        spacer.setText("       ")
        LibPathHlyt.addWidget(spacer)

        UserLibPathField = QtWidgets.QLineEdit()
        UserLibPathField.setPlaceholderText(ASSET_LIBRARY_PATH)
        UserLibPathField.setObjectName("UserLibPathField")
        LibPathHlyt.addWidget(UserLibPathField)



        ## LIBRARY PATH BTN
        LibPathBTN = QtWidgets.QPushButton()
        LibPathBTN.setFixedSize(iconButtonSize,iconButtonSize)
        LibPathBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        LibPathBTN.setIcon(QtGui.QIcon(IconPath + "Folder2.png"))
        LibPathBTN.clicked.connect(self.SET_LibPath)
        LibPathBTN.setToolTip("  Set Your Library Path  ")
        LibPathHlyt.addWidget(LibPathBTN)


        ##________________________________________// SEPARATOR
        separator = QtWidgets.QLabel('')
        separator.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separator.setMaximumHeight(2)
        SETTINGLayout.addWidget(separator)

        ## UI TABS
        UILabel = QtWidgets.QLabel(self)
        UILabel.setText(" - UI - ")
        UILabel.setFont(QtGui.QFont('Candara', 10))
        UILabel.setAlignment(QtCore.Qt.AlignCenter)
        SETTINGLayout.addWidget(UILabel)




        ##_____________________________________________________ UI THEME
        THEMEHlyt = QtWidgets.QHBoxLayout()
        SETTINGLayout.addLayout(THEMEHlyt)
        THEMELabel = QtWidgets.QLabel(self)
        THEMELabel.setText("Theme : ")
        THEMEHlyt.addWidget(THEMELabel)
        self.ThemeComboList = [
            'Default Blue',
            'Maya',
        ]

        self.ThemeCombo = QtWidgets.QComboBox()
        self.ThemeCombo.addItems(self.ThemeComboList)
        self.ThemeCombo.setFixedWidth(150)
        self.ThemeCombo.currentIndexChanged.connect(self.SET_Theme)
        self.ThemeCombo.setCurrentIndex(ThemeIndex)
        THEMEHlyt.addWidget(self.ThemeCombo)

        ## UI ICONSIZE
        IconSizeLabel = QtWidgets.QLabel(self)
        IconSizeLabel.setText("            Icons Size : ")
        THEMEHlyt.addWidget(IconSizeLabel)
        self.IconSizeComboList = [
            '18',
            '26',
            '32',
        ]

        self.IconSizeCombo = QtWidgets.QComboBox()
        self.IconSizeCombo.addItems(self.IconSizeComboList)
        self.IconSizeCombo.setFixedWidth(150)
        self.IconSizeCombo.setCurrentIndex(IconIndex)
        self.IconSizeCombo.currentIndexChanged.connect(self.SET_IconSize)
        THEMEHlyt.addWidget(self.IconSizeCombo)




        ##________________________________________// SEPARATOR
        separator = QtWidgets.QLabel('')
        separator.setMaximumHeight(10)
        SETTINGLayout.addWidget(separator)

        separator = QtWidgets.QLabel('')
        separator.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separator.setMaximumHeight(2)
        SETTINGLayout.addWidget(separator)

        ## UI TABS
        UILabel = QtWidgets.QLabel(self)
        UILabel.setText(" - Import Options - ")
        UILabel.setFont(QtGui.QFont('Candara', 10))
        UILabel.setAlignment(QtCore.Qt.AlignCenter)
        SETTINGLayout.addWidget(UILabel)



        ##_____________________________________________________ CLICK CHOICE
        CLICKHlyt = QtWidgets.QHBoxLayout()
        SETTINGLayout.addLayout(CLICKHlyt)
        CLICKLabel = QtWidgets.QLabel(self)
        CLICKLabel.setText("Import Asset : ")
        CLICKHlyt.addWidget(CLICKLabel)
        self.ClickComboList = [
            'Left Click',
            'Double-Click',
        ]

        self.ClickCombo = QtWidgets.QComboBox()
        self.ClickCombo.addItems(self.ClickComboList)
        self.ClickCombo.setFixedWidth(150)
        self.ClickCombo.currentIndexChanged.connect(self.SET_Click)
        self.ClickCombo.setCurrentIndex(ClickIndex)
        CLICKHlyt.addWidget(self.ClickCombo)



        ##_____________________________________________________ ASSET SIZE MULTI
        CLICKLabel = QtWidgets.QLabel(self)
        CLICKLabel.setText("              Asset Size Multiplier : ")
        CLICKHlyt.addWidget(CLICKLabel)

        SaveSize_pref = json.load(open(PreferencePath + 'MultiSize.json', "r"))
        MULTISIZEVALUE = (SaveSize_pref['MULTISIZEVALUE'])


        self.SizeSpinBox = QtWidgets.QDoubleSpinBox()
        self.SizeSpinBox.setDecimals(1)
        self.SizeSpinBox.setFixedWidth(50)
        self.SizeSpinBox.setRange(0, 100)
        self.SizeSpinBox.setValue(MULTISIZEVALUE)
        self.SizeSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.SizeSpinBox.editingFinished.connect(self.set_MultiSize)
        CLICKHlyt.addWidget(self.SizeSpinBox)



        ##_____________________________________________________ SHADER CHOICE
        separator = QtWidgets.QLabel('')
        separator.setMaximumHeight(10)
        SETTINGLayout.addWidget(separator)

        SHADERHlyt = QtWidgets.QHBoxLayout()
        SETTINGLayout.addLayout(SHADERHlyt)
        SHADERLabel = QtWidgets.QLabel(self)
        SHADERLabel.setText("/ When importing an Asset with a shader already existing in the scene : ")
        SHADERHlyt.addWidget(SHADERLabel)

        ImportShaderHLyt = QtWidgets.QHBoxLayout()
        SETTINGLayout.addLayout(ImportShaderHLyt)


        #_______________________________________DEFAULT : USE EXISTING ONE
        ImportShaderMode_pref = json.load(open(PreferencePath + 'ImportShader.json', "r"))
        IMPORTSHADERMODE = (ImportShaderMode_pref['IMPORTSHADERMODE'])


        UseExistingLyt = QtWidgets.QHBoxLayout()
        UseExistingLyt.addSpacing(20)
        ImportShaderHLyt.addLayout(UseExistingLyt)
        KeepExistingBtn = QtWidgets.QRadioButton("Use existing one (Slower)")
        KeepExistingBtn.clicked.connect(self.set_KeepExisting)
        if IMPORTSHADERMODE == 0:
            KeepExistingBtn.setChecked(1)
        else:
            KeepExistingBtn.setChecked(0)
        UseExistingLyt.addWidget(KeepExistingBtn)


        # _______________________________________CREATE NEW SHADER
        CreateNewLyt = QtWidgets.QHBoxLayout()
        CreateNewLyt.addSpacing(20)
        ImportShaderHLyt.addLayout(CreateNewLyt)
        CreateNewBtn = QtWidgets.QRadioButton("Create a new shader")
        CreateNewBtn.clicked.connect(self.set_CreateNew)
        if IMPORTSHADERMODE == 1:
            CreateNewBtn.setChecked(1)
        else:
            CreateNewBtn.setChecked(0)
        CreateNewLyt.addWidget(CreateNewBtn)
        ImportShaderHLyt.addStretch()




        ##________________________________________// SEPARATOR
        separator = QtWidgets.QLabel('')
        separator.setMaximumHeight(10)
        SETTINGLayout.addWidget(separator)

        separator = QtWidgets.QLabel('')
        separator.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separator.setMaximumHeight(2)
        SETTINGLayout.addWidget(separator)

        ## CLEAN FAV BTN
        CleanFavBTN = QtWidgets.QPushButton()
        CleanFavBTN.setText("Clean Favorite Tab")
        CleanFavBTN.setObjectName("CleanFav")
        CleanFavBTN.setFixedHeight(25)
        CleanFavBTN.clicked.connect(self.CleanFav)
        CleanFavBTN.setToolTip("That will delete all Favorite tab content")
        SETTINGLayout.addWidget(CleanFavBTN)



        ##________________________________________// SAVE SETTING
        separator = QtWidgets.QLabel('')
        separator.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separator.setMaximumHeight(2)
        SETTINGLayout.addWidget(separator)

        ## SAVE BTN
        SaveSettingBTN = QtWidgets.QPushButton()
        SaveSettingBTN.setText("SAVE SETTING")
        SaveSettingBTN.setObjectName("SaveSetting")
        SaveSettingBTN.setFixedHeight(25)
        SaveSettingBTN.clicked.connect(self.Apply)
        SaveSettingBTN.setToolTip("Apply and Save Setting")
        SETTINGLayout.addWidget(SaveSettingBTN)


        THEMEHlyt.addStretch()
        SETTINGLayout.addStretch()
        CLICKHlyt.addStretch()
        SHADERHlyt.addStretch()


        return UserLibPathField

    def set_MultiSize(self):
        value = self.SizeSpinBox.value()
        SaveSize = {"MULTISIZEVALUE" : value}
        open(PreferencePath + 'MultiSize.json', "w").write(json.dumps(SaveSize))



    def CleanFav(self):
        BackgroundColor = 0.16
        Message = "Are you sure you want to delete all your saved favourites?"
        # ________________//
        if mc.window("WarningWindow", exists=True):
            mc.deleteUI("WarningWindow")
        mc.window("WarningWindow", title=' Warning ', s=False, vis=True, rtf=False)
        mc.columnLayout(adj=True, rs=3, bgc=[BackgroundColor, BackgroundColor, BackgroundColor])
        mc.separator(h=8, style='none')
        mc.text(l="  " + Message + "  ", al="center")
        mc.separator(h=8, style='none')
        mc.rowColumnLayout( numberOfRows=1 )
        mc.separator(w=35, style='none')
        mc.button(l="YES", c=self.WarningDeleteLayerYES, width= 100, h=20)
        mc.separator(w=10, style='none')
        mc.button(l="NO", c=self.WarningDeleteLayerNO, width= 100, h=20)
        mc.window("WarningWindow", e=True, wh=(300, 80))

        qw = omui.MQtUtil.findWindow("WarningWindow")
        widget = wrapInstance(int(qw), QWidget)
        icon = QIcon(IconPath + "Windows_Ico_Warning.png")
        widget.setWindowIcon(icon)

        mc.showWindow()

    def WarningDeleteLayerYES(self, *args):
        favouriteFilePath = ASSET_FAVOURITES_PATH
        infoToSave = []
        s = json.dumps(infoToSave)
        open(favouriteFilePath, "w").write(s)

        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()


    def WarningDeleteLayerNO(self, *args):
        mc.deleteUI("WarningWindow")

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

        #copyfile(presetFilePath, SelectPath + "/EnvIt_SpeedTree_Preset.ini" )


        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()



        if LIBFOLDEREXIST == 1:
            infoToSave = {"FIRST_LAUNCH" : 1}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'FirstLaunch.json', "w").write(s)

            from . import AssetIt_Launcher
            importlib.reload(AssetIt_Launcher)


            AssetIt_Launcher.showUI()

    def SET_Theme(self):
        ChoosenValue = self.ThemeCombo.currentIndex()
        if ChoosenValue == 0:
            ThemeValue =0
        if ChoosenValue == 1:
            ThemeValue =1
        if ChoosenValue == 2:
            ThemeValue =2

        infoToSave = {"THEME": ThemeValue}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'Pref_Theme.json', "w").write(s)

    def SET_IconSize(self):
        ChoosenValue = self.IconSizeCombo.currentIndex()
        if ChoosenValue == 0:
            IconValue =18
        if ChoosenValue == 1:
            IconValue =26
        if ChoosenValue == 2:
            IconValue =32

        infoToSave = {"ICONSIZE": IconValue}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'Pref_IconSize.json', "w").write(s)

    def SET_Click(self):
        ChoosenValue = self.ClickCombo.currentIndex()
        if ChoosenValue == 0:
            ClickValue =0
        if ChoosenValue == 1:
            ClickValue =1

        infoToSave = {"CLICK": ClickValue}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'Pref_Click.json', "w").write(s)

    def set_KeepExisting(self):
        SaveImportShaderMode = {"IMPORTSHADERMODE" : 0}
        open(PreferencePath + 'ImportShader.json', "w").write(json.dumps(SaveImportShaderMode))

    def set_CreateNew(self):
        SaveImportShaderMode = {"IMPORTSHADERMODE" : 1}
        open(PreferencePath + 'ImportShader.json', "w").write(json.dumps(SaveImportShaderMode))



    def Apply(self):
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
    ui = Dock(Setting_UI)
    ui.show()

    # Get a pointer and convert it to Qt Widget object
    qw = omui.MQtUtil.findWindow(WindowsTitle)
    widget = wrapInstance(int(qw), QWidget)
    # Create a QIcon object
    icon = QIcon(IconPath + "Windows_Ico2.png")
    # Assign the icon
    widget.setWindowIcon(icon)

    return ui

