
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

from .Asset_Creation import AsssetIt_CameraThumb
importlib.reload(AsssetIt_CameraThumb)




##PATH_SET
IconPath = AssetIt_Global.IconsPathThemeClassic
PreferencePath = AssetIt_Global.PreferencePath
ToolsPath = AssetIt_Global.ToolPath
AssetCreationPath = AssetIt_Global.AssetCreationPath

##GLOBAL VAR
WindowsTitle = "Add Asset"
ASSET_LIBRARY_PATH = AssetIt_Global.ASSET_LIBRARY_PATH
ASSET_FAVOURITES_PATH = AssetIt_Global.ASSET_FAVOURITES_PATH
ASSET_CREATION_PATH = AssetIt_Global.AssetCreationPath
ACTIVEMAINTAB = ""
ACTIVESUBTAB_NAME = ""
RENDERDONE = False

##PREF LOAD
Renderer_pref = json.load(open(PreferencePath + 'RenderChoice.json', "r"))
RENDERERCHOICE = (Renderer_pref['Renderer'])


Clay_pref = json.load(open(PreferencePath + 'ClayPref.json', "r"))
CLAYRENDER = (Clay_pref['CLAY'])

SaveMat_pref = json.load(open(PreferencePath + 'SaveMat.json', "r"))
SAVEMATERIAL = (SaveMat_pref['SAVEMAT'])

TextureChoice_pref = json.load(open(PreferencePath + 'TextureChoice.json', "r"))
TEXTURECHOICE = (TextureChoice_pref['TEXTURECHOICE'])

try:
    SELECTION = mc.ls(sl= True)
except:
    SELECTION = "Asset Name"




##UI INFO
# ________________//
# ___________________________________________
# ________________//
def SEND_INFO(MainTabActiveName, SecondTabActiveName):
    global ACTIVEMAINTAB
    ACTIVEMAINTAB = MainTabActiveName

    global ACTIVESUBTAB_NAME
    ACTIVESUBTAB_NAME = SecondTabActiveName

    return ACTIVEMAINTAB + ACTIVESUBTAB_NAME


class AddAsset_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AddAsset_UI, self).__init__()
        self.setMinimumSize(420, 815)
        self.buildUI()



    def buildUI(self):
        # ________________//
        # ___________________________________________##At WINDOWS OPEN
        # ________________//

        if mc.objExists("AssetIt_Thumb_Group"):
            pass
        else:
            #mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene_Redshift.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)
            if RENDERERCHOICE == "Redshift":
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Redshift_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)
            elif RENDERERCHOICE == "Vray":
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Vray_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)
                mel.eval('setAttr"vraySettings.pixelAspect"1;')
            else:
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene.ma", rnn=True, i=True,  ignoreVersion=True, mergeNamespacesOnClash=False)
        mc.select( clear=True )



        ASSETLayout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_Global.Theme)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize

        #######_______________________________________________// UI THUMBNAIL
        ## ASSET Thumb
        #Init IMG
        self.EmptyImg = QtGui.QPixmap(AssetCreationPath + "/Thumb_Empty.png") #Empty One

        # Thumb Support Label
        self.ThumbLabel = QtWidgets.QLabel()
        self.ThumbLabel.setPixmap(self.EmptyImg)
        self.ThumbLabel.setObjectName("ThumbAsset")
        self.ThumbLabel.setFixedSize(400, 400)
        ASSETLayout.addWidget(self.ThumbLabel)




        #######_______________________________________________// UI THUMBNAIL
        TOOLBARLayout = QtWidgets.QHBoxLayout(self)
        ASSETLayout.addLayout(TOOLBARLayout)

        ## CAMERA BTN
        self.CameraBTN = QtWidgets.QPushButton()
        self.CameraBTN.setFixedSize(iconButtonSize,iconButtonSize)
        self.CameraBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.CameraBTN.setIcon(QtGui.QIcon(IconPath + "Camera2.png"))
        self.CameraBTN.setToolTip("  Thumb Camera Placement  ")
        self.CameraBTN.clicked.connect(self.PlaceCamera)
        TOOLBARLayout.addWidget(self.CameraBTN, alignment=QtCore.Qt.AlignRight)

        ## SEPARATOR
        self.Separator = QtWidgets.QPushButton()
        self.Separator.setObjectName("Separator")
        self.Separator.setFixedSize(iconButtonSize,iconButtonSize)
        self.Separator.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.Separator.setIcon(QtGui.QIcon(IconPath + "SeparatorBtn.png"))
        self.Separator.setEnabled(0)
        TOOLBARLayout.addWidget(self.Separator)

        ## SPACE
        self.Space = QtWidgets.QLabel()
        self.Space.setFixedSize(290,iconButtonSize)
        TOOLBARLayout.addWidget(self.Space)







        ## ARNOLD
        self.ArnoldBTN = QtWidgets.QPushButton()
        self.ArnoldBTN.setFixedSize(iconButtonSize, iconButtonSize)
        self.ArnoldBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        if RENDERERCHOICE == "Arnold":
            self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold.png"))
        else:
            self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.ArnoldBTN.setObjectName("Arnold")
        self.ArnoldBTN.clicked.connect(self.set_Arnold)
        TOOLBARLayout.addWidget(self.ArnoldBTN)

        TOOLBARLayout.addSpacing(12)

        ## VRAY
        self.VrayBTN = QtWidgets.QPushButton()
        self.VrayBTN.setFixedSize(iconButtonSize, iconButtonSize)
        self.VrayBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        if RENDERERCHOICE == "Vray":
            self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray.png"))
        else:
            self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))
        self.VrayBTN.setObjectName("Vray")
        self.VrayBTN.clicked.connect(self.set_Vray)
        TOOLBARLayout.addWidget(self.VrayBTN)
        TOOLBARLayout.addSpacing(12)


        ## REDSHIFT
        self.RedshiftBTN = QtWidgets.QPushButton()
        self.RedshiftBTN.setFixedSize(iconButtonSize, iconButtonSize)
        self.RedshiftBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        if RENDERERCHOICE == "Redshift":
            self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift.png"))
        else:
            self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.RedshiftBTN.setObjectName("Redshift")
        self.RedshiftBTN.clicked.connect(self.set_Redshift)
        TOOLBARLayout.addWidget(self.RedshiftBTN)
        TOOLBARLayout.addSpacing(12)

        ## VIEWPORT
        self.VpBTN = QtWidgets.QPushButton()
        self.VpBTN.setFixedSize(iconButtonSize, iconButtonSize)
        self.VpBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        if RENDERERCHOICE == "Viewport":
            self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp.png"))
        else:
            self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp_Off.png"))
        self.VpBTN.setObjectName("Viewport")
        self.VpBTN.clicked.connect(self.set_Viewport)
        TOOLBARLayout.addWidget(self.VpBTN)






        ## SPACE
        self.Space = QtWidgets.QLabel()
        self.Space.setFixedSize(100, iconButtonSize)
        TOOLBARLayout.addWidget(self.Space)

        ## SEPARATOR
        self.SeparatorToHide = QtWidgets.QPushButton()
        self.SeparatorToHide.setObjectName("Separator")
        self.SeparatorToHide.setFixedSize(iconButtonSize,iconButtonSize)
        self.SeparatorToHide.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.SeparatorToHide.setIcon(QtGui.QIcon(IconPath + "SeparatorBtn.png"))
        self.SeparatorToHide.setEnabled(0)
        TOOLBARLayout.addWidget(self.SeparatorToHide)
        self.SeparatorToHide.hide()

        ## CLAY RENDER
        self.ClayRenderBTN = QtWidgets.QCheckBox()
        self.ClayRenderBTN.setFixedSize(iconButtonSize, iconButtonSize)
        TOOLBARLayout.addWidget(self.ClayRenderBTN)
        self.ClayRenderBTN.setObjectName("ClayRender")
        self.ClayRenderBTN.setCheckable(1)
        self.ClayRenderBTN.setChecked(CLAYRENDER)
        self.ClayRenderBTN.toggled.connect(self.set_ClayRenderBTN)
        self.ClayRenderBTN.hide()

        if RENDERERCHOICE == "Arnold":
            self.ClayRenderBTN.show()
            self.SeparatorToHide.show()







        ## SEPARATOR
        self.Separator = QtWidgets.QPushButton()
        self.Separator.setObjectName("Separator")
        self.Separator.setFixedSize(iconButtonSize, iconButtonSize)
        self.Separator.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.Separator.setIcon(QtGui.QIcon(IconPath + "SeparatorPointBtn.png"))
        self.Separator.setEnabled(0)
        TOOLBARLayout.addWidget(self.Separator)

        ## RENDER BTN
        self.RenderBTN = QtWidgets.QPushButton()
        self.RenderBTN.setFixedSize(iconButtonSize,iconButtonSize)
        self.RenderBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.RenderBTN.setIcon(QtGui.QIcon(IconPath + "Render.png"))
        self.RenderBTN.setToolTip("  Render Thumb  ")
        #self.RenderBTN.clicked.connect(self.RENDERTHUMB_Redshift)
        self.RenderBTN.clicked.connect(self.RENDERTHUMB)
        TOOLBARLayout.addWidget(self.RenderBTN, alignment=QtCore.Qt.AlignRight)




        ##________________________________________// SEPARATOR
        separatorLine = QtWidgets.QLabel('')
        separatorLine.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separatorLine.setMaximumHeight(2)
        ASSETLayout.addWidget(separatorLine)







        ##________________________________________// ASSET INFO
        ##______________________________/ ASSET NAME
        AssetNameLyt = QtWidgets.QHBoxLayout()
        ASSETLayout.addLayout(AssetNameLyt)


        self.AssetNameFiel = QtWidgets.QLineEdit()
        self.AssetNameFiel.setObjectName("AssetNameFiel")
        self.AssetNameFiel.setAlignment(QtCore.Qt.AlignCenter)
        self.AssetNameFiel.setText(SELECTION[0])
        self.AssetNameFiel.setStyleSheet("QLineEdit{color: #71CCFF;}")
        self.AssetNameFiel.setFixedHeight(30)
        AssetNameLyt.addWidget(self.AssetNameFiel)

        #AssetName Empty
        if self.AssetNameFiel.text() == "Asset Name":
            self.AssetNameFiel.clear()
            self.AssetNameFiel.setPlaceholderText("Asset Name")

        self.AssetNameFielEnterBtn = QtWidgets.QPushButton()
        self.AssetNameFielEnterBtn.setFixedSize(0,0)
        self.AssetNameFielEnterBtn.setIconSize(QtCore.QSize(0, 0))
        self.AssetNameFielEnterBtn.setIcon(QtGui.QIcon(IconPath + "Apply.png"))
        self.AssetNameFielEnterBtn.setToolTip("  Validate Asset Name  ")
        self.AssetNameFielEnterBtn.clicked.connect(self.AssetNameValidate)
        self.AssetNameFielEnterBtn.setShortcut(QtGui.QKeySequence("Return"))
        TOOLBARLayout.addWidget(self.AssetNameFielEnterBtn)



        ##______________________________/       TAB 1
        ##Get MAINTABS Info
        self.firstLevelFolderList = os.listdir(ASSET_LIBRARY_PATH)


        TAB1Hlyt = QtWidgets.QHBoxLayout()
        ASSETLayout.addLayout(TAB1Hlyt)

        self.TAB1_Combo = QtWidgets.QComboBox()
        self.TAB1_Combo.addItems(self.firstLevelFolderList)
        self.TAB1_Combo.currentIndexChanged.connect(self.GetComboTAB1)


        self.TAB1_Combo.setCurrentText(ACTIVEMAINTAB)

        TAB1Hlyt.addWidget(self.TAB1_Combo)





        ##______________________________/     TAB 2
        ##Get SUBTABS Info

        self.secondLevelFolderList = os.listdir(ASSET_LIBRARY_PATH + "/" + ACTIVEMAINTAB)


        TAB2Hlyt = QtWidgets.QHBoxLayout()
        ASSETLayout.addLayout(TAB2Hlyt)

        try:
            FoundIndex = self.secondLevelFolderList.index(str(ACTIVESUBTAB_NAME))
        except:
            FoundIndex = 0


        self.TAB2_Combo = QtWidgets.QComboBox()
        self.TAB2_Combo.addItems(self.secondLevelFolderList)
        #self.TAB2_Combo.currentIndexChanged.connect(self.SET_Theme)
        self.TAB2_Combo.setCurrentIndex(FoundIndex)
        TAB2Hlyt.addWidget(self.TAB2_Combo)



        ##________________________________________// SEPARATOR
        separatorLine = QtWidgets.QLabel('')
        separatorLine.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separatorLine.setMaximumHeight(2)
        ASSETLayout.addWidget(separatorLine)






        ##________________________________________// SAVE MATERIAL
        self.SaveMaterial_GroupBox = QtWidgets.QGroupBox("/Save Material")
        self.SaveMaterial_GroupBox.setEnabled(True)
        self.SaveMaterial_GroupBox.setCheckable(1)
        if SAVEMATERIAL == 1:
            self.SaveMaterial_GroupBox.setChecked(1)
        else:
            self.SaveMaterial_GroupBox.setChecked(0)
        ASSETLayout.addWidget(self.SaveMaterial_GroupBox)
        self.SaveMaterialGBVLayout = QtWidgets.QVBoxLayout()
        self.SaveMaterial_GroupBox.setLayout(self.SaveMaterialGBVLayout)
        self.SaveMaterial_GroupBox.setMinimumWidth(360)
        self.SaveMaterial_GroupBox.setMinimumHeight(50)


        ###_____KEEP TEXTURE
        self.TextureLyt = QtWidgets.QHBoxLayout()
        self.TextureLyt.addSpacing(20)
        self.SaveMaterialGBVLayout.addLayout(self.TextureLyt)
        self.KeepOriginal = QtWidgets.QRadioButton("Don't copy textures to asset folder")
        if TEXTURECHOICE == 0:
            self.KeepOriginal.setChecked(1)
        else:
            self.KeepOriginal.setChecked(0)
        self.TextureLyt.addWidget(self.KeepOriginal)

        ###_____COPY TEXTURE
        self.TextureLyt2 = QtWidgets.QHBoxLayout()
        self.TextureLyt2.addSpacing(20)
        self.SaveMaterialGBVLayout.addLayout(self.TextureLyt2)
        self.CopyTexture = QtWidgets.QRadioButton("Copy textures to asset folder")
        if TEXTURECHOICE == 1:
            self.CopyTexture.setChecked(1)
        else:
            self.CopyTexture.setChecked(0)
        self.TextureLyt2.addWidget(self.CopyTexture)






        ##________________________________________// METADATA
        self.AssetInfo_GroupBox = QtWidgets.QGroupBox("/Asset Info")
        self.AssetInfo_GroupBox.setEnabled(True)
        self.AssetInfoGBVLayout = QtWidgets.QVBoxLayout()
        self.AssetInfo_GroupBox.setLayout(self.AssetInfoGBVLayout)
        self.AssetInfo_GroupBox.setMinimumWidth(360)
        self.AssetInfo_GroupBox.setMinimumHeight(50)
        ASSETLayout.addWidget(self.AssetInfo_GroupBox)

        self.AssetInfoField = QtWidgets.QLineEdit()
        self.AssetInfoField.setObjectName("AssetInfoField")
        self.AssetInfoField.setAlignment(QtCore.Qt.AlignCenter)
        self.AssetInfoField.setText(" ")
        self.AssetInfoField.setFixedHeight(30)
        #self.AssetInfoField.setStyleSheet("QLineEdit{color: #71CCFF;}")
        self.AssetInfoGBVLayout.addWidget(self.AssetInfoField)








        ##________________________________________// SEPARATOR
        separatorLine = QtWidgets.QLabel('')
        separatorLine.setStyleSheet( "QLabel {background-color: #3e3e3e; padding: 0; margin: 0; border-bottom: 1 solid #666; border-top: 1 solid #2a2a2a;}")
        separatorLine.setMaximumHeight(2)
        ASSETLayout.addWidget(separatorLine)


        ##_______________________________________ CREATE ASSET BTN
        CreateAssetBtn = QtWidgets.QPushButton()
        CreateAssetBtn.setObjectName("SaveSetting")
        CreateAssetBtn.setText("CREATE ASSET")
        CreateAssetBtn.setFixedHeight(30)
        CreateAssetBtn.clicked.connect(self.CreateAsset)
        CreateAssetBtn.setToolTip("Create and Add asset to Library")
        ASSETLayout.addWidget(CreateAssetBtn)



        ASSETLayout.addStretch()
        TOOLBARLayout.addStretch()

        #INIT
        mc.select(SELECTION)
        mc.viewFit("RenderThumbCam", all= False, f=1)
        mc.select(SELECTION, d=True)




    def set_ClayRenderBTN(self, checked):
        if checked == True:
            infoToSave = {"CLAY": 1}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'ClayPref.json', "w").write(s)

        else:
            infoToSave = {"CLAY": 0}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'ClayPref.json', "w").write(s)

    def set_SaveMatBTN(self):
        checked = self.SaveMaterial_GroupBox.isChecked()
        if checked == True:
            infoToSave = {"SAVEMAT": 1}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'SaveMat.json', "w").write(s)

        else:
            infoToSave = {"SAVEMAT": 0}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'SaveMat.json', "w").write(s)


    def set_TextureChoice(self):
        if self.KeepOriginal.isChecked():
            infoToSave = {"TEXTURECHOICE": 0}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'TextureChoice.json', "w").write(s)

        if self.CopyTexture.isChecked():
            infoToSave = {"TEXTURECHOICE": 1}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'TextureChoice.json', "w").write(s)


    def AssetNameValidate(self):
        AssetName = self.AssetNameFiel.text()

        if ":" in AssetName:
            AssetIt_Global.WarningWindow("You can't use ' : ' character in Asset Name", 250)
            return
        else:
            self.AssetNameFiel.clearFocus()
            self.AssetInfoField.clearFocus()





    def GetComboTAB1(self):
        content = self.TAB1_Combo.currentText()
        self.secondLevelFolderList = os.listdir(ASSET_LIBRARY_PATH + "/" + content)
        self.TAB2_Combo.clear()
        self.TAB2_Combo.addItems(self.secondLevelFolderList)

    def Apply(self):
        pass



    def CreateAsset(self):

        #VARIABLES
        getAssetName = self.AssetNameFiel.text()
        getMainTab = self.TAB1_Combo.currentText()
        getSecondTab = self.TAB2_Combo.currentText()
        ASSET_FOLDER = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName
        ASSET_PATH = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName + "/" + getAssetName
        FormatType = 'mayaAscii'


        #__________________________ASSET NAME
        ##  EMPTY
        if getAssetName == "":
            AssetIt_Global.WarningWindow("Please Enter an Asset Name", 250)
        else:
            print (ASSET_PATH)
            self.AssetNameFiel.clearFocus()

        AssetName = self.AssetNameFiel.text()

        if ":" in AssetName:
            AssetIt_Global.WarningWindow("You can't use ' : ' character in Asset Name", 250)
            return

        # CREATE ASSET FOLDER
        try:  ## Check if Asset Already EXIST
            os.mkdir(ASSET_FOLDER)
        except:
            AssetIt_Global.WarningWindow("An Asset with this name already exist in this folder", 400)
            return


        # EXPORT FILE and SAVE MATERIALS
        #Put at Root Hierarchie
        mc.select(SELECTION)
        saveHiera = mc.ls(sl=True, l=True)
        selInGroup = 0
        print("saveHiera =" + str(saveHiera))

        checkIfParent = mc.listRelatives(saveHiera, p=True, f=True)
        print("checkIfParent = " + str(checkIfParent))

        if checkIfParent == None:
            SELECTION_FULLPATH_MESHONLY = mc.ls(sl=1, type='mesh', dag=1, ni=1, l=True)
        else:
            getParentPath = mc.listRelatives(saveHiera, p=True, f=True)
            print("getParentPath" + str(getParentPath))
            rootSel = mc.parent(saveHiera, w=True)
            selInGroup = 1
            SELECTION_FULLPATH_MESHONLY = mc.ls(sl=True, l=True)




        if self.SaveMaterial_GroupBox.isChecked() == True:
            if self.CopyTexture.isChecked() == True:

                MATERIALS = []
                TEXTURE_LIST = []
                TEXTURE_LIST = []
                FILELIST = []
                ALL_MAT = []

                # Gets all shadingNode
                allChildren = cmds.listRelatives(ad=1, f=True, type="mesh")  # // MODIF ICI pour eviter de prendre les transform

                for eachChild in allChildren:  # POUR GET TOUS LES SHADERS ASSOCIE A LA SELECTION
                    get_SHAPE = cmds.listHistory(eachChild)
                    get_shader_SG = cmds.listConnections(get_SHAPE, s=True)  # Get the SG

                    print ("SHADER_GROUP ======== " + str(get_shader_SG))
                    MATERIALS = mc.ls(mc.listConnections(get_shader_SG), materials=True)  # Get the Material from the SG

                    ALL_MAT.extend(MATERIALS)
                    ALL_MAT_NODOUBLON = list(set(ALL_MAT))  # KILL DOUBLON!

                    print("MATERIALS = " + str(MATERIALS))
                    print("ALL MAT = " + str(ALL_MAT_NODOUBLON))
                    print(len(ALL_MAT_NODOUBLON))

                for each in ALL_MAT_NODOUBLON:  # POUR GET TOUS LES FILES_TEXTURE ASSOCIE AU SHADERS
                    MainShader = cmds.listHistory(each)
                    print("MainShader = " + str(MainShader))
                    listFileNode = mc.ls(MainShader, type="file")
                    print("listFileNode = " + str(listFileNode))
                    FILELIST.extend(listFileNode)


                try:
                    for each in FILELIST:
                        TEXTURE_PATH = mc.getAttr(each + ".fileTextureName")
                        TEXTURE_NAME = TEXTURE_PATH.split("/")[-1]
                        TEXTURE_DEST = ASSET_FOLDER  + "/" + TEXTURE_NAME
                        TEXTURE_LIST.append(mc.getAttr(each + ".fileTextureName"))

                        if TEXTURE_PATH == "":
                            print ("Pass Empty")
                            pass
                        else:
                            shutil.copyfile(TEXTURE_PATH, TEXTURE_DEST)

                except:
                    os.rmdir(ASSET_FOLDER)
                    AssetIt_Global.WarningWindow("There no texture on this selection", 400)
                    return

                print ("DEBUG : MATERIALS = " + str(MATERIALS))
                print ("DEBUG : TEXTURE_PATH = " + str(TEXTURE_LIST))
                print ("DEBUG : TEXTURE_NUMBER = " + str(len(TEXTURE_LIST)))
                print ("DEBUG : FILELIST = " + str(FILELIST))
                print ("DEBUG : FILELIST_LEN = " + str(len(FILELIST)))








            else:#KEEP ORIGINAL
                # Just pour avoir le Texture Number
                MATERIALS = []
                TEXTURE_LIST = []
                for eachChild in SELECTION_FULLPATH_MESHONLY:
                    # Get the shader groups attached to this particular object
                    shaderGroups = cmds.listConnections(cmds.listHistory(eachChild))
                    mat = cmds.ls(cmds.listConnections(shaderGroups), materials=1)
                    MATERIALS.append(mat[0])
                # Gets all the files
                listFileNode = mc.listConnections(MATERIALS, type="file")

                try:
                    # Gets Texture Path
                    for each in listFileNode:
                        TEXTURE_PATH = mc.getAttr(each + ".fileTextureName")
                        TEXTURE_LIST.append(mc.getAttr(each + ".fileTextureName"))
                except:
                    pass


            # EXPORT FILE
            mc.select(SELECTION)
            mc.file(ASSET_PATH, force=True, type= FormatType, exportSelected=True)

        else:
            MATERIALS = []
            TEXTURE_LIST = []
            GroupOrigin = mc.group(SELECTION, n="GroupDupTemp")
            GroupExport = mc.duplicate(GroupOrigin, n="GroupForExport")
            mc.ungroup("GroupForExport")
            DUPSEL = mc.ls(sl=True)
            mc.hyperShade(a="lambert1")

            # EXPORT FILE
            mc.file(ASSET_PATH, force=True, type= FormatType, exportSelected=True)
            mc.delete()
            mc.ungroup("GroupDupTemp")

            # Set for RENDERTHUMB
            self.ClayRenderBTN.setChecked(1)


        #CHECK IF RENDERTHUMB IS DONE
        if RENDERDONE == False:
            self.RENDERTHUMB()



        #EXPORT THUMB
        src = ASSET_CREATION_PATH + "/RenderThumbTemp.png"
        dest = ASSET_PATH + ".png"
        print (src)
        print (dest)
        shutil.copyfile(src, dest)


        #METADATA
        print ("RENDERCHOICE = " + RENDERERCHOICE)
        AssetInfo = self.AssetInfoField.text()
        print ("AssetInfo = " + AssetInfo)
        TextureSaved = self.SaveMaterial_GroupBox.isChecked()
        print ("TextureSaved = " + str(TextureSaved))
        if self.KeepOriginal.isChecked() == 1:
            TextureChoice = "KeepOriginal"
        else:
            TextureChoice = "CopyWithAsset"
        print ("TextureChoice = " + str(TextureChoice))

        # Data to be written
        Metadata = {
            "RenderChoice": RENDERERCHOICE,
            "TextureChoice": TextureChoice,
            "TextureSaved": TextureSaved,
            "TextureNbr": len(TEXTURE_LIST),
            "UserInfo": AssetInfo

        }
        json_metadata = json.dumps(Metadata, indent=5)
        open(ASSET_PATH + '.json', "w").write(json_metadata)
        print ("JSON = " + ASSET_PATH + '.json')


        #KEEP BACK RIGHT TABS
        MainTabIndex = self.TAB1_Combo.currentIndex()
        SecondTabIndex = self.TAB2_Combo.currentIndex()

        FirstTabinfoToSave = {"TAB_OPEN" : MainTabIndex}
        s = json.dumps(FirstTabinfoToSave)
        open(PreferencePath + 'TabOpen.json', "w").write(s)

        SecondTabinfoToSave = {"TAB_OPEN" : SecondTabIndex}
        s = json.dumps(SecondTabinfoToSave)
        open(PreferencePath + 'TabOpenSecond.json', "w").write(s)


        self.set_SaveMatBTN()
        self.set_TextureChoice()

        #Back to hierarchi Group
        if selInGroup == 1:
            mc.parent(SELECTION, getParentPath)


        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()

        mc.flushUndo()

    def updatingProgressBar(self):
        self.step += 1
        self.progress_dialog.setLabelText("{0} : {1}(of {2})".format(self.opName,self.step, self.number_of_operations))
        self.progress_dialog.setValue(self.step)
        QtCore.QCoreApplication.processEvents()



    def RENDERTHUMB(self):
        RENDERTEMPPATH = AssetCreationPath + "/RenderThumbTemp.png"
        DESTPATH = AssetCreationPath + "/RenderThumbTemp"

        #__________________________ P R O G R E S S B A R
        self.number_of_operations = 3
        self.step = 0
        self.opName = "Thumbnail Rendering..."
        self.progress_dialog = QtWidgets.QProgressDialog("Thumbnail Rendering", "", 0, self.number_of_operations, self)
        self.progress_dialog.setWindowTitle("Thumbnail Rendering...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setMinimumSize(550, 80)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.show()

        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Thumbnail Rendering..."

        ##_______________________________________________________________________________
        ##________________________________________________________________________________________RENDER == ARNOLD
        ##_______________________________________________________________________________
        if RENDERERCHOICE == "Arnold":

            #Disable to don't have light scene user affect the render
            mel.eval("optionVar -iv renderSetup_includeAllLights 0;")



            ##____________________________// RENDER SETUP - INIT
            ##________________________/
            if self.ClayRenderBTN.isChecked()==1:
                rs = renderSetup.instance()
                # Create and append the render layer
                rl = rs.createRenderLayer("AssetIt_Layer")
                # Create and append the collections
                c1 = rl.createCollection("AssetIt_Thumb_Collection")

                # Add Selection
                selection = ""
                for each in SELECTION:
                    selection += each + ", "
                c1.getSelector().setPattern(str(selection)+"AssetIt_SkyDome")


                # Shader override
                s1 = c1.createOverride('AssetIt_Thumb_ShaderOverride', typeIDs.shaderOverride)
                s1.setShader("AssetIt_Thumb_shd")

                # Switch to Isolate
                rs.switchToLayer(rl)

            else:
                rs = renderSetup.instance()
                # Create and append the render layer
                rl = rs.createRenderLayer("AssetIt_Layer")
                # Create and append the collections
                c1 = rl.createCollection("AssetIt_Thumb_Collection")

                # Add Selection
                selection = ""
                for each in SELECTION:
                    selection += each + ", "
                c1.getSelector().setPattern(str(selection)+"AssetIt_SkyDome")

                # Switch to Isolate
                rs.switchToLayer(rl)


            mc.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

            ##________________________________________________________________________________________GET RENDERSETTING USER PREF
            R_width = mc.getAttr ("defaultResolution.width")
            R_height = mc.getAttr ("defaultResolution.height")
            R_ratio = mc.getAttr ("defaultResolution.deviceAspectRatio")
            R_pixelAspect = mc.getAttr("defaultResolution.pixelAspect")
            R_AASamples = mc.getAttr("defaultArnoldRenderOptions.AASamples")
            R_GIDiffuse = mc.getAttr("defaultArnoldRenderOptions.GIDiffuseSamples")
            R_GISpecular = mc.getAttr("defaultArnoldRenderOptions.GISpecularSamples")
            R_GISss = mc.getAttr("defaultArnoldRenderOptions.GISssSamples")
            R_Path = mc.getAttr("defaultRenderGlobals.imageFilePrefix")
            try:
                R_Format = mc.getAttr("defaultArnoldDriver.ai_translator")
            except:
                R_Format = "exr"

            try:
                R_ColorManagement = mc.getAttr("defaultArnoldDriver.colorManagement")
            except:
                R_ColorManagement = 1


            ##________________________________________________________________________________________ARNOLD THUMB


            mc.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')  # Set curent render
            mc.setAttr('defaultArnoldDriver.aiTranslator', 'png', type='string')  # Set the TIF image format
            mc.setAttr('defaultArnoldDriver.prefix', DESTPATH, type='string')  # TO SAVE IMG TO DESTINATION PATH
            mc.setAttr('defaultArnoldRenderOptions.renderDevice', 0)  # CPU rendering


            mc.setAttr ("defaultResolution.width", 400)
            mc.setAttr ("defaultResolution.height", 400)
            mc.setAttr ("defaultResolution.deviceAspectRatio", 1)
            mc.setAttr("defaultResolution.pixelAspect", 1)
            mc.setAttr("defaultArnoldRenderOptions.AASamples", 5)
            mc.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", 4)
            mc.setAttr("defaultArnoldRenderOptions.GISpecularSamples", 1)
            mc.setAttr("defaultArnoldRenderOptions.GISssSamples", 4)

            ##POUR LE BACKGROUND
            try:
                mc.connectAttr("AssetIt_Background.message", "defaultArnoldRenderOptions.background")
            except:
                pass

            mc.colorManagementPrefs(e=True, outputTransformEnabled=True, outputUseViewTransform=True)  # Color Management Prefs
            mc.arnoldRender(width= 400, height= 400, camera="RenderThumbCam")  # render and save the image

            # ______________________________ SET CREATION

            # FIX "_1" naming :
            old_name = DESTPATH + '_1.png'
            new_name = DESTPATH + '.png'

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)

            self.ThumbLabel.setPixmap(QtGui.QPixmap(RENDERTEMPPATH))

            # PROGRESBAR UPDATING
            self.updatingProgressBar()
            self.opName = "Updating Thumbnail"
            ##______________________________ END CLEAN
            mel.eval("optionVar -iv renderSetup_includeAllLights 1;")


            # Go back to defaultw
            renderLayer.delete(rl)

            ##________________________________________________________________________________________REVERT BACK RENDERSETTING USER PREF
            mc.setAttr ("defaultResolution.width", R_width)
            mc.setAttr ("defaultResolution.height", R_height)
            mc.setAttr ("defaultResolution.deviceAspectRatio", R_ratio)
            mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)
            mc.setAttr("defaultArnoldRenderOptions.AASamples", R_AASamples)
            mc.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", R_GIDiffuse)
            mc.setAttr("defaultArnoldRenderOptions.GISpecularSamples", R_GISpecular)
            mc.setAttr("defaultArnoldRenderOptions.GISssSamples", R_GISss)
            mc.setAttr("defaultRenderGlobals.imageFilePrefix", str(R_Path), type='string' )
            mc.setAttr("defaultArnoldDriver.ai_translator", str(R_Format), type='string')
            mc.setAttr("defaultArnoldDriver.colorManagement", R_ColorManagement)

            mc.disconnectAttr("AssetIt_Background.message", "defaultArnoldRenderOptions.background")

        if RENDERERCHOICE == "Viewport":
            print("VIEWPORT RENDER MODE")

            imageSize = 400
            CameraName = "RenderThumbCamShape"
            mc.lookThru(CameraName)
            getOverValue = mc.getAttr(CameraName + ".overscan")

            mc.setAttr(CameraName + ".displayResolution", 0)
            mc.setAttr(CameraName + ".overscan", 1)

            mc.playblast(startTime=1, endTime=1, widthHeight=[imageSize, imageSize], format="image", filename=DESTPATH,
                         sequenceTime=True, clearCache=1, fo=True, viewer=1, showOrnaments=0, fp=4, percent=100, compression="png",
                         quality=80)

            mc.setAttr(CameraName + ".displayResolution", 1)
            mc.setAttr(CameraName + ".overscan", getOverValue)


            # FIX "_1" naming :
            old_name = DESTPATH + '.0001.png'
            new_name = DESTPATH + '.png'

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)


            self.ThumbLabel.setPixmap(QtGui.QPixmap(new_name))

        if RENDERERCHOICE == "Redshift":
            print("REDSHIFT RENDER MODE")
            #ISOLATE SELECTION
            mc.select(SELECTION, "AssetIt_Thumb_Group")
            mc.HideUnselectedObjects()
            ##________________________________________________________________________________________GET RENDERSETTING USER PREF
            R_width = mc.getAttr ("defaultResolution.width")
            R_height = mc.getAttr ("defaultResolution.height")
            R_ratio = mc.getAttr ("defaultResolution.deviceAspectRatio")
            R_pixelAspect = mc.getAttr("defaultResolution.pixelAspect")

            ##__________________________________________________________________________________ SET RENDERSETTING
            mc.setAttr("defaultRenderGlobals.currentRenderer", "redshift", type="string")  # Set curent render
            mc.setAttr('redshiftOptions.imageFormat', 2)  # Set the PNG image format / for TIFF - 5
            mc.setAttr("defaultRenderGlobals.imageFilePrefix", DESTPATH ,type="string")  # Set the path where the image is saved
            mc.setAttr("redshiftOptions.subsurfaceScatteringRate", -1)  # -3...3

            mc.setAttr ("defaultResolution.width", R_width)
            mc.setAttr ("defaultResolution.height", R_height)
            mc.setAttr ("defaultResolution.deviceAspectRatio", R_ratio)
            mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)

            mc.rsRender(render=True, blk=True, cam='RenderThumbCam', resolution=[400, 400])  # render and save the image
            mc.showHidden(all=True)
            # FIX "_1" naming :
            old_name = DESTPATH + '_tmp.png'
            new_name = DESTPATH + '.png'

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)


            ##________________________________________________________________________________________REVERT BACK RENDERSETTING USER PREF
            mc.setAttr ("defaultResolution.width", R_width)
            mc.setAttr ("defaultResolution.height", R_height)
            mc.setAttr ("defaultResolution.deviceAspectRatio", R_ratio)
            mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)

            self.ThumbLabel.setPixmap(QtGui.QPixmap(new_name))

        if RENDERERCHOICE == "Vray":
            print("VRAY RENDER MODE")
            #ISOLATE SELECTION
            mc.select(SELECTION, "AssetIt_Thumb_Group")
            mc.HideUnselectedObjects()


            mc.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

            ##________________________________________________________________________________________GET RENDERSETTING USER PREF
            mc.setAttr("vraySettings.width", 400)
            mc.setAttr("vraySettings.height", 400)

            #//
            mc.vray("showVFB")
            mc.vrend(camera="RenderThumbCam")
            mc.vray("vfbControl", "-saveimage", RENDERTEMPPATH)

            mc.showHidden(all=True)
            self.ThumbLabel.setPixmap(QtGui.QPixmap(RENDERTEMPPATH))

            # PROGRESBAR UPDATING
            self.updatingProgressBar()
            self.opName = "Updating Thumbnail"

        if RENDERERCHOICE == "Vray":
            pass
        else:
            self.ThumbLabel.setPixmap(QtGui.QPixmap(new_name))


        ##_______________________________________________________________________________
        ##________________________________________________________________________________________DONE
        ##_______________________________________________________________________________
        global RENDERDONE
        RENDERDONE = True
        # __________________________ E N D I N G
        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Plug Created."
        self.progress_dialog.close()

        #DONE
        mc.flushUndo()
        print ("ASSET RENDER")


    def PlaceCamera(self):

        importlib.reload(AsssetIt_CameraThumb)
        AsssetIt_CameraThumb.SEND_INFO(SELECTION)
        AsssetIt_CameraThumb.showUI()


    def set_Arnold(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Arnold"
        self.ClayRenderBTN.show()
        self.SeparatorToHide.show()
        infoToSave = {"Renderer": "Arnold"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)

        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp_Off.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))

        #Update Import Arnold Scene
        if mc.objExists("AssetIt_Thumb_Group"):
            mc.delete("AssetIt_Thumb_Group")
        mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)


    def set_Vray(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Vray"
        self.ClayRenderBTN.hide()
        self.SeparatorToHide.hide()
        infoToSave = {"Renderer": "Vray"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)

        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray.png"))
        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp_Off.png"))

        #Update Import Redshift Scene
        if mc.objExists("AssetIt_Thumb_Group"):
            mc.delete("AssetIt_Thumb_Group")
        mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Vray_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)
        mel.eval('setAttr"vraySettings.pixelAspect"1;')




    def set_Redshift(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Redshift"
        self.ClayRenderBTN.hide()
        self.SeparatorToHide.hide()
        infoToSave = {"Renderer": "Redshift"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)


        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift.png"))
        self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp_Off.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))

        #Update Import Redshift Scene
        if mc.objExists("AssetIt_Thumb_Group"):
            mc.delete("AssetIt_Thumb_Group")
        mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Redshift_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)


    def set_Viewport(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Viewport"
        self.ClayRenderBTN.hide()
        self.SeparatorToHide.hide()
        infoToSave = {"Renderer": "Viewport"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)


        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VpBTN.setIcon(QtGui.QIcon(IconPath + "Vp.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))

        # Update Import Arnold Scene
        if mc.objExists("AssetIt_Thumb_Group"):
            mc.delete("AssetIt_Thumb_Group")
        mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene.ma", rnn=True, i=True,         ignoreVersion=True, mergeNamespacesOnClash=False)




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

def atClose():
    if mc.window("Thumbnail Framing", exists=True):
        mc.deleteUI("Thumbnail Framing")


    if mc.objExists("AssetIt_Thumb_Group"):
        mc.delete("AssetIt_Thumb_Group")
        if mc.objExists("AssetIt_Thumb_shd"):
            mc.delete("AssetIt_Thumb_shd")
        mc.delete("AssetIt_ThumbScene_HDR")
        mc.delete("AssetI_ThumbScene_place2dTexture")
        if mc.objExists("AssetIt_Thumb_Scene_uiConfigurationScriptNode"):
            mc.delete("AssetIt_Thumb_Scene_uiConfigurationScriptNode")
        if mc.objExists("AssetIt_Thumb_Scene_sceneConfigurationScriptNode"):
            mc.delete("AssetIt_Thumb_Scene_sceneConfigurationScriptNode")
        if mc.objExists("AssetIt_Background"):
            mc.delete("AssetIt_Background")

    mc.select(SELECTION)




def showUI():
    ui = Dock(AddAsset_UI)
    ui.show()

    if mc.window("Thumbnail Framing", exists=True):
        mc.deleteUI("Thumbnail Framing")


    # Get a pointer and convert it to Qt Widget object
    qw = omui.MQtUtil.findWindow(WindowsTitle)
    widget = wrapInstance(int(qw), QWidget)
    # Create a QIcon object
    icon = QIcon(IconPath + "Windows_Ico2.png")
    # Assign the icon
    widget.setWindowIcon(icon)
    mc.scriptJob(uiDeleted=['Add Asset', atClose])

    return ui

