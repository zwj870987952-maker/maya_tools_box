from maya import cmds
'https://bindpose.com/seamless-ik-fk-switch-maya-python/'

def RightBlendIKFK(*args):
    if cmds.getAttr("R_Leg_PV|R_FKIK_Blend_locShape.FK_IK_Blend") == 0:
        IK01 = cmds.parentConstraint('leg_end_R_joint_FK', 'R_Leg_IK_CC', mo=0)    
        cmds.delete(IK01)        
        #PV
        arm01Vec = [cmds.xform("lowerleg_R_joint_FK", t=1, ws=1, q=1)[i] - cmds.xform("upperleg_R_joint_FK", t=1, ws=1, q=1)[i] for i in range(3)]
        arm02Vec = [cmds.xform("lowerleg_R_joint_FK", t=1, ws=1, q=1)[i] - cmds.xform("leg_end_R_joint_FK", t=1, ws=1, q=1)[i] for i in range(3)]
        cmds.xform("R_Leg_PV", t=[cmds.xform("lowerleg_R_joint_FK", t=1, q=1, ws=1)[i] + arm01Vec[i] * .75 + arm02Vec[i] * .75 for i in range(3)], ws=1)
        cmds.setAttr("R_Leg_PV|R_FKIK_Blend_locShape.FK_IK_Blend", 1)
        #RollBall
        RB01 = cmds.orientConstraint('toes_R_joint_FK', 'toes_R_joint_RFR_CC_2', mo=0)    
        cmds.delete(RB01)        
        
    else:
        
        FK01 = cmds.orientConstraint('upperleg_R_joint_IK', 'upperleg_R_joint_FK', mo= 0)
        FK02 = cmds.orientConstraint('lowerleg_R_joint_IK', 'lowerleg_R_joint_FK', mo= 0)
        FK03 = cmds.orientConstraint('R_Leg_IK_CC', 'leg_end_R_joint_FK', mo= 0)
        cmds.delete(FK01,FK02,FK03)
        cmds.setAttr("R_Leg_PV|R_FKIK_Blend_locShape.FK_IK_Blend", 0)
        #RollBall
        RBIK = cmds.orientConstraint('toes_R_joint_IK','toes_R_joint_FK', mo =0)
        cmds.delete(RBIK)

RightBlendIKFK()