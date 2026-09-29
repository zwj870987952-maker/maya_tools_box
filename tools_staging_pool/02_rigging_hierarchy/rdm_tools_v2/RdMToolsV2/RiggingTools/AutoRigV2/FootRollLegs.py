from maya import cmds

def footRoll():
    cmds.group(n ="L_FootRoll_Auto", em = True)
    cmds.parent('L_FootRoll_Auto', 'L_RF_Ball_Auto')
    cmds.setAttr("L_FootRoll_Auto.rotateZ", 0)
    cmds.setAttr("L_FootRoll_Auto.translateX", 0)
    cmds.setAttr("L_FootRoll_Auto.translateY", 0)
    cmds.setAttr("L_FootRoll_Auto.translateZ", 0)
    cmds.setAttr("L_FootRoll_Auto.rotateX", 0)
    cmds.setAttr("L_FootRoll_Auto.rotateY", 0)
    cmds.parent('L_FootRoll_Auto', 'L_RF_Ball_Root')
    cmds.parent('L_RF_Ball_Auto', 'L_FootRoll_Auto')
    
    cmds.addAttr('L_Ankle_JJ_IK_CC', ln="_________", en=".::", at="enum")
    cmds.setAttr('L_Ankle_JJ_IK_CC._________', e=1, channelBox=True)
    cmds.setAttr("L_Ankle_JJ_IK_CC._________", lock=True)
    
    
    cmds.group(n ="R_FootRoll_Auto", em = True)
    cmds.parent('R_FootRoll_Auto', 'R_RF_Ball_Auto')
    cmds.setAttr("R_FootRoll_Auto.rotateZ", 0)
    cmds.setAttr("R_FootRoll_Auto.translateX", 0)
    cmds.setAttr("R_FootRoll_Auto.translateY", 0)
    cmds.setAttr("R_FootRoll_Auto.translateZ", 0)
    cmds.setAttr("R_FootRoll_Auto.rotateX", 0)
    cmds.setAttr("R_FootRoll_Auto.rotateY", 0)
    cmds.parent('R_FootRoll_Auto', 'R_RF_Ball_Root')
    cmds.parent('R_RF_Ball_Auto', 'R_FootRoll_Auto')
    
    cmds.addAttr('R_Ankle_JJ_IK_CC', ln="_________", en=".::", at="enum")
    cmds.setAttr('R_Ankle_JJ_IK_CC._________', e=1, channelBox=True)
    cmds.setAttr("R_Ankle_JJ_IK_CC._________", lock=True)
    
    cmds.addAttr('R_Ankle_JJ_IK_CC', ln="FootRoll", dv=0, at='double', min=-30, max = 30)
    cmds.setAttr('R_Ankle_JJ_IK_CC.FootRoll', e=1, keyable=True)
    cmds.addAttr('L_Ankle_JJ_IK_CC', ln="FootRoll", dv=0, at='double', min=-30, max = 30)
    cmds.setAttr('L_Ankle_JJ_IK_CC.FootRoll', e=1, keyable=True)
    
    ##
    cmds.setDrivenKeyframe('L_RF_Fingers_Root.rotateX', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('L_FootRoll_Auto.rotateZ', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", 15)
    cmds.setAttr("L_FootRoll_Auto.rotateZ", -30)
    cmds.setAttr("L_RF_Fingers_Root.rotateX", 0)
    cmds.setDrivenKeyframe('L_RF_Fingers_Root.rotateX', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('L_FootRoll_Auto.rotateZ', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", 30)
    
    #cmds.setAttr("L_FootRoll_Auto.rotateZ", 40)
##############################################################################################################################
    cmds.setAttr("L_FootRoll_Auto.rotateZ", 0)
    cmds.setAttr("L_RF_Fingers_Root.rotateX", 60)
    cmds.setDrivenKeyframe('L_RF_Fingers_Root.rotateX', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('L_FootRoll_Auto.rotateZ', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    
    cmds.selectKey('L_FootRoll_Auto_rotateZ', add=1, k=1)
    #cmds.keyTangent(itt='linear', ott='linear')
    cmds.setAttr("L_FootRoll_Auto_rotateZ.preInfinity", 1)
    cmds.setAttr("L_FootRoll_Auto_rotateZ.postInfinity", 1)
    
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", 0)
    
    
    
    
    
    ##
    cmds.setDrivenKeyframe('R_RF_Fingers_Root.rotateX', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('R_FootRoll_Auto.rotateZ', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", 15)
    cmds.setAttr("R_FootRoll_Auto.rotateZ", -30)
    cmds.setAttr("R_RF_Fingers_Root.rotateX", 0)
    cmds.setDrivenKeyframe('R_RF_Fingers_Root.rotateX', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('R_FootRoll_Auto.rotateZ', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", 30)
    
    #####################################################################################################################################################
    #cmds.setAttr("R_FootRoll_Auto.rotateZ", 40)

    cmds.setAttr("R_FootRoll_Auto.rotateZ", 0)
    cmds.setAttr("R_RF_Fingers_Root.rotateX", 60)
    cmds.setDrivenKeyframe('R_RF_Fingers_Root.rotateX', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    cmds.setDrivenKeyframe('R_FootRoll_Auto.rotateZ', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    # Result: 1 // 
    
    cmds.selectKey('R_FootRoll_Auto_rotateZ', add=1, k=1)
    #cmds.keyTangent(itt='linear', ott='linear')
    cmds.setAttr("R_FootRoll_Auto_rotateZ.preInfinity", 1)
    cmds.setAttr("R_FootRoll_Auto_rotateZ.postInfinity", 1)
    
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", 0)

    #Nuevo Automatismo para foot roll HEEL
    cmds.group(n = 'L_RF_Heel_FootRoll', em = True)
    cmds.parent('L_RF_Heel_FootRoll', 'L_RF_Heel_Root')
    cmds.setAttr("L_RF_Heel_FootRoll.rotateX", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.translateX", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.translateY", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.translateZ", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.rotateX", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.rotateY", 0)
    cmds.parent('L_RF_Heel_Auto', 'L_RF_Heel_FootRoll')
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", 0)
    cmds.setAttr("L_RF_Heel_FootRoll.rotateX", 0)
    cmds.setDrivenKeyframe('L_RF_Heel_FootRoll.rotateX', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", -30)
    cmds.setAttr("L_RF_Heel_FootRoll.rotateX", -50)
    cmds.setDrivenKeyframe('L_RF_Heel_FootRoll.rotateX', currentDriver='L_Ankle_JJ_IK_CC.FootRoll')
    cmds.setAttr("L_Ankle_JJ_IK_CC.FootRoll", 0)

    cmds.group(n = 'R_RF_Heel_FootRoll', em = True)
    cmds.parent('R_RF_Heel_FootRoll', 'R_RF_Heel_Root')
    cmds.setAttr("R_RF_Heel_FootRoll.rotateX", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.translateX", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.translateY", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.translateZ", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.rotateX", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.rotateY", 0)
    cmds.parent('R_RF_Heel_Auto', 'R_RF_Heel_FootRoll')
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", 0)
    cmds.setAttr("R_RF_Heel_FootRoll.rotateX", 0)
    cmds.setDrivenKeyframe('R_RF_Heel_FootRoll.rotateX', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", -30)
    cmds.setAttr("R_RF_Heel_FootRoll.rotateX", -50)
    cmds.setDrivenKeyframe('R_RF_Heel_FootRoll.rotateX', currentDriver='R_Ankle_JJ_IK_CC.FootRoll')
    cmds.setAttr("R_Ankle_JJ_IK_CC.FootRoll", 0)



    cmds.select(cl = True)
