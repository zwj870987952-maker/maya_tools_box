
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
WindowsTitle = "Multi Asset Creation from Scene"
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
class MultiScene_UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MultiScene_UI, self).__init__()
        self.setMinimumSize(510, 370)
        self.buildUI()


    def buildUI(self):
        BATCH_MAINLayout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet(AssetIt_Global.Theme)
        ##UI - Preferences
        iconButtonSize = AssetIt_Global.IconButtonSize


        ##____________________________________________________________// RENDER CHOICE
        self.Renderer_GroupBox = QtWidgets.QGroupBox("/ Render Engine Choice")
        self.Renderer_GroupBox.setEnabled(True)

        #BATCH_MAINLayout.addWidget(self.Renderer_GroupBox)
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
        self.Pivot_GroupBox.setChecked(1)

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
        CreateAssetBtn.setText("CREATE ASSETS")
        CreateAssetBtn.setFixedHeight(30)
        CreateAssetBtn.clicked.connect(self.CreateAsset)
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




    def CreateAsset(self):
        global RENDERERCHOICE
        # START BOUCLE PROCESS
        SELECTION = mc.ls(sl=True)
        print ("SELECTION = " + str(SELECTION))

        for eachName in SELECTION:
            if ":" in eachName:
                AssetIt_Global.WarningWindow("You can't use ' : ' character in Asset Name", 250)
                return



        #VARIABLES
        getMainTab = self.TAB1_Combo.currentText()
        getSecondTab = self.TAB2_Combo.currentText()
        FormatType = 'mayaAscii'

        RENDERERCHOICE = "NotDefine"

        if self.Arnoldcheck.isChecked():
            RENDERERCHOICE = "Arnold"
        if self.Redshiftcheck.isChecked():
            RENDERERCHOICE = "Redshift"
        if self.Vraycheck.isChecked():
            RENDERERCHOICE = "Vray"

        if SELECTION == []:
            AssetIt_Global.WarningWindow("You should select at least 2 Assets.", 250)
            return
        elif len(SELECTION) == 1:
            AssetIt_Global.WarningWindow("You should select at least 2 Assets otherwise use Add Asset tool.", 450)
            return


        # IMPORT LIGHT SCENE
        if RENDERERCHOICE == "Arnold":
            mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)

        if RENDERERCHOICE == "Redshift":
            mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Redshift_Scene.ma", rnn=True, i=True, ignoreVersion=True, mergeNamespacesOnClash=False)

        if RENDERERCHOICE == "Vray":
            mc.file(AssetCreationPath + "Thumb_Creation/AssetIt_Thumb_Vray_Scene.ma", rnn=True, i=True,  ignoreVersion=True, mergeNamespacesOnClash=False)


        ###_______________________________________PROGRESSBAR
        self.number_of_operations = len(SELECTION)
        self.step = 0
        self.opName = "Rendering Asset : "
        self.progress_dialog = QtWidgets.QProgressDialog("Batch Process", "", 0, self.number_of_operations, self)
        self.progress_dialog.setWindowTitle("Batch Process...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setMinimumSize(550, 80)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.show()

        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Rendering Asset : "


        for each in SELECTION:
            print ("each =" + each)
            getAssetName = str(each)
            ASSET_FOLDER = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName
            ASSET_PATH = ASSET_LIBRARY_PATH + "/" + getMainTab + "/" + getSecondTab + "/" + getAssetName + "/" + getAssetName

            #1 - ICI LE CHOIX DE PIVOT ET PLACEMENT DANS LA SCENE
            # PIVOT
            if self.Pivot_GroupBox.isChecked():
                mc.select(each)
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


            #2 - CREATE ASSET FOLDER
            try:  ## Check if Asset Already EXIST
                os.mkdir(ASSET_FOLDER)
                print ("ASSET_FOLDER ======= " +  ASSET_FOLDER)
            except:
                AssetIt_Global.WarningWindow("An Asset with this name already exist in this folder", 400)
                return


            #3 - EXPORT FILE and SAVE MATERIALS
            mc.select(each)
            # Put at Root Hierarchie

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

                    for files in ALL_MAT_NODOUBLON:  # POUR GET TOUS LES FILES_TEXTURE ASSOCIE AU SHADERS
                        MainShader = cmds.listHistory(files)
                        print("MainShader = " + str(MainShader))
                        listFileNode = mc.ls(MainShader, type="file")
                        print("listFileNode = " + str(listFileNode))
                        FILELIST.extend(listFileNode)


                    try:
                        for thefile in FILELIST:
                            TEXTURE_PATH = mc.getAttr(thefile + ".fileTextureName")
                            TEXTURE_NAME = TEXTURE_PATH.split("/")[-1]
                            TEXTURE_DEST = ASSET_FOLDER  + "/" + TEXTURE_NAME
                            TEXTURE_LIST.append(mc.getAttr(thefile + ".fileTextureName"))
                            print ("TEXTURE_DEST =" + TEXTURE_DEST)

                            if TEXTURE_PATH == "":
                                print ("Pass Empty")
                                pass
                            else:
                                shutil.copyfile(TEXTURE_PATH, TEXTURE_DEST)

                    except:
                        os.rmdir(ASSET_FOLDER)
                        AssetIt_Global.WarningWindow("There no texture on this selection", 400)
                        return

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
                        for item in listFileNode:
                            TEXTURE_PATH = mc.getAttr(item + ".fileTextureName")
                            TEXTURE_LIST.append(mc.getAttr(item + ".fileTextureName"))
                    except:
                        pass


                # EXPORT FILE
                mc.select(each)
                mc.file(ASSET_PATH, force=True, type=FormatType, exportSelected=True)

            else:
                MATERIALS = []
                TEXTURE_LIST = []
                GroupOrigin = mc.group(each, n="GroupDupTemp")
                GroupExport = mc.duplicate(GroupOrigin, n="GroupForExport")
                mc.ungroup("GroupForExport")
                DUPSEL = mc.ls(sl=True)
                mc.hyperShade(a="lambert1")

                # EXPORT FILE
                mc.file(ASSET_PATH, force=True, type= FormatType, exportSelected=True)
                mc.delete()
                mc.ungroup("GroupDupTemp")







            mc.select(each)
            mc.viewFit("RenderThumbCam", all=False, f=1)
            self.RENDERTHUMB()

            #4 -  EXPORT THUMB
            src = ASSET_CREATION_PATH + "RenderThumbTemp.png"
            dest = ASSET_PATH + ".png"
            print (src)
            print (dest)
            shutil.copyfile(src, dest)


            #5 - METADATA
            print ("RENDERCHOICE = " + RENDERERCHOICE)

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
                "UserInfo": "Create with MultiScene"

            }
            json_metadata = json.dumps(Metadata, indent=5)
            open(ASSET_PATH + '.json', "w").write(json_metadata)
            print ("JSON = " + ASSET_PATH + '.json')



            #Replace a sa position origin
            mc.setAttr(str(each) + ".translateX", 0)
            mc.setAttr(str(each) + ".translateY", 0)
            mc.setAttr(str(each) + ".translateZ", 0)

            # Back to hierarchi Group
            if selInGroup == 1:
                mc.parent(SELECTION, getParentPath)

            # PROGRESBAR UPDATING
            self.updatingProgressBar()
            self.opName = "Rendering Asset : "



        #KEEP BACK RIGHT TABS
        MainTabIndex = self.TAB1_Combo.currentIndex()
        SecondTabIndex = self.TAB2_Combo.currentIndex()

        FirstTabinfoToSave = {"TAB_OPEN" : MainTabIndex}
        s = json.dumps(FirstTabinfoToSave)
        open(PreferencePath + 'TabOpen.json', "w").write(s)

        SecondTabinfoToSave = {"TAB_OPEN" : SecondTabIndex}
        s = json.dumps(SecondTabinfoToSave)
        open(PreferencePath + 'TabOpenSecond.json', "w").write(s)

        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "All Assets from Selection Created."
        self.progress_dialog.close()

        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()

        mc.flushUndo()





    def RENDERTHUMB(self):
        global RENDERERCHOICE
        RENDERTEMPPATH = AssetCreationPath + "/RenderThumbTemp.png"
        SELECTION = mc.ls(sl=True)

        #__________________________ P R O G R E S S B A R
        self.number_of_operations = 3
        self.step = 0
        self.opName = "Arnold Thumb Rendering..."
        self.progress_dialog = QtWidgets.QProgressDialog("Arnold Rendering", "", 0, self.number_of_operations, self)
        self.progress_dialog.setWindowTitle("Arnold Rendering...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setMinimumSize(550, 80)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.show()

        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Arnold Thumb Rendering..."

        #Disable to don't have light scene user affect the render
        mel.eval("optionVar -iv renderSetup_includeAllLights 0;")

        ##____________________________// RENDER SETUP - INIT
        ##________________________/
        print ("self.SaveMaterial_GroupBox.isChecked() =" + str(self.SaveMaterial_GroupBox.isChecked()))
        if self.SaveMaterial_GroupBox.isChecked()== False:
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
            print ("FUCK 1")

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
            print ("FUCK 2")


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

        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Updating Thumbnail"
        DESTPATH = AssetCreationPath + "/RenderThumbTemp"

        print("RENDERCHOICE SUCK = " + str(RENDERERCHOICE))

        if RENDERERCHOICE == "Arnold":
            ##POUR LE BACKGROUND
            try:
                mc.connectAttr("AssetIt_Background.message", "defaultArnoldRenderOptions.background")
            except:
                pass

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

            mc.select(SELECTION)
            mc.viewFit("RenderThumbCam", all=False, f=1)

            mc.colorManagementPrefs(e=True, outputTransformEnabled=True, outputUseViewTransform=True)  # Color Management Prefs
            mc.arnoldRender(width= 400, height= 400, camera="RenderThumbCam")  # render and save the image


            # FIX "_1" naming :
            old_name = DESTPATH + '_1.png'
            new_name = DESTPATH + '.png'

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)

            ##______________________________ END CLEAN
            mel.eval("optionVar -iv renderSetup_includeAllLights 1;")

            # Go back to defaultw
            renderLayer.delete(rl)

            ##________________________________________________________________________________________REVERT BACK RENDERSETTING USER PREF
            mc.setAttr("defaultArnoldRenderOptions.AASamples", R_AASamples)
            mc.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", R_GIDiffuse)
            mc.setAttr("defaultArnoldRenderOptions.GISpecularSamples", R_GISpecular)
            mc.setAttr("defaultArnoldRenderOptions.GISssSamples", R_GISss)
            mc.setAttr("defaultRenderGlobals.imageFilePrefix", str(R_Path), type='string' )
            mc.setAttr("defaultArnoldDriver.ai_translator", str(R_Format), type='string')
            mc.setAttr("defaultArnoldDriver.colorManagement", R_ColorManagement)

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

            mc.select(SELECTION)
            mc.viewFit("RenderThumbCam", all=False, f=1)


            mc.rsRender(render=True, blk=True, cam='RenderThumbCam',    resolution=[400, 400])  # render and save the image

            # FIX "_1" naming :
            old_name = DESTPATH + '_tmp.png'
            new_name = DESTPATH + '.png'

            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(old_name, new_name)

        if RENDERERCHOICE == "Vray":
            print("VRAY RENDER MODE")
            mc.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

            mc.select(SELECTION)
            mc.viewFit("RenderThumbCam", all=False, f=1)

            ##________________________________________________________________________________________GET RENDERSETTING USER PREF
            mc.setAttr("vraySettings.width", 400)
            mc.setAttr("vraySettings.height", 400)

            # //
            mc.vray("showVFB")
            mc.vrend(camera="RenderThumbCam")
            mc.vray("vfbControl", "-saveimage", RENDERTEMPPATH)




        if RENDERERCHOICE == "Vray":
            pass
        else:
            ##________________________________________________________________________________________REVERT BACK RENDERSETTING USER PREF
            mc.setAttr("defaultResolution.width", R_width)
            mc.setAttr("defaultResolution.height", R_height)
            mc.setAttr("defaultResolution.deviceAspectRatio", R_ratio)
            mc.setAttr("defaultResolution.pixelAspect", R_pixelAspect)


        # __________________________ E N D I N G
        # PROGRESBAR UPDATING
        self.updatingProgressBar()
        self.opName = "Plug Created."
        self.progress_dialog.close()

        #DONE
        mc.flushUndo()
        print ("ASSET RENDER")














    def set_Arnold(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Arnold"

        infoToSave = {"Renderer": "Arnold"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)

        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))
        self.RendermanBTN.setIcon(QtGui.QIcon(IconPath + "Renderman_Off.png"))
    def set_Redshift(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Redshift"

        infoToSave = {"Renderer": "Redshift"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)


        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))
        self.RendermanBTN.setIcon(QtGui.QIcon(IconPath + "Renderman_Off.png"))
    def set_Vray(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Vray"

        infoToSave = {"Renderer": "Vray"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)


        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray.png"))
        self.RendermanBTN.setIcon(QtGui.QIcon(IconPath + "Renderman_Off.png"))
    def set_Renderman(self):
        global RENDERERCHOICE
        RENDERERCHOICE = "Renderman"

        infoToSave = {"Renderer": "Renderman"}
        s = json.dumps(infoToSave)
        open(PreferencePath + 'RenderChoice.json', "w").write(s)


        self.ArnoldBTN.setIcon(QtGui.QIcon(IconPath + "Arnold_Off.png"))
        self.RedshiftBTN.setIcon(QtGui.QIcon(IconPath + "Redshift_Off.png"))
        self.VrayBTN.setIcon(QtGui.QIcon(IconPath + "Vray_Off.png"))
        self.RendermanBTN.setIcon(QtGui.QIcon(IconPath + "Renderman.png"))

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
    ui = Dock(MultiScene_UI)
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

