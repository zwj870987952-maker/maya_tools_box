from maya import cmds
import pymel.core as pm
import maya.mel as mel 
import RdMToolsV2
from RdMToolsV2.RiggingTools.Tools.FollicleOnPositionAlt import createFol

#Controllers on face

mouthControllers = ['upperLip_Bind_CC1','upperLip_Bind_CC2','upperLip_Bind_CC3','upperLip_Bind_CC4','upperLip_Bind_CC5',
                    'lowerLip_Bind_CC1','lowerLip_Bind_CC2','lowerLip_Bind_CC3','lowerLip_Bind_CC4','lowerLip_Bind_CC5',
                    'L_MouthCorner_CC','R_MouthCorner_CC','MouthUp_CC','MouthDown_CC']

for i in mouthControllers:
    #Create negative Grp
    negGrp = cmds.group(em = True, n = str(i)+ '_Neg')
    cmds.xform(negGrp, m = cmds.xform(i, q = True, m = True, ws = True), ws = True)
    cmds.parent(negGrp, str(i) + '_Root')
    cmds.parent(str(i) + '_Auto', negGrp)
    #Activate Negative Aspect
    MultDivide = cmds.shadingNode('multiplyDivide', asUtility=True, n=i+'_MultDiv')
    cmds.setAttr(str(MultDivide)+ '.input2X',-1)
    cmds.setAttr(str(MultDivide)+ '.input2Y',-1)
    cmds.setAttr(str(MultDivide)+ '.input2Z',-1)

    cmds.connectAttr(str(i)+'.translate', str(MultDivide)+'.input1')
    cmds.connectAttr(str(MultDivide)+'.output', str(negGrp)+'.translate')

#Create Follicles for Controllers                      
#mel.eval('select -r AddyOddGeo.f[647] AddyOddGeo.f[671] AddyOddGeo.f[7610] AddyOddGeo.f[7634] AddyOddGeo.f[7645] ;')
upMouthFaces = cmds.ls(sl = True)

cmds.select(cl = True)

#mel.eval('select -r AddyOddGeo.f[1577] AddyOddGeo.f[3018] AddyOddGeo.f[8540] AddyOddGeo.f[9977] AddyOddGeo.f[9981];')
dwMouthFaces = cmds.ls(sl = True)

#mel.eval('select -r AddyOddGeo.f[4053] AddyOddGeo.f[7614] AddyOddGeo.f[7658] AddyOddGeo.f[9976] ;')
cornerFaces = cmds.ls(sl = True)

allFaces = upMouthFaces #+ dwMouthFaces + cornerFaces
cmds.group(em = True, n = 'MouthPointsOnPolys')

for i in allFaces:
    cmds.select(i)
    createFol(addJoint = False, NewName = i + 'Follicle')
    cmds.parent(i + 'Follicle', 'MouthPointsOnPolys')    

