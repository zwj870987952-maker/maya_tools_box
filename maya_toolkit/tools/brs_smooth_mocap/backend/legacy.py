import maya.cmds as cmds
from . import scene as _scene
from .runtime import require_active as _guard
from .ui import feedback as _feedback
_options = {}
locSuffix = '_mtbBRSSmoothSnapLoc'
BRSAnimLocGrp = 'mtbBRSSmoothAnimLoc_Grp'
redirectGuide = 'mtbBRSSmoothRedirectGuide'
version = '1.09'
winID = 'mtbBRSSMOOTH_BACKEND'
winWidth = 200
colorSet = {'bg': (0.2, 0.2, 0.2), 'red': (0.8, 0.4, 0), 'green': (0.7067, 1, 0), 'blue': (0, 0.4, 0.8), 'yellow': (1, 0.8, 0), 'shadow': (0.15, 0.15, 0.15), 'highlight': (0.3, 0.3, 0.3)}

def snap(object, target):
    _guard()
    snapper = cmds.parentConstraint(target, object, weight=1.0)
    cmds.delete(snapper)

def snapPoint(object, target):
    _guard()
    pointCon = cmds.pointConstraint(target, object, mo=False, weight=1.0)
    cmds.delete(pointCon)

def getAllKeyframe(objectName):
    _guard()
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    keyframeList = []
    attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    if type(objectName) == list:
        objectName = objectName[0]
    for attr in attrList:
        keyList = cmds.keyframe(objectName + '.' + attr, q=True, timeChange=True)
        if keyList != None:
            for k in keyList:
                if not k in keyframeList:
                    keyframeList.append(k)
    keyframeList = sorted(keyframeList)
    return keyframeList

def bakeKey(objectList, keyframeList, inTimeline=False):
    _guard()
    at = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    if inTimeline:
        minKeyframe = round(cmds.playbackOptions(q=True, minTime=True))
        maxKeyframe = round(cmds.playbackOptions(q=True, maxTime=True))
    else:
        minKeyframe = round(min(keyframeList))
        maxKeyframe = round(max(keyframeList))
    cmds.refresh(suspend=True)
    cmds.bakeResults(objectList, sampleBy=1, disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False, t=(minKeyframe, maxKeyframe), at=at)
    cmds.filterCurve(objectList)
    cmds.refresh(suspend=False)
    if cmds.ogs(q=True, pause=True) == True:
        cmds.ogs(pause=True)

def keepKeyframe(objectList, keyframeList):
    _guard()
    newKeyframeList = []
    for k in keyframeList:
        k = round(k, 0)
        newKeyframeList.append(k)
    for k in range(int(min(newKeyframeList)), int(max(newKeyframeList))):
        if not float(k) in newKeyframeList:
            cmds.cutKey(objectList, time=(float(k), float(k)))

def setKeyBreakdown(objectList, breakdownList=[]):
    _guard()
    if breakdownList != None:
        for f in breakdownList:
            cmds.keyframe(objectList, e=True, breakdown=True, time=(f,))

def objectToLocatorSnap(toGroup=True, forceConstraint=False):
    _guard()
    curTime = cmds.currentTime(query=True)
    bakeK = _options['bake_all']
    cons = _options['constrain']
    tl = _options['in_timeline']
    tran = _options['translate']
    rot = _options['rotate']
    if forceConstraint:
        cons = forceConstraint
    selected = cmds.ls(sl=True)
    if toGroup:
        createBRSAnimLocGrp(selected)
    gMainProgressBar = None
    _feedback()
    for objName in selected:
        keyframeList = getAllKeyframe(objName)
        breakdownList = cmds.keyframe(objName, q=True, breakdown=True) or []
        if len(keyframeList) > 1:
            statTextUI('get keyframe {} {} - {}'.format(objName, min(keyframeList), max(keyframeList)))
            SnapLoc = getMimicLocator(objName)[0]
            if toGroup:
                SnapLoc = cmds.parent(SnapLoc, BRSAnimLocGrp)[0]
            statTextUI('Bake to {}'.format(SnapLoc))
            bakeKey(SnapLoc, keyframeList, inTimeline=tl)
            if bakeK == False:
                keepKeyframe(SnapLoc, keyframeList)
                setKeyBreakdown(SnapLoc, breakdownList=breakdownList)
            else:
                breakdownList = list(set(cmds.keyframe(SnapLoc, q=True, timeChange=True)) - set(keyframeList)) + list(breakdownList)
                setKeyBreakdown(SnapLoc, breakdownList=breakdownList)
            deleteConstraint(SnapLoc)
            if cons:
                parentConstraint(objName, SnapLoc, translate=tran, rotate=rot)
        _feedback()
    _feedback()
    cmds.currentTime(curTime)
    cmds.select(selected, r=True)
    resetViewport()
    statTextUI('')
    print('Create Anim Locator {}'.format(selected))
    _feedback()
    None
    None

def locatorToObjectSnap(*_):
    _guard()
    curTime = cmds.currentTime(query=True)
    bakeK = _options['bake_all']
    tran = _options['translate']
    rot = _options['rotate']
    at = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    selected = cmds.ls(sl=True)
    gMainProgressBar = None
    _feedback()
    for objName in selected:
        SnapLoc = _scene.locator_for(objName, required=True)
        print(SnapLoc)
        try:
            keyframeList = getAllKeyframe(SnapLoc)
            breakdownList = cmds.keyframe(SnapLoc, q=True, breakdown=True) or []
            cmds.select(SnapLoc)
        except:
            pass
        else:
            cmds.cutKey(objName, cl=True, at=at, time=(min(keyframeList), max(keyframeList)))
            deleteConstraint(objName)
            parentConstraint(objName, SnapLoc, translate=tran, rotate=rot)
            statTextUI('Bake to {}'.format(objName))
            bakeKey(objName, keyframeList)
            if bakeK == False:
                keepKeyframe(objName, keyframeList)
                setKeyBreakdown(objName, breakdownList=breakdownList)
            else:
                breakdownList = list(set(cmds.keyframe(objName, q=True, timeChange=True)) - set(keyframeList)) + list(breakdownList)
                setKeyBreakdown(objName, breakdownList=breakdownList)
            _scene.delete_locator(SnapLoc)
            if cmds.listRelatives(BRSAnimLocGrp, children=True) == None:
                _scene.delete_group_if_empty()
        _feedback()
    cmds.snapKey(selected, timeMultiple=1.0)
    _feedback()
    cmds.currentTime(curTime)
    cmds.select(selected, r=True)
    resetViewport()
    statTextUI('')
    print('Apply Anim Locator {}'.format(selected))
    _feedback()

def applyRedirectGuide(*_):
    _guard()
    attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    try:
        cmds.select([redirectGuide, BRSAnimLocGrp])
    except:
        pass
    else:
        for a in attr:
            cmds.setAttr('{}.{}'.format(BRSAnimLocGrp, a), lock=False)
        selection = _scene.locators()
        cmds.select(selection)
        objectToLocatorSnap(toGroup=False, forceConstraint=True)
        snap(BRSAnimLocGrp, redirectGuide)
        locatorToObjectSnap()
        _scene.delete_guide()
        for a in attr:
            cmds.setAttr('{}.{}'.format(BRSAnimLocGrp, a), lock=True)

def resetViewport(*_):
    _guard()
    return None

def parentConstraint(object, target, translate=True, rotate=True):
    _guard()
    return _scene.constraints(object, target, translate, rotate)

def createBRSAnimLocGrp(snapObj):
    _guard()
    return _scene.ensure_group(snapObj)

def createRedirectGuide(*_):
    _guard()
    return _scene.create_guide()

def getMimicLocator(objectName, locName=None):
    _guard()
    return [_scene.make_locator(objectName, _options['annotation'])]

def deleteConstraint(objectName):
    _guard()
    return _scene.delete_constraints(objectName)

def statTextUI(text):
    return _feedback(text)

def BRSLocTransferUI(*_):
    return build_ui()

def build_ui():
    global statText, ConsChk, AnnoChk, BakeChk, TimelineChk, translateChk, rotateChk
    from . import ui as _bridge
    if cmds.window(winID, exists=True):
        cmds.deleteUI(winID)
    cmds.window(winID, t='BRS Locator Transfer' + ' - ' + version, w=winWidth, sizeable=True, retain=True, bgc=colorSet['bg'])
    cmds.columnLayout(adj=False, w=winWidth)
    cmds.text(l='BRS Locator Transfer' + ' - ' + version, fn='boldLabelFont', h=20, w=winWidth, bgc=colorSet['green'])
    statText = cmds.text(l='', fn='smallPlainLabelFont', h=25, w=winWidth, bgc=colorSet['shadow'])
    cmds.frameLayout(label='Anim Locator', w=winWidth, collapsable=True, collapse=False, bgc=colorSet['shadow'])
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
    ConsChk = cmds.checkBox(label='Constraint', align='center', v=True)
    AnnoChk = cmds.checkBox(label='Annotation', align='center', v=True)
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
    BakeChk = cmds.checkBox(label='Bake Keyframe', align='center')
    TimelineChk = cmds.checkBox(label='In Timeline', align='center')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.frameLayout(label='Align', w=winWidth, collapsable=True, collapse=True, bgc=colorSet['shadow'])
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
    translateChk = cmds.checkBox(label='Position', align='center', v=True)
    rotateChk = cmds.checkBox(label='Rotation', align='center', v=True)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(l='Create Anim Locator', h=25, w=winWidth - 2, c=lambda *_: _bridge.dispatch('create'), bgc=colorSet['highlight'])
    cmds.button(l='Apply Anim Locator', h=25, w=winWidth - 2, c=lambda *_: _bridge.dispatch('apply'), bgc=colorSet['highlight'])
    cmds.setParent('..')
    cmds.frameLayout(label='Redirection', w=winWidth, collapsable=True, collapse=True, bgc=colorSet['shadow'])
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(l='Create Redirection Guide', h=25, w=winWidth - 4, bgc=colorSet['highlight'], c=lambda *_: _bridge.dispatch('create_guide'))
    cmds.button(l='Apply Redirection', h=25, w=winWidth - 4, bgc=colorSet['highlight'], c=lambda *_: _bridge.dispatch('redirect'))
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.text(l='Created by Burasate Uttha', h=20, al='left', fn='smallPlainLabelFont')
    cmds.showWindow(winID)
    cmds.window(winID, e=True, h=100, w=100)
    return winID
