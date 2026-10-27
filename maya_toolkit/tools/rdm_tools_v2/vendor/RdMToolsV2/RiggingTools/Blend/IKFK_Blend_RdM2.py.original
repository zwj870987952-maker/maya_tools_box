from maya import cmds
'https://bindpose.com/seamless-ik-fk-switch-maya-python/'

##############################################################################3

def ArmsBlendIKFK(Side, *args): #FK a IK
    if cmds.getAttr(str(Side)+"_Elbow_PV|"+str(Side)+"_Arm_FKIK_BlendShape.Blend_IKFK") == 0:
        IK01 = cmds.parentConstraint(str(Side)+'_Wrist_FK_CC', str(Side)+'_arm_IK_CC', mo=0)    
        cmds.delete(IK01)        
        #PV
        arm01Vec = [cmds.xform(str(Side)+"_Elbow_FK_CC", t=1, ws=1, q=1)[i] - cmds.xform(str(Side)+"_Shoulder_FK_CC", t=1, ws=1, q=1)[i] for i in range(3)]
        arm02Vec = [cmds.xform(str(Side)+"_Elbow_FK_CC", t=1, ws=1, q=1)[i] - cmds.xform(str(Side)+"_Wrist_FK_CC", t=1, ws=1, q=1)[i] for i in range(3)]
        cmds.xform(str(Side)+"_Elbow_PV", t=[cmds.xform(str(Side)+"_Elbow_FK_CC", t=1, q=1, ws=1)[i] + arm01Vec[i] * .75 + arm02Vec[i] * .75 for i in range(3)], ws=1)
        cmds.setAttr(str(Side)+"_Elbow_PV|"+str(Side)+"_Arm_FKIK_BlendShape.Blend_IKFK", 1)

    else: #IK a FK
    
        #AutoClav OFF
        cmds.setAttr(str(Side)+"_Elbow_PV|"+str(Side)+"_Arm_FKIK_BlendShape.FK_AutoClavicule", 0)
        #Do the change
        FK01 = cmds.xform(str(Side)+'_Shoulder_FK_CC', m = cmds.xform(str(Side)+'_arm_2_IK', q = True, m =True, ws = True), ws = True)
        FK02 = cmds.xform(str(Side)+'_Elbow_FK_CC', m = cmds.xform(str(Side)+'_arm_3_IK', q = True, m =True, ws = True), ws = True)
        FK03 = cmds.xform(str(Side)+'_Wrist_FK_CC', m = cmds.xform(str(Side)+'_arm_4_IK', q = True, m =True, ws = True), ws = True)
        cmds.setAttr(str(Side)+"_Elbow_PV|"+str(Side)+"_Arm_FKIK_BlendShape.Blend_IKFK", 0)
        



#ArmsBlendIKFK(Side = 'L')
#ArmsBlendIKFK(Side = 'R')

##############################################################################

def LegsBlendIKFK(Side, *args): #FK a IK

    if cmds.getAttr(str(Side)+"_Knee_PV|"+str(Side)+"_Leg_FKIK_BlendShape.Blend_IKFK") == 0:
        IK01 = cmds.parentConstraint(str(Side)+'_BlendIK', str(Side)+'_Leg_IK_CC', mo=0)    
        cmds.delete(IK01)        
        #PV
        arm01Vec = [cmds.xform(str(Side)+"_Knee_FK_CC", t=1, ws=1, q=1)[i] - cmds.xform(str(Side)+"_Leg_FK_CC", t=1, ws=1, q=1)[i] for i in range(3)]
        arm02Vec = [cmds.xform(str(Side)+"_Knee_FK_CC", t=1, ws=1, q=1)[i] - cmds.xform(str(Side)+"_Ankle_FK_CC", t=1, ws=1, q=1)[i] for i in range(3)]
        cmds.xform(str(Side)+"_Knee_FK_CC", t=[cmds.xform(str(Side)+"_Knee_FK_CC", t=1, q=1, ws=1)[i] + arm01Vec[i] * .75 + arm02Vec[i] * .75 for i in range(3)], ws=1)
        cmds.setAttr(str(Side)+"_Knee_PV|"+str(Side)+"_Leg_FKIK_BlendShape.Blend_IKFK", 1)
        
        #Set RFL control to FK Ball
        cmds.delete(cmds.orientConstraint(str(Side)+'_Ball_FK_CC', str(Side)+'_RF_Ball2'))

    else: #IK a FK    

        FK01 = cmds.xform(str(Side)+'_Leg_FK_CC', m = cmds.xform(str(Side)+'_Leg_JJ_IK', q = True, m =True, ws = True), ws = True)
        FK02 = cmds.xform(str(Side)+'_Knee_FK_CC', m = cmds.xform(str(Side)+'_Knee_JJ_IK', q = True, m =True, ws = True), ws = True)
        FK03 = cmds.xform(str(Side)+'_Ankle_FK_CC', m = cmds.xform(str(Side)+'_Ankle_JJ_IK', q = True, m =True, ws = True), ws = True)
        FK04 = cmds.xform(str(Side)+'_Ball_FK_CC', m = cmds.xform(str(Side)+'_Ball_JJ_IK', q = True, m =True, ws = True), ws = True)

        cmds.setAttr(str(Side)+"_Knee_PV|"+str(Side)+"_Leg_FKIK_BlendShape.Blend_IKFK", 0)
        
        #Set RFL to 0
        cmds.setAttr(str(Side)+"_Leg_IK_CC.FootRoll", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.RollFingers", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.PivotFingers", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.UpDownFingers", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.PivotBall", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.RollBall", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.PivotHeel", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.RollHeel", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.TiltOut", 0)
        cmds.setAttr(str(Side)+"_Leg_IK_CC.TiltIn", 0)
        
        cmds.setAttr(str(Side)+"_RF_Fingers.rotateZ", 0)
        cmds.setAttr(str(Side)+"_RF_Fingers.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_OutFoot.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_InFoot.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_Heel.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_Ball.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_Ball2.rotateX", 0)
        cmds.setAttr(str(Side)+"_RF_Fingers.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_OutFoot.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_InFoot.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_Heel.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_Ball.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_Ball2.rotateY", 0)
        cmds.setAttr(str(Side)+"_RF_OutFoot.rotateZ", 0)
        cmds.setAttr(str(Side)+"_RF_InFoot.rotateZ", 0)
        cmds.setAttr(str(Side)+"_RF_Heel.rotateZ", 0)
        cmds.setAttr(str(Side)+"_RF_Ball.rotateZ", 0)
        cmds.setAttr(str(Side)+"_RF_Ball2.rotateZ", 0)
            
#LegsBlendIKFK(Side = 'L')
#LegsBlendIKFK(Side = 'R')