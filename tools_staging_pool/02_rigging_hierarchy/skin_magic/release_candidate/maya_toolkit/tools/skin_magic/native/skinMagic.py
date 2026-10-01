from .. import ui_support as bridge
import os
import time
import subprocess
import math
import sys
import inspect
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import webbrowser
import re
from string import ascii_lowercase
from string import ascii_uppercase
from itertools import chain
import pymel.core.datatypes as dt
import copy
import urllib.request, urllib.error, urllib.parse
from shutil import copyfile
import random
import maya.OpenMaya as OpenMaya
import operator
version = 40000
scriptName = inspect.getframeinfo(inspect.currentframe()).filename
scriptPath = os.path.dirname(os.path.abspath(scriptName))
skinMagic_MainUIFile = scriptPath + os.sep + 'skinMagic.ui'
paypalLink = 'https://www.paypal.me/Yanbin'
linkedinLink = 'https://ca.linkedin.com/in/baiyanbin'
vimeoLink = ''
bilibiliLink = 'https://animbai.com/zh/2017/10/14/skintools-tutorials/'
youtubeLink = 'https://animbai.com/2017/10/14/skintools-tutorials/'
bitcoin = '1HT1L4tGobHVmJJZMsj2GG1oZRaowedwUs'
updateLink = 'https://animbai.com/category/download/'
versionCheckLink = 'http://animbai.com/skintoolsver/'
spam_word = ['', '', '', '', '']
influenceAssociationSetting = ['label', 'name', 'closestJoint', 'oneToOne']

def showSpam():
    sWrod = spam_word[random.randint(0, 4)]
    printTextLable(main_processLable, str(sWrod))

def removeUnknowNodeButtonCmd(ignoreInputs):
    removeUnknowNode()

def meshCleanUpButtonCmd(ignoreInputs):
    meshCleanUp()

def bindSkinPlusButtonCmd(ignoreInputs):
    bindSkinPlus()

def scaleJointButtonCmd(ignoreInputs):
    scaleJoint()

def cleanAttrButtonCmd(ignoreInputs):
    cleanAttr()

def shrinkSelectionCmd(ignoreInputs):
    shrinkSelection()

def growSelectionCmd(ignoreInputs):
    growSelection()

def elementSelectionCmd(ignoreInputs):
    elementSelection()

def waveSelectionCmd(ignoreInputs):
    waveSelection()

def ringSelectionCmd(ignoreInputs):
    ringSelection()

def loopSelectionCmd(ignoreInputs):
    loopSelection()

def setWeight0Cmd(ignoreInputs):
    setWeightFromBotton(0)

def setWeight01Cmd(ignoreInputs):
    setWeightFromBotton(0.1)

def setWeight025Cmd(ignoreInputs):
    setWeightFromBotton(0.25)

def setWeight05Cmd(ignoreInputs):
    setWeightFromBotton(0.5)

def setWeight075Cmd(ignoreInputs):
    setWeightFromBotton(0.75)

def setWeight09Cmd(ignoreInputs):
    setWeightFromBotton(0.9)

def setWeight1Cmd(ignoreInputs):
    setWeightFromBotton(1)

def setWeightFromValueCmd(ignoreInputs):
    setWeightFromValue()

def plusWeightCmd(ignoreInputs):
    plusWeight()

def minusWeightCmd(ignoreInputs):
    minusWeight()

def copyWeightCmd(ignoreInputs):
    copyWeight()

def pasteWeightCmd(ignoreInputs):
    pasteWeight()

def relaxWeightCmd(ignoreInputs):
    relaxWeight_2()

def rangeExtCmd(ignoreInputs):
    rangeExtend()

def rangeShrCmd(ignoreInputs):
    rangeShrink()

def weightToolOnCmd(ignoreInputs):
    weightToolOn()

def weightToolOffCmd(ignoreInputs):
    weightToolOff()

def addBoneCmd(ignoreInputs):
    addBone()

def removeBoneCmd(ignoreInputs):
    removeBone()

def boneListSelectedCmd(ignoreInputs=False):
    boneListSelected()

def vertexSizeCmd(ignoreInputs):
    vertexSize()

def pruneWeightCmd(ignoreInputs):
    pruneWeight()

def mirrorWeightCmd(ignoreInputs):
    mirrorWeight()

def swapWeightCmd(ignoreInputs):
    swapWeight()

def swapLoadBoneACmd(ignoreInputs):
    swapLoadBoneA()

def swapLoadBoneBCmd(ignoreInputs):
    swapLoadBoneB()

def transferWeightCmd(ignoreInputs):
    transferWeight()

def mirrorXSelectedCmd(ignoreInputs):
    mirrorXSelected()

def mirrorYSelectedCmd(ignoreInputs):
    mirrorYSelected()

def mirrorZSelectedCmd(ignoreInputs):
    mirrorZSelected()

def paintVertexOnCmd(ignoreInputs):
    paintVertexOn()

def paintVertexOffCmd(ignoreInputs):
    paintVertexOff()

def setVertexSizeCmd(ignoreInputs):
    setVertexSize()

def normalizeWeightCmd(ignoreInputs):
    normalizeWeight()

def exportVtxWeightCmd(ignoreInputs):
    exportVtxManager()

def importVtxWeightCmd(ignoreInputs):
    importVtxManager()

def lodSourceMeshButtonCmd(ignoreInputs):
    lodGetMesh('source')

def lodTargetMeshButtonCmd(ignoreInputs):
    lodGetMesh('target')

def lodAddButtonCmd(ignoreInputs):
    lodAdd()

def lodRemoveButtonCmd(ignoreInputs):
    lodRemove()

def lodRefreshButtonCmd(ignoreInputs):
    lodUpdateReceiver()

def lodClearButtonCmd(ignoreInputs):
    lodClear()

def lodSaveButtonCmd(ignoreInputs):
    lodSave()

def lodLoadButtonCmd(ignoreInputs):
    lodLoad()

def lodResetButtonCmd(ignoreInputs):
    lodReset()

def lodMakeButtonCmd(ignoreInputs):
    lodMakeLauncher()

def lodBoneListSelectedCmd(ignoreInputs=False):
    lodBoneListSelected()

def goreGetBaseMeshButtonCmd(ignoreInputs):
    goreGetBaseMesh()

def goreAddButtonCmd(ignoreInputs):
    goreAdd()

def goreRemoveButtonCmd(ignoreInputs):
    goreRemove()

def goreClearButtonCmd(ignoreInputs):
    goreClear()

def goreMakeButtonCmd(ignoreInputs):
    goreMake()

def checkInfluenceCmd(ignoreInputs):
    checkInfluence()

def bsTransLoadSrcButtonCmd(ignoreInputs):
    bsTransLoadSrc()

def bsTransLoadTgtButtonCmd(ignoreInputs):
    bsTransLoadTgt()

def bsTransDoButtonCmd(ignoreInputs):
    bsTransDo()

def boneLabelDoButtonCmd(ignoreInputs):
    boneLabelDo()

def buildWeightMapCmd(ignoreInputs):
    buildWeightMap()

def linkinCmd(ignoreInputs):
    url = linkedinLink
    webbrowser.open(url, new=2)

def renameMakeCmd(ignoreInputs):
    renameMake()

def renameStartChangeCmd(ignoreInputs=False):
    if renameStart_lineEdit.getText():
        if renameStart_lineEdit.getText() == '1':
            renameStart_label.setLabel('st')
        elif renameStart_lineEdit.getText() == '2':
            renameStart_label.setLabel('nd')
        elif renameStart_lineEdit.getText() == '3':
            renameStart_label.setLabel('rd')
        elif renameStart_lineEdit.getText() == '0':
            renameStart_lineEdit.setText('1')
            renameStart_label.setLabel('st')
        else:
            renameStart_label.setLabel('th')
    else:
        renameStart_lineEdit.setText('1')
        renameStart_label.setLabel('st')
    if renamePreview_lineEdit.getText():
        renameUpdatePreview()

def renameUpdatePreviewCmd(ignoreInputs=False):
    renameUpdatePreview()

def deformerOKCmd(ignoreInputs):
    deformerOK()

def deformerWebCmd(ignoreInputs):
    url = 'http://www.creativecrash.com/maya/script/deformer-to-blendshape'
    webbrowser.open(url, new=2)

def springPasteCmd(ignoreInputs):
    pass

def springSetCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springStraightCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springApplyCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springCopyCmd(ignoreInputs):
    copyBonePose()

def springPasteCmd(ignoreInputs):
    pasteBonePose()

def springWebCmd(ignoreInputs):
    url = 'http://www.scriptspot.com/3ds-max/scripts/spring-magic'
    webbrowser.open(url, new=2)

def springTwistChangeCmd(ignoreInputs=False):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springChangeCmd(ignoreInputs=False):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springTensionChangeCmd(ignoreInputs=False):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springSubDivChangeCmd(ignoreInputs=False):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springAddWindCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springAddBodyCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springRemoveBodyCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springClearBodyCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springBindControllerCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def springClearBindCmd(ignoreInputs):
    raise RuntimeError('Spring algorithm and controls are absent from supplied SkinMagic 4.0; use the separate Spring Magic candidate')

def goShelfCmd(ignoreInputs):
    goShelf()

def languageCmd(ignoreInputs):
    if language_list.getVisible():
        language_list.setVisible(False)
    else:
        language_list.setVisible(True)

def languageSelectedCmd(ignoreInputs=False):
    language_list.setVisible(False)
    applyLanguage(int(language_list.getSelectIndexedItem()[0]))

def reSkinPickBoneCmd(ignoreInputs):
    reSkinPickBone()

def reSkinCmd(ignoreInputs):
    reSkin()

def meshDelNonSkinHistoryCmd(ignoreInputs):
    meshDelNonSkinHistory2()

def bilibiliCmd(ignoreInputs):
    url = bilibiliLink
    try:
        webbrowser.open(url, new=2)
    except:
        pass

def youtubeCmd(ignoreInputs):
    url = youtubeLink
    try:
        webbrowser.open(url, new=2)
    except:
        pass

def vimeoCmd(ignoreInputs):
    pass

def donatePayPal_buttonCmd(ignoreInputs):
    url = paypalLink
    try:
        webbrowser.open(url, new=2)
    except:
        pass

def dockScriptEditorCmd(ignoreInputs):
    mel.eval('ScriptEditor;')

def updatePageCmd(ignoreInputs):
    url = updateLink
    try:
        webbrowser.open(url, new=2)
    except:
        pass

def applyLanguage(lanId):
    return bridge.switch_language({1: 'chn', 2: 'eng', 3: 'jpn'}[lanId])

def detectMayaLanguage():
    mayaLan = None
    try:
        mayaLan = os.environ['MAYA_UI_LANGUAGE']
    except:
        import locale
        mayaLan = locale.getdefaultlocale()[0]
    if mayaLan == 'en_US':
        applyLanguage(2)
    elif mayaLan == 'zh_CN':
        applyLanguage(1)
    elif mayaLan == 'ja_JP':
        applyLanguage(3)

def meshCleanWeightlessBoneCmd(ignoreInputs):
    meshCleanWeightlessBone()

def selectWeightedBoneCmd(ignoreInputs):
    selectWeightBone()
closest_sourceVtxsList = ()
closest_sourceVtxsPosList = ()
closest_sourceVtxSkinCluster = None

def loadSourceVtxCmd(ignoreInputs):
    global closest_sourceVtxsList
    global closest_sourceVtxsPosList
    global closest_sourceVtxSkinCluster
    vList = pm.ls(vertexInfo[0], flatten=1)
    if vList:
        if pm.nodeType(vList[0]) == 'mesh':
            closest_sourceVtxsList = vList
            closest_sourceVtxsPosList = [x.getPosition() for x in closest_sourceVtxsList]
            closest_sourceVtxSkinCluster = vertexInfo[2]
            sVertexCount_label.setLabel(str(len(vList)))

def copyClosestVtxCmd(ignoreInputs):
    global closest_sourceVtxsList
    global closest_sourceVtxsPosList
    global closest_sourceVtxSkinCluster
    copyClosestVtx(warp_FineCopy_checkBox.getValue())
    if not warp_HoldVtxs_checkBox.getValue():
        closest_sourceVtxsList = ()
        closest_sourceVtxsPosList = ()
        closest_sourceVtxSkinCluster = None
        sVertexCount_label.setLabel('0')

def selectWeightedVertsCmd(ignoreInputs):
    selectWeightedVerts()

def swapMergeWeightCmd(ignoreInputs):
    swapWeight()

def renameUpdatePreview(doRename=False, renameObjList=[], initial=False):
    if initial:
        return
    previewText = None
    currentSelectionIndex = 0
    if doRename and renameObjList:
        for i in range(len(renameObjList)):
            previewText = renameObjList[i].name()
            currentSelectionIndex = i
            previewText = renameBuildString(previewText, currentSelectionIndex)
            if previewText == 'Error: Only one # allowed!':
                pass
            else:
                pm.rename(renameObjList[i], previewText)
    elif pm.ls(sl=1):
        previewText = pm.ls(sl=1)[-1].name()
        currentSelectionIndex = pm.ls(sl=1).index(pm.ls(sl=1)[-1])
    if previewText:
        previewText = renameBuildString(previewText, currentSelectionIndex)
    if doRename and renameHierarchy_radioButton.getSelect() and renameTemplate_lineEdit.getEnable():
        if len(pm.ls(sl=1)) > 1:
            renamePreview_lineEdit.setText('Only one selection allowed in "Hierarchy" mode!')
    elif previewText:
        renamePreview_lineEdit.setText(previewText)

def renameBuildString(previewText, currentSelectionIndex):
    if renameTemplate_lineEdit.getEnable():
        previewText = templateString(renameTemplate_lineEdit.getText(), startNumberAs=int(renameOrderStart_lineEdit.getText()), stepAs=int(renameOrderStep_lineEdit.getText()), startLetterAs=renameOrderLetter_lineEdit.getText(), isUppercase=renameUpcase_checkBox.getValue(), isUseLetter=renameLetter_checkBox.getValue(), index=currentSelectionIndex)
    else:
        if renameSearch_lineEdit.getText():
            previewText = replaceString(previewText, renameSearch_lineEdit.getText(), renameReplace_lineEdit.getText(), isCaseSensitive=renameCase_CheckBox.getValue())
        if renamePerfix_lineEdit.getText():
            previewText = addString(previewText, renamePerfix_lineEdit.getText(), isPrefix=renamePrefix_radioButton.getSelect(), isSuffix=renameSuffix_radioButton.getSelect(), isStartFrom=renameStart_radioButton.getSelect(), startFromNumber=int(renameStart_lineEdit.getText()))
    return previewText

def replaceString(oriString, search, replace, isCaseSensitive=True):
    if isCaseSensitive:
        return oriString.replace(search, replace)
    else:
        pattern = re.compile(search, re.IGNORECASE)
        return pattern.sub(replace, oriString)

def addString(oriString, addString, isPrefix=True, isSuffix=False, isStartFrom=False, startFromNumber=1):
    if isPrefix:
        outString = addString + oriString
    elif isSuffix:
        outString = oriString + addString
    elif isStartFrom:
        outString = oriString[:startFromNumber] + addString + oriString[startFromNumber:]
    return outString

def templateString(templateText, startNumberAs=None, stepAs=None, startLetterAs=None, isUppercase=True, isUseLetter=False, index=0):
    renameSetOrderLetter(isUppercase=renameUpcase_checkBox.getValue())
    if '#' in templateText:
        templateTextList = templateText.split('#')
        if len(templateTextList) > 2:
            return 'Error: Only one # allowed!'
        elif isUseLetter:
            if isUppercase:
                index = ascii_uppercase.index(startLetterAs.upper()) + index
                letter = ascii_uppercase[index]
            else:
                index = ascii_lowercase.index(startLetterAs.lower()) + index
                letter = ascii_lowercase[index]
            return templateTextList[0] + letter + templateTextList[1]
        else:
            number = startNumberAs + index * stepAs
            return templateTextList[0] + str(number) + templateTextList[1]

def renameSetOrderLetter(isUppercase=True):
    text = renameOrderLetter_lineEdit.getText()
    if isUppercase:
        renameOrderLetter_lineEdit.setText(text.upper())
    else:
        renameOrderLetter_lineEdit.setText(text.lower())

def renameMake():
    renameObjList = []
    if not pm.ls(sl=1):
        pass
    elif renameHierarchy_radioButton.getSelect():
        if len(pm.ls(sl=1)) > 1 and renameTemplate_lineEdit.getEnable():
            renamePreview_lineEdit.setText('Only one selection allowed in "Hierarchy" mode!')
        else:
            renameObjList.append(pm.listRelatives(pm.ls(sl=1)[0], allDescendents=1))
            renameObjList.append(pm.ls(sl=1))
            renameObjList = list(chain.from_iterable(renameObjList))
            renameObjList = list(reversed(renameObjList))
    elif renameSelected_radioButton.getSelect():
        renameObjList = pm.ls(sl=1)
    renameUpdatePreview(doRename=True, renameObjList=renameObjList)
    if len(pm.ls(sl=1)) > 1 and renameHierarchy_radioButton.getSelect():
        pass
    else:
        renameUpdatePreview()

def renameResetUI():
    renameSearch_lineEdit.setText('')
    renameReplace_lineEdit.setText('')
    renamePerfix_lineEdit.setText('')

def printTextEdit(textEdit, inputString):
    ctime = time.ctime()
    ptime = ctime.split(' ')
    inputString = ptime[3] + '  -  ' + inputString
    pm.scrollField(textEdit, edit=True, insertionPosition=0, insertText=inputString + '\n')

def printTextLable(label, inputString):
    pm.text(label, edit=True, label=inputString)
realProgress = 0

def runProgressBar(bar, inputNumber=0.0):
    global realProgress
    if 0 < inputNumber < 100:
        realProgress = realProgress + inputNumber
        pm.progressBar(bar, edit=True, progress=realProgress)
    else:
        realProgress = 0
        pm.progressBar(bar, edit=True, progress=inputNumber)

def setProgressBar(bar, inputNumber):
    if 0 <= inputNumber <= 100:
        pm.progressBar(bar, edit=True, progress=inputNumber)
    elif inputNumber < 0:
        pm.progressBar(bar, edit=True, progress=0)
    else:
        pm.progressBar(bar, edit=True, progress=100)
reSkinBone = []
swapBoneA = swapBoneB = None

def resetUI():
    weight_paintVertexCheckBox.setValue(False)
    runProgressBar(main_progressBar, 0)
    lodReset()

def closeUI():
    return bridge.close_cleanup()

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''

def checkUpdate():
    return bridge.update_status()

def getCurrentSelectVertexs():
    return mel.eval('ls -sl -type "float3" -flatten')

def changeVertPriority(isRevert=False):
    return bridge.selection_priority(isRevert)
vertexDetail = {}
proxyMesh = None
vertexInfo = []
previousVertexInfo = []
oldBoneListItemIndex = 1
copiedVtxWeight = []
previousTimeStamp = 0.0
oldVertexSelevtion = []

def getRangeStep():
    try:
        rangeStep = int(weight_rangeStepTextEdit.getText())
        if rangeStep - 1 in range(9):
            return rangeStep
        else:
            weight_rangeStepTextEdit.setText('1')
            return 1
    except:
        weight_rangeStepTextEdit.setText('1')
        return 1

def getDifVertex(vLstSmall, vLstLarge):
    return list(set(vLstLarge) - set(vLstSmall))

def getBoneListBone():
    return pm.ls(weight_boneListBox.getSelectItem()[0], type='joint')[0]

def rangeExtend():
    relaxWeight_2(operation='scale', value=1.1)

def rangeShrink():
    relaxWeight_2(operation='scale', value=0.9)

def reSkinPickBone():
    global reSkinBone
    reSkinBone = pm.ls(sl=1, type='joint')
    if reSkinBone:
        weight_reSkinLabel.setLabel(len(reSkinBone))

def reSkin():
    global reSkinBone
    if vertexInfo and reSkinBone:
        isoState1 = pm.isolateSelect('modelPanel1', state=1, q=1)
        isoState2 = pm.isolateSelect('modelPanel2', state=1, q=1)
        isoState3 = pm.isolateSelect('modelPanel3', state=1, q=1)
        isoState4 = pm.isolateSelect('modelPanel4', state=1, q=1)
        pm.isolateSelect('modelPanel1', state=0)
        pm.isolateSelect('modelPanel2', state=0)
        pm.isolateSelect('modelPanel3', state=0)
        pm.isolateSelect('modelPanel4', state=0)
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        vertexList = vertexInfo[0]
        skinedBone = meshSkinCluster.getInfluence()
        for joint in skinedBone:
            pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
        for joint in reSkinBone:
            if joint not in skinedBone:
                meshSkinCluster.addInfluence(joint)
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
        pm.select(mesh)
        newPoly = pm.duplicate()[0]
        newPolyVertexList = []
        for v in vertexList:
            newPolyVertexList.append(v.replace(mesh.name(), newPoly.name()))
        newPolySkinCluster = pm.skinCluster(newPoly, reSkinBone, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True, toSelectedBones=True)
        newPolyVertexInfo = []
        newPolyVertexInfo.append(newPolyVertexList)
        newPolyVertexInfo.append(None)
        newPolyVertexInfo.append(newPolySkinCluster)
        pm.select(newPolyVertexList)
        vtxWeights = prepareExprotVertexData(newPolyVertexInfo)
        for vName in list(vtxWeights.keys()):
            oriVName = vName.replace(newPoly.name(), mesh.name())
            vtxWeights[oriVName] = vtxWeights.pop(vName)
        pm.delete(newPoly)
        applyVertexData(vtxWeights, vertexInfo)
        pm.isolateSelect('modelPanel1', state=isoState1)
        pm.isolateSelect('modelPanel2', state=isoState2)
        pm.isolateSelect('modelPanel3', state=isoState3)
        pm.isolateSelect('modelPanel4', state=isoState4)
        if not weight_reSkinHoldBone.getValue():
            reSkinBone = []
            weight_reSkinLabel.setLabel('0')

def vertexSize():
    pm.runtime.ChangeVertexSize()

def updateWeightUI():
    """
    update Weight Tool UI, triger by script job sJob_weight_updateSelection
    """
    runProgressBar(main_progressBar, 0)
    global vertexDetail
    vertexDetail = {}
    global proxyMesh
    global vertexInfo
    global currentSelection
    global oldVertexSelevtion
    currentSelection = pm.ls(sl=1)
    previousVertexInfo = vertexInfo
    vertexInfo = []
    step = 0
    lagLimit = 2000
    weight_valueListBox.setEnable(False)
    vertexInfo = getSelectedVertexInfo()
    if vertexInfo:
        UIList = {}
        newUIList = {}
        vertexList = vertexInfo[0]
        meshSkinCluster = vertexInfo[2]
        outKeys = []
        outValue = []
        weightInfo = []
        weight_vertsNumLabel.setLabel(str(len(vertexList)))
        fullJointList = meshSkinCluster.getInfluence()
        if len(vertexList) > lagLimit:
            runProgressBar(main_progressBar, 0)
            step = 100 / float(len(vertexList))
        for vertex in vertexList:
            weightInfo = getRelativedJoint(vertex, meshSkinCluster, fullJointList)
            for i in range(len(weightInfo[0])):
                newUIList[weightInfo[0][i]] = weightInfo[1][i]
            vertexDetail[vertex] = newUIList
            if len(vertexList) > lagLimit:
                runProgressBar(main_progressBar, step)
        for j in newUIList:
            if j in UIList:
                pass
            else:
                UIList[j] = newUIList[j]
        outKeys = list(UIList.keys())
        outKeys.sort()
        for key in outKeys:
            outValue.append(UIList[key])
        updateValueListUI(outValue)
        updateBoneListUI(outKeys)
        if len(vertexList) > lagLimit:
            runProgressBar(main_progressBar, 100)
            showSpam()
        return True
    else:
        paintWeightedVertex(None, None, proxyMesh, clear=True)
        oldVertexSelevtion = []
        return False

def getRelativedJoint(vertex, meshSkinCluster, fullJointList):
    """
    To find out the joint relative the select vertex, and weight > 0, return joint list and weight values list
    """
    outJoint = []
    outValue = []
    fullValueList = pm.skinPercent(meshSkinCluster, vertex, query=True, value=True)
    for i in range(len(fullValueList)):
        if fullValueList[i] > 0:
            outJoint.append(fullJointList[i])
            outValue.append(round(fullValueList[i], 2))
    return (outJoint, outValue)

def updateBoneListUI(boneList):
    """
    Update bone list UI
    If old picked joint still exists in new bone list, select it, or select first one
    """
    global oldBoneListItemIndex
    pickedJoint = weight_boneListBox.getSelectItem()
    weight_boneListBox.removeAll()
    weight_boneListBox.extend(boneList)
    getOldPicked = False
    if pickedJoint and pickedJoint[0] in boneList:
        getOldPicked = True
    if getOldPicked:
        weight_boneListBox.setSelectItem(pickedJoint[0])
        oldBoneListItemIndex = weight_boneListBox.getSelectIndexedItem()[0]
        boneListSelected(False)
    else:
        oldBoneListItemIndex = 1
        weight_boneListBox.setSelectIndexedItem(1)
        boneListSelected()

def updateValueListUI(valueList):
    weight_valueListBox.removeAll()
    weight_valueListBox.extend(valueList)

def boneListSelected(paintVertex=True):
    """
    Select relative item in value list, colorful vertex which infulenced by the joint
    """
    global oldBoneListItemIndex
    itemIndex = weight_boneListBox.getSelectIndexedItem()
    if itemIndex > 0:
        weight_valueListBox.deselectAll()
        weight_valueListBox.setSelectIndexedItem(itemIndex)
        if paintVertex:
            if weight_paintVertexCheckBox.getValue() and oldBoneListItemIndex is not itemIndex[0]:
                updateVertexColor()
        oldBoneListItemIndex = itemIndex[0]
        if weight_syncBoneCheckBox.getValue():
            pm.select(pm.ls(type='joint'), deselect=True)
            pm.select(weight_boneListBox.getSelectItem()[0], add=True)
    else:
        weight_valueListBox.deselectAll()

def updateVertexColor():
    global vertexInfo
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        proxyMesh = mesh.name() + '_colorProxy'
    else:
        printTextEdit(main_lineEdit, 'No vertex selected!')
        if not pm.objExists(proxyMesh):
            weight_paintVertexCheckBox.setValue(False)
        return
    pickedJoint = weight_boneListBox.getSelectItem()[0]
    paintWeightedVertex(meshSkinCluster, pickedJoint, proxyMesh)

def paintVertexOn():
    """
    Create and resize a proxy mesh from weight mesh to ready for paint color.
    Origonal mesh will not be painted to avoid skin broken, but will be set to shade off mode
    """
    global proxyMesh
    global vertexInfo
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        vertexList = vertexInfo[0]
        proxyMesh = mesh.name() + '_colorProxy'
        currentTime = pm.getCurrentTime()
        pm.select(mesh)
        pm.runtime.GoToBindPose(mesh)
        pm.select(vertexList)
        if pm.objExists(proxyMesh):
            pickedJoint = weight_boneListBox.getSelectItem()[0]
            paintWeightedVertex(meshSkinCluster, pickedJoint, proxyMesh)
        else:
            pm.duplicate(mesh, name=proxyMesh)
            bone = pm.skinCluster(meshSkinCluster, query=True, inf=True)[0]
            inputList = []
            inputList.append(bone)
            inputList.append(mesh)
            inputList.append(proxyMesh)
            bindSkinPlus(inputList)
            pm.polyChipOff(proxyMesh + '.f[:]', constructionHistory=1, keepFacesTogether=1, duplicate=0, localTranslateZ=-0.03)
            proxyMeshShape = pm.ls(proxyMesh)[0].getShape()
            pm.setAttr(proxyMeshShape + '.overrideEnabled', 1)
            pm.setAttr(proxyMeshShape + '.overrideDisplayType', 2)
            pm.setAttr(meshShape + '.overrideEnabled', 1)
            pm.setAttr(meshShape + '.overrideShading', 0)
            mel.eval('setWireframeOnShadedOption false modelPanel4')
            melCommand = 'doMenuComponentSelection("' + mesh + '", "vertex")'
            mel.eval(melCommand)
            mel.eval('updateObjectSelectionMasks')
            pm.select(vertexList)
            printTextEdit(main_lineEdit, 'Color proxy mesh created!')
            if weight_boneListBox.getSelectItem():
                pickedJoint = weight_boneListBox.getSelectItem()[0]
                paintWeightedVertex(meshSkinCluster, pickedJoint, proxyMesh)
            else:
                printTextEdit(main_lineEdit, 'No bone selected!')
        pm.setCurrentTime(currentTime)
    else:
        printTextEdit(main_lineEdit, 'No vertex selected!')
        pm.warning('No skinned vertex selected!')
        weight_paintVertexCheckBox.setValue(False)

def paintVertexOff():
    return bridge.paint_off()

def paintWeightedVertex(skinCluster_proxy, bone, proxyMesh, clear=False, update=False, updatedVertexAndValueList=[]):
    """
    Paint vertex color on proxy mesh
    """
    if clear:
        try:
            pm.polyColorPerVertex(proxyMesh, remove=True)
        except:
            pass
    else:
        if update:
            pass
        else:
            try:
                pm.polyColorPerVertex(proxyMesh, remove=True)
            except:
                pass
        proxyMeshShape = pm.ls(proxyMesh)[0].getShape()
        if updatedVertexAndValueList:
            flattenVertexList = updatedVertexAndValueList[0]
            infValueList = updatedVertexAndValueList[1]
        else:
            skinCluster_proxy = pm.ls(skinCluster_proxy)[0]
            infList = skinCluster_proxy.getPointsAffectedByInfluence(bone)
            infVertexList = infList[0]
            infValueList = infList[1]
            flattenVertexList = []
            for vertex in infVertexList:
                flattenVertexList.append(pm.ls(vertex, flatten=True))
            flattenVertexList = flattenVertexList[0]
        t = 0.05
        vertexDict = {}
        vertexAndValueList = list(zip(flattenVertexList, infValueList))
        while t <= 1.05:
            collectList = []
            for vertex in vertexAndValueList:
                if round(vertex[1], 2) > t - 0.05 and round(vertex[1], 2) <= t:
                    proxyMeshVertex = proxyMesh + '.' + str(vertex[0]).split('.')[1]
                    collectList.append(proxyMeshVertex)
            if collectList:
                vertexDict[t] = collectList
            t += 0.05
        step = 0.0
        allStep = len(list(vertexDict.keys()))
        oriVertex = pm.ls(sl=1)
        for value in list(vertexDict.keys()):
            step += 100 / allStep
            jointValue = round(value, 2)
            if jointValue >= 0.25:
                colorR = 1
                colorG = (0.75 - jointValue) * 2
                colorB = 0
            else:
                colorR = jointValue * 2
                colorG = jointValue * 2
                colorB = (0.5 - jointValue) * 2
            if jointValue <= 0:
                colorR = 0
                colorG = 0
                colorB = 0
            proxyVertex = vertexDict[value]
            pm.select(proxyVertex)
            proxyVertex = pm.ls(sl=1)
            vertexString = ''.join((str(e) + ' ' for e in proxyVertex))
            melCommand = 'polyColorPerVertex -rgb ' + str(colorR) + ' ' + str(colorG) + ' ' + str(colorB) + ' -nun'
            mel.eval(melCommand)
        pm.select(oriVertex)
        pm.polyOptions(proxyMeshShape, colorShadedDisplay=True)
        pm.polyOptions(proxyMeshShape, colorMaterialChannel='channelambientDiffuse')
        pm.polyOptions(proxyMeshShape, materialBlend='modulate2x')
        showSpam()

def shrinkSelection():
    if mel.eval('ls -sl -type "float3"'):
        cmds.ShrinkPolygonSelectionRegion()
        return getCurrentSelectVertexs()
    else:
        return None

def growSelection():
    if getCurrentSelectVertexs():
        cmds.GrowPolygonSelectionRegion()
        return getCurrentSelectVertexs()
    else:
        return None

def elementSelection():
    oldVertexNum = 0
    vertexNum = 0
    if getCurrentSelectVertexs():
        while vertexNum == 0 or vertexNum != oldVertexNum:
            oldVertexNum = vertexNum
            vertexNum = growSelection()

def ringSelection():
    if getCurrentSelectVertexs() < 2:
        pass
    else:
        cmds.ConvertSelectionToContainedEdges()
        cmds.SelectContiguousEdges()
        cmds.ConvertSelectionToVertices()

def waveSelection():
    global oldVertexSelevtion
    currentSelection = getCurrentSelectVertexs()
    if currentSelection:
        oldVertexSelevtion = oldVertexSelevtion + currentSelection
        cmds.GrowPolygonSelectionRegion()
        pm.select(oldVertexSelevtion, deselect=1)
    return getCurrentSelectVertexs()

def setWeightFromBotton(weightValue):
    setVertexWeight(weightValue)

def checkInfluence(forceCut=False):
    global vertexInfo
    if not vertexInfo:
        if pm.ls(sl=1, type='transform'):
            if pm.ls(sl=1, type='transform')[0].getShape():
                if pm.nodeType(pm.ls(sl=1, type='transform')[0].getShape()) == 'mesh':
                    pm.select(pm.ls(sl=1, type='transform')[0].verts)
                    vertexInfo = getSelectedVertexInfo()
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        i = 0
        step = 100.0 / len(vertexInfo[0])
        sList = []
        if forceCut:
            isCutMinor = True
        else:
            isCutMinor = checkInflunce_cutMinor_checkBox.getValue()
        maxInfGap = int(weight_checkInflunceTexEdit.getText())
        fullJointList = meshSkinCluster.getInfluence()
        for vertex in vertexInfo[0]:
            weightInfo = getRelativedJoint(vertex, meshSkinCluster, fullJointList)
            weightDict = {}
            valueList = weightInfo[1]
            boneList = weightInfo[0]
            overInfCount = len(valueList) - maxInfGap
            if overInfCount > 0:
                if isCutMinor:
                    for j in range(len(boneList)):
                        weightDict[boneList[j]] = valueList[j]
                    minorWeightLst = sorted(list(weightDict.items()), key=operator.itemgetter(1))[:overInfCount]
                    for vertexData in minorWeightLst:
                        pm.skinPercent(meshSkinCluster, vertex, transformValue=(vertexData[0], 0.0), normalize=True, zeroRemainingInfluences=False)
                else:
                    sList.append(vertex)
            i += step
            setProgressBar(main_progressBar, i)
        if not isCutMinor:
            pm.select(clear=1)
            if sList:
                pm.select(sList)
                vertSet = pm.sets()
                vertSet.rename('OverInfVertsSet_SkinMagicSet')
        setProgressBar(main_progressBar, 0)
        selectionChanged()

def setWeightFromValue():
    try:
        weightValue = float(weight_setWeightTextEdit.getText())
    except:
        printTextEdit(main_lineEdit, 'Wrong weight number!')
        weight_setWeightTextEdit.setText('0.35')
        raise IOError('Wrong weight number!')
    if weightValue > 1:
        printTextEdit(main_lineEdit, 'Weight Number should no big than 1!')
        weight_setWeightTextEdit.setText('1.0')
        raise IOError('Wrong weight number!')
    elif weightValue < 0:
        printTextEdit(main_lineEdit, 'Weight Number should no small than 0!')
        weight_setWeightTextEdit.setText('0.0')
        raise IOError('Wrong weight number!')
    else:
        setVertexWeight(weightValue)

def setVertexWeight(weightValue=0, relativeValue=False, exactJoint=None, isNormalize=False):
    """
    update joint infulence weight value for each selected vertex according the number in value list
    """
    lagLimit = 2000
    runProgressBar(main_progressBar, 0)
    global vertexInfo
    weightJoint = []
    weightJointList = []
    weightValueList = []
    global vertexDetail
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        vertexList = vertexInfo[0]
        oldMaintainMaxInfluences = pm.getAttr(meshSkinCluster.maintainMaxInfluences)
        pm.setAttr(meshSkinCluster.maintainMaxInfluences, 0)
        if weight_paintVertexCheckBox.getValue():
            proxyMesh = mesh.name() + '_colorProxy'
            try:
                proxyMeshSkinCluster = getMeshSkinCluster(proxyMesh)
            except:
                pass
        autoKeyState = pm.autoKeyframe()
        pm.autoKeyframe(state=False)
        pickedJoint = str(weight_boneListBox.getSelectItem()[0])
        oldBoneList = weight_boneListBox.getAllItems()
        fullJointList = meshSkinCluster.getInfluence()
        jointWeightLockLst = []
        for idx in range(len(fullJointList)):
            melCmd = 'skinCluster -inf ' + fullJointList[idx] + ' -q -lw ' + meshSkinCluster
            jointWeightLockLst.append(mel.eval(melCmd))
        for joint in fullJointList:
            pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
            if weight_paintVertexCheckBox.getValue():
                pm.skinCluster(proxyMeshSkinCluster, inf=joint, edit=True, lockWeights=True)
        tickGate = 10.0
        isLagLimit = len(vertexList) > lagLimit
        for vertex in vertexList:
            if vertex in list(vertexDetail.keys()):
                weightJoint = list(vertexDetail[vertex].keys())
                if exactJoint:
                    for weightInform in exactJoint:
                        vertexDetail[vertex][weightInform[0]] = weightInform[1]
                else:
                    vertexDetail[vertex][pickedJoint] = weightValue
        weightJoint.sort()
        for joint in weightJoint:
            pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=False)
            if weight_paintVertexCheckBox.getValue():
                pm.skinCluster(proxyMeshSkinCluster, inf=joint, edit=True, lockWeights=False)
        if exactJoint:
            transformValue = exactJoint
        else:
            transformValue = (pickedJoint, weightValue)
        pm.skinPercent(meshSkinCluster, vertexList, relative=relativeValue, transformValue=transformValue, normalize=isNormalize)
        if weight_paintVertexCheckBox.getValue():
            proxyMeshVertexList = []
            proxyMeshValueList = []
            for vertex in vertexList:
                proxyVertex = proxyMesh + '.' + str(vertex).split('.')[1]
                proxyMeshVertexList.append(proxyVertex)
                paintWeightValue = pm.skinPercent(meshSkinCluster, vertex, query=True, value=True, transform=pickedJoint)
                proxyMeshValueList.append(paintWeightValue)
            pm.skinPercent(proxyMeshSkinCluster, proxyMeshVertexList, relative=relativeValue, transformValue=transformValue, normalize=False)
        step = 50
        for joint in weightJoint:
            pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
            if weight_paintVertexCheckBox.getValue():
                pm.skinCluster(proxyMeshSkinCluster, inf=joint, edit=True, lockWeights=True)
            jointValue = pm.skinPercent(meshSkinCluster, vertexList[0], query=True, value=True, transform=joint)
            if not joint in weightJointList:
                weightValueList.append(round(jointValue, 2))
                weightJointList.append(joint)
        if isNormalize:
            for joint in fullJointList:
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=False)
            pm.skinPercent(meshSkinCluster, normalize=True)
            for joint in fullJointList:
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
        updateValueListUI(weightValueList)
        updateBoneListUI(weightJointList)
        if weight_paintVertexCheckBox.getValue():
            updatedVertexAndValueList = []
            updatedVertexAndValueList.append(proxyMeshVertexList)
            updatedVertexAndValueList.append(proxyMeshValueList)
            paintWeightedVertex(proxyMeshSkinCluster, pickedJoint, proxyMesh, update=True, updatedVertexAndValueList=updatedVertexAndValueList)
        pm.setAttr(meshSkinCluster.maintainMaxInfluences, oldMaintainMaxInfluences)
        pm.autoKeyframe(state=autoKeyState)
        for idx in range(len(fullJointList)):
            pm.skinCluster(meshSkinCluster, inf=fullJointList[idx], edit=True, lockWeights=jointWeightLockLst[idx])
        if len(vertexList) > lagLimit:
            showSpam()
            setProgressBar(main_progressBar, 0)

def plusWeight():
    try:
        value = float(weight_valueListBox.getSelectItem()[0])
    except:
        value = None
    if value:
        if value + 0.05 > 1:
            setVertexWeight(1, False)
        else:
            setVertexWeight(0.05, True)

def minusWeight():
    try:
        value = float(weight_valueListBox.getSelectItem()[0])
    except:
        value = None
    if value:
        if value - 0.05 < 0:
            setVertexWeight(0, False)
        else:
            setVertexWeight(-0.05, True)

def copyWeight():
    global copiedVtxWeight
    global vertexInfo
    global copiedSkinCluster
    '\n    Copy selected vertex weight, call Maya function\n    '
    vertexNum = float(weight_vertsNumLabel.getLabel())
    if vertexNum == 0:
        printTextEdit(main_lineEdit, 'No Vertex Selected!')
    elif vertexNum > 1:
        printTextEdit(main_lineEdit, 'No more than 1 Vertex!')
        raise IOError('No more than 1 Vertex!')
    else:
        sJoint = pm.ls(type='joint')
        pm.select(sJoint, deselect=True)
        mel.eval('artAttrSkinWeightCopy')
        vtxSource = pm.ls(sl=1)[0]
        vtxTransformNode = vtxSource.node().getParent()
        vtxIndex = vtxSource.index()
        copiedVtxWeight = list(vertexDetail['{0}.vtx[{1}]'.format(vtxTransformNode, vtxIndex)].items())
        copiedSkinCluster = vertexInfo[2]
        if weight_syncBoneCheckBox.getValue():
            pm.select(sJoint, add=True)

def getMeshSkinCluster(inputMesh):
    meshSkinCluster = None
    skinHistory = pm.listHistory(inputMesh, type='skinCluster')
    for skinCluster in skinHistory:
        if skinCluster.envelope.get():
            meshSkinCluster = skinCluster
            break
    return meshSkinCluster

def getSelectedVertexInfo():
    selectedVertexList = getCurrentSelectVertexs()
    if not selectedVertexList:
        return None
    mesh = pm.PyNode(selectedVertexList[0].split('.')[0])
    if pm.nodeType(mesh) == 'mesh':
        mesh = mesh.getParent()
    meshSkinCluster = getMeshSkinCluster(mesh)
    if not meshSkinCluster:
        return None
    weight_normalizeLabel.setLabel({0: 'OFF', 1: 'ON', 2: 'POST'}.get(meshSkinCluster.getNormalizeWeights(), 'UNKNOWN'))
    return (selectedVertexList, mesh, meshSkinCluster)

def pasteWeight():
    """
    Paste copied weight, call Maya function
    """
    global vertexInfo
    global copiedSkinCluster
    if vertexInfo:
        if copiedSkinCluster == vertexInfo[2]:
            mel.eval('artAttrSkinWeightPaste')
        else:
            setVertexWeight(relativeValue=False, exactJoint=copiedVtxWeight)
        updateWeightUI()
    else:
        printTextEdit(main_lineEdit, 'No skined vertex(s) selected!')

def setVertexSize():
    melTxt = 'polyOptions -sizeVertex ' + str(weight_vertexSizeSlider.getValue())
    mel.eval(melTxt)

def normalizeWeightObj(obj):
    if obj.getShape():
        if pm.nodeType(obj.getShape()) == 'mesh':
            meshShape = obj.getShape()
            meshSkinCluster = getMeshSkinCluster(meshShape)
            if meshSkinCluster:
                meshSkinCluster.setNormalizeWeights(True)
                pm.skinPercent(meshSkinCluster, normalize=True)
                print(obj + ' normalized')

def normalizeWeight(obj=None):
    if pm.ls(sl=1, type='transform'):
        for obj in pm.ls(sl=1, type='transform'):
            normalizeWeightObj(obj)

def weightToolOff():
    if pm.objExists('*_colorProxy'):
        paintVertexOff()
    resetWeightUI()

def resetWeightUI():
    weight_boneListBox.removeAll()
    weight_valueListBox.removeAll()
    weight_vertsNumLabel.setLabel(0)
    weight_paintVertexCheckBox.setValue(False)

def addBone():
    global vertexInfo
    if vertexInfo:
        global vertexDetail
        newUIList = {}
        vertexList = vertexInfo[0]
        meshSkinCluster = vertexInfo[2]
        pickedBone = pm.layoutDialog(title='Add Bone', ui=addBoneUI)
        if pickedBone == 'Cancel' or pickedBone == 'dismiss':
            pass
        elif pickedBone not in weight_boneListBox.getAllItems():
            weight_boneListBox.append(pickedBone)
            weight_valueListBox.append('0.0')
            fullJointList = pm.skinPercent(meshSkinCluster, query=True, transform=None)
            for vertex in vertexList:
                weightInfo = getRelativedJoint(vertex, meshSkinCluster, fullJointList)
                for i in range(len(weightInfo[0])):
                    newUIList[weightInfo[0][i]] = weightInfo[1][i]
                newUIList[pickedBone] = 0.0
                vertexDetail[vertex] = newUIList
            n = weight_boneListBox.getNumberOfItems()
            weight_boneListBox.setSelectIndexedItem(n)
            weight_valueListBox.setSelectIndexedItem(n)
    else:
        printTextEdit(main_lineEdit, 'No vertex selected!')

def addBoneGetSelectBone():
    """
    Get selection from addBone_boneList
    """
    global addBone_boneList
    selectItem = addBone_boneList.getSelectItem()[0]
    pm.layoutDialog(dismiss=selectItem)

def addBoneUpdateJointList():
    global vertexInfo
    global addBone_boneList
    global addBone_filterEdit
    filterWordLst = addBone_filterEdit.getText().split(' ')
    meshSkinCluster = vertexInfo[2]
    mesh = vertexInfo[1]
    meshShape = mesh.getShape()
    weightJointList = meshSkinCluster.getInfluence()
    filtedWeightJointList = []
    for jjj in weightJointList:
        hitCount = 0
        for filterWord in filterWordLst:
            if filterWord.lower() in jjj.name().lower():
                hitCount += 1
        if hitCount == len(filterWordLst):
            filtedWeightJointList.append(jjj)
    filtedWeightJointList.sort
    addBone_boneList.removeAll()
    addBone_boneList.extend(filtedWeightJointList)

def addBoneUI():
    global vertexInfo
    global addBone_filterEdit
    meshSkinCluster = vertexInfo[2]
    mesh = vertexInfo[1]
    meshShape = mesh.getShape()
    form = pm.setParent(query=True)
    addBone_textLabel = pm.text(label='Pick a bone here:', w=100)
    addBone_filterLabel = pm.text(label='Filter:')
    addBone_filterEdit = pm.textField(w=100, changeCommand='addBoneUpdateJointList()')
    weightJointList = meshSkinCluster.getInfluence()
    weightJointList.sort
    global addBone_boneList
    addBone_boneList = pm.textScrollList(allowMultiSelection=False, append=weightJointList)
    addBone_boneList.setSelectItem(weight_boneListBox.getSelectItem()[0])
    addBone_OKButton = pm.button(label='OK', command=lambda *unused: addBoneGetSelectBone())
    addBone_CancelButton = pm.button(label='Cancel', command=lambda *unused: pm.layoutDialog(dismiss='Cancel'))
    spacer = 5
    top = 8
    edge = 6
    pm.formLayout(form, edit=True, attachForm=[(addBone_textLabel, 'top', 5), (addBone_textLabel, 'left', edge), (addBone_filterEdit, 'top', 2), (addBone_filterEdit, 'right', edge), (addBone_filterLabel, 'top', 5), (addBone_filterLabel, 'right', edge + 104), (addBone_boneList, 'top', top * 3), (addBone_boneList, 'left', edge), (addBone_boneList, 'right', edge), (addBone_boneList, 'bottom', 40), (addBone_CancelButton, 'right', edge)], attachNone=[(addBone_OKButton, 'bottom'), (addBone_CancelButton, 'bottom')], attachControl=[(addBone_OKButton, 'top', spacer, addBone_boneList), (addBone_OKButton, 'left', -153, addBone_CancelButton), (addBone_CancelButton, 'top', spacer, addBone_boneList)])

def removeBone():
    obj = weight_boneListBox.getSelectIndexedItem()
    if obj:
        if float(weight_valueListBox.getSelectItem()[0]) > 0:
            printTextEdit(main_lineEdit, 'Cannot Remove No-Zero Weight Bone!')
        else:
            weight_boneListBox.removeIndexedItem(obj[0])
            weight_valueListBox.removeIndexedItem(obj[0])
            boneListSelected()
    else:
        printTextEdit(main_lineEdit, 'No Bone Selected in List!')

def pruneWeight():
    """
    Prune small weight as number seted in UI
    """
    mesh = pm.ls(sl=True, type='transform')
    if mesh:
        if len(mesh) > 1:
            printTextEdit(main_lineEdit, 'Too many selection!')
            raise IOError('Too many selection!')
        else:
            shape = mesh[0].getShape()
    else:
        printTextEdit(main_lineEdit, 'No Skined Mesh Selected!')
        raise IOError('No Skined Mesh Selected!')
    try:
        meshSkinCluster = getMeshSkinCluster(shape)
    except:
        printTextEdit(main_lineEdit, 'No Skined Mesh Selected!')
        raise IOError('No Skined Mesh Selected!')
    try:
        pruneWeights = float(weight_pruneWeightTextEdit.getText())
    except:
        printTextEdit(main_lineEdit, 'Wrong input "{0}", reset to default!'.format(weight_pruneWeightTextEdit.getText()))
        weight_pruneWeightTextEdit.setText('0.04')
        pruneWeights = float(weight_pruneWeightTextEdit.getText())
    if pruneWeights < 0 or pruneWeights > 1:
        printTextEdit(main_lineEdit, 'Wrong input "{0}", reset to default!'.format(weight_pruneWeightTextEdit.getText()))
        weight_pruneWeightTextEdit.setText('0.04')
        pruneWeights = float(weight_pruneWeightTextEdit.getText())
    fullJointList = meshSkinCluster.getInfluence()
    jointWeightLockLst = []
    for idx in range(len(fullJointList)):
        melCmd = 'skinCluster -inf ' + fullJointList[idx] + ' -q -lw ' + meshSkinCluster
        jointWeightLockLst.append(mel.eval(melCmd))
    for joint in fullJointList:
        pm.skinCluster(meshSkinCluster, inf=joint, e=True, lw=False)
    pm.skinPercent(meshSkinCluster, shape, pruneWeights=pruneWeights, normalize=True)
    for idx in range(len(fullJointList)):
        pm.skinCluster(meshSkinCluster, inf=fullJointList[idx], e=True, lw=jointWeightLockLst[idx])
    printTextEdit(main_lineEdit, '"{0}" prune weight Done!'.format(str(mesh[0])))

def mirrorXSelected():
    weight_mirrorCheckBox.setLabel('+ X to - X')

def mirrorYSelected():
    weight_mirrorCheckBox.setLabel('+ Y to - Y')

def mirrorZSelected():
    weight_mirrorCheckBox.setLabel('+ Z to - Z')

def mirrorWeight():
    transferWeight(noMirror=False, isMirrorPart=weight_mirrorPartCheckBox.getValue())

def transferWeight(noMirror=True, isMirrorPart=False):
    global vertexInfo
    skinClusterList = []
    vertexInfo = getSelectedVertexInfo()
    if vertexInfo:
        pm.select(vertexInfo[1])
    objs = pm.ls(sl=True, type='transform')
    if objs:
        for obj in objs:
            if obj.getShape():
                try:
                    meshSkinCluster = getMeshSkinCluster(obj.getShape())
                except:
                    printTextEdit(main_lineEdit, 'Non-skined Mesh "{0}" Selected!'.format(obj))
                    raise IOError('Non-skined Mesh "{0}" Selected!'.format(obj))
                skinClusterList.append(meshSkinCluster)
            else:
                printTextEdit(main_lineEdit, 'No Mesh Selected!')
                raise IOError('No Mesh Selected!')
    else:
        printTextEdit(main_lineEdit, 'Nothing Selected!')
        raise IOError('Nothing Selected!')
    if noMirror:
        if len(skinClusterList) < 2:
            printTextEdit(main_lineEdit, 'Need at least 2 skined mesh selected!')
            raise IOError('Need at least 2 skined mesh selected!')
        source = skinClusterList[0]
        targetList = skinClusterList[1:]
        for target in targetList:
            pm.copySkinWeights(sourceSkin=source, destinationSkin=target, surfaceAssociation='closestPoint', influenceAssociation=influenceAssociationSetting, normalize=True, noMirror=noMirror)
            sourceMesh = str(source.getGeometry()[0].getParent())
            targetMesh = str(target.getGeometry()[0].getParent())
            printTextEdit(main_lineEdit, 'Skin weight copied from "{0}" to "{1}" !'.format(sourceMesh, targetMesh))
    else:
        currentTime = pm.getCurrentTime()
        if len(skinClusterList) > 1:
            printTextEdit(main_lineEdit, '1 selection only!')
            raise IOError('1 selection only!')
        source = skinClusterList[0]
        if weight_mirrorXRadioButton.getSelect():
            mirrorMode = 'YZ'
        if weight_mirrorYRadioButton.getSelect():
            mirrorMode = 'XZ'
        if weight_mirrorZRadioButton.getSelect():
            mirrorMode = 'XY'
        _before_mirror = bridge.capture_weights(str(source))
        pm.runtime.GoToBindPose()
        pm.copySkinWeights(sourceSkin=source, destinationSkin=source, mirrorMode=mirrorMode, mirrorInverse=not weight_mirrorCheckBox.getValue(), influenceAssociation=['label', 'name', 'oneToOne'], normalize=True, noMirror=noMirror)
        if isMirrorPart:
            pm.select(vertexInfo[0])
            vtxWeights = prepareExprotVertexData(vertexInfo)
            bridge.restore_weights(_before_mirror)
            applyVertexData(vtxWeights, vertexInfo)
        pm.setCurrentTime(currentTime)
        if vertexInfo:
            melCommand = 'doMenuComponentSelection("' + vertexInfo[1].name() + '", "vertex")'
            mel.eval(melCommand)
            mel.eval('updateObjectSelectionMasks')
            pm.select(vertexInfo[0])
        sourceMesh = str(source.getGeometry()[0].getParent())
        printTextEdit(main_lineEdit, '"{0}" skin weight mirrored!'.format(sourceMesh))

def exchangeSkinWeight(skinCluster, boneA, boneB):
    vtxs = pm.selected()
    influenceBoneList = pm.skinCluster(skinCluster, influence=boneA, query=1)
    if vtxs and boneA in influenceBoneList and (boneB in influenceBoneList):
        vtxs = pm.ls(sl=1, flatten=1)
        if isinstance(vtxs[0], pm.MeshVertex):
            printTextLable(main_processLable, 'Processing vertex weight ...')
            runProgressBar(main_progressBar, 0)
            step = 100 / float(len(vtxs))
            for vtx in vtxs:
                boneAValue = pm.skinPercent(skinCluster, vtx, ignoreBelow=0.01, query=True, transform=boneA, value=True)
                boneBValue = pm.skinPercent(skinCluster, vtx, ignoreBelow=0.01, query=True, transform=boneB, value=True)
                pm.skinPercent(skinCluster, vtx, transformValue=[(boneA, boneBValue), (boneB, boneAValue)], normalize=True)
                runProgressBar(main_progressBar, step)
            runProgressBar(main_progressBar, 100)

def swapWeight():
    global vertexInfo
    global swapBoneA
    global swapBoneB
    isMerge = swapMerge_checkBox.getValue()
    if vertexInfo:
        if len(vertexInfo[0]) > 0 and swapBoneA and swapBoneB:
            if isMerge:
                mergeSkinWeight(vertexInfo[0], swapBoneA, swapBoneB)
            else:
                exchangeSkinWeight(vertexInfo[2], swapBoneA, swapBoneB)

def swapLoadBoneA():
    global swapBoneA
    if pm.ls(sl=1, type='joint'):
        weight_swapBoneATexEdit.setText(pm.ls(sl=1, type='joint')[0].name())
        swapBoneA = pm.ls(sl=1, type='joint')[0]
    elif pm.ls(sl=1, type='float3'):
        weight_swapBoneATexEdit.setText(weight_boneListBox.getSelectItem()[0])
        swapBoneA = pm.ls(weight_boneListBox.getSelectItem()[0], type='joint')[0]

def swapLoadBoneB():
    global swapBoneB
    if pm.ls(sl=1, type='joint'):
        weight_swapBoneBTexEdit.setText(pm.ls(sl=1, type='joint')[0].name())
        swapBoneB = pm.ls(sl=1, type='joint')[0]
    elif pm.ls(sl=1, type='float3'):
        weight_swapBoneBTexEdit.setText(weight_boneListBox.getSelectItem()[0])
        swapBoneB = pm.ls(weight_boneListBox.getSelectItem()[0], type='joint')[0]

def exportVtxManager():
    if vertexInfo:
        exportVtxWeight()
    else:
        exportVtxWeight2()

def importVtxManager():
    if vertexInfo:
        importVtxWeight()
    else:
        importVtxWeight2()

def exportVtxWeight2(isOutputFile=True):
    return bridge.xml_export(isOutputFile)

def importVtxWeight2(isFromFile=True):
    return bridge.xml_import(isFromFile)
exprotVertexWeightData = None

def exportVtxWeight(isOutputFile=True):
    return bridge.vertex_export(isOutputFile)

def prepareExprotVertexData(vertexInfo):
    """
    collect weight inform of all selected vertex
    """
    vertexData = {}
    boneWeightValue = {}
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        vertexList = vertexInfo[0]
        jointList = vertexInfo[2].getInfluence()
    else:
        pm.warning('No skined vertex selected!')
        return
    printTextLable(main_processLable, 'Exporting vertex weight data ...')
    runProgressBar(main_progressBar, 0)
    step = 100 / float(len(vertexList))
    for vertex in vertexList:
        valueList = pm.skinPercent(meshSkinCluster, vertex, query=True, value=True)
        valueList = [round(x, 2) for x in valueList]
        boneWeightValue = list(zip(jointList, valueList))
        boneWeightValue = [a for a in boneWeightValue if a[1] != 0.0]
        vertexData[vertex] = boneWeightValue
        boneWeightValue = []
        runProgressBar(main_progressBar, step)
    runProgressBar(main_progressBar, 100)
    return vertexData

def importVtxWeight(isFromFile=True):
    return bridge.vertex_import(isFromFile)

def applyVertexData(vertexData, vertexInfo):
    """
    apply weight value to selected vtxs
    """
    printTextLable(main_processLable, 'Importing vertex weight data ...')
    runProgressBar(main_progressBar, 0)
    step = 100 / float(len(vertexInfo[0]))
    mesh = vertexInfo[1]
    meshSkinCluster = vertexInfo[2]
    sceneVertexList = []
    dataMeshName = list(vertexData.keys())[0].split('.')[0]
    for vertex in vertexInfo[0]:
        dataVertex = dataMeshName + '.' + vertex.split('.')[1]
        if dataVertex in list(vertexData.keys()):
            pm.skinPercent(meshSkinCluster, vertex, transformValue=vertexData[dataVertex], zeroRemainingInfluences=True)
        else:
            pm.warning(str(vertex) + 'missing, skipped!')
        sceneVertexList.append(vertex)
        runProgressBar(main_progressBar, step)
    runProgressBar(main_progressBar, 100)
    updateSkinClusterCache(meshSkinCluster)
    pm.select(sceneVertexList)

def relaxWeight():
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        vertexList = vertexInfo[0]
        vNum = len(vertexList)
        maxInf = pm.skinCluster(meshSkinCluster, q=1, maximumInfluences=True)
        fullJointList = meshSkinCluster.getInfluence()
        jointWeightLockLst = []
        for idx in range(len(fullJointList)):
            melCmd = 'skinCluster -inf ' + fullJointList[idx] + ' -q -lw ' + meshSkinCluster
            jointWeightLockLst.append(mel.eval(melCmd))
        for joint in fullJointList:
            pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=False)
        i = 0.0
        for vtxName in vertexList:
            vtx = pm.ls(vtxName)[0]
            surVtxLst = vtx.connectedVertices()
            surVtxNum = len(surVtxLst)
            bDict = {}
            vertexData = []
            for sVtx in surVtxLst:
                valueList = pm.skinPercent(meshSkinCluster, sVtx, query=True, value=True)
                valueList = [round(x, 2) for x in valueList]
                boneWeightValue = list(zip(meshSkinCluster.getInfluence(), valueList))
                boneWeightValue = [a for a in boneWeightValue if a[1] != 0.0]
                for inform in boneWeightValue:
                    if not inform[0] in list(bDict.keys()):
                        bDict[inform[0]] = 0.0
                    bDict[inform[0]] += inform[1]
            for bone in list(bDict.keys()):
                vertexData.append((bone, bDict[bone] / surVtxNum))
            pm.skinPercent(meshSkinCluster, vtx, transformValue=vertexData, normalize=True, zeroRemainingInfluences=False)
            valueList = pm.skinPercent(meshSkinCluster, vtx, ignoreBelow=0.0, query=True, value=True)
            valueList.sort()
            pruneValue = valueList[-1 * maxInf] - 0.01
            pm.skinPercent(meshSkinCluster, vtx, pruneWeights=pruneValue, normalize=True)
            i += 1.0
            setProgressBar(main_progressBar, i / vNum * 100.0)
        for idx in range(len(fullJointList)):
            pm.skinCluster(meshSkinCluster, inf=fullJointList[idx], e=True, lw=jointWeightLockLst[idx])
        pm.select(vertexList)

def relaxWeight_2(operation='smooth', value=1.0):
    if vertexInfo:
        meshSkinCluster = vertexInfo[2]
        mesh = vertexInfo[1]
        meshShape = mesh.getShape()
        vertexList = vertexInfo[0]
        vNum = len(vertexList)
        unlockBoneList = []
        for item in weight_boneListBox.getAllItems():
            unlockBoneList.append(pm.ls(item)[0])
        fullJointList = meshSkinCluster.getInfluence()
        jointWeightLockLst = []
        for idx in range(len(fullJointList)):
            melCmd = 'skinCluster -inf ' + fullJointList[idx] + ' -q -lw ' + meshSkinCluster
            jointWeightLockLst.append(mel.eval(melCmd))
        if vNum > 1:
            for joint in fullJointList:
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=True)
            for joint in unlockBoneList:
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=False)
        preJoint = None
        preTool = pm.currentCtx()
        mel.eval('ArtPaintSkinWeightsTool;')
        mel.eval('artAttrSkinToolScript 4;')
        mel.eval('artAttrInitPaintableAttr;')
        pm.setToolTo('artAttrSkinContext')
        if operation == 'scale':
            unlockBoneList = [getBoneListBone()]
        i = 0.0
        boneNum = len(unlockBoneList)
        for joint in unlockBoneList:
            if not preJoint:
                preJoint = unlockBoneList[0]
            mel.eval('artSkinInflListChanging "%s" 0;' % preJoint.name())
            mel.eval('artSkinInflListChanging "%s" 1;' % joint.name())
            mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')
            pm.artAttrSkinPaintCtx('artAttrSkinContext', edit=True, sao=operation, value=value)
            pm.artAttrSkinPaintCtx('artAttrSkinContext', edit=True, clear=1)
            preJoint = joint
            i += 1.0
            if boneNum > 10:
                setProgressBar(main_progressBar, i / boneNum * 100.0)
        if vNum > 1:
            for joint in meshSkinCluster.getInfluence():
                pm.skinCluster(meshSkinCluster, inf=joint, edit=True, lockWeights=False)
        pm.skinPercent(meshSkinCluster, normalize=True)
        if vNum > 1:
            for idx in range(len(fullJointList)):
                pm.skinCluster(meshSkinCluster, inf=fullJointList[idx], e=True, lw=jointWeightLockLst[idx])
        pm.setToolTo(preTool)
        mel.eval('doMenuComponentSelection("%s", "vertex");' % mesh.name())
        updateWeightUI()

def selectWeightedVerts(boneLst=None):
    if not boneLst:
        boneLst = pm.ls(sl=1, type='joint')
    if not boneLst:
        boneLst = [getBoneListBone()]
    if boneLst:
        meshLst = pm.ls(sl=1, type='transform')
        pm.select(clear=True)
        skinClusterLst = []
        for mesh in meshLst:
            meshskinCluster = getMeshSkinCluster(mesh)
            if meshskinCluster:
                skinClusterLst.append(meshskinCluster)
        vtxsLst = []
        for bone in boneLst:
            if not skinClusterLst:
                skinClusterLst = bone.worldMatrix[0].connections(type='skinCluster')
            for skinCluster in skinClusterLst:
                if bone in skinCluster.getInfluence():
                    for vtxs in skinCluster.getPointsAffectedByInfluence(bone)[0]:
                        vtxsLst.append(vtxs)
        for vtx in vtxsLst:
            pm.select(vtx, add=1)
        if infVerts_makeSet_checkBox.getValue() and vtxsLst:
            pm.sets(name='Inf_Vtxs_Set')
    return getCurrentSelectVertexs()
lodSourceMesh = None
lodSourceMeshShape = None
lodSourceMeshSkinCluster = None
lodTargetMesh = None
lodTargetMeshShape = None
lodTargetMeshSkinCluster = None
lodBoneDict = {}

def lodGetMesh(meshType):
    global lodSourceMesh
    global lodSourceMeshShape
    global lodSourceMeshSkinCluster
    global lodTargetMesh
    global lodTargetMeshShape
    global lodTargetMeshSkinCluster
    if meshType == 'source':
        if pm.ls(sl=1):
            lodSourceMesh = pm.ls(sl=1)[0]
        else:
            lodSourceMesh = None
        if lodSourceMesh == lodTargetMesh:
            lodSourceMesh = None
        if lodSourceMesh:
            lodSourceMeshShape = lodSourceMesh.getShape()
            if pm.nodeType(lodSourceMeshShape) == 'mesh':
                lodSourceMeshSkinClusterList = lodSourceMeshShape.listHistory(type='skinCluster')
                if lodSourceMeshSkinClusterList:
                    if len(lodSourceMeshSkinClusterList) == 1:
                        lodSourceMeshSkinCluster = lodSourceMeshSkinClusterList[0]
                        lodSourceMesh_lineEdit.setText(lodSourceMesh)
                    else:
                        pass
                else:
                    lodSourceMeshSkinCluster = None
                    lodSourceMesh = None
                    lodSourceMesh_lineEdit.setText('Pick Skined Mesh')
        else:
            lodSourceMesh = None
            lodSourceMesh_lineEdit.setText('Pick Skined Mesh')
    else:
        if pm.ls(sl=1):
            lodTargetMesh = pm.ls(sl=1)[0]
        else:
            lodTargetMesh = None
        if lodTargetMesh == lodSourceMesh:
            lodTargetMesh = None
        if lodTargetMesh:
            lodTargetMeshShape = lodTargetMesh.getShape()
            if pm.nodeType(lodTargetMeshShape) == 'mesh':
                lodTargetMesh_lineEdit.setText(lodTargetMesh)
        else:
            lodTargetMesh = None
            lodTargetMesh_lineEdit.setText('Pick Mesh ( Optional )')

def lodAdd():
    """
    add picked bones to pick bone list and weight receiver list
    """
    global lodBoneDict
    global lodSourceMesh
    if not lodSourceMesh:
        pm.warning('Pick source mesh first before pick bone(s)!')
        return
    weightBoneList = lodGetSelectBones()
    for bone in list(lodBoneDict.keys()):
        weightBoneList.append(bone)
    lodBoneDict.update(makeBoneDict(weightBoneList))
    lodUpdateBoneListUI(lodBoneDict)

def makeBoneDict(boneList):
    """
    prepare both pick bone and receiver list for ui
    """
    global lodSourceMesh
    global lodSourceMeshSkinCluster
    global lodBoneDict
    if lodSourceMeshSkinCluster:
        lodSourceBoneList = pm.ls(lodSourceMeshSkinCluster)[0].getInfluence()
    boneDict = {}
    for bone in boneList:
        getWeightBone = False
        if bone in list(lodBoneDict.keys()):
            boneDict[bone] = lodBoneDict[bone]
        else:
            for boneParent in bone.getAllParents():
                if boneParent in boneList:
                    boneDict[bone] = boneParent.getParent()
                    getWeightBone = True
            if getWeightBone == False:
                weightReceiver = getWeightReceiver(bone, boneList)
                boneDict[bone] = weightReceiver
    return boneDict

def getWeightReceiver(bone, boneList):
    if bone.getParent() in boneList:
        bone = getWeightReceiver(bone.getParent(), boneList)
        return bone
    else:
        return bone.getParent()

def lodUpdateBoneListUI(boneDict):
    """
    Update bone list UI
    If old picked joint still exists in new bone list, select it, or select first one
    """
    weightBoneList = []
    pickedJoint = lodSourceBone_ListBox.getSelectItem()
    lodSourceBone_ListBox.removeAll()
    lodTargetBone_ListBox.removeAll()
    pickBonelist = sorted(boneDict.keys())
    for bone in pickBonelist:
        weightBoneList.append(boneDict[bone])
    lodSourceBone_ListBox.extend(pickBonelist)
    lodTargetBone_ListBox.extend(weightBoneList)
    a = 0
    for bone in boneDict:
        if pickedJoint:
            if pickedJoint[0] == bone:
                a = 1
    if a == 1:
        lodSourceBone_ListBox.setSelectItem(pickedJoint)
    elif a == 0 and len(lodSourceBone_ListBox.getAllItems()) >= 1:
        lodSourceBone_ListBox.setSelectIndexedItem(1)

def getRootBone(obj):
    if pm.listRelatives(obj, allParents=1):
        return pm.listRelatives(obj, allParents=1)[0]
    else:
        return obj

def lodGetSelectBones():
    """
    make bone dict from selected and filted out non weight bone
    """
    global lodSourceBoneList
    global lodSourceMeshSkinCluster
    global lodSourceMesh
    lodSourceBoneList = []
    lodSourceAllBoneList = []
    if lodSourceMeshSkinCluster:
        lodSourceBoneList = pm.ls(lodSourceMeshSkinCluster)[0].getInfluence()
    lodSourceAllBoneList = pm.listRelatives(getRootBone(lodSourceBoneList[0]), allDescendents=1)
    outBoneList = []
    pickBoneList = pm.ls(sl=1, exactType='joint')
    for bone in pickBoneList:
        if lodSourceBoneList and bone in lodSourceAllBoneList:
            outBoneList.append(bone)
        else:
            pm.warning(bone + ' is not skin influence bone of ' + lodSourceMesh + ', skipped!')
    return outBoneList

def lodRemove():
    global lodBoneDict
    obj = lodSourceBone_ListBox.getSelectIndexedItem()
    removeList = lodSourceBone_ListBox.getSelectItem()
    f = lambda x: not str(x[0]) in removeList
    lodBoneDict = dict(list(filter(f, list(lodBoneDict.items()))))
    lodUpdateBoneListUI(lodBoneDict)
    lodSourceBone_ListBox.deselectAll()
    try:
        lodSourceBone_ListBox.setSelectIndexedItem(obj[0] - 1)
    except:
        pass
    lodBoneListSelected()

def lodUpdateReceiver():
    """
    update weight bone UI and dictionary as select bone
    """
    global lodBoneDict
    global lodSourceMeshSkinCluster
    global lodSourceMesh
    if lodSourceMeshSkinCluster:
        lodSourceBoneList = pm.ls(lodSourceMeshSkinCluster)[0].getInfluence()
    obj = lodSourceBone_ListBox.getSelectIndexedItem()
    updateList = lodSourceBone_ListBox.getSelectItem()
    newWeightBone = pm.ls(sl=1)[0]
    if newWeightBone not in lodSourceBoneList:
        pm.warning(newWeightBone + ' is not the influence bone of ' + lodSourceMesh + ', pick again!')
        return
    if newWeightBone.name() in updateList:
        pm.warning(newWeightBone.name() + ' is dupilicated with remove bone, pick again!')
        return
    f = lambda x: str(x[0]) in updateList
    g = lambda x: (x[0], newWeightBone) if f(x) else x
    lodBoneDict = dict(list(map(g, list(lodBoneDict.items()))))
    lodUpdateBoneListUI(lodBoneDict)
    lodSourceBone_ListBox.deselectAll()
    lodSourceBone_ListBox.setSelectIndexedItem(obj)
    lodBoneListSelected()

def lodClear():
    global lodBoneDict
    lodBoneDict.clear()
    lodUpdateBoneListUI(lodBoneDict)

def lodSave():
    return bridge.lod_export()

def toJoint(name):
    if pm.objExists(name):
        return pm.nt.Joint(name)
    else:
        return None

def lodLoad():
    return bridge.lod_import()

def lodReset():
    global lodSourceMesh
    global lodSourceMeshShape
    global lodSourceMeshSkinCluster
    global lodTargetMesh
    global lodTargetMeshShape
    global lodTargetMeshSkinCluster
    global lodBoneDict
    lodSourceMesh = None
    lodSourceMeshShape = None
    lodSourceMeshSkinCluster = None
    lodTargetMesh = None
    lodTargetMeshShape = None
    lodTargetMeshSkinCluster = None
    lodBoneDict.clear()
    lodSourceMesh_lineEdit.setText('Pick Skined Mesh')
    lodTargetMesh_lineEdit.setText('Pick Mesh ( Optional )')
    lodClear()

def lodVerifyReceiveBoneList():
    global lodSourceMeshSkinCluster
    global lodBoneDict
    childBoneList = []
    allList = []
    for key in list(lodBoneDict.keys()):
        childBoneList = pm.listRelatives(key, allDescendents=1) or []
        childBoneList.append(key)
        allList += childBoneList
    allList = list(set(allList))
    lodUpdateBoneListUI(lodBoneDict)

def lodMake(isBatch=False, isBatchLastOne=False):
    """
    Process Lod Mesh base on settings
    """
    global lodSourceMesh
    global lodSourceMeshShape
    global lodSourceMeshSkinCluster
    global lodTargetMesh
    global lodTargetMeshShape
    global lodTargetMeshSkinCluster
    global lodBoneDict
    lodVerifyReceiveBoneList()
    for key in list(lodBoneDict.keys()):
        if lodBoneDict[key] == 'Not specified':
            pm.warning('Missing receiver or receiver in remove bone hierarchy, please check!')
            return
    if lodSourceMesh and lodBoneDict:
        if not lodTargetMesh:
            lodTargetMesh = lodSourceMesh
            lodTargetMeshShape = lodSourceMeshShape
            lodTargetMeshSkinCluster = lodSourceMeshSkinCluster
            isSelfReduce = True
        else:
            isSelfReduce = False
        runProgressBar(main_progressBar, 0)
        if not isSelfReduce:
            forceDeleteHistory(lodTargetMesh)
            rootBone = getRootBone(list(lodBoneDict.keys())[0])
            printTextLable(main_processLable, 'Binding LoD skin ...')
            lodTargetMeshSkinCluster = pm.skinCluster(lodTargetMesh, rootBone, name=lodTargetMesh + 'SkinCluster', maximumInfluences=3, normalizeWeights=1, obeyMaxInfluences=True)
            pm.copySkinWeights(sourceSkin=lodSourceMeshSkinCluster, destinationSkin=lodTargetMeshSkinCluster, noMirror=True, influenceAssociation='name')
            pm.skinPercent(lodTargetMeshSkinCluster, lodTargetMesh, pruneWeights=0.04, normalize=True)
        childBoneList = []
        allChildBoneNum = 0
        for key in list(lodBoneDict.keys()):
            boneList = pm.listRelatives(key, allDescendents=1) or []
            allChildBoneNum += len(boneList)
        number = 20.0 / float(len(list(lodBoneDict.keys())))
        mergeFullJointList = lodTargetMeshSkinCluster.getInfluence()
        for joint in mergeFullJointList:
            pm.skinCluster(lodTargetMeshSkinCluster, inf=joint, edit=True, lockWeights=True)
        for key in list(lodBoneDict.keys()):
            runProgressBar(main_progressBar, number)
            if pm.objExists(key):
                if not key in mergeFullJointList:
                    lodTargetMeshSkinCluster.addInfluence(key)
                    pm.skinCluster(lodTargetMeshSkinCluster, inf=key, edit=True, lockWeights=True)
                    mergeFullJointList.append(key)
                targetBone = lodBoneDict[key]
                if pm.objExists(targetBone):
                    if not targetBone in mergeFullJointList:
                        lodTargetMeshSkinCluster.addInfluence(targetBone)
                        pm.skinCluster(lodTargetMeshSkinCluster, inf=targetBone, edit=True, lockWeights=True)
                        mergeFullJointList.append(targetBone)
                else:
                    pm.warning('Missing object, ' + lodBoneDict[key] + ' skipped')
            else:
                pm.warning('Missing object, ' + key + ' skipped')
        number = 70.0 / float(len(list(lodBoneDict.keys())))
        pm.select(clear=True)
        preTool = pm.currentCtx()
        pm.select(lodTargetMesh)
        mel.eval('ArtPaintSkinWeightsTool;')
        mel.eval('artAttrSkinToolScript 4;')
        mel.eval('artAttrInitPaintableAttr;')
        pm.setToolTo('artAttrSkinContext')
        oldMaintainMaxInfluences = pm.getAttr(lodTargetMeshSkinCluster.maintainMaxInfluences)
        pm.setAttr(lodTargetMeshSkinCluster.maintainMaxInfluences, 0)
        for key in list(lodBoneDict.keys()):
            printTextLable(main_processLable, 'Cleaning up ' + key + '...')
            runProgressBar(main_progressBar, number)
            lockBoneLst = []
            pm.skinCluster(lodTargetMeshSkinCluster, inf=key, edit=True, lockWeights=False)
            lockBoneLst.append(key)
            for cbone in pm.listRelatives(key, allDescendents=1) or []:
                if cbone in mergeFullJointList:
                    pm.skinCluster(lodTargetMeshSkinCluster, inf=cbone, edit=True, lockWeights=False)
                    lockBoneLst.append(cbone)
            targetBone = lodBoneDict[key]
            mel.eval('artSkinInflListChanging "%s" 1;' % targetBone.name())
            mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')
            pm.artAttrSkinPaintCtx('artAttrSkinContext', edit=True, clear=1, sao='absolute', val=1.0)
            mel.eval('artSkinInflListChanging "%s" 0;' % targetBone.name())
            for lBone in lockBoneLst:
                pm.skinCluster(lodTargetMeshSkinCluster, inf=lBone, edit=True, lockWeights=True)
        pm.setAttr(lodTargetMeshSkinCluster.maintainMaxInfluences, oldMaintainMaxInfluences)
        pm.setToolTo(preTool)
        for joint in mergeFullJointList:
            pm.skinCluster(lodTargetMeshSkinCluster, inf=joint, edit=True, lockWeights=False)
        lodTargetMeshSkinCluster.setNormalizeWeights(True)
        pm.skinPercent(lodTargetMeshSkinCluster, normalize=True)
        runProgressBar(main_progressBar, 5.0)
        updateSkinClusterCache(lodTargetMeshSkinCluster)
        printTextLable(main_processLable, 'Deleting bones ...')
        isDoDleteBone = False
        if lodDeleteBone_CheckBox.getValue():
            if isBatch:
                if isBatchLastOne:
                    isDoDleteBone = True
            else:
                isDoDleteBone = True
        if isDoDleteBone:
            for key in list(lodBoneDict.keys()):
                if pm.objExists(key):
                    try:
                        pm.delete(key)
                    except:
                        pass
            lodClear()
        updateSkinClusterCache(lodTargetMeshSkinCluster)
        normalizeWeightObj(lodTargetMesh)
        if not isSelfReduce and lodDeleteBase_CheckBox.getValue():
            pm.delete(lodSourceMesh)
            lodSourceMesh = None
            lodSourceMesh_lineEdit.setText('Pick Skined Mesh')
        else:
            lodTargetMesh = None
            lodTargetMeshShape = None
            lodTargetMeshSkinCluster = None
        if lodDeleteShader_CheckBox.getValue():
            try:
                pm.warning('Automatic scene-wide unused shader deletion removed; use a scoped cleanup separately')
            except:
                pass
        runProgressBar(main_progressBar, 100)
        showSpam()

def updateSkinClusterCache(skinCluster):
    origonalValue = pm.getAttr(skinCluster.useComponents)
    pm.setAttr(skinCluster.useComponents, not origonalValue)
    pm.setAttr(skinCluster.useComponents, origonalValue)

def lodMakeLauncher():
    global lodSourceMesh
    global lodSourceMeshShape
    global lodSourceMeshSkinCluster
    selectMeshLst = []
    if lodBatch_CheckBox.getValue():
        for obj in pm.ls(sl=1):
            if pm.nodeType(obj.getShape()) == 'mesh':
                if getMeshSkinCluster(obj):
                    selectMeshLst.append(obj)
        for mesh in selectMeshLst:
            lodSourceMesh = mesh
            lodSourceMeshShape = lodSourceMesh.getShape()
            lodSourceMeshSkinCluster = lodSourceMeshShape.listHistory(type='skinCluster')[0]
            isLastOne = False
            if mesh == selectMeshLst[len(selectMeshLst) - 1]:
                isLastOne = True
            lodMake(isBatch=True, isBatchLastOne=isLastOne)
        for mesh in selectMeshLst:
            try:
                normalizeWeightObj(mesh)
            except:
                pass
    else:
        lodMake()

def findChildrenBone(parentBone, childBoneList):
    if parentBone.listRelatives(children=True, type='joint'):
        for bone in parentBone.listRelatives(children=True):
            findChildrenBone(bone, childBoneList)
            childBoneList.append(bone)
    return childBoneList

def mergeSkinWeight(vtxs, scourceBone, targetBone):
    global vertexInfo
    skinCluster = vertexInfo[2]
    for joint in skinCluster.getInfluence():
        pm.skinCluster(skinCluster, inf=joint, edit=True, lockWeights=True)
    pm.skinCluster(skinCluster, inf=scourceBone, edit=True, lockWeights=False)
    pm.skinCluster(skinCluster, inf=targetBone, edit=True, lockWeights=False)
    pm.skinPercent(skinCluster, vtxs, transformValue=[(scourceBone, 0.0), (targetBone, 1.0)], normalize=False)
    for joint in skinCluster.getInfluence():
        pm.skinCluster(skinCluster, inf=joint, edit=True, lockWeights=False)

def lodBoneListSelected():
    itemIndex = lodSourceBone_ListBox.getSelectIndexedItem()
    if itemIndex > 0:
        lodTargetBone_ListBox.deselectAll()
        lodTargetBone_ListBox.setSelectIndexedItem(itemIndex)
    else:
        lodTargetBone_ListBox.deselectAll()
goreSourceMesh = None
goreSourceMeshSkinCluster = None
goreTargetMeshList = []

def goreGetBaseMesh():
    global goreSourceMesh
    global goreSourceMeshSkinCluster
    global goreTargetMeshList
    if pm.ls(sl=1):
        goreSourceMesh = pm.ls(sl=1)[0]
    else:
        goreSourceMesh = None
    if goreSourceMesh in goreTargetMeshList:
        goreSourceMesh = None
        return
    if goreSourceMesh:
        goreSourceMeshShape = goreSourceMesh.getShape()
        if pm.nodeType(goreSourceMeshShape) == 'mesh':
            goreSourceMeshSkinClusterList = goreSourceMeshShape.listHistory(type='skinCluster')
            if goreSourceMeshSkinClusterList and len(goreSourceMeshSkinClusterList) == 1:
                goreSourceMeshSkinCluster = goreSourceMeshSkinClusterList[0]
                goreBaseMesh_lineEdit.setText(goreSourceMesh)
            else:
                goreSourceMesh = None
                goreSourceMeshSkinCluster = None
                goreBaseMesh_lineEdit.setText('Pick Skined Base Mesh')
    else:
        goreSourceMesh = None
        goreBaseMesh_lineEdit.setText('Pick Skined Base Mesh')

def goreAdd():
    global goreSourceMesh
    global goreTargetMeshList
    goreTargetMesh = pm.ls(sl=1)
    if goreTargetMesh:
        for mesh in goreTargetMesh:
            shape = mesh.getShape()
            if shape:
                if pm.nodeType(shape) == 'mesh' and mesh not in goreTargetMeshList and (mesh != goreSourceMesh):
                    goreTargetMeshList.append(mesh)
    if goreTargetMeshList:
        goreMesh_ListBox.removeAll()
        goreMesh_ListBox.extend(goreTargetMeshList)

def goreRemove():
    global goreTargetMeshList
    obj = goreMesh_ListBox.getSelectIndexedItem()
    removeList = goreMesh_ListBox.getSelectItem()
    itemList = []
    for item in goreTargetMeshList:
        if item.name() in removeList:
            itemList.append(item)
    for item in itemList:
        goreTargetMeshList.remove(item)
    if goreTargetMeshList:
        goreMesh_ListBox.removeAll()
        goreMesh_ListBox.extend(goreTargetMeshList)
    else:
        goreMesh_ListBox.removeAll()
        goreTargetMeshList = ['Pick Gore Meshes and Add']
        goreMesh_ListBox.extend(goreTargetMeshList)
        goreTargetMeshList = []
    goreMesh_ListBox.deselectAll()
    try:
        goreMesh_ListBox.setSelectIndexedItem(obj[0] - 1)
    except:
        pass

def goreClear():
    global goreTargetMeshList
    goreMesh_ListBox.removeAll()
    goreTargetMeshList = ['Pick Gore Meshes and Add']
    goreMesh_ListBox.extend(goreTargetMeshList)
    goreTargetMeshList = []

def goreMake():
    global goreSourceMesh
    global goreSourceMeshSkinCluster
    global goreTargetMeshList
    if goreSourceMesh and goreTargetMeshList:
        pass
    else:
        return
    bone = goreSourceMeshSkinCluster.getInfluence()[0]
    runProgressBar(main_progressBar, 0)
    number = round(100 / len(goreTargetMeshList))
    for mesh in goreTargetMeshList:
        printTextLable(main_processLable, 'Processing ' + mesh.name() + '...')
        runProgressBar(main_progressBar, number)
        forceDeleteHistory(mesh)
        bindSkinList = [bone, mesh, goreSourceMesh]
        bindSkinPlus(bindSkinList)
    showSpam()
    runProgressBar(main_progressBar, 100)
    goreClear()
    if goreDeleteBase_CheckBox.getValue():
        pm.delete(goreSourceMesh)
        goreSourceMesh = None
        goreBaseMesh_lineEdit.setText('Pick Skined Base Mesh')
    if goreDeleteShader_CheckBox.getValue():
        try:
            pm.warning('Automatic scene-wide unused shader deletion removed; use a scoped cleanup separately')
        except:
            pass

def unlockTransform(mesh):
    attrList = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz']
    for txt in attrList:
        unlockAttrTxt = 'CBunlockAttr ' + mesh.name() + txt
        unlockAttrTxt = unlockAttrTxt + ';'
        unlockAttrTxt = 'if (!`exists CBunlockAttr`)\n{\nsource channelBoxCommand;\n}\n' + unlockAttrTxt
        mel.eval(unlockAttrTxt)
    pm.refresh()

def forceDeleteHistory(mesh, isKeepSkin=False):
    pm.select(mesh.name(), replace=True)
    pm.select(mesh.name(), replace=True)
    cmds.DeleteHistory()
    unlockTransform(mesh)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

def goShelf():
    return bridge.add_shelf_button()

def scaleJoint():
    try:
        scaleRate = float(scaleJoint_lineEdit.getText())
    except:
        scaleRate = 1.0
        scaleJoint_lineEdit.setText(1.0)
    for bone in pm.ls(sl=1, type='joint'):
        bone.setTranslation(bone.getTranslation() * scaleRate)

def cleanAttr():
    for bone in pm.ls(sl=1, type='joint'):
        if pm.deleteAttr(bone, q=True):
            attrList = []
            for attr in pm.deleteAttr(bone, q=True):
                attrList.append(attr)
            for attr in attrList:
                try:
                    pm.deleteAttr(bone.name(), at=attr)
                except:
                    pass

def removeUnknowNode():
    return bridge.remove_selected_unknown()

def meshCleanUp(removeSkinHistory=False):
    allSelection = pm.ls(selection=True)
    if len(allSelection) < 1:
        printTextEdit(main_lineEdit, 'No mesh selected!')
    else:
        for currentOne in allSelection:
            pm.select(currentOne)
            currentChildType = pm.nodeType(pm.pickWalk(direction='down')[0])
            if currentChildType != 'mesh':
                printTextEdit(main_lineEdit, '{0} is a {1}, Skiped!'.format(currentOne, currentChildType))
            else:
                meshUVSet = pm.polyUVSet(query=True, allUVSets=True)
                if len(meshUVSet) == 1:
                    pm.select(currentOne)
                    try:
                        pm.makeIdentity(apply=True)
                    except:
                        pass
                    pm.polySoftEdge(name=currentOne, angle=180)
                    pm.select(currentOne)
                    if removeSkinHistory:
                        cmds.DeleteAllHistory()
                    else:
                        cmds.BakeNonDefHistory(name=currentOne)
                    printTextEdit(main_lineEdit, '{0} Cleaned!'.format(currentOne))
                else:
                    printTextEdit(main_lineEdit, '{0} has {1} UVSet(s), Skiped!'.format(currentOne, len(meshUVSet)))

def bindSkinPlus(inputList=[]):
    """
    Input list should be transform node
    """
    if inputList:
        allSelection = inputList
    else:
        allSelection = pm.ls(selection=True)
    childType = []
    i = 0
    sourceBone = None
    sourceSkinCluster = None
    sourceMesh = None
    targetMesh = None
    for currentOne in allSelection:
        pm.select(currentOne)
        currentOneChild = pm.pickWalk(direction='down')[0]
        childType.append(pm.nodeType(currentOneChild))
        if childType[i] == 'joint':
            sourceBone = pm.pickWalk(direction='up')[0]
            while sourceBone != pm.pickWalk(direction='up')[0]:
                sourceBone = pm.pickWalk(direction='up')[0]
        elif childType[i] == 'mesh':
            meshSkinCluster = getMeshSkinCluster(currentOneChild)
            if meshSkinCluster:
                if sourceSkinCluster != None:
                    printTextEdit(main_lineEdit, 'Only 1 skined mesh allowed! Stop processing!')
                    pm.select(currentOne)
                    raise
                else:
                    sourceSkinCluster = meshSkinCluster
                    sourceMesh = currentOne
            else:
                targetMesh = currentOne
        else:
            pm.select(currentOne)
            raise IOError('{0} is not a joint or mesh! Stop processing!'.format(currentOne))
        i += 1
    pm.select(clear=True)
    if len(allSelection) < 1:
        printTextEdit(main_lineEdit, 'Nothing selected!')
    elif len(allSelection) == 1:
        if childType[0] == 'joint':
            printTextEdit(main_lineEdit, 'Mesh must be selected! Stop processing!')
            pm.select(allSelection[0])
            raise
        elif childType[0] == 'mesh':
            printTextEdit(main_lineEdit, 'You must select at least one joint! Stop processing!')
            pm.select(allSelection[0])
            raise
    elif len(allSelection) == 2:
        if sourceBone == None:
            printTextEdit(main_lineEdit, 'You must select at least one joint! Stop processing!')
            pm.select(allSelection[1])
            raise
        elif targetMesh == None:
            printTextEdit(main_lineEdit, '{0} has already skined! Stop processing!'.format(sourceMesh))
            pm.select(sourceMesh)
            raise
        else:
            targetSkinCluster = targetMesh + 'SkinCluster'
            pm.skinCluster(targetMesh, sourceBone, name=targetSkinCluster, maximumInfluences=3, normalizeWeights=1, obeyMaxInfluences=True)
            pm.skinPercent(targetSkinCluster, targetMesh, pruneWeights=0.03, normalize=True)
            printTextEdit(main_lineEdit, 'Bind {0} to {1}!'.format(targetMesh, sourceBone))
            pm.select(targetMesh)
    elif len(allSelection) == 3:
        if sourceBone == None:
            printTextEdit(main_lineEdit, 'You must select at least one joint! Stop processing!')
            pm.select(allSelection[1])
            raise
        elif targetMesh == None:
            printTextEdit(main_lineEdit, 'You must select at least one skin-able mesh! Stop processing!')
            pm.select(sourceMesh)
            raise
        elif sourceSkinCluster == None:
            printTextEdit(main_lineEdit, 'You must select at least one skined mesh! Stop processing!')
            pm.select(sourceMesh)
            raise
        else:
            targetSkinCluster = targetMesh + 'SkinCluster'
            sourceBone = pm.ls(sourceSkinCluster)[0].getInfluence()
            pm.skinCluster(targetMesh, sourceBone, name=targetSkinCluster, maximumInfluences=3, normalizeWeights=1, obeyMaxInfluences=True, toSelectedBones=True)
            pm.copySkinWeights(sourceSkin=sourceSkinCluster, destinationSkin=targetSkinCluster, noMirror=True, influenceAssociation='name')
            pm.skinPercent(targetSkinCluster, targetMesh, pruneWeights=0.03, normalize=True)
            pm.skinCluster(targetSkinCluster, edit=True, removeUnusedInfluence=True)
            printTextEdit(main_lineEdit, 'Skin weights copied from "{0}" to "{1}" !'.format(sourceMesh, targetMesh))
    elif len(allSelection) > 3:
        printTextEdit(main_lineEdit, 'No more selection then 3 items! Stop processing!')
        raise

def deformerOK():
    meshes = []
    objs = pm.ls(sl=1)
    for obj in objs:
        if obj.getShape():
            if pm.nodeType(obj.getShape()) == 'mesh':
                meshes.append(obj)
    a = 'proc BBF_DeftoSeq(string $objectName, int $frameStart, int $frameEnd, int $repeats){   \n\n        //Duplicate Base Object\n        currentTime $frameStart;\n        select -r $objectName;\n        string $baseArray[]=`duplicate -rr`;\n        string $base = $baseArray[0];\n        string $baseNew= `rename $baseArray[0] ($baseArray[0]+"_Baked")`;\n            \n        //Create blendShape\n        string $blend = ($baseNew+"Blend");\n        blendShape -n $blend $baseNew;\n        \n        //create and attach blend targets\n        int $numberofFrames= $frameEnd - $frameStart;\n        $step=100/$numberofFrames;\n        for($i=$frameStart;$i<=$frameEnd;$i++){\n            currentTime $i;\n            select -r $objectName;\n            $targetarray=`duplicate -rr`;\n            $target = `rename $targetarray[0] ($objectName+$i)`;\n            \n            blendShape -e -t $baseNew $i $target 1 $baseNew;\n            delete $target;\n            //progressBar -edit -step $step convertProgress;\n        }\n        hide $objectName;\n        //Key blend\n        for($i=$frameStart;$i<=$frameEnd;$i++){ \n            setAttr ($blend+"."+$objectName+$i) 1;\n            if($i>$frameStart){ \n                $prevFrame = $i-1;\n                setAttr ($blend+"."+$objectName+$prevFrame) 0;\n            }\n            setKeyframe -t $i $blend;\n            \n            //Loop if requested\n            for($r=0;$r<=$repeats;$r++){\n                setKeyframe -t ($i+ ( ($frameEnd+1) * $r) ) $blend;\n                \n            }\n        }       \n        //deleteUI BBF_DeformerToblend;\n    }'
    mel.eval(a)
    if deformerActive_radioButton.getSelect():
        startFrame = int(pm.playbackOptions(q=1, minTime=1))
        endFrame = int(pm.playbackOptions(q=1, maxTime=1))
    else:
        startFrame = int(deformerStart_lineEdit.getText())
        endFrame = int(deformerEnd_lineEdit.getText())
    for mesh in meshes:
        mel.eval('BBF_DeftoSeq("{0}", "{1}", "{2}", "{3}")'.format(mesh, startFrame, endFrame, 0))

def meshCleanWeightlessBone():
    mel.eval('removeUnusedInfluences()')

def selectWeightBone():
    skinCluster_a = scourceBone = influenceBoneList = None
    if pm.ls(type='joint'):
        scourceBone = pm.ls(type='joint')
    skinCluster_a = getMeshSkinCluster(pm.ls(sl=1)[0])
    if skinCluster_a:
        influenceBoneList = pm.skinCluster(skinCluster_a, influence=1, query=1)
        if influenceBoneList:
            pm.select(clear=1)
            pm.select(influenceBoneList)
        else:
            pm.warning('No Weighted Bone with ' + pm.ls(sl=1)[0].name())

def copyVertexWeight(sourve_v, target_v):
    pm.select(sourve_v)
    mel.eval('artAttrSkinWeightCopy')
    pm.select(target_v)
    mel.eval('artAttrSkinWeightPaste')

def m_getClosestVtx(sVtx, tVtxLst):
    pos = sVtx.getPosition()
    pointA = OpenMaya.MPoint(pos.x, pos.y, pos.z)
    space = OpenMaya.MSpace.kWorld
    closestVert = None
    minLength = None
    for v in tVtxLst:
        thisLength = (pos - v.getPosition(space='world')).length()
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v
    return closestVert

def copyClosestVtx(isFineCopy):
    global vertexInfo
    vtxs2 = pm.ls(vertexInfo[0], flatten=1)
    targetSkinCluster = vertexInfo[2]
    i = 0.0
    if len(vtxs2) > 0:
        printTextLable(main_processLable, 'Warping ...')
        if isFineCopy:
            for v2 in vtxs2:
                v2Pos = v2.getPosition()
                v1LengthLst = [(v2Pos - x).length() for x in closest_sourceVtxsPosList]
                closest_v1 = closest_sourceVtxsList[v1LengthLst.index(min(v1LengthLst))]
                copyVertexWeight(closest_v1, v2)
                i += 100.0 / len(vtxs2)
                setProgressBar(main_progressBar, i)
        else:
            weightPxyMesName = pm.polyCreateFacet(point=closest_sourceVtxsPosList, name='sm_weightPxyMesh')[0]
            weightPxyMesh = pm.ls(weightPxyMesName)[0]
            sourceVtxsSkinBone = closest_sourceVtxSkinCluster.getInfluence()
            weightPxyMeshSkinCluster = pm.skinCluster(weightPxyMesh, sourceVtxsSkinBone, name='sm_weightPxyMesh_SkinCluster', maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
            pm.copySkinWeights(sourceSkin=closest_sourceVtxSkinCluster, destinationSkin=weightPxyMeshSkinCluster, surfaceAssociation='closestPoint', influenceAssociation=influenceAssociationSetting, normalize=True, smooth=True, noMirror=True)
            _before_transfer = bridge.capture_weights(str(targetSkinCluster))
            pm.copySkinWeights(sourceSkin=weightPxyMeshSkinCluster, destinationSkin=targetSkinCluster, surfaceAssociation='closestPoint', influenceAssociation=influenceAssociationSetting, normalize=True, smooth=True, noMirror=True)
            vtxWeights = prepareExprotVertexData(vertexInfo)
            bridge.restore_weights(_before_transfer)
            applyVertexData(vtxWeights, vertexInfo)
            pm.delete(weightPxyMesh)
    setProgressBar(main_progressBar, 0)
    showSpam()

def bakeAnim(objLst, startFrame, endFrame):
    pm.bakeResults(objLst, t=(startFrame, endFrame), sampleBy=1.0, disableImplicitControl=False, preserveOutsideKeys=True, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, minimizeRotation=True, shape=False, simulation=False)

def limitTextEditValue(ui_object, minValue=0, maxValue=1, roundF=2, defaultValue=0):
    value = 0
    try:
        value = float(ui_object.getText())
    except:
        ui_object.setText(str(defaultValue))
        return
    if value < minValue:
        ui_object.setText(str(minValue))
    elif value > maxValue:
        ui_object.setText(str(maxValue))
    else:
        ui_object.setText(str(round(float(value), roundF)))
boneTransformDict = {}

def copyBonePose():
    global boneTransformDict
    for obj in pm.ls(sl=1):
        boneTransformDict[obj] = [obj.getTranslation(), obj.getRotation()]

def pasteBonePose():
    for obj in pm.ls(sl=1):
        if obj in list(boneTransformDict.keys()):
            obj.setTranslation(boneTransformDict[obj][0])
            obj.setRotation(boneTransformDict[obj][1])

def getBlendShapeList(obj):
    return pm.listHistory(obj, type='blendShape')

def bsTransLoadSrc():
    bsTransSrcBs_List.clear()
    if pm.nodeType(pm.ls(sl=1, type='transform')[0].getShape()) == 'mesh':
        bsTransSrcMesh = pm.ls(sl=1, type='transform')[0]
        bsTransSrcMesh_lineEdit.setText(bsTransSrcMesh.name())
        bsList = getBlendShapeList(bsTransSrcMesh)
        if bsList:
            bsTransSrcBs_List.addItems(bsList)
        else:
            bsTransSrcBs_List.addItems(['None'])
    else:
        bsTransSrcMesh = None
        bsTransSrcMesh_lineEdit.setText('None')
        bsTransSrcBs_List.addItems(['None'])

def bsTransLoadTgt():
    if pm.nodeType(pm.ls(sl=1, type='transform')[0].getShape()) == 'mesh':
        bsTransTgtMesh = pm.ls(sl=1, type='transform')[0]
        bsTransTgtMesh_lineEdit.setText(bsTransTgtMesh.name())
    else:
        bsTransTgtMesh = None
        bsTransTgtMesh_lineEdit.setText('None')

def bsTransDo():
    bsTransSrcMesh = None
    bsTransTgtMesh = None
    bsNode = None
    if pm.ls(bsTransSrcMesh_lineEdit.getText()):
        bsTransSrcMesh = pm.ls(bsTransSrcMesh_lineEdit.getText())[0]
        if pm.ls(bsTransSrcBs_List.getValue(), type='blendShape'):
            bsLst = pm.listHistory(bsTransSrcMesh, type='blendShape')
            if pm.ls(bsTransSrcBs_List.getValue(), type='blendShape')[0] in bsLst:
                bsNode = pm.ls(bsTransSrcBs_List.getValue(), type='blendShape')[0]
    if pm.ls(bsTransTgtMesh_lineEdit.getText()):
        bsTransTgtMesh = pm.ls(bsTransTgtMesh_lineEdit.getText())[0]
    if not bsTransSrcMesh:
        raise IOError('Need Assign Source Mesh!')
    if not bsTransTgtMesh:
        raise IOError('Need Assign Target Mesh!')
    if not bsNode:
        raise IOError('Not Valid Blend Shape Node!')
    if bsTransTgtMesh == bsTransSrcMesh:
        raise IOError('Cannot Apply to Self!')
    else:
        if bsTransTargetSkin_radioButton.getSelect() and bsTransTargetSkin_radioButton.getEnable():
            pm.select(bsTransTgtMesh)
            target_meshSkinCluster = getMeshSkinCluster(bsTransTgtMesh)
            if target_meshSkinCluster:
                target_meshSkinBone = target_meshSkinCluster.getInfluence()
                target_meshSkinName = target_meshSkinCluster.name()
                exportVtxWeight2(isOutputFile=False)
        forceDeleteHistory(bsTransTgtMesh)
        pm.select(clear=1)
        pm.select(bsTransTgtMesh, bsTransSrcMesh)
        _wrap_existing = bridge.scene_uuids()
        mel.eval('CreateWrap')
        wrapNode = pm.listHistory(bsTransTgtMesh, type='wrap')[0]
        wrapBaseShape = None
        for item in pm.listHistory(pm.ls(sl=1), type='mesh'):
            if 'BaseShape' in item.name() and bridge.node_uuid(item.getParent()) not in _wrap_existing:
                wrapBaseShape = item.getParent()
        bsCount = bsNode.numWeights()
        bsAttrLst = cmds.aliasAttr(bsNode.name(), query=True)
        tgtBsMeshLst = []
        for i in range(bsCount):
            bsNode.setWeight(i, 0)
        for i in range(bsCount):
            bsId = int(bsAttrLst[i * 2 + 1].split('[')[1][:-1])
            bsNode.setWeight(bsId, 1)
            bsName = bsAttrLst[i * 2]
            if pm.ls(bsName):
                raise ValueError('An unrelated object occupies the blendshape target name: ' + bsName)
            tgtBsMeshLst.append(pm.duplicate(bsTransTgtMesh, name=bsName))
            bsNode.setWeight(bsId, 0)
        forceDeleteHistory(bsTransTgtMesh, isKeepSkin=True)
        pm.select(clear=1)
        for mesh in tgtBsMeshLst:
            pm.select(tgtBsMeshLst, add=1)
        pm.select(bsTransTgtMesh, add=1)
        mel.eval('CreateBlendShape')
        pm.delete(tgtBsMeshLst)
        if wrapBaseShape:
            pm.delete(wrapBaseShape)
        pm.select(clear=1)
    if bsTransSourceSkin_radioButton.getSelect() and bsTransSourceSkin_radioButton.getEnable():
        meshSkinCluster = getMeshSkinCluster(bsTransSrcMesh)
        if meshSkinCluster:
            meshSkinBone = meshSkinCluster.getInfluence()
            bsTransTgtMeshSkinCluster = pm.skinCluster(bsTransTgtMesh, meshSkinBone, name=bsTransTgtMesh + '_SkinCluster', maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
            pm.copySkinWeights(sourceSkin=meshSkinCluster, destinationSkin=bsTransTgtMeshSkinCluster, noMirror=True, influenceAssociation='name')
            pm.skinPercent(bsTransTgtMeshSkinCluster, bsTransTgtMesh, pruneWeights=0.04, normalize=True)
    if bsTransTargetSkin_radioButton.getSelect() and bsTransTargetSkin_radioButton.getEnable():
        bsTransTgtMeshSkinCluster = pm.skinCluster(bsTransTgtMesh, target_meshSkinBone, name=target_meshSkinName, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
        pm.select(bsTransTgtMesh, replace=True)
        importVtxWeight2(isFromFile=False)

def removeBoneKwd(boneStr, kwd):
    boneTokenLst = boneStr.split(kwd)
    boneStr = ''
    for boneToken in boneTokenLst:
        if boneToken and boneToken != '_':
            boneStr += boneToken
            if boneToken != boneTokenLst[-1]:
                boneStr += '_'
    return boneStr

def boneLabelDo():
    lKwd = boneLabelLeftKey_lineEdit.getText()
    rKwd = boneLabelRightKey_lineEdit.getText()
    try:
        prefixCount = int(boneLabelPrefixCount_lineEdit.getText())
    except:
        prefixCount = 1
        boneLabelPrefixCount_lineEdit.setText('1')
    boneLst = pm.ls(sl=1, type='joint')
    for bone in boneLst:
        sideNum = 0
        if lKwd in bone.name():
            sideNum = 1
        if rKwd in bone.name():
            sideNum = 2
        pm.setAttr(bone.name() + '.side', sideNum)
        pm.setAttr(bone.name() + '.type', 18)
        boneTokenLst = bone.name().split('_')
        boneStr = ''
        for boneToken in boneTokenLst[prefixCount:]:
            boneStr += boneToken
            if boneToken != boneTokenLst[-1]:
                boneStr += '_'
        if sideNum == 1:
            boneStr = removeBoneKwd(boneStr, lKwd)
        if sideNum == 2:
            boneStr = removeBoneKwd(boneStr, rKwd)
        pm.setAttr(bone.name() + '.otherType', boneStr)

def meshDelNonSkinHistory2():
    global vertexInfo
    meshLst = []
    newMeshLst = []
    objLst = pm.ls(sl=1, type='transform')
    for obj in objLst:
        if pm.nodeType(obj.getShape()) == 'mesh':
            meshLst.append(obj)
    for mesh in meshLst:
        vertexInfo = None
        pm.select(mesh, replace=True)
        meshSkinClusterExists = False
        meshSkinCluster = getMeshSkinCluster(mesh)
        if meshSkinCluster:
            meshSkinClusterExists = True
            meshSkinBone = meshSkinCluster.getInfluence()
            meshSkinName = meshSkinCluster.name()
            meshName = mesh.name()
            pm.rename(mesh, mesh.name() + '_NonSkinHistory')
            newMesh = pm.duplicate(mesh, name=meshName)
            newMeshLst.append(newMesh)
            newMeshSkinCluster = pm.skinCluster(newMesh, meshSkinBone, name=meshSkinName, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
            pm.copySkinWeights(sourceSkin=meshSkinCluster, destinationSkin=newMeshSkinCluster, surfaceAssociation='closestPoint', influenceAssociation=influenceAssociationSetting, normalize=True, noMirror=True)
    for mesh in meshLst:
        pm.delete(mesh)

def meshDelNonSkinHistory():
    global vertexInfo
    meshLst = []
    objLst = pm.ls(sl=1, type='transform')
    for obj in objLst:
        if pm.nodeType(obj.getShape()) == 'mesh':
            meshLst.append(obj)
    for mesh in meshLst:
        vertexInfo = None
        pm.select(mesh, replace=True)
        meshSkinClusterExists = False
        meshSkinCluster = getMeshSkinCluster(mesh)
        if meshSkinCluster:
            meshSkinClusterExists = True
            meshSkinBone = meshSkinCluster.getInfluence()
            meshSkinName = meshSkinCluster.name()
            exportVtxWeight(isOutputFile=False)
        pm.select(mesh, replace=True)
        cmds.DeleteHistory()
        if meshSkinClusterExists:
            newMeshSkinCluster = pm.skinCluster(mesh, meshSkinBone, name=meshSkinName, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
            pm.select(mesh, replace=True)
            importVtxWeight(isFromFile=False)

def createWeightMapProxyMesh(mesh, boneLst=[]):
    meshShape = mesh.getShape()
    meshSkinCluster = getMeshSkinCluster(mesh)
    proxyMeshName = mesh.name() + '_colorProxy'
    if pm.ls(mesh.name() + '_WeightMap'):
        groupNode = pm.ls(mesh.name() + '_WeightMap')[0]
    else:
        groupNode = pm.createNode('transform', n=mesh.name() + '_WeightMap')
    meshBox = pm.exactWorldBoundingBox(mesh)
    meshSizeX = meshBox[3] - meshBox[0]
    meshSizeY = meshBox[4] - meshBox[1]
    meshSizeZ = meshBox[5] - meshBox[2]
    currentTime = pm.getCurrentTime()
    pm.select(mesh)
    pm.runtime.GoToBindPose(mesh)
    pm.duplicate(mesh, name=proxyMeshName)
    bone = pm.skinCluster(meshSkinCluster, query=True, inf=True)[0]
    inputList = []
    inputList.append(bone)
    inputList.append(mesh)
    inputList.append(proxyMeshName)
    bindSkinPlus(inputList)
    proxyMeshShape = pm.ls(proxyMeshName)[0].getShape()
    mel.eval('setWireframeOnShadedOption false modelPanel4')
    pm.setCurrentTime(currentTime)
    proxyMesh = pm.ls(proxyMeshName)[0]
    proxyMeshSkinCluster = getMeshSkinCluster(proxyMesh)
    proxyMeshMetal = pm.shadingNode('lambert', asShader=True, name='weightMeshMetal')
    proxyMeshShader = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='proxyMeshShader')
    proxyMeshMetal.outColor >> proxyMeshShader.surfaceShader
    pm.sets(proxyMeshShader, forceElement=proxyMesh)
    try:
        pm.polyColorPerVertex(proxyMesh, remove=True)
    except:
        pass
    if not boneLst:
        boneLst = proxyMeshSkinCluster.getInfluence()
    setProgressBar(main_progressBar, 0)
    step = 0.0
    allStep = float(len(boneLst))
    offsetStep = 0
    offsetStep_Z = 2
    offsetStep_Z2 = 3
    for boneObj in boneLst:
        infVertexCount = len(proxyMeshSkinCluster.getPointsAffectedByInfluence(boneObj)[0])
        if infVertexCount > 0:
            printTextLable(main_processLable, 'Painting bone weight: ' + boneObj.name())
            paintWeightedVertex(proxyMeshSkinCluster, boneObj, proxyMesh)
            weightMeshName = mesh.name() + '_' + boneObj.name() + '_WeightMap'
            pm.duplicate(proxyMesh, name=weightMeshName)
            weightMesh = pm.ls(weightMeshName)[0]
            unlockTransform(weightMesh)
            pm.refresh()
            weightMesh.setParent(groupNode)
            offsetStep += 1
            offset_X = (2 * offsetStep - (offsetStep_Z2 - 2) * offsetStep_Z2) * meshSizeX
            offset_Y = 1 * offsetStep_Z2 * meshSizeY
            offset_Z = -2 * offsetStep_Z2 * meshSizeZ
            pm.setAttr(weightMesh.name() + '.translateX', offset_X)
            pm.setAttr(weightMesh.name() + '.translateY', offset_Y)
            pm.setAttr(weightMesh.name() + '.translateZ', offset_Z)
            if offsetStep % offsetStep_Z == 0:
                offsetStep_Z += offsetStep_Z2
                offsetStep_Z2 += 1
            meshPiv = pm.objectCenter(weightMesh)
            meshLabel = pm.annotate(weightMesh, tx=boneObj.name(), p=(meshPiv[0], meshSizeY / 2 * 1.2 + meshPiv[1], meshPiv[2]))
            _label_parent = meshLabel.getParent()
            meshLabel.setParent(weightMesh)
            if _label_parent and (not _label_parent.getChildren()):
                pm.delete(_label_parent)
            pm.setAttr(meshLabel.name() + '.displayArrow', 0)
            pm.setAttr(meshLabel.name() + '.overrideEnabled', 1)
            pm.setAttr(meshLabel.name() + '.overrideDisplayType', 2)
        step += 100.0 / allStep
        runProgressBar(main_progressBar, step)
    pm.delete(proxyMesh)
    setProgressBar(main_progressBar, 100)
    pass
    pm.select(clear=1)

def buildWeightMap():
    mesh = None
    boneObjLst = []
    for obj in pm.ls(sl=1, type='transform'):
        if pm.nodeType(obj.getShape()) == 'mesh':
            mesh = obj
        if pm.nodeType(obj) == 'joint':
            boneObjLst.append(obj)
    meshSkinCluster = getMeshSkinCluster(mesh)
    if meshSkinCluster:
        boneLst = []
        for bone in meshSkinCluster.getInfluence():
            if bone in boneObjLst:
                boneLst.append(bone)
        createWeightMapProxyMesh(mesh, boneLst)
    else:
        print('Not a Skined Mesh')
currentSelection = []

def selectionChanged():
    updateWeightUI()
    if currentSelection:
        renameUpdatePreview()

def printPerformanceTime(lable=None):
    global previousTimeStamp
    currentTimeStamp = pm.timerX()
    if previousTimeStamp:
        print((lable, currentTimeStamp - previousTimeStamp))
    previousTimeStamp = currentTimeStamp

def weightToolOn():
    return updateWeightUI()

def loopSelection():
    return pm.runtime.SelectEdgeLoopSp()

def testCmd(ignoreInputs=False):
    return bridge.update_status()

def build_ui(language=''):
    global boneLabelLeftKey_lineEdit, boneLabelPrefixCount_lineEdit, boneLabelRightKey_lineEdit, boneTransformDict, bsTransCopySkin_checkBox, bsTransSourceSkin_radioButton, bsTransSrcBs_List, bsTransSrcMesh_lineEdit, bsTransTargetSkin_radioButton, bsTransTgtMesh_lineEdit, centralwidget, checkInflunce_cutMinor_checkBox, currentSelection, deformerActive_radioButton, deformerEnd_lineEdit, deformerStart_lineEdit, donateBitcoin_lineEdit, donate_tab, exprotVertexWeightData, goreSourceMesh, goreSourceMeshSkinCluster, goreTargetMeshList, gore_tab, infVerts_makeSet_checkBox, language_button, language_list, lodBatch_CheckBox, lodBoneDict, lodDeleteBase_CheckBox, lodDeleteBone_CheckBox, lodDeleteShader_CheckBox, lodSourceBone_ListBox, lodSourceMesh, lodSourceMeshShape, lodSourceMeshSkinCluster, lodSourceMesh_lineEdit, lodTargetBone_ListBox, lodTargetMesh, lodTargetMeshShape, lodTargetMeshSkinCluster, lodTargetMesh_lineEdit, lod_tab, main_lang_id, main_lineEdit, main_processLable, main_progressBar, miscUpdate_button, misc_tab, renameAll_radioButton, renameCase_CheckBox, renameHierarchy_radioButton, renameLetter_checkBox, renameOrderLetter_lineEdit, renameOrderStart_lineEdit, renameOrderStep_lineEdit, renamePerfix_lineEdit, renamePrefix_radioButton, renamePreview_lineEdit, renameReplace_lineEdit, renameSearch_lineEdit, renameSelected_radioButton, renameStart_label, renameStart_lineEdit, renameStart_radioButton, renameSuffix_radioButton, renameTemplate_lineEdit, renameUpcase_checkBox, rename_tab, sVertexCount_label, scaleJoint_lineEdit, skinMagic_MainUI, swapMerge_button, swapMerge_checkBox, warp_FineCopy_checkBox, warp_HoldVtxs_checkBox, weight_boneListBox, weight_checkInflunceTexEdit, weight_mirrorCheckBox, weight_mirrorPartCheckBox, weight_mirrorXRadioButton, weight_mirrorYRadioButton, weight_mirrorZRadioButton, weight_normalizeLabel, weight_onOffCheckBox, weight_paintVertexCheckBox, weight_pruneWeightTextEdit, weight_rangeStepTextEdit, weight_reSkinHoldBone, weight_reSkinLabel, weight_scrollArea, weight_setWeightTextEdit, weight_swapBoneATexEdit, weight_swapBoneBTexEdit, weight_syncBoneCheckBox, weight_tab, weight_valueListBox, weight_vertexSizeSlider, weight_vertsNumLabel, weight_weightOnCheckBox
    skinMagic_MainUI = bridge.load_ui(language)
    centralwidget = skinMagic_MainUI + '|centralwidget'
    weight_tab = centralwidget + '|main_tab|weight_tab'
    weight_scrollArea = weight_tab + '|weight_groupBox|weight_scrollArea|weight_scrollAreaWidgetContents'
    lod_tab = centralwidget + '|main_tab|Lod_tab'
    gore_tab = centralwidget + '|main_tab|gore_tab'
    rename_tab = centralwidget + '|main_tab|rename_tab'
    misc_tab = centralwidget + '|main_tab|misc_tab'
    donate_tab = centralwidget + '|main_tab|donate_tab'
    main_progressBar = centralwidget + '|main_progressBar'
    main_processLable = centralwidget + '|main_processLable'
    main_lineEdit = centralwidget + '|main_textEdit'
    main_lang_id = pm.text(centralwidget + '|main_lang_id', edit=True)
    language_button = pm.button(centralwidget + '|language_button', edit=True)
    language_list = pm.textScrollList(centralwidget + '|language_list', edit=True)
    weight_normalizeLabel = pm.text(weight_scrollArea + '|Normalize_label', edit=True)
    weight_onOffCheckBox = pm.checkBox(weight_tab + '|weightOn_checkBox', edit=True)
    weight_setWeightTextEdit = pm.textField(weight_tab + '|weight_groupBox|setWeight_lineEdit', edit=True)
    weight_rangeStepTextEdit = pm.textField(weight_tab + '|weight_groupBox|weightRange_groupBox|rangeStep_lineEdit', edit=True)
    weight_vertsNumLabel = pm.text(weight_tab + '|weight_groupBox|vertsNum_label', edit=True)
    weight_boneListBox = pm.textScrollList(weight_tab + '|weight_groupBox|bone_listBox', edit=True)
    weight_valueListBox = pm.textScrollList(weight_tab + '|weight_groupBox|value_listBox', edit=True)
    weight_pruneWeightTextEdit = pm.textField(weight_scrollArea + '|pruneWeight_groupBox|pruneWeight_lineEdit', edit=True)
    weight_mirrorXRadioButton = pm.radioButton(weight_scrollArea + '|mirror_groupBox|mirrorX_radioButton', edit=True)
    weight_mirrorYRadioButton = pm.radioButton(weight_scrollArea + '|mirror_groupBox|mirrorY_radioButton', edit=True)
    weight_mirrorZRadioButton = pm.radioButton(weight_scrollArea + '|mirror_groupBox|mirrorZ_radioButton', edit=True)
    weight_mirrorCheckBox = pm.checkBox(weight_scrollArea + '|mirror_groupBox|mirror_checkBox', edit=True)
    weight_mirrorPartCheckBox = pm.checkBox(weight_scrollArea + '|mirror_groupBox|mirrorPart_checkBox', edit=True)
    weight_weightOnCheckBox = pm.checkBox(weight_tab + '|weightOn_checkBox', edit=True)
    weight_paintVertexCheckBox = pm.checkBox(weight_tab + '|weight_groupBox|paintVertex_checkBox', edit=True)
    weight_syncBoneCheckBox = pm.checkBox(weight_tab + '|weight_groupBox|syncBone_checkBox', edit=True)
    weight_vertexSizeSlider = pm.intSlider(weight_scrollArea + '|size_groupBox|weightVertexSize_Slider', edit=True)
    weight_reSkinLabel = pm.text(weight_scrollArea + '|reSkin_groupBox|reSkin_label', edit=True)
    weight_reSkinHoldBone = pm.checkBox(weight_scrollArea + '|reSkin_groupBox|reSkinHoldBone_checkBox', edit=True)
    weight_setWeightTextEdit.setText('0.35')
    weight_rangeStepTextEdit.setText('1')
    weight_vertsNumLabel.setLabel('0')
    weight_pruneWeightTextEdit.setText('0.04')
    weight_mirrorCheckBox.setLabel('+ X to - X')
    weight_swapBoneATexEdit = pm.textField(weight_scrollArea + '|swap_group|swapBoneA_lineEdit', edit=True)
    weight_swapBoneBTexEdit = pm.textField(weight_scrollArea + '|swap_group|swapBoneB_lineEdit', edit=True)
    swapMerge_checkBox = pm.checkBox(weight_scrollArea + '|swap_group|swapMerge_checkBox', edit=True)
    swapMerge_button = pm.button(weight_scrollArea + '|swap_group|swapMerge_button', edit=True)
    swapMerge_button.setVisible(False)
    weight_checkInflunceTexEdit = pm.textField(weight_scrollArea + '|checkInflunce_groupBox|checkInflunce_lineEdit', edit=True)
    checkInflunce_cutMinor_checkBox = pm.checkBox(weight_scrollArea + '|checkInflunce_groupBox|checkInflunce_cutMinor_checkBox', edit=True)
    infVerts_makeSet_checkBox = pm.checkBox(weight_scrollArea + '|InfVerts_groupBox|InfVerts_makeSet_checkBox', edit=True)
    sVertexCount_label = pm.text(weight_scrollArea + '|warp_groupBox|sVertexCount_label', edit=True)
    warp_HoldVtxs_checkBox = pm.checkBox(weight_scrollArea + '|warp_groupBox|warp_HoldVtxs_checkBox', edit=True)
    warp_FineCopy_checkBox = pm.checkBox(weight_scrollArea + '|warp_groupBox|warp_FineCopy_checkBox', edit=True)
    lodSourceMesh_lineEdit = pm.textField(lod_tab + '|lodMesh_groupBox|lodSource_lineEdit', edit=True)
    lodTargetMesh_lineEdit = pm.textField(lod_tab + '|lodMesh_groupBox|lodTarget_lineEdit', edit=True)
    lodSourceBone_ListBox = pm.textScrollList(lod_tab + '|lodBone_groupBox|lodSourceBone_listBox', edit=True)
    lodTargetBone_ListBox = pm.textScrollList(lod_tab + '|lodBone_groupBox|lodTargetBone_listBox', edit=True)
    lodDeleteBase_CheckBox = pm.checkBox(lod_tab + '|lodDeleteBase_checkBox', edit=True)
    lodDeleteShader_CheckBox = pm.checkBox(lod_tab + '|lodDeleteShader_checkBox', edit=True)
    lodDeleteBone_CheckBox = pm.checkBox(lod_tab + '|lodDeleteBone_checkBox', edit=True)
    lodBatch_CheckBox = pm.checkBox(lod_tab + '|lodBatch_checkBox', edit=True)
    renamePreview_lineEdit = pm.textField(rename_tab + '|renamePreview_groupBox|renamePreview_lineEdit', edit=True)
    renameSearch_lineEdit = pm.textField(rename_tab + '|renameReplace_groupBox|renameSearch_lineEdit', edit=True)
    renameReplace_lineEdit = pm.textField(rename_tab + '|renameReplace_groupBox|renameReplace_lineEdit', edit=True)
    renameCase_CheckBox = pm.checkBox(rename_tab + '|renameReplace_groupBox|renameCase_checkBox', edit=True)
    renamePerfix_lineEdit = pm.textField(rename_tab + '|renameAdd_groupBox|renamePerfix_lineEdit', edit=True)
    renamePrefix_radioButton = pm.radioButton(rename_tab + '|renameAdd_groupBox|renamePrefix_radioButton', edit=True)
    renameSuffix_radioButton = pm.radioButton(rename_tab + '|renameAdd_groupBox|renameSuffix_radioButton', edit=True)
    renameStart_radioButton = pm.radioButton(rename_tab + '|renameAdd_groupBox|renameStart_radioButton', edit=True)
    renameStart_lineEdit = pm.textField(rename_tab + '|renameAdd_groupBox|renameStart_lineEdit', edit=True)
    renameStart_label = pm.text(rename_tab + '|renameAdd_groupBox|renameStart_label', edit=True)
    renameTemplate_lineEdit = pm.textField(rename_tab + '|renameTemplate_groupBox|renameTemplate_lineEdit', edit=True)
    renameOrderLetter_lineEdit = pm.textField(rename_tab + '|renameTemplate_groupBox|renameOrderLetter_lineEdit', edit=True)
    renameUpcase_checkBox = pm.checkBox(rename_tab + '|renameTemplate_groupBox|renameUpcase_checkBox', edit=True)
    renameOrderStart_lineEdit = pm.textField(rename_tab + '|renameTemplate_groupBox|renameOrderNumber_groupBox|renameOrderStart_lineEdit', edit=True)
    renameOrderStep_lineEdit = pm.textField(rename_tab + '|renameTemplate_groupBox|renameOrderNumber_groupBox|renameOrderStep_lineEdit', edit=True)
    renameLetter_checkBox = pm.checkBox(rename_tab + '|renameTemplate_groupBox|renameLetter_checkBox', edit=True)
    renameHierarchy_radioButton = pm.radioButton(rename_tab + '|renameHierarchy_radioButton', edit=True)
    renameSelected_radioButton = pm.radioButton(rename_tab + '|renameSelected_radioButton', edit=True)
    renameAll_radioButton = pm.radioButton(rename_tab + '|renameAll_radioButton', edit=True)
    deformerActive_radioButton = pm.radioButton(misc_tab + '|deformer_groupBox|deformerActive_radioButton', edit=True)
    deformerStart_lineEdit = pm.textField(misc_tab + '|deformer_groupBox|deformerStart_lineEdit', edit=True)
    deformerEnd_lineEdit = pm.textField(misc_tab + '|deformer_groupBox|deformerEnd_lineEdit', edit=True)
    scaleJoint_lineEdit = pm.textField(misc_tab + '|scale_groupBox|scale_lineEdit', edit=True)
    bsTransSrcBs_List = pm.optionMenu(misc_tab + '|bsTrans_group|bsTransSrcBs_List', edit=True)
    bsTransSrcMesh_lineEdit = pm.textField(misc_tab + '|bsTrans_group|bsTransSrcMesh_lineEdit', edit=True)
    bsTransTgtMesh_lineEdit = pm.textField(misc_tab + '|bsTrans_group|bsTransTgtMesh_lineEdit', edit=True)
    bsTransCopySkin_checkBox = pm.checkBox(misc_tab + '|bsTrans_group|bsTransCopySkin_checkBox', edit=True)
    bsTransSourceSkin_radioButton = pm.radioButton(misc_tab + '|bsTrans_group|bsTransSkinWeight_groupBox|bsTransSourceSkin_radioButton', edit=True)
    bsTransTargetSkin_radioButton = pm.radioButton(misc_tab + '|bsTrans_group|bsTransSkinWeight_groupBox|bsTransTargetSkin_radioButton', edit=True)
    boneLabelPrefixCount_lineEdit = pm.textField(misc_tab + '|boneLabel_group|boneLabelPrefixCount_lineEdit', edit=True)
    boneLabelLeftKey_lineEdit = pm.textField(misc_tab + '|boneLabel_group|boneLabelLeftKey_lineEdit', edit=True)
    boneLabelRightKey_lineEdit = pm.textField(misc_tab + '|boneLabel_group|boneLabelRightKey_lineEdit', edit=True)
    donateBitcoin_lineEdit = pm.textField(donate_tab + '|eng_groupBox|donateBitcoin_lineEdit', edit=True)
    donateBitcoin_lineEdit.setText(bitcoin)
    miscUpdate_button = pm.button(centralwidget + '|miscUpdate_pushButton', edit=True)
    showSpam()
    runProgressBar(main_progressBar, 0)
    exprotVertexWeightData = None
    lodSourceMesh = None
    lodSourceMeshShape = None
    lodSourceMeshSkinCluster = None
    lodTargetMesh = None
    lodTargetMeshShape = None
    lodTargetMeshSkinCluster = None
    lodBoneDict = {}
    goreSourceMesh = None
    goreSourceMeshSkinCluster = None
    goreTargetMeshList = []
    boneTransformDict = {}
    currentSelection = []
    renameOrderLetter_lineEdit.setVisible(0)
    renameUpcase_checkBox.setVisible(0)
    language_list.setVisible(False)
    bridge.bind_controls(skinMagic_MainUI, language)
    return skinMagic_MainUI
