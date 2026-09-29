import os

try:
    import maya.mel as mel
    import maya.cmds as mc
    import shutil
    isMaya = True
except ImportError:
    isMaya = False

def isWritable(fileToCheck):
    if os.path.exists(fileToCheck):
        if os.path.isfile(fileToCheck):
            return os.access(fileToCheck, os.W_OK)
    else:
        return True

def defineScriptCommand(scriptName,mayaScriptDir,function):
    command = '''
# -----------------------------------
# {myScriptName}
# Copyright (c) <2025> <JesseOngPho>
# jesseongpho@hotmail.com
# -----------------------------------

import os
import sys
from imp import reload

if not os.path.exists(r'{path}'):
    mc.error( r'The source path "{path}" does not exist!')
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

import {myScriptName}
reload({myScriptName})
{myScriptName}.{myCommand}()
'''.format(myScriptName = scriptName,path=mayaScriptDir, myCommand=function)
    return command

def createShelfButton(scriptName,mayaScriptDir,iconsToCopy):
    #Check if the current shelf is non-writable
    shelf = mel.eval("$gShelfTopLevel=$gShelfTopLevel;")
    parent = mc.tabLayout(shelf, query=True,selectTab=True)

    if not isWritable(str(mc.internalVar(userPrefDir=True) + 'shelves/shelf_' + parent + '.mel')):
        mc.confirmDialog(title='Can\'t install',icon = 'warning', message='The current shelf is non-writable. Select another shelf and try the installation again')

    else:
        command = defineScriptCommand(scriptName,mayaScriptDir,'main')
        
        #Check if button already exists in current shelf and save/delete its position index then reapply it to the new Button
        targetButtonLabel = scriptName
        buttons = mc.shelfLayout(parent, q=True, ca=True)
        myButton=''
        counter = 0
        myPosition=0         
        if (buttons): 
            for myScriptButton in buttons:
                label = mc.shelfButton(myScriptButton, q=True, label=True)
                if (label == targetButtonLabel):
                    mc.deleteUI(myScriptButton, control=True)     
                    myPosition = counter+1
                    break
                counter+=1  
        
        #Create the button with all the attributes
        myNewButton=mc.shelfButton(
            command=command,
            annotation=scriptName+'\n1) Choose to check the Bake check box or not.\n2) Select controllers to save.\n3) Click on the save button.\n4) Do the wanted modification.\n5) Click on Retarget Animation ',
            sourceType='Python',
            image=iconsToCopy,
            parent=parent, 
            label = scriptName
         )

        if myPosition:
            mc.shelfLayout(parent, e=True, position=[myNewButton,myPosition])
        
                
        mc.inViewMessage( amg=(scriptName+  " has been Added/Updated to the current shelf."), pos='midCenter', fade=True)

def getScriptName():
    installPath = (os.path.realpath(__file__)) 
    scriptName = installPath.split(os.sep)[-2]
    return scriptName
    
def fileSetup(scriptName):
#currentLocation
    installPath = (os.path.realpath(__file__)) 
    currentFolder = installPath.split('dragAndDrop.py') [0]
    iconsToCopy = currentFolder+ scriptName+"_icon.png"
    scriptToCopy= currentFolder+ scriptName+".py"
    
    #target directories

    mayaPref = os.path.normpath(mc.internalVar(userPrefDir=True))
    mayaIconTraget = os.sep.join([mayaPref, 'icons',scriptName+"_icon.png"])
    mayaScriptDir = os.sep.join([mayaPref, 'scripts'])
    print(mayaPref, mayaIconTraget, mayaScriptDir)
    
    #check if the files are at the good location
    if not os.path.exists(iconsToCopy):
        mc.error('The icon is missing. Make sure the icon file is in the installation folder' )
    if not os.path.exists(scriptToCopy):
        mc.error('The script is missing. Make sure the script file is in the installation folder' )
    
    return iconsToCopy, mayaIconTraget,scriptToCopy, mayaScriptDir

#When Drag and Drop
def onMayaDropped(*args, **kwargs):
    scriptName = getScriptName()

    iconsToCopy, mayaIconTraget,scriptToCopy, mayaScriptDir = fileSetup(scriptName)
    
    #copy the icon and the python script to maya preferences.
    shutil.copy( iconsToCopy, mayaIconTraget)
    shutil.copy( scriptToCopy, mayaScriptDir)

    createShelfButton (scriptName,mayaScriptDir,mayaIconTraget)
    
if isMaya:
    onMayaDropped()
