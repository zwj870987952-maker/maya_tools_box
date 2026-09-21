import maya.cmds as mc

scriptVersion = 'v09'
scriptName = 'lockToWorld'

'''
Copyright (c) <2020> <JesseOngPho>
jesseongpho@hotmail.com

DESCRIPTION : 
Lock 1 or multiple objects to the world. Really useful to fix feet sliding. 

FEATURES:
- Snap the selected controller to the world for the selected amount of frames 
- Work with multiple selection 
- Work with selected attributes on the channel box (Translation and Rotation only)
- Work on controllers that have frozen transformation
- Work on maya 2016,2018,2020, 2022 both Linux and Windows (Did not try other version but it should work)

UPDATE 
2021/06/22: Made the script compatible with maya 2022

HOW TO USE : 
1) Get on the frame where the controller should start to be snapped
2) Click on the Start button
3) Get to the frame where the controller should stop to be snapped 
4) Click on the End button
5) Select the controller(s)
6) Click on Lock to World button

INSTALLATION:
To install, drag and drop the install.mel file onto the maya viewport
'''


#Script is using matrix and quaternion nodes so we make sure the plug in is loaded
mc.loadPlugin('matrixNodes.mll',quiet=True)
mc.loadPlugin('quatNodes.mll',quiet=True)

def checkEmptySelection(myCtrlList):
    if not myCtrlList :
        mc.confirmDialog( title='Selection Error', message='The selection is empty. Please select object(s) and try again', button=['ok'], defaultButton='ok')
        mc.error('The selection is empty. Please select an object')
    
#Consider that if the controller has frozen transformation, rotatePivot is different from [0,0,0]      
def hasBeenFrozen (myCtl):
    hasBeenFrozen = True
    if mc.getAttr(myCtl+'.rotatePivot') == [(0,0,0)]:
        hasBeenFrozen = False
    return hasBeenFrozen


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

#return a list of attribute : ex = ['tx','ty','rx']. Raw data from Channel Box
def getSelectedChannelBoxAttributes(): 
    channels = []
    selectedChannelBoxAttr =  ([] + (mc.channelBox("mainChannelBox", selectedMainAttributes=True, q=True) or []))		
    return selectedChannelBoxAttr

#return 2 lists in the format : ['X', 'Y', 'Z'] from the Raw data from Channel Box
def getSelectedAttrList(selectedCBAttr):

    selectedTranslation = []
    selectedRotation = []
    #if some attribute are selected in channel box
    if selectedCBAttr: 
        for i in selectedCBAttr :
            #remove selected Attributes from the skip lists
            if i[0] =='t' and len(i)==2:
                selectedTranslation.append(i[1].upper())
            elif i[0] =='r' and len(i)==2:
                selectedRotation.append(i[1].upper())
            else: 
                mc.confirmDialog( title='Selected Attribute Error', message='The script only supports translation and rotation attributes. Please select the good attributes and try again', button=['ok'], defaultButton='ok')
                mc.error('Sorry, the script only support translation and rotation attributes.')        
    else: 
        selectedTranslation = ['X','Y','Z']
        selectedRotation = ['X','Y','Z']  

    return selectedTranslation,selectedRotation

#Get The attr VALUE of the Output depending on the node in a form of an axis tab. Translate is the default 
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

def getWorldMatrixStartPosition (myCtl, time): 
    matrix=[]
    if hasBeenFrozen(myCtl):
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
        matrix= mc.getAttr(myCtl+'.worldMatrix',t=time)	
    return matrix

#=================END GET FUNCTIONS=================#

#Function that set the keys on the controller at TimeT
def setKeysToCtrl (selectedAxis, ctrl, manip, output, timeT):
    for i in range(0,len(selectedAxis)): 
        mc.setKeyframe(ctrl+manip+selectedAxis[i], v= mc.getAttr(output[i]), time = timeT )


#snap the ctrl to the matrice previously created. 
def snapCtlFromMatrixList(ctlList, matrixList, min, max,selectedCBAttr):
    
    selectedTranslation,selectedRotation = getSelectedAttrList(selectedCBAttr)
    
    #Create the neeeded nodes and making connection
    multMatrixGaea, decomposeMatrixGaea = createMultDecompeCombo()
    quatToEulerGaea = createQuatToEuler(decomposeMatrixGaea)    
    plusMinusOdin = createPlusMinusAverage(decomposeMatrixGaea)
 
    try: 
    
        for ctlNumber in range(0,len(ctlList)):
            mc.connectAttr(ctlList[ctlNumber]+'.rotatePivot', plusMinusOdin+'.input3D[1]')
            for timeT in range(min, max+1):
                #Plug worldMatrix and parentInverseMatrix to the MultMatrix
                mc.setAttr(multMatrixGaea+'.matrixIn[0]', matrixList[ctlNumber], type='matrix')
                mc.setAttr(multMatrixGaea+'.matrixIn[1]', mc.getAttr(ctlList[ctlNumber]+'.parentInverseMatrix[0]', time=timeT),type='matrix')  
                #change rotateOrder in case rig wasnt build with XYZ rotate order    
                mc.setAttr(quatToEulerGaea+'.inputRotateOrder',mc.getAttr(ctlList[ctlNumber]+'.rotateOrder', time=timeT))
                            
                
                #Get Output name 
                if hasBeenFrozen(ctlList[ctlNumber]):              
                    selectedTranslationSmall =  [x.lower() for x in selectedTranslation] 
                    trOut = getOutput(plusMinusOdin, selectedTranslationSmall)
                else:
                    trOut = getOutput(decomposeMatrixGaea,selectedTranslation)
                    
                roOut = getOutput(quatToEulerGaea, selectedRotation,'Rotate') 
                #print  (trOut,   roOut  )   
                
                        
                setKeysToCtrl(selectedTranslation, ctlList[ctlNumber], '.translate', trOut, timeT)
                setKeysToCtrl(selectedRotation, ctlList[ctlNumber], '.rotate', roOut, timeT)
                
                
            #disconnect for next controller because cannot connect to an attribute already connected
            mc.disconnectAttr(ctlList[ctlNumber]+'.rotatePivot',plusMinusOdin+'.input3D[1]')
    except: 
        mc.delete(multMatrixGaea,decomposeMatrixGaea,quatToEulerGaea,plusMinusOdin)    
        mc.confirmDialog( title='Rotate Order Error', message='Error on the lock to WORLD SCRIPT, Check the rotate Order attribute.', button=['ok'], defaultButton='ok')
        mc.error('Error on the lock to WORLD SCRIPT, Check the rotate Order attribute.')                  
        
        
    #Clean
    mc.delete(multMatrixGaea,decomposeMatrixGaea,quatToEulerGaea,plusMinusOdin)  
            
            
           
    mc.warning ('Success : %s object(s) was lockToWorld' %(str(len(ctlList))))
           
def lockToWorld(min,max ):

    mySelection = mc.ls(sl=True)
    checkEmptySelection(mySelection)
    matrixList = []
    for ctrl in mySelection: 
        matrixList.append(getWorldMatrixStartPosition(ctrl,min))
    #print (matrixList)
    
    attributeToKeyList = getSelectedChannelBoxAttributes()
    snapCtlFromMatrixList (mySelection, matrixList, int(min), int(max),attributeToKeyList)
    mc.select(mySelection)
    
    
class MyLockWorldWindowClass (object):
    def __init__(self):
        self.window = scriptName + '_' + scriptVersion
        self.title = scriptName
        self.size = (180 , 100)
        self.minValue = mc.playbackOptions(q=1,min=1)
        self.maxValue = mc.playbackOptions(q=1,max=1)
        self.startString = 'Start \n'
        self.endString = 'End \n'
        self.buttonHeight = 50
        self.buttonWidth = 180
        self.buttonSmallWidth = 90
        self.backgroundColor = [.8,0.6,.1] 
        
    def create (self):
        #Makes sure we close previous window
        if mc.window (self.window, exists = True ):
            mc.deleteUI (self.window, window = True)
        self.window = mc.window (self.window, title = self.title , widthHeight = self.size,sizeable=False)
        
        #master Layouts
        myMasterLayout = mc.columnLayout()
        #horizontal layout
        myRowLayout = mc.rowColumnLayout(numberOfColumns =2)
        
        #button
        startButton = mc.button(label =self.startString+str(self.minValue), width = self.buttonSmallWidth, height= self.buttonHeight , command = lambda x : self.updateStartButton(startButton))
        endButton = mc.button(label =self.endString+str(self.maxValue), width = self.buttonSmallWidth, height= self.buttonHeight ,command =lambda x: self.updateEndButton(endButton))
        
        mc.setParent(myMasterLayout)
        mySecondLayout = mc.columnLayout()
        
        mc.button(label ='Lock to World', command= lambda x: lockToWorld(self.minValue,self.maxValue), width = self.buttonWidth, height= self.buttonHeight ,backgroundColor=self.backgroundColor  )

        mc.showWindow ()
    
    #Everytime the user click on start or end, it update the string on the button and set new range    
    def updateStartButton(self, startButton):
        self.minValue = mc.currentTime(q=True)
        mc.button(startButton, e=True, label = self.startString + str(self.minValue ))
    def updateEndButton (self, endButton):
        self.maxValue = mc.currentTime(q=True)
        mc.button(endButton, e=True, label = self.endString + str(self.maxValue ))
       
def main():
    lockWorldWindow = MyLockWorldWindowClass()
    lockWorldWindow.create()