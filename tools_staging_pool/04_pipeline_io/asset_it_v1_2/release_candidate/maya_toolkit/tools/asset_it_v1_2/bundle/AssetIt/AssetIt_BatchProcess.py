
##                                         BATCH PROCESS
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

from shutil import move
from shutil import copytree
from shutil import rmtree


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
WindowsTitle = "Multi Asset Creation from Files"
ASSET_LIBRARY_PATH = AssetIt_Global.ASSET_LIBRARY_PATH
ASSET_FAVOURITES_PATH = AssetIt_Global.ASSET_FAVOURITES_PATH
ASSET_CREATION_PATH = AssetIt_Global.AssetCreationPath
ACTIVEMAINTAB = ""
ACTIVESUBTAB_NAME = ""



def SEND_INFO(MainTabActiveName, SecondTabActiveName):
    global ACTIVEMAINTAB
    ACTIVEMAINTAB = MainTabActiveName

    global ACTIVESUBTAB_NAME
    ACTIVESUBTAB_NAME = SecondTabActiveName

    return ACTIVEMAINTAB + ACTIVESUBTAB_NAME


##UI INFO
# ________________//
class BatchProcess_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BatchProcess_UI, self).__init__()
        self.setMinimumSize(500, 505)
        self.buildUI()


    def buildUI(self):
        BATCH_MAINLayout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_Global.Theme)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize

        ##_________________________________________________________________//  FOLDER
        ## LABEL
        Folder_Label = QtWidgets.QLabel(self)
        Folder_Label.setText("Meshes to import folder :")
        BATCH_MAINLayout.addWidget(Folder_Label)

        ## PATH FIELD
        FolderPathHlyt = QtWidgets.QHBoxLayout()
        BATCH_MAINLayout.addLayout(FolderPathHlyt)
        FolderPathHlyt.setAlignment(QtCore.Qt.AlignCenter)

        spacer = QtWidgets.QLabel(self)
        spacer.setText("    ")
        FolderPathHlyt.addWidget(spacer)

        self.UserFoldePathField = QtWidgets.QLineEdit()
        self.UserFoldePathField.setObjectName("UserLibPathField")
        FolderPathHlyt.addWidget(self.UserFoldePathField)


        ## FOLDER PATH BTN
        FolderPathBTN = QtWidgets.QPushButton()
        FolderPathBTN.setFixedSize(iconButtonSize,iconButtonSize)
        FolderPathBTN.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        FolderPathBTN.setIcon(QtGui.QIcon(IconPath + "Folder2.png"))
        FolderPathBTN.clicked.connect(self.SET_FolderPath)
        FolderPathBTN.setToolTip("  Choose the meshes folder  ")
        FolderPathBTN.setShortcut(QtGui.QKeySequence("Return"))
        FolderPathHlyt.addWidget(FolderPathBTN)


        ##____________________________________________________________// RENDER CHOICE
        self.Renderer_GroupBox = QtWidgets.QGroupBox("/ Render Engine Choice")
        self.Renderer_GroupBox.setEnabled(True)

        BATCH_MAINLayout.addWidget(self.Renderer_GroupBox)
        self.RendererGBVLayout = QtWidgets.QHBoxLayout()
        self.Renderer_GroupBox.setLayout(self.RendererGBVLayout)
        self.Renderer_GroupBox.setMinimumWidth(360)
        self.Renderer_GroupBox.setMinimumHeight(50)

        ###_____ARNOLD
        self.ARNOLDLyt = QtWidgets.QHBoxLayout()
        self.ARNOLDLyt.addSpacing(15)
        self.RendererGBVLayout.addLayout(self.ARNOLDLyt)
        self.Arnoldcheck = QtWidgets.QRadioButton("Arnold")
        self.Arnoldcheck.setChecked(1)
        self.ARNOLDLyt.addWidget(self.Arnoldcheck)

        ###_____REDSHIFT
        self.REDSHIFTLyt = QtWidgets.QHBoxLayout()
        self.REDSHIFTLyt.addSpacing(15)
        self.RendererGBVLayout.addLayout(self.REDSHIFTLyt)
        self.Redshiftcheck = QtWidgets.QRadioButton("Redshift")
        self.REDSHIFTLyt.addWidget(self.Redshiftcheck)

        ###_____VRAY
        self.VRAYLyt = QtWidgets.QHBoxLayout()
        self.VRAYLyt.addSpacing(15)
        self.RendererGBVLayout.addLayout(self.VRAYLyt)
        self.Vraycheck = QtWidgets.QRadioButton("Vray")
        self.VRAYLyt.addWidget(self.Vraycheck)





















        ##____________________________________________________________// FORMAT TO IMPORT
        self.Format_GroupBox = QtWidgets.QGroupBox("/ Format to import")
        self.Format_GroupBox.setEnabled(True)

        BATCH_MAINLayout.addWidget(self.Format_GroupBox)
        self.FormatGBVLayout = QtWidgets.QHBoxLayout()
        self.Format_GroupBox.setLayout(self.FormatGBVLayout)
        self.Format_GroupBox.setMinimumWidth(360)
        self.Format_GroupBox.setMinimumHeight(50)

        ###_____MA
        self.MALyt = QtWidgets.QHBoxLayout()
        self.MALyt.addSpacing(15)
        self.FormatGBVLayout.addLayout(self.MALyt)
        self.MAcheck = QtWidgets.QRadioButton(".ma")
        self.MAcheck.setChecked(1)
        self.MALyt.addWidget(self.MAcheck)

        ###_____MB
        self.MBLyt = QtWidgets.QHBoxLayout()
        self.MBLyt.addSpacing(15)
        self.FormatGBVLayout.addLayout(self.MBLyt)
        self.MBcheck = QtWidgets.QRadioButton(".mb")
        self.MBLyt.addWidget(self.MBcheck)

        ###_____OBJ
        self.OBJLyt = QtWidgets.QHBoxLayout()
        self.OBJLyt.addSpacing(15)
        self.FormatGBVLayout.addLayout(self.OBJLyt)
        self.OBJcheck = QtWidgets.QRadioButton(".obj")
        self.OBJLyt.addWidget(self.OBJcheck)

        ###_____FBX
        self.FBXLyt = QtWidgets.QHBoxLayout()
        self.FBXLyt.addSpacing(15)
        self.FormatGBVLayout.addLayout(self.FBXLyt)
        self.FBXcheck = QtWidgets.QRadioButton(".fbx")
        self.FBXLyt.addWidget(self.FBXcheck)

        ###_____ABC
        self.ABCLyt = QtWidgets.QHBoxLayout()
        self.ABCLyt.addSpacing(15)
        self.FormatGBVLayout.addLayout(self.ABCLyt)
        self.ABCcheck = QtWidgets.QRadioButton(".abc")
        self.ABCLyt.addWidget(self.ABCcheck)



        ##_______________________________________________________// TABS
        self.Tabs_GroupBox = QtWidgets.QGroupBox("/ Asset destination")
        self.Tabs_GroupBox.setEnabled(True)

        BATCH_MAINLayout.addWidget(self.Tabs_GroupBox)
        self.TabGBVLayout = QtWidgets.QHBoxLayout()
        self.Tabs_GroupBox.setLayout(self.TabGBVLayout)
        self.Tabs_GroupBox.setMinimumWidth(360)
        self.Tabs_GroupBox.setMinimumHeight(50)



        ##______________________________/       TAB 1

        MAINTABPATH = os.listdir(ASSET_LIBRARY_PATH)
        SUBTABPATH = os.listdir(ASSET_LIBRARY_PATH + "/" + MAINTABPATH[0])


        self.firstLevelFolderList = os.listdir(ASSET_LIBRARY_PATH)

        TAB1Hlyt = QtWidgets.QHBoxLayout()
        self.TabGBVLayout.addLayout(TAB1Hlyt)
        self.TAB1_Combo = QtWidgets.QComboBox()
        self.TAB1_Combo.addItems(MAINTABPATH)
        self.TAB1_Combo.currentIndexChanged.connect(self.GetComboTAB1)

        self.TAB1_Combo.setCurrentText(ACTIVEMAINTAB)

        TAB1Hlyt.addWidget(self.TAB1_Combo)


        ##______________________________/     TAB 2

        self.secondLevelFolderList = os.listdir(ASSET_LIBRARY_PATH + "/" + ACTIVEMAINTAB)

        TAB2Hlyt = QtWidgets.QHBoxLayout()
        self.TabGBVLayout.addLayout(TAB2Hlyt)

        try:
            FoundIndex = self.secondLevelFolderList.index(str(ACTIVESUBTAB_NAME))
        except:
            FoundIndex = 0




        self.TAB2_Combo = QtWidgets.QComboBox()
        self.TAB2_Combo.addItems(self.secondLevelFolderList)
        #self.TAB2_Combo.currentIndexChanged.connect(self.SET_Theme)
        self.TAB2_Combo.setCurrentIndex(FoundIndex)
        TAB2Hlyt.addWidget(self.TAB2_Combo)





        ##__________________________________________________________________________________________// SAVE MATERIAL
        self.SaveMaterial_GroupBox = QtWidgets.QGroupBox("/ Save Material" )
        self.SaveMaterial_GroupBox.setEnabled(True)
        self.SaveMaterial_GroupBox.setCheckable(1)
        self.SaveMaterial_GroupBox.setChecked(1)
        BATCH_MAINLayout.addWidget(self.SaveMaterial_GroupBox)
        self.SaveMaterialGBVLayout = QtWidgets.QVBoxLayout()
        self.SaveMaterial_GroupBox.setLayout(self.SaveMaterialGBVLayout)
        self.SaveMaterial_GroupBox.setMinimumWidth(360)
        self.SaveMaterial_GroupBox.setMinimumHeight(50)


        ###_____KEEP TEXTURE
        self.TextureLyt = QtWidgets.QHBoxLayout()
        self.TextureLyt.addSpacing(20)
        self.SaveMaterialGBVLayout.addLayout(self.TextureLyt)
        self.KeepOriginal = QtWidgets.QRadioButton("Don't copy textures to asset folder")
        self.KeepOriginal.setChecked(1)
        self.TextureLyt.addWidget(self.KeepOriginal)

        ###_____COPY TEXTURE
        self.TextureLyt2 = QtWidgets.QHBoxLayout()
        self.TextureLyt2.addSpacing(20)
        self.SaveMaterialGBVLayout.addLayout(self.TextureLyt2)
        self.CopyTexture = QtWidgets.QRadioButton("Copy textures to asset folder")
        self.CopyTexture.setChecked(0)
        self.TextureLyt2.addWidget(self.CopyTexture)

        ##__________________________________________________________________________________// PIVOTS
        self.Pivot_GroupBox = QtWidgets.QGroupBox("/ Pivot")
        self.Pivot_GroupBox.setEnabled(True)

        BATCH_MAINLayout.addWidget(self.Pivot_GroupBox)
        self.PivotGBVLayout = QtWidgets.QHBoxLayout()
        self.Pivot_GroupBox.setLayout(self.PivotGBVLayout)
        self.Pivot_GroupBox.setMinimumWidth(360)
        self.Pivot_GroupBox.setMinimumHeight(50)
        self.Pivot_GroupBox.setEnabled(True)
        self.Pivot_GroupBox.setCheckable(1)
        self.Pivot_GroupBox.setChecked(0)

        ## BTN PIVOT ORIGIN GRID
        self.PivotOriginGridLyt = QtWidgets.QHBoxLayout()
        self.PivotOriginGridLyt.addSpacing(10)
        self.PivotGBVLayout.addLayout(self.PivotOriginGridLyt)
        # self.PivotOriginGrid.clicked.connect(self.PivotGrid)
        self.PivotOriginGrid = QtWidgets.QRadioButton("Grid Base")
        self.PivotOriginGrid.setChecked(1)
        self.PivotOriginGrid.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.PivotOriginGrid.setIcon(QtGui.QIcon(IconPath + "AlignGridBase.png"))
        self.PivotOriginGrid.setToolTip("  Pivot at Bottom and Grid Origin  ")
        self.PivotOriginGridLyt.addWidget(self.PivotOriginGrid)

        ## BTN PIVOT BASE GRID
        self.GridCenterLyt = QtWidgets.QHBoxLayout()
        self.GridCenterLyt.addSpacing(10)
        self.PivotGBVLayout.addLayout(self.GridCenterLyt)
        self.GridCenter = QtWidgets.QRadioButton("Grid Origin")
        # self.GridCenter.clicked.connect(self.GridCenter)
        self.GridCenter.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.GridCenter.setIcon(QtGui.QIcon(IconPath + "AlignGrid.png"))
        self.GridCenter.setToolTip("  Object at Grid Center  ")
        self.GridCenterLyt.addWidget(self.GridCenter)

        ## BTN PIVOT BOTTOM
        self.PivotBottomLyt = QtWidgets.QHBoxLayout()
        self.PivotBottomLyt.addSpacing(10)
        self.PivotGBVLayout.addLayout(self.PivotBottomLyt)
        self.PivotBottom = QtWidgets.QRadioButton("Pivot Base")
        # self.PivotBottom.clicked.connect(self.PivotBottom)
        self.PivotBottom.setToolTip("  Pivot at Object Bottom  ")
        self.PivotBottom.setIconSize(QtCore.QSize(iconButtonSize, iconButtonSize))
        self.PivotBottom.setIcon(QtGui.QIcon(IconPath + "AlignPivotBase.png"))
        self.PivotBottomLyt.addWidget(self.PivotBottom)

        #######__________________________________________________________________________________// CREATE ASSET BTN
        TOOLBARLayout = QtWidgets.QHBoxLayout(self)
        BATCH_MAINLayout.addLayout(TOOLBARLayout)

        ##_______________________________________ CREATE ASSET BTN
        CreateAssetBtn = QtWidgets.QPushButton()
        CreateAssetBtn.setObjectName("SaveSetting")
        CreateAssetBtn.setText("CREATE ASSET")
        CreateAssetBtn.setFixedHeight(30)
        CreateAssetBtn.clicked.connect(self.CREATE_ASSET)
        CreateAssetBtn.setToolTip("Create and Add asset to Library")
        BATCH_MAINLayout.addWidget(CreateAssetBtn)



        BATCH_MAINLayout.addStretch()
        TOOLBARLayout.addStretch()


    def GetComboTAB1(self):
        content = self.TAB1_Combo.currentText()
        self.secondLevelFolderList = os.listdir(ASSET_LIBRARY_PATH + "/" + content)
        self.TAB2_Combo.clear()
        self.TAB2_Combo.addItems(self.secondLevelFolderList)



    def set_TextureChoice(self):
        if self.KeepOriginal.isChecked():
            infoToSave = {"TEXTURECHOICE": 0}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'TextureChoice.json', "w").write(s)

        if self.CopyTexture.isChecked():
            infoToSave = {"TEXTURECHOICE": 1}
            s = json.dumps(infoToSave)
            open(PreferencePath + 'TextureChoice.json', "w").write(s)

    def SET_FolderPath(self):
        Path = mc.fileDialog2(ds=1, cap="Select a folder", fm=3)
        PathFolder = Path[0]
        self.UserFoldePathField.setText(PathFolder)


    def updatingProgressBar(self):
        self.step += 1
        self.progress_dialog.setLabelText("{0} : {1}(of {2})".format(self.opName,self.step, self.number_of_operations))
        self.progress_dialog.setValue(self.step)
        QtCore.QCoreApplication.processEvents()


    def CREATE_ASSET(self):
        #VARIABLES
        MESHFOLDER = self.UserFoldePathField.text()

        getMainTab = self.TAB1_Combo.currentText()
        getSecondTab = self.TAB2_Combo.currentText()

        if self.MAcheck.isChecked():
            FormatType = 'mayaAscii'
            FormatExt = ".ma"
        if self.MBcheck.isChecked():
            FormatType = 'mayaBinary'
            FormatExt = ".mb"
        if self.OBJcheck.isChecked():
            FormatType = 'OBJ'
            FormatExt = ".obj"
        if self.FBXcheck.isChecked():
            FormatType = 'Fbx'
            FormatExt = ".fbx"
        if self.ABCcheck.isChecked():
            FormatType = 'Alembic'
            FormatExt = ".abc"

        if self.Arnoldcheck.isChecked():
            RENDERERCHOICE = "Arnold"
        if self.Redshiftcheck.isChecked():
            RENDERERCHOICE = "Redshift"
        if self.Vraycheck.isChecked():
            RENDERERCHOICE = "Vray"

        print("FUCKING CHOICE = " + str(RENDERERCHOICE))
        print("FUCKING FORMAT = " + str(FormatType))


        #ASSET_FOLDER = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName
        #ASSET_PATH = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName + "/" + getAssetName

        #__________________________ASSET NAME
        ##  EMPTY
        if MESHFOLDER == "":
            AssetIt_Global.WarningWindow("You should choose a folder", 250)

        # NOT ON SAME DRIVE BUG
        USERAPPDIR_HDD_LETTER = mc.internalVar(userAppDir=True).split("/")[0]
        MESHFOLDER_HDD_LETTER = MESHFOLDER.split("/")[0]


        if MESHFOLDER_HDD_LETTER != USERAPPDIR_HDD_LETTER :
            AssetIt_Global.WarningWindow("The chosen folder should be located on the same Hard Drive then Maya is installed.", 450)
            return






        listFolder = os.listdir(MESHFOLDER)
        LIST = []

        for each in listFolder:
            print (each)
            if each.endswith(str(FormatExt)):
                LIST.append(each)

        ## IF WRONG CHOOSE FORMAT
        if LIST == []:
           print(LIST)
           AssetIt_Global.WarningWindow("The import format selected doesn't correspond to files in folder.", 350)
           return


        ##__________________________________________________________
        ##_______________________________________________________________________________________________________________________________// PROCESS
        ##__________________________________________________________

        ###_______________________________________PROGRESSBAR
        self.number_of_operations = len(LIST)+1
        self.step = 0
        self.opName = "Batch Process Starting"
        self.progress_dialog = QtWidgets.QProgressDialog("Batch Process", "", 0, self.number_of_operations, self)
        self.progress_dialog.setWindowTitle("Batch Process...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setMinimumSize(550, 80)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.show()


        for each in LIST:
            ##________________________________________________________________________________________INIT
            ASSET_NAME = each.replace(str(FormatExt), "")
            #Create Asset Folder
            os.mkdir(MESHFOLDER + "/" + str(ASSET_NAME))


            ##________________________________________________________________________________________IMPORT ASSET
            mc.file(f = True, new = True)
            before = set(mc.ls(assemblies=True))
            mc.file(MESHFOLDER + "/" + str(each), i=True, ignoreVersion=True, f= True)
            after = set(mc.ls(assemblies=True))
            imported = after.difference(before)
            mc.select(imported)
            ASSETPATH = mc.ls(sl=True, l=True)
            mc.setToolTo('moveSuperContext')

            ##________________________________________________________________________________________IMPORT LIGHTING SCENE + FRAMING
            if RENDERERCHOICE == "Arnold":
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)

            if RENDERERCHOICE == "Redshift":
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Redshift_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)

            if RENDERERCHOICE == "Vray":
                mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Vray_Scene.ma", rnn=True, i=True,  ignoreVersion=True, mergeNamespacesOnClash=False)
                mel.eval('setAttr"vraySettings.pixelAspect"1;')

            print ("ASSETPATH Debug = " + str(ASSETPATH))
            mc.select(ASSETPATH)
            mc.viewFit("RenderThumbCam", all=False, f=1)


            ##________________________________________________________________________________________SHADER
            if self.SaveMaterial_GroupBox.isChecked() == True:
                pass
            else:
                mc.select(ASSETPATH)
                mc.hyperShade(a="AssetIt_Thumb_shd")

            DESTPATH = MESHFOLDER + "/" + str(ASSET_NAME) + "/" + str(ASSET_NAME)
            RENDERTEMPPATH = DESTPATH + ".png"


            if RENDERERCHOICE == "Arnold":
                ##________________________________________________________________________________________SET ARNOLD RENDER
                mc.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')  # Set curent render
                try:
                    mc.setAttr('defaultArnoldDriver.ai_translator', 'png', type='string')
                except:
                    mel.eval("unifiedRenderGlobalsWindow;")
                    mc.setAttr('defaultArnoldDriver.ai_translator', 'png', type='string')

                try:
                    mc.setAttr('defaultArnoldDriver.prefix', DESTPATH, type='string')  # TO SAVE IMG TO DESTINATION PATH
                except:
                    mel.eval("unifiedRenderGlobalsWindow;")
                    mc.setAttr('defaultArnoldDriver.prefix', DESTPATH, type='string')  # TO SAVE IMG TO DESTINATION PATH

                try:
                    mc.setAttr('defaultArnoldRenderOptions.renderDevice', 0)  # CPU rendering
                except:
                    mel.eval("unifiedRenderGlobalsWindow;")
                    mc.setAttr('defaultArnoldRenderOptions.renderDevice', 0)  # CPU rendering

                mc.setAttr("defaultResolution.width", 400)
                mc.setAttr("defaultResolution.height", 400)
                mc.setAttr("defaultResolution.deviceAspectRatio", 1)
                mc.setAttr("defaultResolution.pixelAspect", 1)
                mc.setAttr("defaultArnoldRenderOptions.AASamples", 5)
                mc.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", 4)
                mc.setAttr("defaultArnoldRenderOptions.GISpecularSamples", 1)
                mc.setAttr("defaultArnoldRenderOptions.GISssSamples", 4)

                    ##POUR LE BACKGROUND
                try:
                    mc.connectAttr("AssetIt_Background.message", "defaultArnoldRenderOptions.background")
                except:
                    print ("NOT CONNECT")
                    pass

                mc.colorManagementPrefs(e=True, outputTransformEnabled=True,  outputUseViewTransform=True)  # Color Management Prefs
                mc.arnoldRender(width=400, height=400, camera="RenderThumbCam")  # render and save the image

                # FIX "_1" naming :
                old_name = DESTPATH + '_1.png'
                new_name = DESTPATH + '.png'
                if os.path.exists(new_name):
                    os.remove(new_name)
                os.rename(old_name, new_name)
                mc.disconnectAttr("AssetIt_Background.message", "defaultArnoldRenderOptions.background")

            if RENDERERCHOICE == "Redshift":
                print("REDSHIFT RENDER MODE")
                ##________________________________________________________________________________________GET RENDERSETTING USER PREF
                R_width = mc.getAttr("defaultResolution.width")
                R_height = mc.getAttr("defaultResolution.height")
                R_ratio = mc.getAttr("defaultResolution.deviceAspectRatio")
                R_pixelAspect = mc.getAttr("defaultResolution.pixelAspect")

                ##__________________________________________________________________________________ SET RENDERSETTING
                mc.setAttr("defaultRenderGlobals.currentRenderer", "redshift", type="string")  # Set curent render
                mc.setAttr('redshiftOptions.imageFormat', 2)  # Set the PNG image format / for TIFF - 5
                mc.setAttr("defaultRenderGlobals.imageFilePrefix", DESTPATH,
                           type="string")  # Set the path where the image is saved
                mc.setAttr("redshiftOptions.subsurfaceScatteringRate", -1)  # -3...3

                mc.setAttr("defaultResolution.width", R_width)
                mc.setAttr("defaultResolution.height", R_height)
                mc.setAttr("defaultResolution.deviceAspectRatio", R_ratio)
                mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)

                mc.rsRender(render=True, blk=True, cam='RenderThumbCam',
                            resolution=[400, 400])  # render and save the image

                # FIX "_1" naming :
                old_name = DESTPATH + '_tmp.png'
                new_name = DESTPATH + '.png'

                if os.path.exists(new_name):
                    os.remove(new_name)
                os.rename(old_name, new_name)

                ##________________________________________________________________________________________REVERT BACK RENDERSETTING USER PREF
                mc.setAttr("defaultResolution.width", R_width)
                mc.setAttr("defaultResolution.height", R_height)
                mc.setAttr("defaultResolution.deviceAspectRatio", R_ratio)
                mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)


            if RENDERERCHOICE == "Vray":
                print("VRAY RENDER MODE")
                ##__________________________________________________________________________________ SET RENDERSETTING
                mc.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

                ##________________________________________________________________________________________GET RENDERSETTING USER PREF
                mc.setAttr("vraySettings.width", 400)
                mc.setAttr("vraySettings.height", 400)

                # //
                mc.vray("showVFB")
                mc.vrend(camera="RenderThumbCam")
                mc.vray("vfbControl", "-saveimage", RENDERTEMPPATH)






            ##________________________________________________________________________________________SAVE .MA and TEXTURES
            #PIVOT
            if self.Pivot_GroupBox.isChecked():
                mc.select(ASSETPATH)
                if self.PivotOriginGrid.isChecked():
                    sel = mc.ls(sl=True)
                    bbox = mc.exactWorldBoundingBox(sel)
                    bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
                    mc.xform(sel, piv=bottom, ws=True)
                    mc.move(0, 0, 0, sel, rpr=True)
                if self.GridCenter.isChecked():
                    mc.group(n="GroupTemp")
                    mc.CenterPivot()
                    mc.move(0, 0, 0, rpr=True)
                    mc.ungroup("GroupTemp")
                if self.PivotBottom.isChecked():
                    sel = mc.ls(sl=True)
                    bbox = mc.exactWorldBoundingBox(sel)
                    bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
                    mc.xform(sel, piv=bottom, ws=True)






            # EXPORT MATERIALS
            mc.select(ASSETPATH)
            SELECTION_FULLPATH_MESHONLY = mc.ls(sl=1, type='mesh', dag=1, ni=1, l=True)

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
                        MATERIALS = mc.ls(mc.listConnections(get_shader_SG),
                                          materials=True)  # Get the Material from the SG

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


                    for each in FILELIST:
                        TEXTURE_PATH = mc.getAttr(each + ".fileTextureName")
                        TEXTURE_NAME = TEXTURE_PATH.split("/")[-1]
                        TEXTURE_DEST = MESHFOLDER + "/" + str(ASSET_NAME) + "/" + TEXTURE_NAME
                        TEXTURE_LIST.append(mc.getAttr(each + ".fileTextureName"))

                        if TEXTURE_PATH == "":
                            print ("Pass Empty")
                            pass
                        else:
                            shutil.copyfile(TEXTURE_PATH, TEXTURE_DEST)


                else:  # KEEP ORIGINAL
                    #___________________________________________________________ Just pour avoir le Texture Number
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
            mc.select(ASSETPATH)
            if self.SaveMaterial_GroupBox.isChecked() == True:
                mc.file(rename= MESHFOLDER + "/" + str(ASSET_NAME) + "/" + str(ASSET_NAME))
                mc.file(type='mayaAscii' , exportSelected = True)
            else:
                MATERIALS = []
                TEXTURE_LIST = []
                mc.hyperShade(a="lambert1")
                mc.file(rename = MESHFOLDER + "/" + str(ASSET_NAME) + "/" + str(ASSET_NAME))
                mc.file(type='mayaAscii', exportSelected=True)

            ##________________________________________________________________________________________METADATA
            # METADATA
            print ("RENDERCHOICE = " + RENDERERCHOICE)
            AssetInfo = "Create wwith BatchProcess"
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
            open(MESHFOLDER + "/" + str(ASSET_NAME) + "/" + str(ASSET_NAME) + '.json', "w").write(json_metadata)


            ##________________________________________________________________________________________MOVE ASSET FOLDER
            TAB_CHOICE = ASSET_LIBRARY_PATH + "/" + str(self.TAB1_Combo.currentText()) + "/" + str(self.TAB2_Combo.currentText())

            print ("MESHFOLDER copyMove = " + str(MESHFOLDER))
            print ("ASSET_NAME copyMove = " + str(ASSET_NAME))
            try:
                move(MESHFOLDER + "/" + str(ASSET_NAME), TAB_CHOICE, copy_function=copytree)
            except:
                shutil.rmtree(TAB_CHOICE+ "/" + str(ASSET_NAME))
                move(MESHFOLDER + "/" + str(ASSET_NAME), TAB_CHOICE, copy_function=copytree)

            # PROGRESBAR UPDATING
            self.updatingProgressBar()
            self.opName = "Creating Assets"






        ##________________________________________________________________________________________END CLEAN
        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "All Assets Created"
        self.progress_dialog.close()

        mc.deleteUI("Multi Asset Creation from Files")

        mc.file(f=True, new=True)



        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()







    def WARNING_SaveOpen(self):
        BackgroundColor = 0.16
        Message = "Save changes before to open?"
        # ________________//
        if mc.window("WarningWindow", exists=True):
            mc.deleteUI("WarningWindow")
        mc.window("WarningWindow", title=' Save Changes ', s=False, vis=True, rtf=False)
        mc.columnLayout(adj=True, rs=3, bgc=[BackgroundColor, BackgroundColor, BackgroundColor])
        mc.separator(h=8, style='none')
        mc.text(l="  " + Message + "  ", al="center")
        mc.separator(h=8, style='none')
        mc.rowColumnLayout( numberOfRows=1 )
        mc.separator(w=10, style='none')
        mc.button(l="Save", c=self.WarningSave, width= 85, h=20)
        mc.separator(w=10, style='none')
        mc.button(l="Don't save", c=self.WarningDontSave, width= 85, h=20)
        mc.separator(w=10, style='none')
        mc.button(l="Cancel", c=self.WarningCancel, width= 85, h=20)
        mc.window("WarningWindow", e=True, wh=(300, 80))

        qw = omui.MQtUtil.findWindow("WarningWindow")
        widget = wrapInstance(int(qw), QWidget)
        icon = QIcon(IconPath + "Windows_Ico_Warning.png")
        widget.setWindowIcon(icon)

        mc.showWindow()
    def WarningSave(self, *args):
        selectedObject = self.itemPath[:-4]
        mc.file(f=True, save=True )
        mc.file(selectedObject + ".ma", o=True, f=True)
        mc.deleteUI("WarningWindow")
    def WarningDontSave(self, *args):
        selectedObject = self.itemPath[:-4]
        mc.file(selectedObject + ".ma", o=True, f=True)
        mc.deleteUI("WarningWindow")
    def WarningCancel(self, *args):
        mc.deleteUI("WarningWindow")

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
    ui = Dock(BatchProcess_UI)
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


    return ui

