from .proxy import mc
from . import runtime as _r
scriptVersion = 'v09'
scriptName = 'mtbJopRetargetAnimation'
'\nCopyright (c) <2025> <JesseOngPho>\njesseongpho@hotmail.com\n\nDESCRIPTION : \nSave and load the world space location of selected controllers. Really useful if you want to change the position of your character easily, change space, change rotate order without loosing your animation.\n\nFEATURES:\n- Work on multiple selection\n- Work on the current timeline\n- Has the option to bake (= Key every frames) to get maximum accuracy\n- Work on controllers that have frozen transformation\n- Work on maya 2016,2018,2020, 2022 both Linux and Windows (Did not try other version but it should work)\n\n\nUPDATE \n2021/06/22: Made the script compatible with maya 2022\n\n\nHOW TO USE : \n1) Choose to check the Bake check box or not  \n2) Select controllers to save \n3) Click on the save button \n4) Do the wanted modification\n5) Click on Retarget Animation  \n\n\n\nINSTALLATION:\nTo install, drag and drop the install.mel file onto the maya viewport.\n'

def checkEmptySelection(myCtrlList):
    if not myCtrlList:
        raise ValueError('需要选择控制器')
    return myCtrlList

def hasBeenFrozen(myCtl):
    hasBeenFrozen = True
    if mc.getAttr(myCtl + '.rotatePivot') == [(0, 0, 0)]:
        hasBeenFrozen = False
    return hasBeenFrozen

def endExistingTimer(timerName):
    timerResult = 'none'
    try:
        timerResult = mc.timer(endTimer=True, name=timerName)
    except:
        pass
    return timerResult

def createMultDecompeCombo():
    _r.require_active()
    multMatrixGaea = mc.createNode('multMatrix')
    decomposeMatrixGaea = mc.createNode('decomposeMatrix')
    mc.connectAttr(multMatrixGaea + '.matrixSum', decomposeMatrixGaea + '.inputMatrix')
    return (multMatrixGaea, decomposeMatrixGaea)

def createQuatToEuler(decomposeMatrixGaea):
    _r.require_active()
    quatToEulerGaea = mc.createNode('quatToEuler')
    mc.connectAttr(decomposeMatrixGaea + '.outputQuat', quatToEulerGaea + '.inputQuat')
    return quatToEulerGaea

def createPlusMinusAverage(decomposeMatrixGaea):
    _r.require_active()
    plusMinusOdin = mc.createNode('plusMinusAverage')
    mc.connectAttr(decomposeMatrixGaea + '.outputTranslate', plusMinusOdin + '.input3D[0]')
    mc.setAttr(plusMinusOdin + '.operation', 2)
    return plusMinusOdin

def getOutput(node, axis, transform='Translate'):
    outputTab = []
    nodeType = mc.nodeType(node)
    if nodeType == 'decomposeMatrix':
        res = node + '.output' + transform
    elif nodeType == 'pointMatrixMult':
        res = node + '.output'
    elif nodeType == 'plusMinusAverage':
        res = node + '.output3D'
    elif nodeType == 'quatToEuler':
        res = node + '.output' + transform
    else:
        mc.error('%s node is not defined in getOutput() function' % node)
        res = 'none'
    for i in range(0, len(axis)):
        outputTab.append(res + axis[i])
    return outputTab

def getWorldMatrix(myCtl, time):
    return _r.world_matrix(myCtl, time)

def getKeyframeTab(myCtl):
    minValue = mc.playbackOptions(q=1, min=1)
    maxValue = mc.playbackOptions(q=1, max=1)
    try:
        keyFrameNumberList = list(set(mc.keyframe(myCtl, time=(minValue, maxValue), query=True, absolute=True, timeChange=True)))
    except:
        mc.confirmDialog(title='Keyframes Error', message='The selected object : %s do not have keys on the current timerange. Please set at lease ONE keyframe.' % myCtl, button=['ok'], defaultButton='ok')
        mc.error('The selected object : %s do not have keys on the current timerange. Please set at lease ONE keyframe.' % myCtl)
    return keyFrameNumberList

def getFullTimeRange():
    minValue = int(mc.playbackOptions(q=1, min=1))
    maxValue = int(mc.playbackOptions(q=1, max=1)) + 1
    return list(range(minValue, maxValue))

def setKeysToCtrl(selectedAxis, ctrl, manip, output, timeT):
    _r.require_active()
    for i in range(0, len(selectedAxis)):
        mc.setKeyframe(ctrl + manip + selectedAxis[i], v=mc.getAttr(output[i]), time=timeT)

@_r.capture_bridge
def saveAnimToList(bake):
    timerName = 'saveAnimToListTimer'
    endExistingTimer(timerName)
    mc.timer(startTimer=True, name='saveAnimToListTimer')
    bakeChecked = mc.checkBox(bake, q=True, value=True)
    myCtlList = mc.ls(sl=True)
    if not myCtlList:
        checkEmptySelection(myCtlList)
    else:
        dicAnimList = []
        for myCtl in myCtlList:
            myDic = {}
            keyTab = []
            if bakeChecked:
                keyTab = getFullTimeRange()
            else:
                keyTab = getKeyframeTab(myCtl)
            for keyframeNumber in keyTab:
                myDic[keyframeNumber] = getWorldMatrix(myCtl, keyframeNumber)
            dicAnimList.append(myDic)
        saveAnimToListSpeed = endExistingTimer(timerName)
        mc.warning('Success : %s object(s) animation saved in %s sec' % (str(len(myCtlList)), saveAnimToListSpeed))
    return (myCtlList, dicAnimList)

@_r.restore_bridge
def snapCtlFromMatrixDic(ctlList, dicList):
    if not dicList:
        mc.confirmDialog(title='No saved animation Error', message='No animation was saved so NO transfer could be done. Please save animation first.', button=['ok'], defaultButton='ok')
        mc.error('No animation was saved so NO transfer could be done. Please save animation first')
    else:
        timerName = 'snapCtlFromMatrixDicTimer'
        endExistingTimer(timerName)
        mc.timer(startTimer=True, name=timerName)
        multMatrixGaea, decomposeMatrixGaea = createMultDecompeCombo()
        quatToEulerGaea = createQuatToEuler(decomposeMatrixGaea)
        plusMinusOdin = createPlusMinusAverage(decomposeMatrixGaea)
        axis = ['X', 'Y', 'Z']
        for ctlNumber in range(0, len(ctlList)):
            mc.connectAttr(ctlList[ctlNumber] + '.rotatePivot', plusMinusOdin + '.input3D[1]')
            for u in dicList[ctlNumber].keys():
                mc.setAttr(multMatrixGaea + '.matrixIn[0]', dicList[ctlNumber][u], type='matrix')
                mc.setAttr(multMatrixGaea + '.matrixIn[1]', mc.getAttr(ctlList[ctlNumber] + '.parentInverseMatrix[0]', time=u), type='matrix')
                mc.setAttr(quatToEulerGaea + '.inputRotateOrder', mc.getAttr(ctlList[ctlNumber] + '.rotateOrder', time=u))
                if hasBeenFrozen(ctlList[ctlNumber]):
                    axisSmall = [x.lower() for x in axis]
                    trOut = getOutput(plusMinusOdin, axisSmall)
                else:
                    trOut = getOutput(decomposeMatrixGaea, axis)
                roOut = getOutput(quatToEulerGaea, axis, 'Rotate')
                setKeysToCtrl(axis, ctlList[ctlNumber], '.translate', trOut, u)
                setKeysToCtrl(axis, ctlList[ctlNumber], '.rotate', roOut, u)
            mc.disconnectAttr(ctlList[ctlNumber] + '.rotatePivot', plusMinusOdin + '.input3D[1]')
        mc.delete(multMatrixGaea, decomposeMatrixGaea, quatToEulerGaea, plusMinusOdin)
        mc.filterCurve(ctlList)
        snapCtlFromMatrixDicSpeed = endExistingTimer(timerName)
        mc.warning('Success : %s object(s) animation retargeted in %s sec' % (str(len(ctlList)), snapCtlFromMatrixDicSpeed))

class MyRetargetAnimWindowClass(object):

    def __init__(self):
        self.window = scriptName + '_' + scriptVersion
        self.title = scriptName
        self.size = (180, 120)
        self.buttonWidth = 180
        self.buttonHeight = 50
        self.backgroundColor = [0.8, 0.6, 0.1]
        self.bakeCheckBox = False
        self.labelCheckBox = '1. Bake Anim'
        self.labelSaveButton = '2. Save Anim'
        self.labelRetargetButton = '3. Retarget Anim'
        self.dicAnimList = []
        self.myCtlList = []

    def create(self):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True)
        self.window = mc.window(self.window, title=self.title, widthHeight=self.size, sizeable=True)
        myMasterLayout = mc.columnLayout(adjustableColumn=True)
        myRowLayout = mc.rowLayout(numberOfColumns=2)
        mc.text(label='', width=40)
        self.bakeCheckBox = mc.checkBox(label=self.labelCheckBox, value=0)
        mc.setParent(myMasterLayout)
        mc.button(label=self.labelSaveButton, width=self.buttonWidth, height=self.buttonHeight, command=lambda x: self.updateDicAndList(self.bakeCheckBox))
        mc.button(label=self.labelRetargetButton, width=self.buttonWidth, height=self.buttonHeight, backgroundColor=self.backgroundColor, command=lambda x: snapCtlFromMatrixDic(self.myCtlList, self.dicAnimList))
        mc.showWindow()

    def updateDicAndList(self, checkBoxValue):
        self.myCtlList, self.dicAnimList = saveAnimToList(checkBoxValue)

def main():
    retargetAnimWindow = MyRetargetAnimWindowClass()
    retargetAnimWindow.create()
