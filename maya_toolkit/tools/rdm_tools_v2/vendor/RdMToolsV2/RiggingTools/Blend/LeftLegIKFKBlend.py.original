from maya import cmds
'https://bindpose.com/seamless-ik-fk-switch-maya-python/'

def LeftBlendIKFK(*args):
    if cmds.getAttr("L_Leg_PV|L_FKIK_Blend_locShape.FK_IK_Blend") == 0:
        IK01 = cmds.parentConstraint('leg_end_l_joint_FK', 'L_Leg_IK_CC', mo=0)    
        cmds.delete(IK01)        
        #PV
        arm01Vec = [cmds.xform("lowerleg_l_joint_FK", t=1, ws=1, q=1)[i] - cmds.xform("upperleg_l_joint_FK", t=1, ws=1, q=1)[i] for i in range(3)]
        arm02Vec = [cmds.xform("lowerleg_l_joint_FK", t=1, ws=1, q=1)[i] - cmds.xform("leg_end_l_joint_FK", t=1, ws=1, q=1)[i] for i in range(3)]
        cmds.xform("L_Leg_PV", t=[cmds.xform("lowerleg_l_joint_FK", t=1, q=1, ws=1)[i] + arm01Vec[i] * .75 + arm02Vec[i] * .75 for i in range(3)], ws=1)
        cmds.setAttr("L_Leg_PV|L_FKIK_Blend_locShape.FK_IK_Blend", 1)
        #RollBall
        RB01 = cmds.orientConstraint('toes_l_joint_FK', 'toes_l_joint_RFR_CC_2', mo=0)    
        cmds.delete(RB01)     
        
    else:
        
        FK01 = cmds.orientConstraint('upperleg_l_joint_IK', 'upperleg_l_joint_FK', mo= 0)
        FK02 = cmds.orientConstraint('lowerleg_l_joint_IK', 'lowerleg_l_joint_FK', mo= 0)
        FK03 = cmds.orientConstraint('L_Leg_IK_CC', 'leg_end_l_joint_FK', mo= 0)
        cmds.delete(FK01,FK02,FK03)
        cmds.setAttr("L_Leg_PV|L_FKIK_Blend_locShape.FK_IK_Blend", 0)
        #RollBall
        RBIK = cmds.orientConstraint('toes_l_joint_IK','toes_l_joint_FK', mo =0)
        cmds.delete(RBIK)
        cmds.setAttr('L_Leg_IK_CC.FootRoll',0)
        cmds.setAttr('L_Leg_IK_CC.Heel',0)
        cmds.setAttr('L_Leg_IK_CC.FootRoll',0)
        cmds.setAttr('L_Leg_IK_CC.ToeTip',0)
        cmds.setAttr('L_Leg_IK_CC.Ball',0)
        cmds.setAttr('L_Leg_IK_CC.Tilt',0)

        
LeftBlendIKFK()