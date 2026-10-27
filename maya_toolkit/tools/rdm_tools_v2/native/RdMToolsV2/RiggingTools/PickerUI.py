from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import maya.cmds as mc
from functools import partial
window = 'PickerUI'

def selectControls(controls, *args):
    mods = cmds.getModifiers()
    if mods & 1 > 0:
        cmds.select(controls, add=True)
    else:
        cmds.select(clear=True)
        cmds.select(controls, tgl=True)
NAMESPACE = ''

def KeyFrameThis(*args):
    cmds.setKeyframe(All_CC, breakdown=0, hierarchy=0, controlPoints=0, shape=0)

def ChangeThumb(value):
    cmds.setAttr('L_armIK_CC.CurlThumb', value)

def ChangeIndex(value):
    cmds.setAttr('L_armIK_CC.CurlIndex', value)

def ChangeMiddle(value):
    cmds.setAttr('L_armIK_CC.CurlMiddle', value)

def ChangeRing(value):
    cmds.setAttr('L_armIK_CC.CurlRing', value)

def ChangePinky(value):
    cmds.setAttr('L_armIK_CC.CurlPinky', value)

def ChangeSize(value):
    cmds.setAttr('L_armIK_CC.scaleX', value)

def WideHand(value):
    cmds.setAttr('LeftPinkyController.rotateZ', -value * 2)
    cmds.setAttr('Lfingers_5.rotateZ', -value)
    cmds.setAttr('Lfingers_13.rotateZ', value)

def ResetFunc(*args):
    cmds.setAttr('L_armIK_CC.scaleX', 1)
    cmds.setAttr('L_armIK_CC.CurlThumb', 0)
    cmds.setAttr('L_armIK_CC.CurlIndex', 0)
    cmds.setAttr('L_armIK_CC.CurlMiddle', 0)
    cmds.setAttr('L_armIK_CC.CurlRing', 0)
    cmds.setAttr('L_armIK_CC.CurlPinky', 0)
    cmds.setAttr('LeftPinkyController.rotateZ', 0)
    cmds.setAttr('Lfingers_5.rotateZ', 0)
    cmds.setAttr('Lfingers_13.rotateZ', 0)
    cmds.floatSliderGrp(HandScale, e=True, v=1)
    cmds.floatSliderGrp(CurlThumbSlider, e=True, v=0)
    cmds.floatSliderGrp(CurlIndex, e=True, v=0)
    cmds.floatSliderGrp(CurlMiddle, e=True, v=0)
    cmds.floatSliderGrp(CurlRing, e=True, v=0)
    cmds.floatSliderGrp(CurlPinky, e=True, v=0)
    cmds.floatSliderGrp(OpenFingers, e=True, v=0)

def RChangeThumb(value):
    cmds.setAttr('R_armIK_CC.CurlThumb', value)

def RChangeIndex(value):
    cmds.setAttr('R_armIK_CC.CurlIndex', value)

def RChangeMiddle(value):
    cmds.setAttr('R_armIK_CC.CurlMiddle', value)

def RChangeRing(value):
    cmds.setAttr('R_armIK_CC.CurlRing', value)

def RChangePinky(value):
    cmds.setAttr('R_armIK_CC.CurlPinky', value)

def RChangeSize(value):
    cmds.setAttr('R_armIK_CC.scaleX', value)

def RWideHand(value):
    cmds.setAttr('Rfingers_16.rotateZ', value * 2)
    cmds.setAttr('Rfingers_12.rotateZ', -value)
    cmds.setAttr('Rfingers_4.rotateX', -value)

def RResetFunc(*args):
    cmds.setAttr('R_armIK_CC.scaleX', 1)
    cmds.setAttr('R_armIK_CC.CurlThumb', 0)
    cmds.setAttr('R_armIK_CC.CurlIndex', 0)
    cmds.setAttr('R_armIK_CC.CurlMiddle', 0)
    cmds.setAttr('R_armIK_CC.CurlRing', 0)
    cmds.setAttr('R_armIK_CC.CurlPinky', 0)
    cmds.setAttr('Rfingers_16.rotateZ', 0)
    cmds.setAttr('Rfingers_12.rotateZ', 0)
    cmds.setAttr('Rfingers_4.rotateX', 0)
    cmds.floatSliderGrp(RHandScale, e=True, v=1)
    cmds.floatSliderGrp(RCurlThumbSlider, e=True, v=0)
    cmds.floatSliderGrp(RCurlIndex, e=True, v=0)
    cmds.floatSliderGrp(RCurlMiddle, e=True, v=0)
    cmds.floatSliderGrp(RCurlRing, e=True, v=0)
    cmds.floatSliderGrp(RCurlPinky, e=True, v=0)
    cmds.floatSliderGrp(ROpenFingers, e=True, v=0)


def run_script():
    exec(compile("imagePath = bundled_scripts_dir(usd=True)\nwindow = 'PickerUI'\nif mc.window(window, exists=True):\n    mc.deleteUI(window)\nmc.window(window, title='Picker UI', widthHeight=(545, 380), maximizeButton=0, resizeToFitChildren=True, s=0)\ncmds.tabLayout('Picker UI')\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.frameLayout('Rig Picker', label='Picker', backgroundColor=(0.2, 0.2, 0.2))\nmainLayout = cmds.columnLayout(w=545, h=380)\nformLayout = cmds.formLayout(w=545, h=380)\nimagePath = bundled_scripts_dir(usd=True)\nButtonImages = imagePath + str('RdMTools/icons/')\nBackground = cmds.image(image=ButtonImages + 'ModelJesusRef.png')\nNAMESPACE = ''\nSpine1 = str(NAMESPACE) + 'Spine_End_CC'\nSpine2 = str(NAMESPACE) + 'Spine3_CC'\nSpine3 = str(NAMESPACE) + 'Spine2_CC'\nSpine4 = str(NAMESPACE) + 'Spine1_CC'\nCOG = str(NAMESPACE) + 'COG_CC'\nReverseSpine = str(NAMESPACE) + 'ReverseSpine_CC'\nL_Clavicule = str(NAMESPACE) + 'L_clavicule_01_CC'\nR_Clavicule = str(NAMESPACE) + 'R_clavicule_01_CC'\nL_Arm = str(NAMESPACE) + 'L_armIK_CC'\nR_Arm = str(NAMESPACE) + 'R_armIK_CC'\nL_ArmPV = str(NAMESPACE) + 'L_PV01'\nR_ArmPV = str(NAMESPACE) + 'R_PV01'\nL_Leg = str(NAMESPACE) + 'L_LegIK_CC'\nR_Leg = str(NAMESPACE) + 'R_LegIK_CC'\nL_LegPV = str(NAMESPACE) + 'LLeg_PV01'\nR_LegPV = str(NAMESPACE) + 'RLeg_PV01'\nLArmFK1 = str(NAMESPACE) + 'L_armFK_01_CC'\nLArmFK2 = str(NAMESPACE) + 'L_armFK_02_CC'\nLArmFK3 = str(NAMESPACE) + 'L_armFK_03_CC'\nRArmFK1 = str(NAMESPACE) + 'L_armFK_01_CC'\nRArmFK2 = str(NAMESPACE) + 'L_armFK_02_CC'\nRArmFK3 = str(NAMESPACE) + 'L_armFK_03_CC'\nLLegFK1 = str(NAMESPACE) + 'L_Leg_FK_CC'\nLLegFK2 = str(NAMESPACE) + 'L_Knee_FK_CC'\nLLegFK3 = str(NAMESPACE) + 'L_Ankle_FK_CC'\nLLegFK4 = str(NAMESPACE) + 'L_Ball_FK_CC'\nRLegFK1 = str(NAMESPACE) + 'R_Leg_FK_CC'\nRLegFK2 = str(NAMESPACE) + 'R_Knee_FK_CC'\nRLegFK3 = str(NAMESPACE) + 'R_Ankle_FK_CC'\nRLegFK4 = str(NAMESPACE) + 'R_Ball_FK_CC'\nAll_CC = (Spine1, Spine2, Spine3, Spine4, COG, ReverseSpine, L_Clavicule, R_Clavicule, L_Arm, L_ArmPV, R_Arm, R_ArmPV, L_Leg, L_LegPV, R_Leg, R_LegPV, LArmFK1, LArmFK2, LArmFK3, RArmFK1, RArmFK2, RArmFK3, LLegFK1, LLegFK2, LLegFK3, LLegFK4, RLegFK1, RLegFK2, RLegFK3, RLegFK4)\nNone_CC = cmds.select(cl=True)\nAllButton = cmds.symbolButton(image=ButtonImages + 'SelectAll.png', command=partial(selectControls, All_CC))\nNoneButton = cmds.symbolButton(image=ButtonImages + 'SelectNone.png', command=partial(selectControls, None_CC))\nKeyAllButton = cmds.symbolButton(image=ButtonImages + 'KeyAll.png', command=KeyFrameThis)\nspine1Button = cmds.symbolButton(image=ButtonImages + 'CuadradoVerde.png', command=partial(selectControls, Spine1))\nspine2Button = cmds.symbolButton(image=ButtonImages + 'CuadradoAmarillo.png', command=partial(selectControls, Spine2))\nspine3Button = cmds.symbolButton(image=ButtonImages + 'CuadradoAmarillo.png', command=partial(selectControls, Spine3))\nspine4Button = cmds.symbolButton(image=ButtonImages + 'CuadradoVerde.png', command=partial(selectControls, Spine4))\nCOGButton = cmds.symbolButton(image=ButtonImages + 'Cuadradomorado.png', command=partial(selectControls, COG))\nReverseButton = cmds.symbolButton(image=ButtonImages + 'CuadradoVerdeInv.png', command=partial(selectControls, ReverseSpine))\nL_ClaviculeButton = cmds.symbolButton(image=ButtonImages + 'EsferaAmarilla.png', command=partial(selectControls, L_Clavicule))\nR_ClaviculeButton = cmds.symbolButton(image=ButtonImages + 'EsferaAmarilla.png', command=partial(selectControls, R_Clavicule))\nL_ArmButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, L_Arm))\nR_ArmButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, R_Arm))\nL_ArmPVButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, L_ArmPV))\nR_ArmPVButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, R_ArmPV))\nL_LegButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, L_Leg))\nR_LegButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, R_Leg))\nL_LegPVButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, L_LegPV))\nR_LegPVButton = cmds.symbolButton(image=ButtonImages + 'EsferaRoja.png', command=partial(selectControls, R_LegPV))\nL_ArmFK1Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LArmFK1))\nL_ArmFK2Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LArmFK2))\nL_ArmFK3Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LArmFK3))\nR_ArmFK1Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RArmFK1))\nR_ArmFK2Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RArmFK2))\nR_ArmFK3Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RArmFK3))\nL_LegFK1Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LLegFK1))\nL_LegFK2Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LLegFK2))\nL_LegFK3Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LLegFK3))\nL_LegFK4Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, LLegFK4))\nR_LegFK1Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RLegFK1))\nR_LegFK2Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RLegFK2))\nR_LegFK3Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RLegFK3))\nR_LegFK4Button = cmds.symbolButton(image=ButtonImages + 'EsferaAzul.png', command=partial(selectControls, RLegFK4))\ncmds.formLayout(formLayout, edit=True, af=[(AllButton, 'left', 0), (AllButton, 'top', 10)])\ncmds.formLayout(formLayout, edit=True, af=[(NoneButton, 'left', 50), (NoneButton, 'top', 10)])\ncmds.formLayout(formLayout, edit=True, af=[(KeyAllButton, 'right', 5), (KeyAllButton, 'top', 0)])\ncmds.formLayout(formLayout, edit=True, af=[(spine1Button, 'left', 241), (spine1Button, 'top', 20)])\ncmds.formLayout(formLayout, edit=True, af=[(spine2Button, 'left', 241), (spine2Button, 'top', 70)])\ncmds.formLayout(formLayout, edit=True, af=[(spine3Button, 'left', 241), (spine3Button, 'top', 120)])\ncmds.formLayout(formLayout, edit=True, af=[(spine4Button, 'left', 241), (spine4Button, 'top', 170)])\ncmds.formLayout(formLayout, edit=True, af=[(COGButton, 'left', 210), (COGButton, 'top', 220)])\ncmds.formLayout(formLayout, edit=True, af=[(ReverseButton, 'left', 241), (ReverseButton, 'top', 270)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ClaviculeButton, 'right', 160), (L_ClaviculeButton, 'top', 100)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ClaviculeButton, 'left', 160), (R_ClaviculeButton, 'top', 100)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ArmButton, 'right', 45), (L_ArmButton, 'top', 140)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ArmButton, 'left', 45), (R_ArmButton, 'top', 140)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ArmPVButton, 'right', 100), (L_ArmPVButton, 'top', 120)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ArmPVButton, 'left', 100), (R_ArmPVButton, 'top', 120)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegButton, 'right', 200), (L_LegButton, 'top', 330)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegButton, 'left', 200), (R_LegButton, 'top', 330)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegPVButton, 'right', 200), (L_LegPVButton, 'top', 280)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegPVButton, 'left', 200), (R_LegPVButton, 'top', 280)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ArmFK1Button, 'right', 110), (L_ArmFK1Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ArmFK2Button, 'right', 69), (L_ArmFK2Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(L_ArmFK3Button, 'right', 30), (L_ArmFK3Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ArmFK1Button, 'left', 110), (R_ArmFK1Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ArmFK2Button, 'left', 69), (R_ArmFK2Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(R_ArmFK3Button, 'left', 30), (R_ArmFK3Button, 'top', 80)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegFK1Button, 'right', 150), (L_LegFK1Button, 'top', 250)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegFK2Button, 'right', 150), (L_LegFK2Button, 'top', 290)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegFK3Button, 'right', 150), (L_LegFK3Button, 'top', 330)])\ncmds.formLayout(formLayout, edit=True, af=[(L_LegFK4Button, 'right', 100), (L_LegFK4Button, 'top', 330)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegFK1Button, 'left', 150), (R_LegFK1Button, 'top', 250)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegFK2Button, 'left', 150), (R_LegFK2Button, 'top', 290)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegFK3Button, 'left', 150), (R_LegFK3Button, 'top', 330)])\ncmds.formLayout(formLayout, edit=True, af=[(R_LegFK4Button, 'left', 100), (R_LegFK4Button, 'top', 330)])\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.frameLayout('Hands', label='LeftHand', backgroundColor=(0.2, 0.2, 0.2))\nmc.scrollLayout(w=210)\nmc.rowColumnLayout(numberOfColumns=1)\ncmds.separator(h=15)\nmc.rowColumnLayout(numberOfColumns=1, columnWidth=[(1, 400)])\ncmds.separator(h=25)\nBotonSet = cmds.button(l='Reset', w=50, c=ResetFunc)\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.frameLayout('Hands', label='RightHand', backgroundColor=(0.2, 0.2, 0.2))\nmc.scrollLayout(w=210)\nmc.rowColumnLayout(numberOfColumns=1)\ncmds.separator(h=15)\nmc.rowColumnLayout(numberOfColumns=1, columnWidth=[(1, 400)])\ncmds.separator(h=25)\nBotonSet = cmds.button(l='Reset', w=50, c=RResetFunc)\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.setParent('..')\nmc.frameLayout('Face', label='Face', backgroundColor=(0.2, 0.2, 0.2))\nmc.rowColumnLayout(numberOfColumns=1)\nmc.showWindow(window)", __file__, "exec"), globals())
