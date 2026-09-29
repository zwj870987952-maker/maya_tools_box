from maya import cmds

def improveArms():
    
    cmds.undoInfo(openChunk=True)   
   
    if cmds.objExists('L_Palm'):
        try:
            cmds.parent('L_Palm', w = True)
            cmds.parent('R_Palm', w = True)
        except:
            pass
    
    try: 
        cmds.delete('L_Palm_CC|L_Arm_FKIK_BlendShape')
        cmds.delete('R_Palm_CC|R_Arm_FKIK_BlendShape')
    
    except:    
        print 'cant delete hands bends'
        
        
    for i in range(4):
        cmds.select(cl=True)
        loc= cmds.spaceLocator(n = 'L_arm_' + str(i+1)+'_Loc')
        cmds.delete(cmds.pointConstraint('L_arm_' + str(i+1), loc , mo=False))
    

    cmds.rename('L_arm_1_Loc','L_Clavicule_LOC')
    cmds.rename('L_arm_2_Loc','L_Shoulder_LOC')
    cmds.rename('L_arm_3_Loc','L_Elbow_LOC')
    cmds.rename('L_arm_4_Loc','L_Wrist_LOC')
    
    cmds.delete('RdM_AutoARMS')

    armsNodes = ('Arm01MultDiv01', 'Arm01MultDiv02', 'L_Arm_MultDiv01', 'L_Arm_MultDiv02', 'L_ArmMultDiv', 'L_ArmMultDiv00', 'MultAutoClav_L', 
                'MultAutoClav_R', 'R_Arm_MultDiv01', 'R_Arm_MultDiv02', 'R_ArmMultDiv', 'R_ArmMultDiv00', 'Twist_L_arm_2', 'Twist_L_arm_3', 'Twist_R_arm_2', 'Twist_R_arm_3','L_Arm_normalize_MultDiv','R_Arm_normalize_MultDiv')
                
    for i in armsNodes:
        try:
            cmds.delete(i)
        except:
            pass
    
    try:
        reconnectHands()
    except:
        pass
    
    cmds.undoInfo(closeChunk=True)   

    
def reconnectHands():
    
    cmds.undoInfo(openChunk=True)   
    
    try:
        cmds.parent('L_Palm', 'L_arm_4')
        cmds.parent('R_Palm', 'R_arm_4')
    except:
        pass

    cmds.undoInfo(closeChunk=True)   

#improveArms()


def improveLegs():    

    cmds.undoInfo(openChunk=True)   

    cmds.delete(cmds.pointConstraint('L_RF_Heel', cmds.spaceLocator(n = 'L_Heel_LOC')))
    cmds.delete(cmds.pointConstraint('L_Ankle_JJ', cmds.spaceLocator(n = 'L_Ankle_LOC')))
    cmds.delete(cmds.pointConstraint('L_Knee_JJ', cmds.spaceLocator(n = 'L_Knee_LOC')))
    cmds.delete(cmds.pointConstraint('L_Leg_JJ', cmds.spaceLocator(n = 'L_Leg_LOC')))
    cmds.delete(cmds.pointConstraint('L_Fingers_JJ', cmds.spaceLocator(n = 'L_EndFoot_LOC')))
    cmds.delete(cmds.pointConstraint('L_Ball_JJ', cmds.spaceLocator(n = 'L_Ball_Loc')))
    cmds.delete(cmds.pointConstraint('L_RF_InFoot', cmds.spaceLocator(n = 'L_InFoot_Loc')))
    cmds.delete(cmds.pointConstraint('L_RF_OutFoot', cmds.spaceLocator(n = 'L_OutFoot_Loc')))

    cmds.delete('RdM_AutoLEGS')

    legsNodes = ('L_Leg_MultDiv01', 'L_Leg_MultDiv02', 'L_LegMultDiv', 'L_LegMultDiv00', 'R_Leg_MultDiv01', 'R_Leg_MultDiv02', 'R_LegMultDiv' ,'R_LegMultDiv00', 'Twist_L_Knee_JJ', 'Twist_L_Leg_JJ', 'Twist_R_Knee_JJ', 'Twist_R_Leg_JJ','L_Leg_normalize_MultDiv','R_Leg_normalize_MultDiv')

    for i in legsNodes:
        try:
            cmds.delete(i)
        except:
            pass
  

    cmds.undoInfo(closeChunk=True)   
    
#improveLegs()

def improveSpineHead(SpineAmount, mode ):   

    cmds.undoInfo(openChunk=True)   

    if cmds.objExists('Neck_JJ'):  
        cmds.delete(cmds.pointConstraint('Neck_JJ', cmds.spaceLocator(n = 'Neck_Start_LOC')))
        cmds.delete(cmds.pointConstraint('Head_End_JE', cmds.spaceLocator(n = 'Head_End_LOC')))
        cmds.delete(cmds.pointConstraint('Head_JJ', cmds.spaceLocator(n = 'Head_Start_LOC')))

    if mode == 'FK':
    
        if cmds.objExists('Spine_JntChest'):
            cmds.rename('Spine_JntChest', 'Spine_'+str(SpineAmount-1))
            cmds.rename('Spine_JntEnd', 'Spine_'+str(SpineAmount))
            
        #LastJoint
        cmds.delete(cmds.pointConstraint('Spine_ConnectToArms', cmds.spaceLocator(n = 'Spine_0'+str(SpineAmount)+'_LOC'), mo =False))
        #Pelvis
        cmds.delete(cmds.pointConstraint('ReverseSpine_JE', cmds.spaceLocator(n = 'Pelvis_Loc'), mo =False))
               
        for i in range(SpineAmount):
            try:
                cmds.delete(cmds.pointConstraint('Spine_'+str(i+1), cmds.spaceLocator(n = 'Spine_0'+str(i+1)+'_LOC')))
            except:
                pass
        
    else: #IK
        if cmds.objExists('Spine_JntChest'):
            cmds.rename('Spine_JntChest', 'Spine_'+str(SpineAmount-1))
            cmds.rename('Spine_JntEnd', 'Spine_'+str(SpineAmount))        

        #Pelvis
        cmds.delete(cmds.pointConstraint('ReverseSpine_JE', cmds.spaceLocator(n = 'Pelvis_Loc'), mo =False))
        
        for i in range(SpineAmount):
            try:
                cmds.delete(cmds.pointConstraint('Spine_'+str(i+1), cmds.spaceLocator(n = 'Spine_0'+str(i+1)+'_LOC')))
            except:
                pass


    spineNodes = ['CurveInfoSpine', 'NomralizeDivNode','StretchyDivNode','SquashInvPower','SquashDiv']
    
    for i in spineNodes:
        try:
            cmds.delete(i)
        except:
            pass

    cmds.delete('RdM_AutoSPINE')
    try:
        cmds.delete('RdM_ChickenHead')
    except:
        pass
        
    try :
        cmds.delete('Spine_0%s_LOC1'%(SpineAmount))
    except:
        pass
        
    #Rename Everything to new names
    
    cmds.rename('Spine_01_LOC', 'COG_LOC')
    cmds.rename('Spine_0%s_LOC'%(SpineAmount), 'Spine_END_LOC')
    cmds.rename('Spine_0%s_LOC'%(SpineAmount-1), 'Spine_CHEST_LOC')
    
    try:
        for i in range(SpineAmount-2):
            cmds.rename('Spine_0%s_LOC'%(i+2),'Belly_0%s_LOC'%(i+1) )
            print 'rename %s'%(i)
    except:
        pass 
        
    cmds.undoInfo(closeChunk=True)   

#improveSpineHead(SpineAmount = 7, mode = 'FK')

def improveHands():
    
    cmds.undoInfo(openChunk=True)   

    toDelete = ['L_Fingers','R_Fingers','R_Palm','L_Palm_CC']
    
    try:
        for i in toDelete:
            cmds.delete(i)
            
        cmds.parent('L_Palm', w=True) 
        
    except:
        pass
    
       

    cmds.undoInfo(closeChunk=True)   

#improveHands()   