### AUTO INSTALLER FOR ASSETIT 1.0.1
#______ THAT BACKUP THE ENTIRE PREVIOUS SCRIPT AS .BCKp ON UPDATE TO AVOID LIBRARY LOOSING


import os
from maya import cmds as mc
import maya.mel as mel
from shutil import move
from shutil import copytree
from shutil import rmtree

##____________________________// INIT
ScriptFolderName = "AssetIt"
ScriptIconName = "AssetIt_IconShelf.png"
ScriptCommand = """from AssetIt import AssetIt_UI
import importlib
importlib.reload(AssetIt_UI)
ui = AssetIt_UI.showUI()"""
ScriptUpdate = 0
##____________________________// VARIABLES
USERAPPDIR = mc.internalVar(userAppDir=True)
VERSION = mc.about(v=True)
UserScriptPath = os.path.join(USERAPPDIR, VERSION +'/scripts/'+ ScriptFolderName)
fileDir = __file__
folderDir = fileDir.replace("\Drag_Me_In_Viewport.py", "/" + ScriptFolderName)
DragViewport_Dir = fileDir.replace("\Drag_Me_In_Viewport.py",  "/" + "Drag_Me_In_Viewport.py")
PyCache_Folder = fileDir.replace("\Drag_Me_In_Viewport.py", "/" + "__pycache__")



##____________________________// DEBUG
print ("File_Dir : " + fileDir)
print ("Folder_Dir: " + folderDir)
print("UserScriptPath : " + UserScriptPath)
print("PyCache_Folder : " + PyCache_Folder)



def Warning_SCRIPT_INSTALL():
    BackgroundColor = 0.16
    Message = "AssetIt installed correctly."
    # ________________//
    if mc.window("WarningWindow", exists=True):
        mc.deleteUI("WarningWindow")
    mc.window("WarningWindow", title=' Setup ', s=False, vis=True, rtf=False)
    mc.columnLayout(adj=True, rs=3, bgc=[BackgroundColor, BackgroundColor, BackgroundColor])
    mc.separator(h=8, style='none')
    mc.text(l="  " + Message + "  ", al="center")
    mc.separator(h=8, style='none')
    mc.rowColumnLayout(numberOfRows=1)
    mc.separator(w=80, style='none')
    mc.button(l="OK", c=OK, width=100, h=20)
    mc.window("WarningWindow", e=True, wh=(250, 80))

    mc.showWindow()
def Warning_SCRIPT_ALREADY_EXIST():
    BackgroundColor = 0.16
    Message = "AssetIt is already installed, before to update be sure to copy and save you ASSET LIBRARY folder and Restart Maya."
    # ________________//
    if mc.window("WarningWindow", exists=True):
        mc.deleteUI("WarningWindow")
    mc.window("WarningWindow", title=' Update ', s=False, vis=True, rtf=False)
    mc.columnLayout(adj=True, rs=3, bgc=[BackgroundColor, BackgroundColor, BackgroundColor])
    mc.separator(h=8, style='none')
    mc.text(l="  " + Message + "  ", al="center")
    mc.separator(h=8, style='none')
    mc.rowColumnLayout(numberOfRows=1)
    mc.separator(w=180, style='none')
    mc.button(l="UPDATE", c=YES_UPDATE, width=100, h=20)
    mc.separator(w=10, style='none')
    mc.button(l="CANCEL", c=CANCEL, width=100, h=20)
    mc.window("WarningWindow", e=True, wh=(600, 80))
    mc.showWindow()


def OK(*args):
    print ("AssetIt Install")
    mc.deleteUI("WarningWindow")
    
    
def YES_UPDATE(*args):
    print ("UPDATE")
    mc.deleteUI("WarningWindow")
    
    #COPY AS BACKUP PREVIOUS VERSION TO RECOVEREDD LIBRARY
    copytree(UserScriptPath, UserScriptPath+".bckp")
    
    
    #DELETE AND REPLACE ASSETIT
    rmtree(UserScriptPath)
    move(folderDir, UserScriptPath, copy_function=copytree)

    

    Warning_SCRIPT_INSTALL()

    # CLEAN ALL
    move(fileDir, PyCache_Folder, copy_function=copytree)
    rmtree(PyCache_Folder)


def CANCEL(*args):
    mc.deleteUI("WarningWindow")


##____________________________// INSTALL FOLDER
#Check if folder Exist
if os.path.exists(UserScriptPath) == True :
    ScriptUpdate = 1
    print("SCRIPT ALREADY INSTALLED")
    Warning_SCRIPT_ALREADY_EXIST()
    exit()

else:
    print("SCRIPT NOT INSTALL")
    move(folderDir, UserScriptPath, copy_function = copytree)


##____________________________// CREATE SHELF
print("ScriptUpdate : " + str(ScriptUpdate))
#GET CURRENT SHELF
# get top shelf
gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
# get top shelf names
currentShelf = mc.tabLayout(gShelfTopLevel, query=1, selectTab=1)
print(currentShelf)
scriptIconDir = UserScriptPath + "/" + ScriptIconName
print("ScriptCommand : " + ScriptCommand)
mc.shelfButton( annotation= ScriptFolderName, image1= scriptIconDir, command= ScriptCommand, p= currentShelf )


Warning_SCRIPT_INSTALL()

#CLEAN ALL
move(fileDir, PyCache_Folder, copy_function = copytree)
rmtree(PyCache_Folder)
