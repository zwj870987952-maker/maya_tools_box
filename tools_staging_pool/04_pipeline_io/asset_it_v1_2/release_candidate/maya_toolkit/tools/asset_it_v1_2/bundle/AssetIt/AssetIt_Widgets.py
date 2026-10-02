# -*- coding: latin-1 -*-
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import maya.cmds as mc
import os, json
import shutil

from . import AssetIt_UI
from . import AssetIt_Global
import importlib
importlib.reload(AssetIt_Global)

from . import AssetIt_Metadata
importlib.reload(AssetIt_Metadata)



# Special cases for different Maya versions
try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

from maya import OpenMayaUI as omui


ASSET_FAVOURITES_PATH = AssetIt_Global.ASSET_FAVOURITES_PATH
##PATH_SET
IconPath = AssetIt_Global.IconsPathThemeClassic
PreferencePath = AssetIt_Global.PreferencePath
ToolsPath = AssetIt_Global.ToolPath


Click_pref = json.load(open(PreferencePath + 'Pref_Click.json', "r"))
PREF_CLICK = (Click_pref['CLICK'])
if PREF_CLICK == 0:
    ClickIndex = 0
if PREF_CLICK == 1:
    ClickIndex = 1

FOLDER_PATH = ""


class AssetIt_ListWidget(QListWidget):
    """           LE WIDGET QUI LISTE LES ASSETS         """
    def __init__(self, path, parent):
        super(AssetIt_ListWidget, self).__init__()
        self.parent=parent # just for updating favoutites
        self.path = path
        self.iconSize = 168
        self.buffer = 4
        self.buttons = []
        self.isFavOrResearch = False # bool: si la QListWidget sera utilisée pour les favoris ou la recherche

        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setGridSize(QSize(self.iconSize + self.buffer, self.iconSize + self.buffer))
        self.setSortingEnabled(0)
        self.verticalScrollBar().setSingleStep(20)


        self.populate()



    def populate(self):
        try:    # tab normal            si self.path est un DOSSIER
            folderList = os.listdir(self.path)
            self.createsButtonsFromFileList(folderList= folderList)

        except: # favoris               si self.path est une LISTE DE FICHIERS
            folderList = self.path
            folderList = json.loads(folderList)
            self.isFavOrResearch = True
            self.createsButtonsFromFileList(folderList=folderList)

    def createsButtonsFromFileList(self, folderList):
        # crée les bouttons grâce a la liste des chemins de tous les assets a afficher
        icon_list = []

        for folder in folderList:
            if not self.isFavOrResearch:
                icon_list.append(folder+"/"+folder+".png")
            else:
                icon_list.append(folder)

        for icon in icon_list:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setSizeHint(QSize(400, 400))
            self.addItem(item)

            if self.isFavOrResearch:
                pixPath = icon
            else:
                pixPath = self.path + "/" + icon


            button = AssetIt_Button(pixPath, self, item)
            icon = QIcon(pixPath)
            #pixMap = QPixmap(pixPath)
            #pixMap.scaled(10,10,Qt.KeepAspectRatio)

            button.setFlat(True)
            button.setIconSize(QSize(self.iconSize, self.iconSize))
            button.setObjectName("Items")
            #button.setContentsMargins(200, 200, 200, 200)
            button.setIcon(icon)
            self.buttons.append(button)

            self.setItemWidget(item, button)



class AssetIt_Button(QPushButton):
    """           ON VA AJOUTER CE BOUTTON POUR CHAQUE ASSET DANS LE AssetIt_ListWidget         """
    def __init__(self, itemPath, parent, itemWidget):
        super(AssetIt_Button, self).__init__()
        self.itemWidget = itemWidget
        self.itemPath = itemPath
        self.parent = parent
        self.assetName = self.itemPath[:-4] # json
        self.assetName = self.assetName[self.assetName.rfind("/") + 1:]
        self.setContextMenuPolicy(Qt.DefaultContextMenu)


    def enterEvent(self, event, action=None):
        # fonction appelée quand la souris hovers le boutton
        self.parent.parent.AssetName.setText(self.assetName)

    def leaveEvent(self, event):
        # fonction appelée quand la souris sort du boutton
        #print ("leave")
        pass


    def mousePressEvent(self, QMouseEvent):
        # fonction appelée quand on fait un clic souris (droit ou gauche)

        # si c'est un clic gauche:
        if QMouseEvent.button() == Qt.LeftButton:
            if ClickIndex == 0:
                PlacementMode_pref = json.load(open(PreferencePath + 'PlacementMode.json', "r"))
                PLACEMENTMODE = (PlacementMode_pref['PLACEMENT_MODE'])

                if PLACEMENTMODE == 0:
                    self.set_ImportFile()
                elif PLACEMENTMODE == 1:
                    self.set_importAtSelection()

                elif PLACEMENTMODE == 2:
                    self.import_PlaceOnTopOf()

                elif PLACEMENTMODE == 3:
                    self.set_ImportDrag()

                elif PLACEMENTMODE == 4:
                    self.set_ImportReplace()


            else:
                pass



        # si c'est un clic miliue:
        if QMouseEvent.button() == Qt.MiddleButton:
            self.set_AssetInfo()


        # si c'est un clic droit
        if QMouseEvent.button() == Qt.RightButton:
            ##KNOW FAV TAB
            FavTabpref_path = open(PreferencePath + 'KnowFavTab.json', "r")
            FavTabdata_pref = json.load(FavTabpref_path)
            FavTabPath = (FavTabdata_pref['TAB_ACTIVE_NAME'])




            self.menu = QMenu(self)





            ##____________________________________________________________________// MRB MENU

            # __________________________________________________________SECURE STEP
            secure = QAction(" // " + str(self.assetName) + " // ")
            self.menu.addAction(secure)

            # __________________________________________________________-----
            sep0 = QAction("------------- ")
            self.menu.addAction(sep0)

            # __________________________________________________________ASSET INFO
            mb_AssetInfo = QAction("Asset Info")
            mb_AssetInfo.triggered.connect(self.set_AssetInfo)
            self.menu.addAction(mb_AssetInfo)

            # __________________________________________________________ADD FAVORITE : add to favourites, sauf si on est déjà dans le tab favourite
            if FavTabPath == "\u2764":
                mb_RemoveFavorite = QAction("Remove from favourite")
                mb_RemoveFavorite.triggered.connect(self.RemoveFavoriteMenuAction)
                self.menu.addAction(mb_RemoveFavorite)

            else:
                mb_Favorite = QAction("Add to favourite")
                mb_Favorite.triggered.connect(self.AddFavoriteMenuAction)
                self.menu.addAction(mb_Favorite)

            # __________________________________________________________-----
            sep = QAction("------------- ")
            self.menu.addAction(sep)

            # __________________________________________________________OPEN FILE
            mb_OpenFile = QAction("Open File ")
            mb_OpenFile.triggered.connect(self.WARNING_SaveOpen)
            self.menu.addAction(mb_OpenFile)

            # __________________________________________________________IMPORT FILE
            mb_ImportFile = QAction("Import File ")
            mb_ImportFile.triggered.connect(self.set_ImportFile)
            self.menu.addAction(mb_ImportFile)

            # __________________________________________________________REFERENCE FILE
            mb_ImportasReferenceFile = QAction("Import as Reference ")
            mb_ImportasReferenceFile.triggered.connect(self.set_ImportAsReference)
            self.menu.addAction(mb_ImportasReferenceFile)

            # __________________________________________________________-----
            sep2 = QAction("------------- ")
            self.menu.addAction(sep2)

            # __________________________________________________________OPEN FOLDER
            mb_OpenFolder = QAction("Open Folder ")
            mb_OpenFolder.triggered.connect(self.set_OpenFolder)
            self.menu.addAction(mb_OpenFolder)

            # __________________________________________________________RENAME
            mb_Rename = QAction("Rename ")
            mb_Rename.triggered.connect(self.set_Rename)
            self.menu.addAction(mb_Rename)

            # __________________________________________________________DELETE
            mb_Delete = QAction("Delete ")
            mb_Delete.triggered.connect(self.set_Delete)
            self.menu.addAction(mb_Delete)








            # show the menu
            self.popup = self.menu.exec_(self.mapToGlobal(QMouseEvent.pos()))


    def mouseDoubleClickEvent(self, QMouseEvent):
        if ClickIndex == 1:
            PlacementMode_pref = json.load(open(PreferencePath + 'PlacementMode.json', "r"))
            PLACEMENTMODE = (PlacementMode_pref['PLACEMENT_MODE'])

            if PLACEMENTMODE == 0:
                self.set_ImportFile()
            elif PLACEMENTMODE == 1:
                self.set_importAtSelection()

            elif PLACEMENTMODE == 2:
                self.import_PlaceOnTopOf()

            elif PLACEMENTMODE == 3:
                self.set_ImportDrag()

            elif PLACEMENTMODE == 4:
                self.set_ImportReplace()

        else:
            pass

    # *****************************************************
    #      UNE FONCTION PAR ACTION DU MENU CLIC DROIT
    # *****************************************************
    def importMenuAction(self):
        mc.file(self.itemPath[:-4] + ".ma", i=True)

    def AddFavoriteMenuAction(self):
        # add to favourite
        favouriteFilePath = ASSET_FAVOURITES_PATH
        with open(favouriteFilePath, 'r+') as file:
            fileContent = file.read()
            JSONtoPYTHON = json.loads(fileContent)

            #check si l'asset est deja en favoris
            if self.itemPath in JSONtoPYTHON:
                mc.warning("this asset is already in your favourites")
                return

            JSONtoPYTHON.append(self.itemPath)
            final = json.dumps(JSONtoPYTHON)

        # update favourite json file for saving
        with open(favouriteFilePath, 'w+') as file:
            file.write(final)

        #update favourite tab
        self.parent.parent.favouritesWidget.createsButtonsFromFileList(folderList=[self.itemPath])
        mc.warning("Asset successfully added to the favourite tab")

    def RemoveFavoriteMenuAction(self):
        favouriteFilePath = ASSET_FAVOURITES_PATH
        with open(favouriteFilePath, 'r+') as file:
            fileContent = file.read()
            JSONtoPYTHON = json.loads(fileContent)


            JSONtoPYTHON.remove(self.itemPath)
            final = json.dumps(JSONtoPYTHON)

            print ("fileContent = " + str(fileContent) )
            print ("JSONtoPYTHON = " + str(JSONtoPYTHON))
            print ("final = " + str(final))

        # update favourite json file for saving
        with open(favouriteFilePath, 'w+') as file:
            file.write(final)


        #update favourite tab
        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        AssetIt_UI.showUI()
        mc.warning("Asset successfully remove to the favourite tab")



    def set_ImportDrag(self):
        #VERIF THERE IS A MESH
        listAllGeometrieScene = mc.ls(type="mesh")
        if listAllGeometrieScene == []:
            AssetIt_Global.WarningWindow("Drag Placement mode need at least one mesh in the scene.", 350)
            return


        from . import AssetIt_DragTool
        importlib.reload(AssetIt_DragTool)

        fileMA = self.itemPath.replace(".png" , ".ma")
        AssetIt_DragTool.goPress(fileMA)




    def set_AssetInfo(self):
        importlib.reload(AssetIt_Metadata)
        AssetIt_Metadata.SEND_INFO(str(self.itemPath), str(self.assetName))
        AssetIt_Metadata.showUI()


    def set_OpenFile(self):
        selectedObject = self.itemPath[:-4]
        mc.file(selectedObject + ".ma", o=True)

    def set_ImportFile(self):
        SaveSize_pref = json.load(open(PreferencePath + 'MultiSize.json', "r"))
        MULTISIZEVALUE = (SaveSize_pref['MULTISIZEVALUE'])

        ImportShaderMode_pref = json.load(open(PreferencePath + 'ImportShader.json', "r"))
        IMPORTSHADERMODE = (ImportShaderMode_pref['IMPORTSHADERMODE'])

        # Clean if previous mode was Drag and still active
        mc.setToolTo('moveSuperContext')
        before = set(mc.ls(assemblies=True, l= True))
        selectedObject = self.itemPath[:-4]

        if IMPORTSHADERMODE == 0:
            shadingNetworksOptVar = mc.optionVar(q='removeDuplicateShadingNetworksOnImport')
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', 1))
            mc.file(selectedObject + ".ma", i=True, removeDuplicateNetworks=True)
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', shadingNetworksOptVar))
        else:
            mc.file(selectedObject + ".ma", i=True)

        after = set(mc.ls(assemblies=True, l= True))
        imported = after.difference(before)

        mc.select(imported)


        if MULTISIZEVALUE != 1.0:
            mc.CreateEmptyGroup()
            mc.rename(self.assetName + '_Ctrl')
            objToPlace = mc.ls(sl=True)
            mc.parent(imported, objToPlace[0])
            mc.select(objToPlace[0])
            mc.makeIdentity(apply=True)
            mc.xform(ws=1, a=1, piv=[0, 0, 0])

            mc.setAttr(objToPlace[0] + ".scaleX", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleY", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleZ", MULTISIZEVALUE)


    def set_ImportReplace(self):
        ##_________________INIT
        SaveSize_pref = json.load(open(PreferencePath + 'MultiSize.json', "r"))
        MULTISIZEVALUE = (SaveSize_pref['MULTISIZEVALUE'])

        ImportShaderMode_pref = json.load(open(PreferencePath + 'ImportShader.json', "r"))
        IMPORTSHADERMODE = (ImportShaderMode_pref['IMPORTSHADERMODE'])




        selection = mc.ls(selection=True, l= True)
        if selection == []:
            AssetIt_Global.WarningWindow("On 'Replace' mode : you should select one Object.", 350)
            return

        ##_________________IMPORT L'ASSET
        before = set(mc.ls(assemblies=True, l= True))
        selectedObject = self.itemPath[:-4]


        if IMPORTSHADERMODE == 0:
            shadingNetworksOptVar = mc.optionVar(q='removeDuplicateShadingNetworksOnImport')
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', 1))
            mc.file(selectedObject + ".ma", i=True, removeDuplicateNetworks=True)
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', shadingNetworksOptVar))
        else:
            mc.file(selectedObject + ".ma", i=True)


        after = set(mc.ls(assemblies=True, l= True))
        imported = after.difference(before)

        ##_______________CREATION DU GROUPE QUI CONTIENT TOUS LES MESH
        mc.CreateEmptyGroup()
        mc.rename(self.assetName + '_Ctrl')
        objToPlace = mc.ls(sl=True)
        mc.parent(imported, objToPlace[0])





        if MULTISIZEVALUE != 1.0:
            mc.setAttr(objToPlace[0] + ".scaleX", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleY", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleZ", MULTISIZEVALUE)
            mc.select(objToPlace[0])
            mc.makeIdentity(apply=True)





        mc.select(objToPlace[0])
        mc.makeIdentity(apply=True)

        allNewSel = []
        #OPERATION DE REPLACEMENT
        if len(selection) > 1:
            for each in selection:
                objDup = mc.duplicate(objToPlace[0])
                mc.matchTransform(objDup[0], each, pos=True, rot=True, scl =True)
                mc.delete(each)
                allNewSel.append(objDup[0])

        else:
            SELECTION = selection
            mc.matchTransform(objToPlace[0], SELECTION, pos=True, rot=True, scl =True)
            mc.delete(SELECTION)

        if len(selection) > 1:
            toAdd = allNewSel.pop(0)
            theGoodSel = allNewSel.append(toAdd)
            #currentSel = mc.ls(sl=True, l=True)
            mc.delete(objToPlace[0])
            print ("allNewSel == " + str(allNewSel))
            print ("theGoodSel == " + str(theGoodSel))
            mc.select(allNewSel)


        else:
            mc.select(objToPlace[0])



        mc.setToolTo('moveSuperContext')



    def set_importAtSelection(self):
        SaveSize_pref = json.load(open(PreferencePath + 'MultiSize.json', "r"))
        MULTISIZEVALUE = (SaveSize_pref['MULTISIZEVALUE'])

        ImportShaderMode_pref = json.load(open(PreferencePath + 'ImportShader.json', "r"))
        IMPORTSHADERMODE = (ImportShaderMode_pref['IMPORTSHADERMODE'])

        selectionCheck = mc.ls(sl=True)
        if selectionCheck == []:
            AssetIt_Global.WarningWindow("On 'Place at Selection' mode : you should select component first.", 350)
            return

        mc.setToolTo('moveSuperContext')
        pos = mc.manipMoveContext('Move', query=True, position=True)
        selection = mc.ls(selection=True, l= True)


        ##_________________IMPORT L'ASSET
        before = set(mc.ls(assemblies=True, l= True))
        selectedObject = self.itemPath[:-4]


        if IMPORTSHADERMODE == 0:
            shadingNetworksOptVar = mc.optionVar(q='removeDuplicateShadingNetworksOnImport')
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', 1))
            mc.file(selectedObject + ".ma", i=True, removeDuplicateNetworks=True)
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', shadingNetworksOptVar))
        else:
            mc.file(selectedObject + ".ma", i=True)


        after = set(mc.ls(assemblies=True, l= True))
        imported = after.difference(before)

        ##_______________CREATION DU GROUPE QUI CONTIENT TOUS LES MESH
        mc.CreateEmptyGroup()
        mc.rename(self.assetName + '_Ctrl')
        objToPlace = mc.ls(sl=True)
        mc.parent(imported, objToPlace[0])


        if MULTISIZEVALUE != 1.0:
            mc.setAttr(objToPlace[0] + ".scaleX", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleY", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleZ", MULTISIZEVALUE)
            mc.select(objToPlace[0])
            mc.makeIdentity(apply=True)


        mc.select(objToPlace[0])
        mc.makeIdentity(apply=True)
        mc.xform(ws=1, a=1, piv=[0, 0, 0])



        mc.move(pos[0], pos[1], pos[2], objToPlace)
        constr = mc.normalConstraint(selection, objToPlace, aimVector=(0, 1, 0), worldUpType=0)
        mc.delete(constr)

        mc.select(objToPlace[0])
        mc.setToolTo('moveSuperContext')




    def set_ImportAsReference(self):
        before = set(mc.ls(assemblies=True))

        selectedObject = self.itemPath[:-4]
        mc.file(selectedObject + ".ma", reference = True)

        after = set(mc.ls(assemblies=True))
        imported = after.difference(before)
        mc.select(imported)
        mc.setToolTo('moveSuperContext')


    def set_OpenFolder(self):
        selectedObject = self.itemPath[:-4]
        removeEnd = selectedObject.replace("/" + self.assetName, "")
        ItemFolderPath = removeEnd + "/" + self.assetName
        os.startfile(ItemFolderPath)


    def set_Rename(self):
        selectedObject = self.itemPath[:-4]
        removeEnd = selectedObject.replace("/" + self.assetName, "")
        ItemFolderPath = removeEnd + "/" + self.assetName


        from . import AssetIt_Rename
        import importlib
        importlib.reload(AssetIt_Rename)
        AssetIt_Rename.SEND_INFO(str(removeEnd), str(ItemFolderPath))
        AssetIt_Rename.showUI()



    def set_Delete(self):
        selectedObject = self.itemPath[:-4]
        removeEnd = selectedObject.replace("/" + self.assetName, "")
        ItemFolderPath = removeEnd + "/" + self.assetName
        shutil.rmtree(ItemFolderPath)



        # FAV CLEAN List
        itemName = (ItemFolderPath.split("/")[-1]).replace(".png", "")
        print ("itemName = " + itemName)

        favouriteFilePath = ASSET_FAVOURITES_PATH
        with open(favouriteFilePath, 'r+') as file:
            fileContent = file.read()
            FAVLIST = json.loads(fileContent)
            FAVLISTLen = len(FAVLIST)-1

        for each in FAVLIST:
            nameInList = (each.split("/")[-1]).replace(".png", "")
            print ("each = " + each)
            print ("nameInList = " + nameInList)
            if nameInList == itemName:
                if FAVLIST.index(each) == 0:
                    print ("PLACE AT : START")
                    stringToReplace = "'" + str(ItemFolderPath) + "/" + str(itemName) + ".png" +  "'" + ","
                elif FAVLIST.index(each) == FAVLISTLen:
                    print ("PLACE AT : END")
                    stringToReplace = ", " + "'" + str(ItemFolderPath) + "/" + str(itemName) + ".png"  + "'"
                else:
                    print ("PLACE AT : MIDDLE")
                    stringToReplace = "'" + str(ItemFolderPath) + "/" + str(itemName) + ".png" + "'" + ","

                print ("stringToReplace IN DELETE == " + stringToReplace)
                newFAV = str(FAVLIST).replace(str(stringToReplace), "")
                print ("NEW FAV IN DELETE == " + newFAV)
                newFAVtoWritte = newFAV.replace("'", '"')

                # update favourite json file for saving
                with open(favouriteFilePath, 'w+') as file:
                    file.write(newFAVtoWritte)



        from . import AssetIt_UI
        import importlib
        importlib.reload(AssetIt_UI)
        ui = AssetIt_UI.showUI()







    def import_PlaceOnTopOf(self):
        SaveSize_pref = json.load(open(PreferencePath + 'MultiSize.json', "r"))
        MULTISIZEVALUE = (SaveSize_pref['MULTISIZEVALUE'])

        ImportShaderMode_pref = json.load(open(PreferencePath + 'ImportShader.json', "r"))
        IMPORTSHADERMODE = (ImportShaderMode_pref['IMPORTSHADERMODE'])

        # VERIF WELL IN OBJECT MODE SELECTED
        all_selected = mc.ls(sl=True)
        checkVertices = mc.filterExpand(sm=31)
        checkEdges = mc.filterExpand(sm=32)
        checkFaces = mc.filterExpand(sm=34)

        if checkVertices != None:
            AssetIt_Global.WarningWindow("In 'Place On Top Of' mode : you should select mesh object and not component.", 400)
            return
        elif checkEdges != None:
            AssetIt_Global.WarningWindow("In 'Place On Top Of' mode : you should select mesh object and not component.", 400)
            return
        elif checkFaces != None:
            AssetIt_Global.WarningWindow("In 'Place On Top Of' mode : you should select mesh object and not component.", 400)
            return

        ##_________________MESH SUR LEQUEL ON VA PLACER L'ASSET
        # Clean if previous mode was Drag and still active
        mc.setToolTo('moveSuperContext')

        selectionCheck = mc.ls(sl=True, l= True)
        if selectionCheck == []:
            AssetIt_Global.WarningWindow("On 'Place On Top Of' mode : you should select a mesh first.", 350)
            return
        SELECTION =selectionCheck[0]

        ##_________________IMPORT L'ASSET
        before = set(mc.ls(assemblies=True, l= True))
        selectedObject = self.itemPath[:-4]

        if IMPORTSHADERMODE == 0:
            shadingNetworksOptVar = mc.optionVar(q='removeDuplicateShadingNetworksOnImport')
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', 1))
            mc.file(selectedObject + ".ma", i=True, removeDuplicateNetworks=True)
            mc.optionVar(intValue=('removeDuplicateShadingNetworksOnImport', shadingNetworksOptVar))
        else:
            mc.file(selectedObject + ".ma", i=True)

        after = set(mc.ls(assemblies=True, l= True))
        imported = after.difference(before)


        ##_______________CREATION DU GROUPE QUI CONTIENT TOUS LES MESH
        mc.CreateEmptyGroup()
        mc.rename(self.assetName + '_Ctrl')
        objToPlace = mc.ls(sl=True)
        mc.parent(imported, objToPlace[0])
        mc.select(objToPlace[0])
        mc.makeIdentity(apply=True)
        mc.xform(ws=1, a=1, piv=[0, 0, 0])

        if MULTISIZEVALUE != 1.0:
            mc.setAttr(objToPlace[0] + ".scaleX", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleY", MULTISIZEVALUE)
            mc.setAttr(objToPlace[0] + ".scaleZ", MULTISIZEVALUE)
            mc.select(objToPlace[0])
            mc.makeIdentity(apply=True)

        ##_______________GET SELECTION BBOX
        bbox = mc.exactWorldBoundingBox(SELECTION)
        Ymin = bbox[1]
        YMax = bbox[4]

        # 0 - Init Freeze at Origin asset
        bbox = mc.exactWorldBoundingBox(objToPlace)
        bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
        mc.xform(objToPlace, piv=bottom, ws=True)
        mc.move(0, 0, 0, objToPlace, rpr=True)
        mc.select(objToPlace)
        mc.makeIdentity( apply=True, t=1, r=1, s=1)

        # 1 - Place at obj posion
        mc.matchTransform(objToPlace, SELECTION, pos=True)

        # 2 - Up to Top
        mc.move(YMax, objToPlace, y=True, a=True)

        mc.select(objToPlace[0])
        mc.setToolTo('moveSuperContext')



    def none (self):
        pass

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
