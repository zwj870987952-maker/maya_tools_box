import maya.cmds as mc
from functools import partial 
import pymel.core as pm

# global variables

imagePath  = cmds.internalVar(usd = True) 

#functions

window = 'PickerUI'

if ( mc.window(window, exists=True)):
    mc.deleteUI(window)

mc.window(window, title= 'Picker UI', widthHeight=(545,380), 
          maximizeButton=0, resizeToFitChildren=True, s = 0)

cmds.tabLayout ('Picker UI')

mc.setParent('..')
mc.setParent('..')
mc.setParent('..')

mc.frameLayout('Rig Picker', label='Picker', backgroundColor=(0.2,0.2,0.2))

mainLayout = cmds.columnLayout (w = 545, h = 380)
formLayout = cmds.formLayout (w = 545, h = 380)



#Path Image
imagePath  = cmds.internalVar(usd = True) 
ButtonImages=imagePath + str ("RdMTools/icons/")
Background = cmds.image(image= ButtonImages + 'ModelJesusRef.png')

#Def Buttons


def selectControls (controls, *args):    

    #Shift command
      
    mods = cmds.getModifiers()
    if (mods & 1) > 0:
        
        cmds.select(controls, add=True)   
        
    else:
    
        cmds.select (clear = True)
        cmds.select(controls, tgl=True)  


NAMESPACE = ''
    


Spine1 = str (NAMESPACE) + 'Spine_End_CC'
Spine2 = str (NAMESPACE) + 'Spine3_CC'
Spine3 = str (NAMESPACE) + 'Spine2_CC'
Spine4 = str (NAMESPACE) + 'Spine1_CC'
COG = str (NAMESPACE) + 'COG_CC'
ReverseSpine = str (NAMESPACE) + 'ReverseSpine_CC'

L_Clavicule = str (NAMESPACE) + 'L_clavicule_01_CC'
R_Clavicule = str (NAMESPACE) + 'R_clavicule_01_CC'

L_Arm = str (NAMESPACE) + 'L_armIK_CC'
R_Arm = str (NAMESPACE) + 'R_armIK_CC'
L_ArmPV = str (NAMESPACE) + 'L_PV01'
R_ArmPV = str (NAMESPACE) + 'R_PV01'

L_Leg = str (NAMESPACE) + 'L_LegIK_CC'
R_Leg = str (NAMESPACE) + 'R_LegIK_CC'
L_LegPV = str (NAMESPACE) + 'LLeg_PV01'
R_LegPV = str (NAMESPACE) + 'RLeg_PV01'

LArmFK1 =  str (NAMESPACE) +'L_armFK_01_CC'
LArmFK2 =  str (NAMESPACE) +'L_armFK_02_CC'
LArmFK3 =  str (NAMESPACE) +'L_armFK_03_CC'

RArmFK1 =  str (NAMESPACE) +'L_armFK_01_CC'
RArmFK2 =  str (NAMESPACE) +'L_armFK_02_CC'
RArmFK3 =  str (NAMESPACE) +'L_armFK_03_CC'

LLegFK1 =  str (NAMESPACE) +'L_Leg_FK_CC'
LLegFK2 =  str (NAMESPACE) + 'L_Knee_FK_CC'
LLegFK3 =  str (NAMESPACE) + 'L_Ankle_FK_CC'
LLegFK4 =  str (NAMESPACE) + 'L_Ball_FK_CC'

RLegFK1 =  str (NAMESPACE) + 'R_Leg_FK_CC'
RLegFK2 =  str (NAMESPACE) + 'R_Knee_FK_CC'
RLegFK3 =  str (NAMESPACE) + 'R_Ankle_FK_CC'
RLegFK4 =  str (NAMESPACE) + 'R_Ball_FK_CC'

All_CC = Spine1,Spine2,Spine3,Spine4, COG, ReverseSpine,L_Clavicule,R_Clavicule, L_Arm,L_ArmPV,R_Arm,R_ArmPV, L_Leg,L_LegPV,R_Leg,R_LegPV, LArmFK1,LArmFK2,LArmFK3,RArmFK1,RArmFK2,RArmFK3,LLegFK1,LLegFK2,LLegFK3,LLegFK4,RLegFK1,RLegFK2,RLegFK3,RLegFK4 

None_CC = cmds.select (cl = True)

def KeyFrameThis (*args):
    
    cmds.setKeyframe (All_CC, breakdown = 0, hierarchy = 0, controlPoints = 0, shape = 0)

#Crear botones

    
    #Generales

AllButton = cmds.symbolButton (image = ButtonImages+'SelectAll.png', command = partial (selectControls, All_CC))
NoneButton = cmds.symbolButton (image = ButtonImages+'SelectNone.png', command = partial (selectControls, None_CC))
KeyAllButton = cmds.symbolButton (image = ButtonImages+'KeyAll.png', command = KeyFrameThis)

spine1Button = cmds.symbolButton (image = ButtonImages+'CuadradoVerde.png', command = partial (selectControls, Spine1))
spine2Button = cmds.symbolButton (image = ButtonImages+'CuadradoAmarillo.png', command = partial (selectControls, Spine2))
spine3Button = cmds.symbolButton (image = ButtonImages+'CuadradoAmarillo.png', command = partial (selectControls, Spine3))
spine4Button = cmds.symbolButton (image = ButtonImages+'CuadradoVerde.png', command = partial (selectControls, Spine4))
COGButton =  cmds.symbolButton (image = ButtonImages+'Cuadradomorado.png', command = partial (selectControls, COG))
ReverseButton =  cmds.symbolButton (image = ButtonImages+'CuadradoVerdeInv.png', command = partial (selectControls, ReverseSpine))


    #IK
L_ClaviculeButton = cmds.symbolButton (image = ButtonImages+'EsferaAmarilla.png', command = partial (selectControls, L_Clavicule))
R_ClaviculeButton = cmds.symbolButton (image = ButtonImages+'EsferaAmarilla.png', command = partial (selectControls, R_Clavicule))

L_ArmButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, L_Arm))
R_ArmButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, R_Arm))
L_ArmPVButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, L_ArmPV))
R_ArmPVButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, R_ArmPV))

L_LegButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, L_Leg))
R_LegButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, R_Leg))
L_LegPVButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, L_LegPV))
R_LegPVButton = cmds.symbolButton (image = ButtonImages+'EsferaRoja.png', command = partial (selectControls, R_LegPV))

    #FK
L_ArmFK1Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LArmFK1))
L_ArmFK2Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LArmFK2))
L_ArmFK3Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LArmFK3))
R_ArmFK1Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RArmFK1))
R_ArmFK2Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RArmFK2))
R_ArmFK3Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RArmFK3))

L_LegFK1Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LLegFK1))
L_LegFK2Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LLegFK2))
L_LegFK3Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LLegFK3))
L_LegFK4Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, LLegFK4))
R_LegFK1Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RLegFK1))
R_LegFK2Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RLegFK2))
R_LegFK3Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RLegFK3))
R_LegFK4Button = cmds.symbolButton (image = ButtonImages+'EsferaAzul.png', command = partial (selectControls, RLegFK4))



#Colocar Botones

    #Generales
cmds.formLayout (formLayout, edit = True, af = [(AllButton, "left", 0), (AllButton, "top", 10)])
cmds.formLayout (formLayout, edit = True, af = [(NoneButton, "left", 50), (NoneButton, "top", 10)])
cmds.formLayout (formLayout, edit = True, af = [(KeyAllButton, "right", 5), (KeyAllButton, "top", 0)])


cmds.formLayout (formLayout, edit = True, af = [(spine1Button, "left", 241), (spine1Button, "top", 20)])
cmds.formLayout (formLayout, edit = True, af = [(spine2Button, "left", 241), (spine2Button, "top", 70)])
cmds.formLayout (formLayout, edit = True, af = [(spine3Button, "left", 241), (spine3Button, "top", 120)])
cmds.formLayout (formLayout, edit = True, af = [(spine4Button, "left", 241), (spine4Button, "top", 170)])
cmds.formLayout (formLayout, edit = True, af = [(COGButton, "left", 210), (COGButton, "top", 220)])
cmds.formLayout (formLayout, edit = True, af = [(ReverseButton, "left", 241), (ReverseButton, "top", 270)])


cmds.formLayout (formLayout, edit = True, af = [(L_ClaviculeButton, "right", 160), (L_ClaviculeButton, "top", 100)])
cmds.formLayout (formLayout, edit = True, af = [(R_ClaviculeButton, "left", 160), (R_ClaviculeButton, "top", 100)])

    #IK
cmds.formLayout (formLayout, edit = True, af = [(L_ArmButton, "right", 45), (L_ArmButton, "top", 140)])
cmds.formLayout (formLayout, edit = True, af = [(R_ArmButton, "left", 45), (R_ArmButton, "top", 140)])
cmds.formLayout (formLayout, edit = True, af = [(L_ArmPVButton, "right", 100), (L_ArmPVButton, "top", 120)])
cmds.formLayout (formLayout, edit = True, af = [(R_ArmPVButton, "left", 100), (R_ArmPVButton, "top", 120)])

cmds.formLayout (formLayout, edit = True, af = [(L_LegButton, "right", 200), (L_LegButton, "top", 330)])
cmds.formLayout (formLayout, edit = True, af = [(R_LegButton, "left", 200), (R_LegButton, "top", 330)])
cmds.formLayout (formLayout, edit = True, af = [(L_LegPVButton, "right", 200), (L_LegPVButton, "top", 280)])
cmds.formLayout (formLayout, edit = True, af = [(R_LegPVButton, "left", 200), (R_LegPVButton, "top", 280)])
    
    #FK    
cmds.formLayout (formLayout, edit = True, af = [(L_ArmFK1Button, "right", 110), (L_ArmFK1Button, "top", 80)])
cmds.formLayout (formLayout, edit = True, af = [(L_ArmFK2Button, "right", 69), (L_ArmFK2Button, "top", 80)])
cmds.formLayout (formLayout, edit = True, af = [(L_ArmFK3Button, "right", 30), (L_ArmFK3Button, "top", 80)])

cmds.formLayout (formLayout, edit = True, af = [(R_ArmFK1Button, "left", 110), (R_ArmFK1Button, "top", 80)])
cmds.formLayout (formLayout, edit = True, af = [(R_ArmFK2Button, "left", 69), (R_ArmFK2Button, "top", 80)])
cmds.formLayout (formLayout, edit = True, af = [(R_ArmFK3Button, "left", 30), (R_ArmFK3Button, "top", 80)])

cmds.formLayout (formLayout, edit = True, af = [(L_LegFK1Button, "right", 150), (L_LegFK1Button, "top", 250)])
cmds.formLayout (formLayout, edit = True, af = [(L_LegFK2Button, "right", 150), (L_LegFK2Button, "top", 290)])
cmds.formLayout (formLayout, edit = True, af = [(L_LegFK3Button, "right", 150), (L_LegFK3Button, "top", 330)])
cmds.formLayout (formLayout, edit = True, af = [(L_LegFK4Button, "right", 100), (L_LegFK4Button, "top", 330)])

cmds.formLayout (formLayout, edit = True, af = [(R_LegFK1Button, "left", 150), (R_LegFK1Button, "top", 250)])
cmds.formLayout (formLayout, edit = True, af = [(R_LegFK2Button, "left", 150), (R_LegFK2Button, "top", 290)])
cmds.formLayout (formLayout, edit = True, af = [(R_LegFK3Button, "left", 150), (R_LegFK3Button, "top", 330)])
cmds.formLayout (formLayout, edit = True, af = [(R_LegFK4Button, "left", 100), (R_LegFK4Button, "top", 330)])





mc.setParent('..')
mc.setParent('..')
mc.setParent('..')

mc.frameLayout('Hands', label='LeftHand', backgroundColor=(0.2,0.2,0.2))
mc.scrollLayout(w=210)
mc.rowColumnLayout(numberOfColumns=1)

def ChangeThumb(value): 
    cmds.setAttr("L_armIK_CC.CurlThumb",value)
def ChangeIndex(value): 
    cmds.setAttr("L_armIK_CC.CurlIndex",value)
def ChangeMiddle(value): 
    cmds.setAttr("L_armIK_CC.CurlMiddle",value)
def ChangeRing(value): 
    cmds.setAttr("L_armIK_CC.CurlRing",value)
def ChangePinky(value): 
    cmds.setAttr("L_armIK_CC.CurlPinky",value)
def ChangeSize(value): 
    cmds.setAttr("L_armIK_CC.scaleX",value)
    


#CurlThumbSlider = cmds.floatSliderGrp (l = 'Curl Thumb:', min = 0 , max = 10, field = True,v = cmds.getAttr('L_armIK_CC.CurlThumb'), dragCommand = lambda x:ChangeThumb(float(x)))
#CurlIndex = cmds.floatSliderGrp (l = 'Curl Index:', min = 0 , max = 10, field = True, v = cmds.getAttr('L_armIK_CC.CurlIndex'), dragCommand = lambda x:ChangeIndex(float(x)))
#CurlMiddle = cmds.floatSliderGrp (l = 'Curl Middle:', min = 0 , max = 10, field = True, v = cmds.getAttr('L_armIK_CC.CurlMiddle'), dragCommand = lambda x:ChangeMiddle(float(x)))
#CurlRing = cmds.floatSliderGrp (l = 'Curl Ring:', min = 0 , max = 10, field = True, v = cmds.getAttr('L_armIK_CC.CurlRing'), dragCommand = lambda x:ChangeRing(float(x)))
#CurlPinky = cmds.floatSliderGrp (l = 'Curl Pinky:', min = 0 , max = 10, field = True, v = cmds.getAttr('L_armIK_CC.CurlPinky'), dragCommand = lambda x:ChangePinky(float(x)))

cmds.separator(h = 15)

def WideHand(value): 
    cmds.setAttr("LeftPinkyController.rotateZ",-value*2)
    cmds.setAttr("Lfingers_5.rotateZ",-value)
    cmds.setAttr("Lfingers_13.rotateZ",value)


#OpenFingers = cmds.floatSliderGrp (l = 'Wide Fingers:', min = -25 , max = 25, field = True, v = cmds.getAttr('Lfingers_13.rotateZ'), step = 0.01, dragCommand = lambda w:WideHand(float(w)))


mc.rowColumnLayout(numberOfColumns=1,columnWidth = [ (1, 400)])

cmds.separator(h = 25)

def ResetFunc(*args):
    
    cmds.setAttr ("L_armIK_CC.scaleX", 1)
    cmds.setAttr ("L_armIK_CC.CurlThumb", 0)
    cmds.setAttr ("L_armIK_CC.CurlIndex", 0)
    cmds.setAttr ("L_armIK_CC.CurlMiddle", 0)
    cmds.setAttr ("L_armIK_CC.CurlRing", 0)
    cmds.setAttr ("L_armIK_CC.CurlPinky", 0)
    cmds.setAttr ("LeftPinkyController.rotateZ", 0)
    cmds.setAttr ("Lfingers_5.rotateZ", 0)
    cmds.setAttr ("Lfingers_13.rotateZ", 0)
    
    cmds.floatSliderGrp (HandScale, e = True, v = 1)
    cmds.floatSliderGrp (CurlThumbSlider, e = True, v = 0)
    cmds.floatSliderGrp (CurlIndex, e = True, v = 0)
    cmds.floatSliderGrp (CurlMiddle, e = True, v = 0)
    cmds.floatSliderGrp (CurlRing, e = True, v = 0)
    cmds.floatSliderGrp (CurlPinky, e = True, v = 0)
    cmds.floatSliderGrp (OpenFingers, e = True, v = 0)


  
    

BotonSet = cmds.button(l = 'Reset', w = 50, c = ResetFunc)



mc.setParent('..')
mc.setParent('..')
mc.setParent('..')



mc.frameLayout('Hands', label='RightHand', backgroundColor=(0.2,0.2,0.2))
mc.scrollLayout(w=210)
mc.rowColumnLayout(numberOfColumns=1)


def RChangeThumb(value): 
    cmds.setAttr("R_armIK_CC.CurlThumb",value)
def RChangeIndex(value): 
    cmds.setAttr("R_armIK_CC.CurlIndex",value)
def RChangeMiddle(value): 
    cmds.setAttr("R_armIK_CC.CurlMiddle",value)
def RChangeRing(value): 
    cmds.setAttr("R_armIK_CC.CurlRing",value)
def RChangePinky(value): 
    cmds.setAttr("R_armIK_CC.CurlPinky",value)
def RChangeSize(value): 
    cmds.setAttr("R_armIK_CC.scaleX",value)
    

#RCurlThumbSlider = cmds.floatSliderGrp (l = 'Curl Thumb:', min = 0 , max = 10, field = True,v = cmds.getAttr('R_armIK_CC.CurlThumb'), dragCommand = lambda x:RChangeThumb(float(x)))
#RCurlIndex = cmds.floatSliderGrp (l = 'Curl Index:', min = 0 , max = 10, field = True, v = cmds.getAttr('R_armIK_CC.CurlIndex'), dragCommand = lambda x:RChangeIndex(float(x)))
#RCurlMiddle = cmds.floatSliderGrp (l = 'Curl Middle:', min = 0 , max = 10, field = True, v = cmds.getAttr('R_armIK_CC.CurlMiddle'), dragCommand = lambda x:RChangeMiddle(float(x)))
#RCurlRing = cmds.floatSliderGrp (l = 'Curl Ring:', min = 0 , max = 10, field = True, v = cmds.getAttr('R_armIK_CC.CurlRing'), dragCommand = lambda x:RChangeRing(float(x)))
#RCurlPinky = cmds.floatSliderGrp (l = 'Curl Pinky:', min = 0 , max = 10, field = True, v = cmds.getAttr('R_armIK_CC.CurlPinky'), dragCommand = lambda x:RChangePinky(float(x)))

cmds.separator(h = 15)

def RWideHand(value): 
    cmds.setAttr("Rfingers_16.rotateZ",value*2)
    cmds.setAttr("Rfingers_12.rotateZ",-value)
    cmds.setAttr("Rfingers_4.rotateX",-value)


#ROpenFingers = cmds.floatSliderGrp (l = 'Wide Fingers:', min = -25 , max = 25, field = True, v = cmds.getAttr('Rfingers_12.rotateZ'), step = 0.01, dragCommand = lambda w:RWideHand(float(w)))


mc.rowColumnLayout(numberOfColumns=1,columnWidth = [ (1, 400)])

cmds.separator(h = 25)

def RResetFunc(*args):
    
    cmds.setAttr ("R_armIK_CC.scaleX", 1)
    cmds.setAttr ("R_armIK_CC.CurlThumb", 0)
    cmds.setAttr ("R_armIK_CC.CurlIndex", 0)
    cmds.setAttr ("R_armIK_CC.CurlMiddle", 0)
    cmds.setAttr ("R_armIK_CC.CurlRing", 0)
    cmds.setAttr ("R_armIK_CC.CurlPinky", 0)
    cmds.setAttr ("Rfingers_16.rotateZ", 0)
    cmds.setAttr ("Rfingers_12.rotateZ", 0)
    cmds.setAttr ("Rfingers_4.rotateX", 0)
    
    cmds.floatSliderGrp (RHandScale, e = True, v = 1)
    cmds.floatSliderGrp (RCurlThumbSlider, e = True, v = 0)
    cmds.floatSliderGrp (RCurlIndex, e = True, v = 0)
    cmds.floatSliderGrp (RCurlMiddle, e = True, v = 0)
    cmds.floatSliderGrp (RCurlRing, e = True, v = 0)
    cmds.floatSliderGrp (RCurlPinky, e = True, v = 0)
    cmds.floatSliderGrp (ROpenFingers, e = True, v = 0)


  
    

BotonSet = cmds.button(l = 'Reset', w = 50, c = RResetFunc)

mc.setParent('..')
mc.setParent('..')
mc.setParent('..')
mc.setParent('..')
mc.setParent('..')
mc.setParent('..')


mc.frameLayout('Face', label='Face', backgroundColor=(0.2,0.2,0.2))
mc.rowColumnLayout(numberOfColumns=1)



mc.showWindow(window)