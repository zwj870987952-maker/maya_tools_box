from .proxy import mc
from . import runtime as _r
scriptVersion = 'v09'
scriptName = 'mtbLockToWorld'
'\nCopyright (c) <2020> <JesseOngPho>\njesseongpho@hotmail.com\n\nDESCRIPTION : \nLock 1 or multiple objects to the world. Really useful to fix feet sliding. \n\nFEATURES:\n- Snap the selected controller to the world for the selected amount of frames \n- Work with multiple selection \n- Work with selected attributes on the channel box (Translation and Rotation only)\n- Work on controllers that have frozen transformation\n- Work on maya 2016,2018,2020, 2022 both Linux and Windows (Did not try other version but it should work)\n\nUPDATE \n2021/06/22: Made the script compatible with maya 2022\n\nHOW TO USE : \n1) Get on the frame where the controller should start to be snapped\n2) Click on the Start button\n3) Get to the frame where the controller should stop to be snapped \n4) Click on the End button\n5) Select the controller(s)\n6) Click on Lock to World button\n\nINSTALLATION:\nTo install, drag and drop the install.mel file onto the maya viewport\n'

def checkEmptySelection(myCtrlList):
    if not myCtrlList:
        raise ValueError('需要控制器')

def hasBeenFrozen(myCtl):
    hasBeenFrozen = True
    if mc.getAttr(myCtl + '.rotatePivot') == [(0, 0, 0)]:
        hasBeenFrozen = False
    return hasBeenFrozen

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

def getSelectedChannelBoxAttributes():
    channels = []
    selectedChannelBoxAttr = [] + (mc.channelBox('mainChannelBox', selectedMainAttributes=True, q=True) or [])
    return selectedChannelBoxAttr

def getSelectedAttrList(selectedCBAttr):
    selectedTranslation = []
    selectedRotation = []
    if selectedCBAttr:
        for i in selectedCBAttr:
            if i[0] == 't' and len(i) == 2:
                selectedTranslation.append(i[1].upper())
            elif i[0] == 'r' and len(i) == 2:
                selectedRotation.append(i[1].upper())
            else:
                mc.confirmDialog(title='Selected Attribute Error', message='The script only supports translation and rotation attributes. Please select the good attributes and try again', button=['ok'], defaultButton='ok')
                mc.error('Sorry, the script only support translation and rotation attributes.')
    else:
        selectedTranslation = ['X', 'Y', 'Z']
        selectedRotation = ['X', 'Y', 'Z']
    return (selectedTranslation, selectedRotation)

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

def getWorldMatrixStartPosition(myCtl, time):
    return _r.world_matrix(myCtl, time)

def setKeysToCtrl(selectedAxis, ctrl, manip, output, timeT):
    _r.require_active()
    for i in range(0, len(selectedAxis)):
        mc.setKeyframe(ctrl + manip + selectedAxis[i], v=mc.getAttr(output[i]), time=timeT)

def snapCtlFromMatrixList(ctlList, matrixList, min, max, selectedCBAttr):
    _r.require_active()
    selectedTranslation, selectedRotation = getSelectedAttrList(selectedCBAttr)
    multMatrixGaea, decomposeMatrixGaea = createMultDecompeCombo()
    quatToEulerGaea = createQuatToEuler(decomposeMatrixGaea)
    plusMinusOdin = createPlusMinusAverage(decomposeMatrixGaea)
    try:
        for ctlNumber in range(0, len(ctlList)):
            mc.connectAttr(ctlList[ctlNumber] + '.rotatePivot', plusMinusOdin + '.input3D[1]')
            for timeT in range(min, max + 1):
                mc.setAttr(multMatrixGaea + '.matrixIn[0]', matrixList[ctlNumber], type='matrix')
                mc.setAttr(multMatrixGaea + '.matrixIn[1]', mc.getAttr(ctlList[ctlNumber] + '.parentInverseMatrix[0]', time=timeT), type='matrix')
                mc.setAttr(quatToEulerGaea + '.inputRotateOrder', mc.getAttr(ctlList[ctlNumber] + '.rotateOrder', time=timeT))
                if hasBeenFrozen(ctlList[ctlNumber]):
                    selectedTranslationSmall = [x.lower() for x in selectedTranslation]
                    trOut = getOutput(plusMinusOdin, selectedTranslationSmall)
                else:
                    trOut = getOutput(decomposeMatrixGaea, selectedTranslation)
                roOut = getOutput(quatToEulerGaea, selectedRotation, 'Rotate')
                setKeysToCtrl(selectedTranslation, ctlList[ctlNumber], '.translate', trOut, timeT)
                setKeysToCtrl(selectedRotation, ctlList[ctlNumber], '.rotate', roOut, timeT)
            mc.disconnectAttr(ctlList[ctlNumber] + '.rotatePivot', plusMinusOdin + '.input3D[1]')
    except:
        raise
    mc.delete(multMatrixGaea, decomposeMatrixGaea, quatToEulerGaea, plusMinusOdin)
    mc.warning('Success : %s object(s) was lockToWorld' % str(len(ctlList)))

@_r.lock_bridge
def lockToWorld(min, max):
    mySelection = mc.ls(sl=True)
    checkEmptySelection(mySelection)
    matrixList = []
    for ctrl in mySelection:
        matrixList.append(getWorldMatrixStartPosition(ctrl, min))
    attributeToKeyList = getSelectedChannelBoxAttributes()
    snapCtlFromMatrixList(mySelection, matrixList, int(min), int(max), attributeToKeyList)
    mc.select(mySelection)

class MyLockWorldWindowClass(object):

    def __init__(self):
        self.window = scriptName + '_' + scriptVersion
        self.title = scriptName
        self.size = (180, 100)
        self.minValue = mc.playbackOptions(q=1, min=1)
        self.maxValue = mc.playbackOptions(q=1, max=1)
        self.startString = 'Start \n'
        self.endString = 'End \n'
        self.buttonHeight = 50
        self.buttonWidth = 180
        self.buttonSmallWidth = 90
        self.backgroundColor = [0.8, 0.6, 0.1]

    def create(self):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True)
        self.window = mc.window(self.window, title=self.title, widthHeight=self.size, sizeable=False)
        myMasterLayout = mc.columnLayout()
        myRowLayout = mc.rowColumnLayout(numberOfColumns=2)
        startButton = mc.button(label=self.startString + str(self.minValue), width=self.buttonSmallWidth, height=self.buttonHeight, command=lambda x: self.updateStartButton(startButton))
        endButton = mc.button(label=self.endString + str(self.maxValue), width=self.buttonSmallWidth, height=self.buttonHeight, command=lambda x: self.updateEndButton(endButton))
        mc.setParent(myMasterLayout)
        mySecondLayout = mc.columnLayout()
        mc.button(label='Lock to World', command=lambda x: lockToWorld(self.minValue, self.maxValue), width=self.buttonWidth, height=self.buttonHeight, backgroundColor=self.backgroundColor)
        mc.showWindow()

    def updateStartButton(self, startButton):
        self.minValue = mc.currentTime(q=True)
        mc.button(startButton, e=True, label=self.startString + str(self.minValue))

    def updateEndButton(self, endButton):
        self.maxValue = mc.currentTime(q=True)
        mc.button(endButton, e=True, label=self.endString + str(self.maxValue))

def main():
    lockWorldWindow = MyLockWorldWindowClass()
    lockWorldWindow.create()
