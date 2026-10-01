from .proxy import cmds, mel
from . import runtime as _r
import time
versionHider = 'FCM_Hider Beta 2.0'
allSets_Ann = 'Left Click:\n -Switch between Show and Hide set\n\nRight click options:\n- Remove all the Body sets\n- Select all content of the set\n- Remove all the Extra sets'
blueButtons_Ann = 'Left Click:\n -Switch between Show and Hide set\n\nRight click options:\n- Add your current selection to the current set\n- Remove your current selection from the current set\n- Select all content of the set\n- Remove all content from the current set'
templateLine_Ann = 'This button allows you to select the usual line between the elbow CRONTROL? and the pole vector control that is mostly unselectable'
editMode_Ann = 'Toggle between Usage and Edit mode'
addSel_Ann = 'Add your current selection to the current set'
addSelExtra_Ann = 'Add your current selection to the current set (Only shapes and polygons)'
grow_Ann = 'Grow selection'
shrink_Ann = 'Shrink selection'
switchPolyOrNurbsCurves_Ann = 'Left Click:\n-Switch between Poly selection and NurbsCurves\nRight Click:\n-Change poly color selection'
objectMode_Ann = 'Object Mode'
deleteAll_Ann = 'Delete everything related to the script'
help_Ann = 'Open help window'
showAllHiddenFaces_Ann = 'Show hidden faces in Hider sets'
checkAllSets_Ann = 'Turn OFF and ON two times each set to check the overall setup'
mirrorButtons_Ann = 'Mirror right Arm and Leg content to the left ones'
unlockAllVisMeshes_Ann = 'Make selectable all visible meshes and unlock layers wholly covered by Hider members'
unlockAllVis_Ann = 'Make selectable all: mesh shape, nurbsCurve shape, transform, annotation shape of the scene'
lockSelection_Ann = 'Make all the items selected unselectables'
rightClickToSeeButtons_Ann = 'Right click to see the buttons'
setsExportSucces = 'Sets exported succesfully!'
setsLoadSucces = 'Sets loaded succesfully!'
setHided = 'Set hidden'
setVisible = 'Set Visible'
allVisMeshSelectable = 'All visible meshes are selectable, and all layerDisplay are unlocked'
allBodySetsRemoved = 'All Body sets removed'
allExtraSetsRemoved = 'All Extra sets removed'
keepYourSecrets = 'Alright then, keep your secrets'
allRemoved = 'everything related to FCM_Hider Removed'
selRemoved = 'Selection removed'
allFacesAreVisible = 'All faces are visible'
setDoesntExistsSet = "Set doesn't exists"
hiderSystemWarning = 'There is more than one Hider system, select the character you want to run'
confirmCheckAllSets = 'This may take a while, do you want to check them?'
errorSaveSets = 'Error trying to load the set, Try to set the namespace the same than when you export the file'
errorExportSets = 'You can only save sets created in the scene'
nothingSel = 'Nothing selected'
setDontExists = "Set doesn't exist"
couldntUnlockAllMeshes = "Couldn't unlock all the meshes because they are in a layerDisplay, check if you can unlock them trough layer display"
couldntUnlockAllLayerDisplay = "Couldn't unlock all layerDisplay"
nothingSelected = 'Nothing selected'
removeAllConfirm = 'Are you sure you want to delete everything related to the script?'
'\n                CREATE SETTINGS AND SETS\n            \n'

def declaringSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, FCM_Hider_Settings
    All_Sets_Hider = namespaceHider + 'All_Sets_Hider'
    Head_Hider = namespaceHider + 'Head_Hider'
    Torso_Hider = namespaceHider + 'Torso_Hider'
    Arm_R_Hider = namespaceHider + 'Arm_R_Hider'
    Arm_L_Hider = namespaceHider + 'Arm_L_Hider'
    Leg_R_Hider = namespaceHider + 'Leg_R_Hider'
    Leg_L_Hider = namespaceHider + 'Leg_L_Hider'
    Extra_One_Hider = namespaceHider + 'Extra_One_Hider'
    Extra_Two_Hider = namespaceHider + 'Extra_Two_Hider'
    Extra_Three_Hider = namespaceHider + 'Extra_Three_Hider'
    FCM_Hider_Settings = namespaceHider + 'FCM_Hider_Settings'

def createAllSets():
    global namespaceHider, All_Sets_Hider, Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, FCM_Hider_Settings
    if cmds.objExists(All_Sets_Hider) == 0:
        cmds.sets(n=All_Sets_Hider, em=True)
    if cmds.objExists(Head_Hider) == 0:
        cmds.sets(n=Head_Hider, em=True)
    if cmds.objExists(Torso_Hider) == 0:
        cmds.sets(n=Torso_Hider, em=True)
    if cmds.objExists(Arm_R_Hider) == 0:
        cmds.sets(n=Arm_R_Hider, em=True)
    if cmds.objExists(Arm_L_Hider) == 0:
        cmds.sets(n=Arm_L_Hider, em=True)
    if cmds.objExists(Leg_R_Hider) == 0:
        cmds.sets(n=Leg_R_Hider, em=True)
    if cmds.objExists(Leg_L_Hider) == 0:
        cmds.sets(n=Leg_L_Hider, em=True)
    if cmds.objExists(Extra_One_Hider) == 0:
        cmds.sets(n=Extra_One_Hider, em=True)
    if cmds.objExists(Extra_Two_Hider) == 0:
        cmds.sets(n=Extra_Two_Hider, em=True)
    if cmds.objExists(Extra_Three_Hider) == 0:
        cmds.sets(n=Extra_Three_Hider, em=True)
    cmds.sets(Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider, edit=True, fe=All_Sets_Hider)

def createSettingsHider():
    if cmds.objExists(FCM_Hider_Settings) == 0:
        selCurrent = cmds.ls(sl=True)
        cmds.group(em=True, n=FCM_Hider_Settings)
        cmds.setAttr('.tx', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.ty', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.tz', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.rx', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.ry', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.rz', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.sx', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.sy', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.sz', lock=True, keyable=False, channelBox=False)
        cmds.setAttr('.v', lock=True, keyable=False, channelBox=False)
        cmds.addAttr(FCM_Hider_Settings, ln='All_Sets_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Head_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Torso_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Arm_R_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Arm_L_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Leg_L_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Leg_R_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Extra_One_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Extra_Two_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Extra_Three_Hider_State', at='bool', dv=True, keyable=True)
        cmds.addAttr(FCM_Hider_Settings, ln='Edit_Mode_State', at='bool', dv=True, keyable=True)
        cmds.select(selCurrent)

def createHiderInTheScene():
    _r.bind_globals(globals())
    createSettingsHider()
    createAllSets()
'\n                    DECLARING NAMESPACES \n            \n'

def declaringNameSpaces():
    _r.bind_globals(globals())
'\n                PRIMARY FUNCTIONS DEF\n            \n'

def queryAllSet():

    def getUniqueItems(iterable):
        result = []
        for item in iterable:
            if item not in result:
                result.append(item)
        return result
        print(''.join(getUniqueItems(list('apple'))))
    return _r.query_members(globals())

def addSelectionToSet():
    global setHider
    try:
        sel = cmds.ls(sl=True, l=True)
        if len(sel) > 0:
            if cmds.objExists(setHider):
                removeNameSpace()
                if shapeMode == 'On':
                    addNameSpace()
                    shapesCtrl = cmds.listRelatives(sel, s=True, fullPath=True)
                    polys = cmds.filterExpand(sel, sm=34, fullPath=True)
                    cmds.sets(shapesCtrl, edit=True, forceElement=setHider)
                    cmds.sets(polys, edit=True, forceElement=setHider)
                if shapeMode == 'Off':
                    addNameSpace()
                    cmds.sets(sel, edit=True, forceElement=setHider)
                queryAllSet()
                hideSet()
                for shape in shapes:
                    cmds.polyOptions(shape, displayInvisibleFaces=1)
                cmds.select(cl=True)
        else:
            cmds.warning(nothingSelected)
    except:
        createSettingsHider()

def hidePolys():
    return _r.hide_member_polys(polys)

def showPolys():
    return _r.show_member_polys(polys)

def hideSet():
    global setHider, namespaceHider
    if cmds.objExists(setHider):
        try:
            value = 0
            currentSel = cmds.ls(sl=True)
            queryAllSet()
            for item in transformAndShapeSet:
                try:
                    cmds.setAttr(item + '.visibility', value)
                except:
                    cmds.setAttr(item + '.lodVisibility', value)
            hidePolys()
            cmds.select(currentSel)
            print(setHided, end=' ')
        except:
            createSettingsHider()
    else:
        cmds.warning("set doesn't exists")
    removeNameSpace()
    cmds.setAttr(FCM_Hider_Settings + '.' + (setHider + '_State'), 0)
    checkStateIcon()

def showSet():
    global setHider, namespaceHider
    if cmds.objExists(setHider):
        value = 1
        currentSel = cmds.ls(sl=True)
        queryAllSet()
        for item in transformAndShapeSet:
            try:
                cmds.setAttr(item + '.visibility', value)
            except:
                cmds.setAttr(item + '.lodVisibility', value)
        showPolys()
        cmds.select(currentSel)
        print(setVisible, end=' ')
    else:
        cmds.warning(setDoesntExists)
    removeNameSpace()
    cmds.setAttr(FCM_Hider_Settings + '.' + (setHider + '_State'), 1)
    checkStateIcon()

def showOrHideButton():
    global setHider
    try:
        contentSet = cmds.sets(setHider, q=True)
        if str(contentSet) == 'None':
            cmds.warning('Set empty')
        else:
            removeNameSpace()
            if cmds.getAttr(FCM_Hider_Settings + '.' + (setHider + '_State')):
                addNameSpace()
                hideSet()
            else:
                addNameSpace()
                showSet()
    except:
        createSettingsHider()
        checkAllIconSets()

def ShowOrHideAllSetsButton():
    global choise
    if cmds.getAttr(FCM_Hider_Settings + '.All_Sets_Hider_State'):
        choise = 'hide'
        ShowOrHideAllSets()
    else:
        choise = 'show'
        ShowOrHideAllSets()

def checkStateIcon():
    global setHider, namespaceHider
    try:
        '\n        # # # check if All_Sets_Hider is empty # # #\n        allSets = cmds.sets(All_Sets_Hider, q=True)\n        result = []\n        for set in allSets:\n            contentSet = cmds.sets(set, q=True)\n            result.append(contentSet)\n            if result == [None, None, None, None, None, None, None, None, None]:\n                # Set icon Empty\n                cmds.iconTextButton ( (All_Sets_Hider + "button"), e=True, image=("Icons_Hider/" + \'All_Sets_Hider\' + "_Empty" + ".png") )\n            else:\n                # All sets hider is not empty\n                # Check settings\n                if cmds.getAttr( (FCM_Hider_Settings + \'.All_Sets_Hider_State\') ):\n                    # Icon On\n                    cmds.iconTextButton ( (All_Sets_Hider + "button"), e=True, image=("Icons_Hider/" + All_Sets_Hider + ".png") )\n                else:\n                    # Icon Off\n                    cmds.iconTextButton ( (All_Sets_Hider + "button"), e=True, image=("Icons_Hider/" + All_Sets_Hider + "_Off" + ".png") )\n        '
        addNameSpace()
        contentSet = cmds.sets(setHider, q=True)
        if str(contentSet) == 'None':
            removeNameSpace()
            cmds.iconTextButton(setHider + 'button', e=True, image='Icons_Hider/' + setHider + '_Empty' + '.png')
        else:
            removeNameSpace()
            if cmds.getAttr(FCM_Hider_Settings + '.' + (setHider + '_State')):
                cmds.iconTextButton(setHider + 'button', e=True, image='Icons_Hider/' + setHider + '.png')
            else:
                cmds.iconTextButton(setHider + 'button', e=True, image='Icons_Hider/' + setHider + '_Off' + '.png')
    except:
        pass

def checkAllIconSets():
    global setHider
    setHider = Head_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Torso_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Arm_R_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Arm_L_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Leg_R_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Leg_L_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Extra_One_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Extra_Two_Hider
    removeNameSpace()
    checkStateIcon()
    setHider = Extra_Three_Hider
    removeNameSpace()
    checkStateIcon()

def ShowOrHideAllSets():
    global setHider
    sets_In_AllSetsHider = cmds.sets(All_Sets_Hider, q=True)
    result = []
    for set in sets_In_AllSetsHider:
        contentSet = cmds.sets(set, q=True)
        result.append(contentSet)
    if result == [None, None, None, None, None, None, None, None, None]:
        cmds.warning('Set empty')
    else:
        for set in sets_In_AllSetsHider:
            setHider = set
            if choise == 'show':
                showSet()
                cmds.setAttr(FCM_Hider_Settings + '.All_Sets_Hider_State', 1)
            if choise == 'hide':
                hideSet()
                cmds.setAttr(FCM_Hider_Settings + '.All_Sets_Hider_State', 0)
        checkStateIcon()

def selectSet():
    if cmds.objExists(setHider):
        cmds.select(setHider)
    else:
        cmds.warning("set doesn't exists")

def showAllHiddenFaces():
    return _r.show_member_faces()
'\n                    LOCK FUNCTIONS\n            \n'

def unlockAllVismeshes():
    return _r.unlock_members(True)

def unlockAllVisible():
    return _r.unlock_members(False)

def lockSelection():
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        selShape = cmds.ls(cmds.pickWalk(sel, d='down'))
        nodes = sel + selShape
        for item in nodes:
            try:
                cmds.setAttr(item + '.overrideDisplayType', 1)
            except:
                pass
        print('Selection Locked', end=' ')
    else:
        cmds.warning(nothingSelected)
'\n                    REMOVE FUNCTIONS DEF\n            \n'

def removeAllBodySets():
    global setHider
    currentSel = cmds.ls(sl=True)
    if cmds.objExists(Head_Hider):
        setHider = Head_Hider
        removeSet()
    if cmds.objExists(Torso_Hider):
        setHider = Torso_Hider
        removeSet()
    if cmds.objExists(Arm_R_Hider):
        setHider = Arm_R_Hider
        removeSet()
    if cmds.objExists(Arm_L_Hider):
        setHider = Arm_L_Hider
        removeSet()
    if cmds.objExists(Leg_R_Hider):
        setHider = Leg_R_Hider
        removeSet()
    if cmds.objExists(Leg_L_Hider):
        setHider = Leg_L_Hider
        removeSet()
    cmds.select(currentSel)
    print(allBodySetsRemoved, end=' ')

def removeAllExtraSets():
    global setHider
    currentSel = cmds.ls(sl=True)
    if cmds.objExists(Extra_One_Hider):
        setHider = Extra_One_Hider
        removeSet()
    if cmds.objExists(Extra_Two_Hider):
        setHider = Extra_Two_Hider
        removeSet()
    if cmds.objExists(Extra_Three_Hider):
        setHider = Extra_Three_Hider
        removeSet()
    cmds.select(currentSel)
    print(allExtraSetsRemoved, end=' ')

def removeAllHider():
    removeAllBodySets()
    removeAllExtraSets()
    if cmds.objExists(FCM_Hider_Settings):
        cmds.delete(FCM_Hider_Settings)
    if cmds.objExists(All_Sets_Hider):
        cmds.delete(All_Sets_Hider)
    if cmds.window('windowHider', exists=True):
        cmds.deleteUI('windowHider')
    print(allRemoved, end=' ')

def confirmRemoveAllHider():
    response = cmds.confirmDialog(title='Confirm Window', message=removeAllConfirm, button=['Yes', 'No'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel')
    if response == 'Yes':
        removeAllHider()
    if response == 'No':
        print(keepYourSecrets, end=' ')

def removeSet():
    return _r.clear_current_set()

def removeSelection():
    global setHider
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        if cmds.objExists(setHider):
            value = 1
            transformSel = cmds.ls(sl=True, type='transform')
            polysSel = cmds.filterExpand(sel, sm=34, fullPath=True)
            shapesSel = cmds.listRelatives(sel, s=True)
            cmds.sets(shapesSel, edit=True, rm=setHider)
            cmds.sets(sel, edit=True, rm=setHider)
            try:
                for item in shapesSel:
                    try:
                        cmds.setAttr(item + '.visibility', value)
                    except:
                        cmds.setAttr(item + '.lodVisibility', value)
            except:
                pass
            for item in transformSel:
                try:
                    cmds.setAttr(item + '.visibility', value)
                except:
                    cmds.setAttr(item + '.lodVisibility', value)
            if value == 1:
                value = 0
            cmds.showHidden(polysSel)
            try:
                for poly in polysSel:
                    cmds.polyHole(poly, assignHole=value)
            except:
                pass
            checkStateIcon()
            print(selRemoved, end=' ')
        else:
            cmds.warning(setDontExists)
    else:
        cmds.warning(nothingSel)
'\n                    NAMESPACES DEF\n            \n'

def queryNamespace():
    return _r.current_system()

def removeNameSpace():
    global setHider
    setHider = setHider.rsplit(':', 1)[-1]

def addNameSpace():
    global setHider
    setHider = namespaceHider + setHider.rsplit(':', 1)[-1]
'\n                SAVE AND LOAD SETS DEF\n            \n'

def saveSetsHider():
    return _r.file_dialog('export_sets')

def LoadSetsHider():
    return _r.file_dialog('import_sets')
'\n                    WINDOW FUNCTIONS DEF\n            \n'

def inViewMessageHider():
    global messageHider
    cmds.inViewMessage(amg='<span style="color:#82C99A;"> ' + messageHider + ' </span> ', dragKill=True, pos='topCenter', fade=True)

def toggleEditMode():
    if cmds.window('windowHider', q=True, h=True) == 36 + highWindow:
        cmds.iconTextButton('Edit_Modebutton', e=True, image1='Icons_Hider/Contract_Hider.png')
        cmds.window('windowHider', edit=True, w=widthWindow, h=74 + highWindow)
        cmds.setAttr(FCM_Hider_Settings + '.Edit_Mode_State', 1)
    else:
        cmds.iconTextButton('Edit_Modebutton', e=True, image1='Icons_Hider/Expand_Hider.png')
        cmds.window('windowHider', edit=True, w=widthWindow, h=36 + highWindow)
        cmds.setAttr(FCM_Hider_Settings + '.Edit_Mode_State', 0)

def checkEditMode():
    if cmds.getAttr(FCM_Hider_Settings + '.Edit_Mode_State'):
        cmds.iconTextButton('Edit_Modebutton', e=True, image1='Icons_Hider/Contract_Hider.png')
        cmds.window('windowHider', edit=True, w=widthWindow, h=74 + highWindow)
    else:
        cmds.iconTextButton('Edit_Modebutton', e=True, image1='Icons_Hider/Expand_Hider.png')
        cmds.window('windowHider', edit=True, w=widthWindow, h=36 + highWindow)

def objectModeHider():
    global messageHider
    cmds.selectMode(object=True)
    mel.eval('selectMode -object; selectType -handle 1 -ikHandle 1 -joint 1 -nurbsCurve 1 -cos 1 -stroke 1 -nurbsSurface 1 -polymesh 1 -subdiv 1 -plane 1 -lattice 1 -cluster 1 -sculpt 1 -nonlinear 1 -particleShape 1 -emitter 1 -field 1 -spring 1 -rigidBody 1 -fluid 1 -hairSystem 1 -follicle 1 -nCloth 1 -nRigid 1 -dynamicConstraint 1 -rigidConstraint 1 -collisionModel 1 -light 1 -camera 1 -texture 1 -ikEndEffector 1 -locator 1 -dimension 1;selectType -byName gpuCache 1;')
    mel.eval('selectMode -component; selectType -cv 1 -vertex 1 -subdivMeshPoint 1 -latticePoint 1 -particle 1 -editPoint 0 -curveParameterPoint 0 -surfaceParameterPoint 0 -puv 0 -polymeshEdge 0 -subdivMeshEdge 0 -isoparm 0 -surfaceEdge 0 -surfaceFace 1 -springComponent 0 -facet 0 -subdivMeshFace 1 -hull 0 -rotatePivot 0 -scalePivot 0 -jointPivot 0 -selectHandle 0 -localRotationAxis 0 -imagePlane 0;')
    mel.eval('changeSelectMode -object')
    messageHider = 'Object Mode'
    inViewMessageHider()

def switchPolyOrNurbsSel():
    global messageHider
    if cmds.iconTextButton('toggleFacesNurbsCurve', q=True, i=True) == 'Icons_Hider/Only_Faces_Hider.png':
        objectModeHider()
        cmds.selectType(cv=True)
        mel.eval('setObjectPickMask "All" 0;setObjectPickMask "Curve" true')
        messageHider = 'NurbsCurve selection Mode'
        inViewMessageHider()
        cmds.iconTextButton('toggleFacesNurbsCurve', e=True, i='Icons_Hider/Only_NurbsCurve_Hider.png')
    else:
        mel.eval('changeSelectMode -component')
        mel.eval('setComponentPickMask "Facet" true; ')
        cmds.selectType(cv=False)
        messageHider = 'Poly Faces selection Mode'
        inViewMessageHider()
        cmds.iconTextButton('toggleFacesNurbsCurve', e=True, i='Icons_Hider/Only_Faces_Hider.png')
'\n                SELECT TEMPLATE LINE DEF\n            \n'

def growSelection():
    cmds.select(cmds.listConnections(t='transform'))

def filterOnlyCurves():
    sel = cmds.ls(sl=True)
    onlyCurves = cmds.filterExpand(sel, sm=9, fullPath=True)
    cmds.select(onlyCurves)
    print('You have selected: ' + str(onlyCurves), end=' ')

def printSelected():
    sel = cmds.ls(sl=True)
    print(str(len(sel)), end=' ')

def SelectTemplateLineWindow():
    if cmds.window('Select_Template_Line', exists=True):
        cmds.deleteUI('Select_Template_Line')
    selectTemplateLine = cmds.window('Select_Template_Line', title='Select Template Line', s=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(l='Usage: First select pole vector Ctrl\nThen grow selection, Filter and add it to a Set', h=30, fn='boldLabelFont')
    cmds.separator()
    cmds.button(l='1- Grow selection', c='growSelection()')
    cmds.separator()
    cmds.button(l='2- Filter Only Curves', c='filterOnlyCurves()')
    cmds.separator()
    cmds.button(l='3- Print number selected', c='printSelected()')
    cmds.showWindow(selectTemplateLine)
    cmds.window('Select_Template_Line', edit=True, w=300, h=110)
    print('Select Template Line Window', end=' ')

def mirrorCtrlsHider():
    global setHiderParent, setHiderChild
    L_Content = []
    finalContentL = []
    L_item = []
    for item in setHiderParent:
        L_item = item.replace(R_Variable, L_Variable)
        if L_item != item:
            L_Content.append(L_item)
            for itemL in L_Content:
                try:
                    cmds.select(itemL)
                    finalContentL.append(itemL)
                    cmds.select(finalContentL)
                    sel = cmds.ls(sl=True)
                    cmds.sets(sel, fe=setHiderChild)
                    cmds.select(cl=True)
                except:
                    pass
'\n                    MIRROR DEF\n            \n'

def mirrorCtrlsHider():
    global setHiderParent, setHiderChild
    L_Content = []
    finalContentL = []
    L_item = []
    for item in setHiderParent:
        L_item = item.replace(R_Variable, L_Variable)
        if L_item != item:
            L_Content.append(L_item)
            for itemL in L_Content:
                try:
                    cmds.select(itemL)
                    finalContentL.append(itemL)
                    cmds.select(finalContentL)
                    sel = cmds.ls(sl=True)
                    cmds.sets(sel, fe=setHiderChild)
                    cmds.select(cl=True)
                except:
                    pass

def tryNomenclaturesMirror():
    global R_Variable, L_Variable
    R_Variable = 'R_'
    L_Variable = 'L_'
    mirrorCtrlsHider()
    R_Variable = '_R'
    L_Variable = '_L'
    mirrorCtrlsHider()
    R_Variable = '_R_'
    L_Variable = '_L_'
    mirrorCtrlsHider()
    R_Variable = 'r_'
    L_Variable = 'l_'
    mirrorCtrlsHider()
    R_Variable = '_r'
    L_Variable = '_l'
    mirrorCtrlsHider()
    R_Variable = '_r_'
    L_Variable = '_l_'
    mirrorCtrlsHider()
    R_Variable = 'Right'
    L_Variable = 'Left'
    mirrorCtrlsHider()
    R_Variable = 'right'
    L_Variable = 'left'
    mirrorCtrlsHider()
    R_Variable = 'rt'
    L_Variable = 'lf'
    mirrorCtrlsHider()
    R_Variable = 'Rt'
    L_Variable = 'Lf'
    mirrorCtrlsHider()
    R_Variable = 'RGT'
    L_Variable = 'LFT'
    mirrorCtrlsHider()
    R_Variable = 'Rgt'
    L_Variable = 'Lft'
    mirrorCtrlsHider()

def mirrorPolyHider():
    return _r.mirror_faces_into(setHiderParent, setHiderChild)

def mirrorHider():
    return _r.mirror_sets()
'\n                    CHECK ALL SETS DEF\n            \n'

def waitAndRefresh():
    cmds.refresh()

def cycleTurnOnAndOff():
    waitAndRefresh()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()

def checkAllSets():
    global setHider, choise
    response = cmds.confirmDialog(title='Confirm Check all sets', message=confirmCheckAllSets, button=['Yes', 'No'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel')
    if response == 'Yes':
        choise = 'show'
        ShowOrHideAllSets()
        allSetsCheck = [Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider]
        cmds.progressWindow(title='Progress Hider test', isInterruptable=True)
        amount = 0
        for set in allSetsCheck:
            cmds.progressWindow(edit=True, progress=amount, status='Testing: ' + set)
            setHider = set
            cycleTurnOnAndOff()
            amount = amount + 11
            if cmds.progressWindow(query=True, isCancelled=True):
                break
            if cmds.progressWindow(query=True, progress=True) >= 100:
                break
        cmds.progressWindow(endProgress=1)

def cycleTurnOnAndOffIsolate():
    waitAndRefresh()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()
    waitAndRefresh()
    addNameSpace()
    showSet()
    waitAndRefresh()
    addNameSpace()
    hideSet()

def checkAllSetsIsolate():
    global setHider, choise
    choise = 'hide'
    ShowOrHideAllSets()
    allSetsCheck = [Head_Hider, Torso_Hider, Arm_R_Hider, Arm_L_Hider, Leg_R_Hider, Leg_L_Hider, Extra_One_Hider, Extra_Two_Hider, Extra_Three_Hider]
    cmds.progressWindow(title='Progress Hider test', isInterruptable=True)
    amount = 0
    for set in allSetsCheck:
        cmds.progressWindow(edit=True, progress=amount, status='Testing: ' + set)
        setHider = set
        cycleTurnOnAndOffIsolate()
        amount = amount + 11
        if cmds.progressWindow(query=True, isCancelled=True):
            break
        if cmds.progressWindow(query=True, progress=True) >= 100:
            break
    cmds.progressWindow(endProgress=1)
    choise = 'show'
    ShowOrHideAllSets()
'\n                    HELP AND CONTACT WINDOW DEF\n            \n'

def launchtutorial():
    cmds.launch(web='https://youtu.be/RDHIFQfD12g')

def toggleImageHelpWindow():
    return _r.help_window()

def helpWindow():
    return _r.help_window()

def contactWindow():
    if cmds.window('FCM_Contact', exists=True):
        cmds.deleteUI('FCM_Contact')
    FCMContact = cmds.window('FCM_Contact', title='Contact', s=False)
    cmds.rowColumnLayout(numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)])
    cmds.text(label='Name:  ')
    name = cmds.textField(text='Francisco Cerchiara Montero', editable=True)
    cmds.text(label='Email:  ')
    address = cmds.textField(text='FranCM127@hotmail.com', editable=True)
    cmds.text(label='Facebook:  ')
    phoneNumber = cmds.textField(text='www.facebook.com/Fran127', editable=True)
    cmds.text(label='Linked-In:  ')
    email = cmds.textField(text='www.linkedin.com/in/francm3danimator/', editable=True)
    cmds.textField(name, edit=True, enterCommand='cmds.setFocus("' + address + '")')
    cmds.textField(address, edit=True, enterCommand='cmds.setFocus("' + phoneNumber + '")')
    cmds.textField(phoneNumber, edit=True, enterCommand='cmds.setFocus("' + email + '")')
    cmds.textField(email, edit=True, enterCommand='cmds.setFocus("' + name + '")')
    cmds.showWindow(FCMContact)
'\n                    WINDOW HIDER DEF\n            \n'
highWindow = 20
widthWindow = 388

def buttonWindowHider():
    global shapeMode
    removeNameSpace()
    cmds.iconTextButton(setHider + 'button', style='iconOnly', ann=blueButtons_Ann, commandRepeatable=True, i='Icons_Hider/' + setHider + '.png', c=commandButton)
    cmds.popupMenu(postMenuCommand=popUpButton)
    cmds.menuItem(i='Icons_Hider/PopUp_Add_Hider.png', l='Add Selection', c="shapeMode = 'Off'; addSelectionToSet()")
    cmds.menuItem(i='Icons_Hider/PopUp_Add_Hider.png', l='Add Selection Shape', c="shapeMode = 'On'; addSelectionToSet()")
    cmds.menuItem(divider=True)
    cmds.menuItem(i='Icons_Hider/PopUp_Remove_Hider.png', l='Remove Selection', c='removeSelection()')
    cmds.menuItem(i='Icons_Hider/PopUp_SelectSet_Hider.png', l='Select Set', c='selectSet()')
    cmds.menuItem(i='Icons_Hider/PopUp_RemoveSet_Hider.png', l='Remove Set', c='removeSet()')

def HiderUI():
    global blueButtons_Ann, commandButton, popUpButton, setHider
    declaringNameSpaces()
    createSettingsHider()
    if cmds.window('windowHider', exists=True):
        cmds.deleteUI('windowHider')
    windowHider = cmds.window('windowHider', s=False, title='FCM_Hider: ' + namespaceHiderForWindow, menuBar=True)
    cmds.menu('FileMenu', label='File')
    cmds.menuItem(l='Save Sets', c='saveSetsHider()')
    cmds.menuItem(l='Load Sets', c='LoadSetsHider()')
    cmds.menu('HelpMenu', label='Help')
    cmds.menuItem(l='Video Tutorial', c='launchtutorial()')
    cmds.menuItem(l='Contact', c='contactWindow()')
    cmds.menuItem(l='About version', c='print(versionHider),')
    cmds.rowColumnLayout(numberOfColumns=11)
    cmds.iconTextButton('Edit_Modebutton', i='Icons_Hider/Contract_Hider.png', c='toggleEditMode()', ann=editMode_Ann)
    setHider = All_Sets_Hider
    removeNameSpace()
    cmds.iconTextButton(setHider + 'button', ann=allSets_Ann, commandRepeatable=True, i='Icons_Hider/' + setHider + '.png', c="cmds.warning('Show or Hide all WIP')")
    cmds.popupMenu(postMenuCommand='setHider = All_Sets_Hider')
    cmds.menuItem(i='Icons_Hider/PopUp_RemoveSet_Hider.png', l='Empty Sets Body', c='removeAllBodySets()')
    cmds.menuItem(i='Icons_Hider/PopUp_RemoveSet_Hider.png', l='Empty Sets Extras', c='removeAllExtraSets()')
    cmds.menuItem(i='Icons_Hider/PopUp_SelectSet_Hider.png', l='Select All Sets', c='cmds.select(All_Sets_Hider)')
    setHider = Head_Hider
    commandButton = 'setHider = Head_Hider; showOrHideButton()'
    popUpButton = 'setHider = Head_Hider'
    buttonWindowHider()
    setHider = Torso_Hider
    commandButton = 'setHider = Torso_Hider; showOrHideButton()'
    popUpButton = 'setHider = Torso_Hider'
    buttonWindowHider()
    setHider = Arm_R_Hider
    commandButton = 'setHider = Arm_R_Hider; showOrHideButton()'
    popUpButton = 'setHider = Arm_R_Hider'
    buttonWindowHider()
    setHider = Arm_L_Hider
    commandButton = 'setHider = Arm_L_Hider; showOrHideButton()'
    popUpButton = 'setHider = Arm_L_Hider'
    buttonWindowHider()
    setHider = Leg_R_Hider
    commandButton = 'setHider = Leg_R_Hider; showOrHideButton()'
    popUpButton = 'setHider = Leg_R_Hider'
    buttonWindowHider()
    setHider = Leg_L_Hider
    commandButton = 'setHider = Leg_L_Hider; showOrHideButton()'
    popUpButton = 'setHider = Leg_L_Hider'
    buttonWindowHider()
    setHider = Extra_One_Hider
    commandButton = 'setHider = Extra_One_Hider; showOrHideButton()'
    popUpButton = 'setHider = Extra_One_Hider'
    buttonWindowHider()
    setHider = Extra_Two_Hider
    commandButton = 'setHider = Extra_Two_Hider; showOrHideButton()'
    popUpButton = 'setHider = Extra_Two_Hider'
    buttonWindowHider()
    setHider = Extra_Three_Hider
    commandButton = 'setHider = Extra_Three_Hider; showOrHideButton()'
    popUpButton = 'setHider = Extra_Three_Hider'
    buttonWindowHider()
    cmds.iconTextButton(i='Icons_Hider/Unlock_Hider.png', c='cmds.warning(rightClickToSeeButtons_Ann),', ann=rightClickToSeeButtons_Ann)
    cmds.popupMenu()
    cmds.menuItem(i='Icons_Hider/Unlock_Hider.png', l='Unlock Hider Members', c='unlockAllVisible()', ann=unlockAllVis_Ann)
    cmds.menuItem(i='Icons_Hider/Unlock_Hider.png', l='Unlock Hider Mesh Members', c='unlockAllVismeshes()', ann=unlockAllVisMeshes_Ann)
    cmds.menuItem(i='Icons_Hider/Lock_Hider.png', l='Lock Selection', c='lockSelection()', ann=lockSelection_Ann)
    cmds.iconTextButton(i='Icons_Hider/ObjectMode_Hider.png', c='objectModeHider()', ann=objectMode_Ann)
    cmds.iconTextButton('toggleFacesNurbsCurve', i='Icons_Hider/Only_Faces_Hider.png', c='switchPolyOrNurbsSel()', ann=switchPolyOrNurbsCurves_Ann)
    cmds.popupMenu()
    cmds.menuItem(i='Icons_Hider/PolyColorSel_Red_Hider.png', l='Poly color selection Red', c="cmds.displayColor ('polyFace', 13, active= True)")
    cmds.menuItem(i='Icons_Hider/PolyColorSel_Green_Hider.png', l='Poly color selection Green', c="cmds.displayColor ('polyFace', 14, active= True)")
    cmds.menuItem(i='Icons_Hider/PolyColorSel_Default_Hider.png', l='Poly color selection default', c="cmds.displayColor ('polyFace', 21, active= True)")
    cmds.iconTextButton(i='Icons_Hider/Grow_Hider.png', c='cmds.polySelectConstraint (pp=1)', commandRepeatable=True, ann=grow_Ann)
    cmds.iconTextButton(i='Icons_Hider/Shrink_Hider.png', c='cmds.polySelectConstraint (pp=2)', commandRepeatable=True, ann=shrink_Ann)
    cmds.iconTextButton(i='Icons_Hider/Template_Line_Hider.png', c='SelectTemplateLineWindow()', ann=templateLine_Ann)
    cmds.iconTextButton(i='Icons_Hider/Mirror_Hider.png', c='mirrorHider()', ann=mirrorButtons_Ann)
    cmds.iconTextButton(i='Icons_Hider/Show_All_Hidden_Faces_Hider.png', c='checkAllSets()', ann=checkAllSets_Ann)
    cmds.popupMenu()
    cmds.menuItem(l='Isolate mode', c='checkAllSetsIsolate()', ann=checkAllSets_Ann + ' but isolating every set')
    cmds.iconTextButton(i='Icons_Hider/Extra_Functions_Hider.png', c='cmds.warning(rightClickToSeeButtons_Ann),', ann=rightClickToSeeButtons_Ann)
    cmds.popupMenu('extraFunctions')
    cmds.menuItem(l='Show hidden faces in Hider sets', c='showAllHiddenFaces()')
    cmds.iconTextButton(i='Icons_Hider/Remove_All_Hider.png', c='confirmRemoveAllHider()', ann=deleteAll_Ann)
    cmds.setParent('..')
    cmds.showWindow(windowHider)
    checkEditMode()
    checkAllIconSets()
