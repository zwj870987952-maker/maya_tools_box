from maya import cmds
import RdMToolsV2
import maya.mel as mel
import pymel.core as pm


###JOINTS LOCATORS

def LocatorsBtn(*args):

    cmds.undoInfo(openChunk=True)   

    jointsNum = 4

    
    for X in range (jointsNum):
    
        cmds.select (clear = True)
        
        cmds.CreateLocator ()
        cmds.move (2.5*X+1, 0, 0)
        cmds.select (clear = True)

    cmds.rename ("locator1","L_Clavicule_LOC")
    cmds.rename ("locator2","L_Shoulder_LOC")
    cmds.rename ("locator3","L_Elbow_LOC")
    cmds.rename ("locator4","L_Wrist_LOC")

    if cmds.objExists ('SpineEnd_JC'):
        
         cmds.parent ('L_Wrist_LOC','L_Elbow_LOC')
         cmds.parent ('L_Elbow_LOC','L_Shoulder_LOC')
         cmds.parent ('L_Shoulder_LOC','L_Clavicule_LOC')
         cmds.pointConstraint ('SpineEnd_JC','L_Clavicule_LOC')
         cmds.delete ('L_Clavicule_LOC_pointConstraint1')
         cmds.parent ('L_Shoulder_LOC', 'L_Elbow_LOC ','L_Wrist_LOC', w = True)
         
    cmds.select('L_Elbow_LOC')
    cmds.move(0,0,-0.4, r = True)     
    cmds.select (clear = True)

    cmds.undoInfo(closeChunk=True)   
    
def JointsBtn(*args):  

    jointsNum = 4

    cmds.undoInfo(openChunk=True)   

    cmds.rename ("L_Clavicule_LOC","locator1")
    cmds.rename ("L_Shoulder_LOC","locator2")
    cmds.rename ("L_Elbow_LOC","locator3")
    cmds.rename ("L_Wrist_LOC","locator4")
   
    cmds.select (cl=True)
    
    for X in range (1,jointsNum + 1):  
                
        cmds.joint (n = "L_arm_" + str(X))
        cmds.pointConstraint ("locator" + str (X) , "L_arm_" + str(X))
        cmds.delete ("L_arm_" + str(X) + "_pointConstraint1")
        cmds.delete ("locator" + str (X))
        #cmds.setAttr ("L_arm_" + str(X) + ".displayLocalAxis", 1)   
    
        
    cmds.joint()    
    cmds.select ("L_arm_1","L_arm_2","L_arm_3","L_arm_4")    
    cmds.joint(e= True, zso=True, oj= "xzy", sao = "zdown")
    cmds.delete ('joint1')

    
    cmds.select (clear = True) 
          
    cmds.undoInfo(closeChunk=True)   
  
def IKFKArms(ArmsSize = 3,Twist = False,Ribbon =False,*args):  

    cmds.undoInfo(openChunk=True)   


    #Fix Arm Twist Orient order
#############################################################################
    #cmds.setAttr("L_arm_1.rotateOrder", 1)
    #cmds.setAttr("L_arm_2.rotateOrder", 1)
    #cmds.setAttr("L_arm_3.rotateOrder", 1)
    #cmds.setAttr("L_arm_4.rotateOrder", 1)
##############################################################################

    
    #Start

    from RdMToolsV2.RiggingTools.Tools.AutoIKFK import RdM_IKFK
    reload (RdMToolsV2.RiggingTools.Tools.AutoIKFK)

    
    cmds.duplicate('L_arm_1', n = 'R_arm_1')
    cmds.select('R_arm_1')
    pm.mel.searchReplaceNames('L', 'R', "hierarchy")
    
    cmds.parent('L_arm_2', w = True)
    cmds.select('L_arm_2','L_arm_3','L_arm_4')
    RdM_IKFK(CustomName = 'L_Arm',size = ArmsSize, Color = 6)
    cmds.select(cl=True)
    
    cmds.parent('R_arm_2', w = True)
    cmds.select('R_arm_2','R_arm_3','R_arm_4')
    RdM_IKFK(CustomName = 'R_Arm',size = ArmsSize, Color = 13)
    cmds.select(cl=True)
    
    cmds.orientConstraint('L_arm_4_IK_CC','L_arm_4_IK', mo=True)
    cmds.orientConstraint('R_arm_4_IK_CC','R_arm_4_IK', mo=True)

    #Clavicule
    def ClaviculePos(armSide, Color ):
        ClaciculeController = cmds.circle(n = str(armSide)+'_Clavicule_CC', nr=(1,0,0), r = ArmsSize*2)
        ClaviculeAuto = cmds.group(ClaciculeController, n =str(ClaciculeController[0])+'_Auto')
       
        ClaviculeGroup = cmds.group(ClaviculeAuto, n =str(ClaciculeController[0])+'_GRP')

        cmds.xform(ClaviculeGroup, m = cmds.xform(str(armSide)+'_arm_1', q =1,m=1))    
        cmds.parentConstraint(ClaciculeController,str(armSide)+'_arm_1', mo =True )
        cmds.parentConstraint(ClaciculeController,str(armSide)+'_arm_2_IK', mo =True )
        cmds.parentConstraint(ClaciculeController,str(armSide)+'_arm_2_IK_Stretchy01', mo =True )
        cmds.parentConstraint(ClaciculeController,str(armSide)+'_arm_2_FK_GRP', mo =True )
        cmds.setAttr (str(ClaciculeController[0])+'.overrideEnabled', 1)
        cmds.setAttr (str(ClaciculeController[0])+'.overrideColor', Color)

        cmds.parent(str(armSide)+'_Arm_FKIK_BlendShape', ClaciculeController[0], s=True, add=True )
        
        #Auto Clavicule FK
        FKAuto=cmds.addAttr(str(armSide) + '_Clavicule_CC|'+str(armSide)+'_Arm_FKIK_BlendShape',ln='FK_AutoClavicule', at = 'double', min = 0 , max = 1)
        cmds.setAttr(str(armSide) + '_Clavicule_CC|'+str(armSide)+'_Arm_FKIK_BlendShape.FK_AutoClavicule', e = 1, keyable = 1)  
        
        
        #Conncet ClaviculeFK Auto
        MultAutoClav=cmds.shadingNode('multiplyDivide', asUtility=1, n  = 'MultAutoClav_'+str(armSide))
        cmds.connectAttr(str(armSide)+'_arm_2_FK_CC.rotate.rotateZ', str(MultAutoClav)+'.input1.input1X')
        cmds.connectAttr(str(MultAutoClav)+'.output.outputX',str(armSide) + '_Clavicule_CC_Auto.rotateZ')
        cmds.connectAttr(str(armSide)+'_Arm_FKIK_BlendShape.FK_AutoClavicule', str(MultAutoClav)+'.input2.input2X')
        
        cmds.setAttr(str(armSide)+'_Arm_FKIK_BlendShape.FK_AutoClavicule', 0.5)

        cmds.connectAttr(str(armSide)+'_arm_2_FK_CC.rotate.rotateY', str(MultAutoClav)+'.input1.input1Y')
        cmds.connectAttr(str(MultAutoClav)+'.output.outputY',str(armSide) + '_Clavicule_CC_Auto.rotateY')
        cmds.connectAttr(str(armSide)+'_Arm_FKIK_BlendShape.FK_AutoClavicule', str(MultAutoClav)+'.input2.input2Y')
        
        #CleanClavicule
        cmds.setAttr(str(armSide)+"_Clavicule_CC.sx", lock=True, channelBox=False, keyable=False)
        cmds.setAttr(str(armSide)+"_Clavicule_CC.sy", lock=True, channelBox=False, keyable=False)
        cmds.setAttr(str(armSide)+"_Clavicule_CC.sz", lock=True, channelBox=False, keyable=False)
        cmds.setAttr(str(armSide)+"_Clavicule_CC.v", lock=True, channelBox=False, keyable=False)


        
    ClaviculePos(armSide='L', Color=6)
    ClaviculePos(armSide='R', Color=13)

#Twist with IK simple chains
    cmds.group('L_arm_2', n = 'L_arm_2_GRP')
    cmds.group('R_arm_2', n = 'R_arm_2_GRP')
    
          
    if Twist or Ribbon ==True:
        print'TwistMethod ON'  
        

                
        from RdMToolsV2.RiggingTools.Tools.AutoTwist import AutoTwistFunc
        reload(RdMToolsV2.RiggingTools.Tools.AutoTwist)
        cmds.select('L_arm_2','L_arm_3')
        AutoTwistFunc(Axis = "X",SwitchVar = 0)        
        cmds.select('R_arm_2','R_arm_3')
        AutoTwistFunc(Axis = "X",SwitchVar = 0)
        cmds.select('L_arm_3','L_arm_4')
        AutoTwistFunc(Axis = "X",SwitchVar = 1)        
        cmds.select('R_arm_3','R_arm_4')
        AutoTwistFunc(  Axis = "X",SwitchVar = 1)          
 
        #CorrectStretchy Twist
        FirstConnectionL = 'L_arm_3'
        SecondConnectionL = 'L_arm_4'
        FirstConnectionR = 'R_arm_3'
        SecondConnectionR = 'R_arm_4'
        
        LTwist1 = ['L_arm_2_Twist_1','L_arm_2_Twist_2','L_arm_2_Twist_3']
        LTwist2 = ['L_arm_3_Twist_1','L_arm_3_Twist_2','L_arm_3_Twist_3']
        RTwist1 = ['R_arm_2_Twist_1','R_arm_2_Twist_2','R_arm_2_Twist_3']
        RTwist2 = ['R_arm_3_Twist_1','R_arm_3_Twist_2','R_arm_3_Twist_3']
                
        MultDivide1 = cmds.shadingNode('multiplyDivide', asUtility=True, n='Arm01MultDiv01')
        cmds.setAttr(str(MultDivide1)+ '.operation', 2)
        cmds.setAttr(str(MultDivide1)+'.input2X', 3)        
        cmds.setAttr(str(MultDivide1)+'.input2Y', 3)        
     
        MultDivide2 = cmds.shadingNode('multiplyDivide', asUtility=True, n='Arm01MultDiv01')
        cmds.setAttr(str(MultDivide2)+ '.operation', 2)
        cmds.setAttr(str(MultDivide2)+'.input2X', 3)        
        cmds.setAttr(str(MultDivide2)+'.input2Y', 3)        

        cmds.connectAttr(FirstConnectionL + '.translateX.',str(MultDivide1)+'.input1X')
        cmds.connectAttr(SecondConnectionL + '.translateX.',str(MultDivide2)+'.input1X')
        cmds.connectAttr(FirstConnectionR + '.translateX.',str(MultDivide1)+'.input1Y')
        cmds.connectAttr(SecondConnectionR + '.translateX.',str(MultDivide2)+'.input1Y')

        for i in  LTwist1:
            cmds.connectAttr(str(MultDivide1)+'.output.outputX', str(i)+'.translateX')  
        for i in  LTwist2:
            cmds.connectAttr(str(MultDivide2)+'.output.outputX', str(i)+'.translateX')  
        for i in  RTwist1:
            cmds.connectAttr(str(MultDivide1)+'.output.outputY', str(i)+'.translateX')  
        for i in  RTwist2:
            cmds.connectAttr(str(MultDivide2)+'.output.outputY', str(i)+'.translateX')  
                            
        cmds.pointConstraint('L_arm_2','L_arm_2_Twist_0' ,mo=True)                    
        cmds.pointConstraint('L_arm_3','L_arm_3_Twist_0' ,mo=True)                    
        cmds.pointConstraint('R_arm_2','R_arm_2_Twist_0' ,mo=True)                    
        cmds.pointConstraint('R_arm_3','R_arm_3_Twist_0' ,mo=True)          
 
        cmds.select ('L_arm_1','L_arm_2_Twist_0', 'L_arm_2_Twist_1', 'L_arm_2_Twist_2', 'L_arm_3_Twist_0', 'L_arm_3_Twist_1', 'L_arm_3_Twist_2')
        cmds.sets (n= 'BindThisTo_Twist_L_Arm' )  
            
        cmds.select ('R_arm_1','R_arm_2_Twist_0', 'R_arm_2_Twist_1', 'R_arm_2_Twist_2', 'R_arm_3_Twist_0', 'R_arm_3_Twist_1', 'R_arm_3_Twist_2')
        cmds.sets (n= 'BindThisTo_Twist_R_Arm' )         
        

    #MirrorRightPart
    
    LeftGroup = cmds.group('L_arm_1','L_arm_2_IK_GRP','L_arm_2_FK_GRP','L_Clavicule_CC_GRP','L_arm_2_GRP', n = 'L_Arm_GRP')
    RightGroup = cmds.group('R_arm_1','R_arm_2_IK_GRP','R_arm_2_FK_GRP','R_Clavicule_CC_GRP','R_arm_2_GRP', n = 'R_Arm_GRP')

    cmds.group(LeftGroup,RightGroup, n = 'RdM_AutoARMS')
    cmds.xform(RightGroup, rp=(0,0,0), sp=(0,0,0) )
    cmds.setAttr(str(RightGroup)+'.rotateX', 180)
    cmds.setAttr(str(RightGroup)+'.scaleX', -1)
    cmds.setAttr(str(RightGroup)+'.scaleY', -1)
    cmds.setAttr(str(RightGroup)+'.scaleZ', -1)

       
   #Clean
    cmds.rename('NoXformConnected','NoXformConnectedArms')
    cmds.parent('NoXformConnectedArms', 'RdM_AutoARMS')
    cmds.select(cl=True)


    if Ribbon ==True:
        
        cmds.delete('BindThisTo_Twist_L_Arm','BindThisTo_Twist_R_Arm')
        
        from RdMToolsV2.RiggingTools.Tools.BendyRibbons import ribbonLimb
        reload(RdMToolsV2.RiggingTools.Tools.BendyRibbons)
        cmds.select('L_arm_2','L_arm_3','L_arm_4')
        ribbonLimb(customName= 'L_Arm', size = ArmsSize)
        
        cmds.select('R_arm_2','R_arm_3','R_arm_4')
        ribbonLimb(customName= 'R_Arm', size = ArmsSize)
        
    
        #Parent to Twists
        cmds.parentConstraint('L_arm_2_Twist_0','L_ArmRibbon_JC_1_GRP', mo =False)
        cmds.parentConstraint('L_arm_2_Twist_1','L_ArmRibbon_JC_2_GRP', mo =False)
        cmds.parentConstraint('L_arm_2_Twist_2','L_ArmRibbon_JC_3_GRP', mo =False)
        cmds.parentConstraint('L_arm_3_Twist_0','L_ArmRibbon_JC_4_GRP', mo =False)
        cmds.parentConstraint('L_arm_3_Twist_1','L_ArmRibbon_JC_5_GRP', mo =False)
        cmds.parentConstraint('L_arm_3_Twist_2','L_ArmRibbon_JC_6_GRP', mo =False)
        cmds.parentConstraint('L_arm_3_Twist_3','L_ArmRibbon_JC_7_GRP', mo =False)
        
        cmds.parentConstraint('R_arm_2_Twist_0','R_ArmRibbon_JC_1_GRP', mo =False)
        cmds.parentConstraint('R_arm_2_Twist_1','R_ArmRibbon_JC_2_GRP', mo =False)
        cmds.parentConstraint('R_arm_2_Twist_2','R_ArmRibbon_JC_3_GRP', mo =False)
        cmds.parentConstraint('R_arm_3_Twist_0','R_ArmRibbon_JC_4_GRP', mo =False)
        cmds.parentConstraint('R_arm_3_Twist_1','R_ArmRibbon_JC_5_GRP', mo =False)
        cmds.parentConstraint('R_arm_3_Twist_2','R_ArmRibbon_JC_6_GRP', mo =False)
        cmds.parentConstraint('R_arm_3_Twist_3','R_ArmRibbon_JC_7_GRP', mo =False)
        
        cmds.parent('L_Arm_RibbonGRP','R_Arm_RibbonGRP', 'RdM_AutoARMS')
        cmds.sets('L_arm_1', edit=1, forceElement='BindThisTo_L_Arm_Ribbon')
        cmds.sets('R_arm_1', edit=1, forceElement='BindThisTo_R_Arm_Ribbon')
         

        #ShowHide Attr
        cmds.addAttr('|RdM_AutoARMS|L_Arm_GRP|L_arm_2_IK_GRP|L_arm_3_IK_PV_GRP|L_arm_3_IK_PV|L_Arm_FKIK_BlendShape', ln="________", en=".:", at="enum")
        cmds.setAttr('|RdM_AutoARMS|L_Arm_GRP|L_arm_2_IK_GRP|L_arm_3_IK_PV_GRP|L_arm_3_IK_PV|L_Arm_FKIK_BlendShape.________', e=1, channelBox=True)
        cmds.addAttr('|RdM_AutoARMS|R_Arm_GRP|R_arm_2_IK_GRP|R_arm_3_IK_PV_GRP|R_arm_3_IK_PV|R_Arm_FKIK_BlendShape', ln="________", en=".:", at="enum")
        cmds.setAttr('|RdM_AutoARMS|R_Arm_GRP|R_arm_2_IK_GRP|R_arm_3_IK_PV_GRP|R_arm_3_IK_PV|R_Arm_FKIK_BlendShape.________', e=1, channelBox=True)


        cmds.addAttr('|RdM_AutoARMS|L_Arm_GRP|L_arm_2_IK_GRP|L_arm_3_IK_PV_GRP|L_arm_3_IK_PV|L_Arm_FKIK_BlendShape', ln="ShowBendyConstrollers", en="Hide:Show:", at="enum")
        cmds.setAttr('|RdM_AutoARMS|L_Arm_GRP|L_arm_2_IK_GRP|L_arm_3_IK_PV_GRP|L_arm_3_IK_PV|L_Arm_FKIK_BlendShape.ShowBendyConstrollers', e=1, keyable=True)
        
        cmds.addAttr('|RdM_AutoARMS|R_Arm_GRP|R_arm_2_IK_GRP|R_arm_3_IK_PV_GRP|R_arm_3_IK_PV|R_Arm_FKIK_BlendShape', ln="ShowBendyConstrollers", en="Hide:Show:", at="enum")
        cmds.setAttr('|RdM_AutoARMS|R_Arm_GRP|R_arm_2_IK_GRP|R_arm_3_IK_PV_GRP|R_arm_3_IK_PV|R_Arm_FKIK_BlendShape.ShowBendyConstrollers', e=1, keyable=True)
        
        cmds.connectAttr('L_arm_3_IK_PV|L_Arm_FKIK_BlendShape.ShowBendyConstrollers', 'L_ArmRibbon_JC_GPR.visibility', f=1)
        cmds.connectAttr('R_arm_3_IK_PV|R_Arm_FKIK_BlendShape.ShowBendyConstrollers', 'R_ArmRibbon_JC_GPR.visibility', f=1)
        
    try:
        cmds.parent('R_Palm','R_arm_4')
        cmds.parent('L_Palm','L_arm_4')
    except:
        pass
        
    #Make nice Names
    
    oldNames = ['L_arm_4_IK_CC','R_arm_4_IK_CC','L_arm_3_IK_PV','R_arm_3_IK_PV', 'L_arm_2_FK_CC','R_arm_2_FK_CC','L_arm_3_FK_CC','R_arm_3_FK_CC','L_arm_4_FK_CC','R_arm_4_FK_CC'] 
    newNames = ['L_arm_IK_CC','R_arm_IK_CC','L_Elbow_PV','R_Elbow_PV', 'L_Shoulder_FK_CC','R_Shoulder_FK_CC','L_Elbow_FK_CC','R_Elbow_FK_CC','L_Wrist_FK_CC','R_Wrist_FK_CC'] 
    
    for i in range(0, 10):
        cmds.rename(oldNames[i] , newNames[i])

   ##Fix FK Stretchy
    '''
    Grupo sobre IKsc
    Aim Constraint del control nuevo al joint
    Switch del aim Constraint IK en , FK En 1
    '''
    NewFkGrpL =cmds.group('L_arm_2TwistIKrp', n = 'FKStretchyAimL')
    NewFkGrpR =cmds.group('R_arm_2TwistIKrp', n = 'FKStretchyAimR')
    cmds.xform(NewFkGrpL, rp = cmds.xform('L_arm_2',q=True, rp=True))
    cmds.xform(NewFkGrpR, rp = cmds.xform('R_arm_2',q=True, rp=True))
    
    cmds.aimConstraint('L_arm_3',NewFkGrpL, weight=1, upVector=(0, 1, 0), mo=1, worldUpType="vector", aimVector=(1, 0, 0), worldUpVector=(0, 1, 0))
    cmds.aimConstraint('R_arm_3',NewFkGrpR, weight=1, upVector=(0, 1, 0), mo=1, worldUpType="vector", aimVector=(1, 0, 0), worldUpVector=(0, 1, 0))

    ######
    #Change RotateOrder
    cmds.setAttr("L_Elbow_PV|L_Arm_FKIK_BlendShape.RotateOrder", 1)
    cmds.setAttr("R_Elbow_PV|R_Arm_FKIK_BlendShape.RotateOrder", 1)
    cmds.connectAttr('L_Elbow_PV|L_Arm_FKIK_BlendShape.RotateOrder', 'L_arm_1.rotateOrder')
    cmds.connectAttr('R_Elbow_PV|R_Arm_FKIK_BlendShape.RotateOrder', 'R_arm_1.rotateOrder')

    
    cmds.undoInfo(closeChunk=True)   


    
#Run Functions
'''

LocatorsBtn() 
JointsBtn()
IKFKArms(ArmsSize = 3, Twist = True, Ribbon = True)

'''
