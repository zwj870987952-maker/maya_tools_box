import maya.cmds as mc
scriptVersion = 'v09'
scriptName = 'retargetAnimation'

'''
Copyright (c) <2025> <JesseOngPho>
jesseongpho@hotmail.com

DESCRIPTION : 
Save and load the world space location of selected controllers. Really useful if you want to change the position of your character easily, change space, change rotate order without loosing your animation.

FEATURES:
- Work on multiple selection
- Work on the current timeline
- Has the option to bake (= Key every frames) to get maximum accuracy
- Work on controllers that have frozen transformation
- Work on maya 2016,2018,2020, 2022 both Linux and Windows (Did not try other version but it should work)


UPDATE 
2021/06/22: Made the script compatible with maya 2022


HOW TO USE : 
1) Choose to check the Bake check box or not  
2) Select controllers to save 
3) Click on the save button 
4) Do the wanted modification
5) Click on Retarget Animation  



INSTALLATION:
To install, drag and drop the install.mel file onto the maya viewport.
'''


#Script is using matrix and quaternion nodes so we make sure the plug in is loaded
mc.loadPlugin('matrixNodes.mll',quiet=True)
mc.loadPlugin('quatNodes.mll',quiet=True)

def checkEmptySelection(myCtrlList):
    if not myCtrlList :
        mc.confirmDialog( title='Selection Error', message='The selection is empty. Please select object(s) and try again', button=['ok'], defaultButton='ok')
        mc.error('The selection is empty. Please select an object')
    return mySelec

#Consider that if the controller has frozen transformation, rotatePivot is different from [0,0,0]     
def hasBeenFrozen (myCtl):
    hasBeenFrozen = True
    if mc.getAttr(myCtl+'.rotatePivot') == [(0,0,0)]:
        hasBeenFrozen = False
    return hasBeenFrozen


#Ending timer 
def endExistingTimer(timerName) :
    #print('Ended timer %s' %timerName) 
    timerResult = 'none'
    try :
        timerResult = mc.timer(endTimer=True, name = timerName)
    except:
        pass
    return timerResult
     




#==============NODE CREATION FUNCTIONS==================#

def createMultDecompeCombo ():
    multMatrixGaea = mc.createNode('multMatrix')
    decomposeMatrixGaea = mc.createNode('decomposeMatrix')
    mc.connectAttr(multMatrixGaea+'.matrixSum', decomposeMatrixGaea+'.inputMatrix' )
    return multMatrixGaea, decomposeMatrixGaea

#create a quad Euler node because of 2016 maya bug of decompose matrix node where we Cannot choose rotation order
def createQuatToEuler (decomposeMatrixGaea):
    quatToEulerGaea =  mc.createNode('quatToEuler')	
    mc.connectAttr(decomposeMatrixGaea+'.outputQuat', quatToEulerGaea+'.inputQuat')
    return quatToEulerGaea
    
def createPlusMinusAverage(decomposeMatrixGaea):
    plusMinusOdin = mc.createNode('plusMinusAverage')
    #Connect Input to plus Minus node
    mc.connectAttr(decomposeMatrixGaea+'.outputTranslate', plusMinusOdin+'.input3D[0]')
    #Set plusMinus node to SUBSTRACT operation
    mc.setAttr(plusMinusOdin+'.operation', 2)
    return plusMinusOdin
#==============END CREATION FUNCTIONS==================#

#=================GET FUNCTIONS=================#

#Set The attr VALUE of the Output in a form of a 3 Axis tab. Translate is the default 
def getOutput(node, axis,transform='Translate' ):
    outputTab =[]
    
    nodeType = mc.nodeType(node)
    if nodeType == 'decomposeMatrix':
        res =  node+'.output'+transform  
    elif nodeType =='pointMatrixMult':
        #print ('%s is a pointMatrixMult Node!' %node)
        res = node+'.output'
    elif nodeType == 'plusMinusAverage':
        #print ('%s is a plusMinusAverage!' %node)
        res = node+'.output3D'
    elif nodeType == 'quatToEuler':
        #print ('%s is a quatToEuler!' %node)
        res =  node+'.output'+transform  
    else:
        mc.error( '%s node is not defined in getOutput() function' %node)
        res = 'none'
    for i in range(0, len(axis)):
        outputTab.append(res + axis[i])
    return outputTab

def getWorldMatrix (myCtl, time): 
    matrix=[]
    if hasBeenFrozen(myCtl):
        #print ('The controller %s has been frozen' %myCtl)

        pointMatrixOdin = mc.createNode('pointMatrixMult',name="Odin")
        decompGaea = mc.createNode('decomposeMatrix',name="Gaea")
        compMatrixThor =  mc.createNode('composeMatrix',name="Thor")

        mc.connectAttr(myCtl+'.worldMatrix', pointMatrixOdin+'.inMatrix')
        mc.connectAttr(myCtl+'.rotatePivot', pointMatrixOdin+'.inPoint')
        mc.connectAttr(myCtl+'.worldMatrix', decompGaea+'.inputMatrix')

        #Thor is composed of Gaea rotation and Odin translation
        mc.connectAttr(decompGaea+'.outputRotate', compMatrixThor+'.inputRotate')
        mc.connectAttr(pointMatrixOdin+'.output', compMatrixThor+'.inputTranslate')

        matrix= mc.getAttr(compMatrixThor+'.outputMatrix',t=time)	
        mc.delete(pointMatrixOdin,decompGaea,compMatrixThor)
    else: 
        #print ('The controller %s has NOT been frozen' %myCtl)
        matrix= mc.getAttr(myCtl+'.worldMatrix',t=time)	
    return matrix

def getKeyframeTab(myCtl):
    minValue = mc.playbackOptions(q=1,min=1)
    maxValue = mc.playbackOptions(q=1,max=1)
    
    try: 
        keyFrameNumberList = list(set(mc.keyframe(myCtl, time=( minValue , maxValue ), query=True, absolute=True, timeChange=True)))
    except: 
        mc.confirmDialog( title='Keyframes Error', message='The selected object : %s do not have keys on the current timerange. Please set at lease ONE keyframe.' %myCtl, button=['ok'], defaultButton='ok')
        mc.error('The selected object : %s do not have keys on the current timerange. Please set at lease ONE keyframe.' %myCtl)
    return keyFrameNumberList

def getFullTimeRange():
    minValue = int(mc.playbackOptions(q=1,min=1))
    maxValue = int(mc.playbackOptions(q=1,max=1))+1
    return list(range(minValue, maxValue))

#=================END GET FUNCTIONS=================#

#Function that set the keys on the controller at TimeT
def setKeysToCtrl (selectedAxis, ctrl, manip, output, timeT):
    for i in range(0,len(selectedAxis)): 
        mc.setKeyframe(ctrl+manip+selectedAxis[i], v= mc.getAttr(output[i]), time = timeT )

def saveAnimToList (bake):
    timerName ='saveAnimToListTimer'
    endExistingTimer(timerName)

    #start the timer
    mc.timer(startTimer=True, name = 'saveAnimToListTimer')
    #check box to bake the anim variable
    bakeChecked = mc.checkBox(bake, q=True,value= True, )
    
    myCtlList = mc.ls(sl=True)
    if not myCtlList:
        checkEmptySelection(myCtlList)
    else:
        dicAnimList = []
        
        for myCtl in myCtlList:
            myDic = {}
            keyTab=[]
            
            if bakeChecked:
                #if Bake, the dictionaries of the keys is gona be filled every single frame. World Matrix of the controller is gona be saved every single frame.
                keyTab = getFullTimeRange()
            else:
                keyTab = getKeyframeTab(myCtl)
            
            for keyframeNumber in keyTab:
                myDic[keyframeNumber] = getWorldMatrix(myCtl, keyframeNumber)
            dicAnimList.append(myDic)
        
        saveAnimToListSpeed =  endExistingTimer(timerName)
        mc.warning ('Success : %s object(s) animation saved in %s sec' %(str(len(myCtlList)),saveAnimToListSpeed))
    return myCtlList,dicAnimList


#With a list of CTRL and a list of Dictionaries, this function create all the node and making all the connection and snap the target to the Matrices previously created. 
def snapCtlFromMatrixDic (ctlList, dicList):
    if not dicList :
        mc.confirmDialog( title='No saved animation Error', message='No animation was saved so NO transfer could be done. Please save animation first.', button=['ok'], defaultButton='ok')
        mc.error('No animation was saved so NO transfer could be done. Please save animation first')
    else:
        timerName = 'snapCtlFromMatrixDicTimer'
        endExistingTimer(timerName)
        mc.timer(startTimer=True, name = timerName)
        
        #Create the neeeded nodes and making connection
        multMatrixGaea, decomposeMatrixGaea = createMultDecompeCombo()
        quatToEulerGaea = createQuatToEuler(decomposeMatrixGaea)    
        plusMinusOdin = createPlusMinusAverage(decomposeMatrixGaea)
                
        axis=['X','Y','Z']
        for ctlNumber in range(0,len(ctlList)):
            mc.connectAttr(ctlList[ctlNumber]+'.rotatePivot', plusMinusOdin+'.input3D[1]')
            for u in dicList[ctlNumber].keys():
                #Plug worldMatrix and parentInverseMatrix to the MultMatrix
                mc.setAttr(multMatrixGaea+'.matrixIn[0]', dicList[ctlNumber][u], type='matrix')
                mc.setAttr(multMatrixGaea+'.matrixIn[1]', mc.getAttr(ctlList[ctlNumber]+'.parentInverseMatrix[0]', time=u),type='matrix')  
                #change rotateOrder in case rig wasnt build with XYZ rotate order    
                mc.setAttr(quatToEulerGaea+'.inputRotateOrder',mc.getAttr(ctlList[ctlNumber]+'.rotateOrder', time=u))
                
                #Get Output name 
                if hasBeenFrozen(ctlList[ctlNumber]):      
                    axisSmall= [x.lower() for x in axis]                
                    trOut = getOutput(plusMinusOdin, axisSmall)
                else:
                    trOut = getOutput(decomposeMatrixGaea,axis)
                roOut = getOutput(quatToEulerGaea, axis,'Rotate') 
                
                setKeysToCtrl(axis, ctlList[ctlNumber], '.translate', trOut, u)
                setKeysToCtrl(axis, ctlList[ctlNumber], '.rotate', roOut, u)
            
                
            #disconnect because cannot connect to a attribute already connected
            mc.disconnectAttr(ctlList[ctlNumber]+'.rotatePivot',plusMinusOdin+'.input3D[1]')
        #Clean
        mc.delete(multMatrixGaea,decomposeMatrixGaea,quatToEulerGaea,plusMinusOdin)         	
        mc.filterCurve(ctlList)
        
        snapCtlFromMatrixDicSpeed = endExistingTimer(timerName)
        mc.warning ('Success : %s object(s) animation retargeted in %s sec' %(str(len(ctlList)),snapCtlFromMatrixDicSpeed))
 
 
class MyRetargetAnimWindowClass (object):
    def __init__(self):
        self.window = scriptName + '_' + scriptVersion
        self.title = scriptName
        self.size = (180 , 120)
        self.buttonWidth = 180
        self.buttonHeight = 50
        self.backgroundColor = [.8,0.6,.1] 
        
        self.bakeCheckBox = False
        
        self.labelCheckBox = '1. Bake Anim'
        self.labelSaveButton = '2. Save Anim'
        self.labelRetargetButton = '3. Retarget Anim'
        
        
        self.dicAnimList = []
        self.myCtlList = []
        
    def create (self):
        #Makes sure we close previous window
        if mc.window (self.window, exists = True ):
            mc.deleteUI (self.window, window = True)
        self.window = mc.window (self.window, title = self.title , widthHeight = self.size,sizeable=True)
        
        #Layouts
        myMasterLayout = mc.columnLayout(adjustableColumn=True)
        #mc.setParent(myMasterLayout)
        #horizontal layout
        myRowLayout = mc.rowLayout( numberOfColumns=2)
        #checkBox
        mc.text(label='',width = 40)
        self.bakeCheckBox = mc.checkBox( label=self.labelCheckBox ,value=0)
        #button
        
        mc.setParent(myMasterLayout)
        
        mc.button(label =self.labelSaveButton, width = self.buttonWidth, height= self.buttonHeight, command= lambda x: self.updateDicAndList(self.bakeCheckBox))
        mc.button(label =self.labelRetargetButton,  width = self.buttonWidth, height= self.buttonHeight,backgroundColor=self.backgroundColor ,command=lambda x: snapCtlFromMatrixDic(self.myCtlList ,self.dicAnimList)  )
 
        mc.showWindow ()


    def updateDicAndList(self, checkBoxValue):
        self.myCtlList ,self.dicAnimList=  saveAnimToList (checkBoxValue)

def main():
    retargetAnimWindow = MyRetargetAnimWindowClass()
    retargetAnimWindow.create()