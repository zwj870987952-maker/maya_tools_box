#Create joints for game!

gameJoints = ['COG', 'Spine_1','Spine_2','Spine_3','Spine_4','Head_Start_JJ','Neck_Start_JJ','ReverseSpine_JJ',
                'L_arm_1','L_arm_2_Twist_0','L_arm_3_Twist_0','L_arm_3_Twist_2',
                'R_arm_1','R_arm_2_Twist_0','R_arm_3_Twist_0','R_arm_3_Twist_2',
                'L_Palm','R_Palm',
                #'L_Index_1_JJ','L_Index_2_JJ','L_Index_3_JJ',
                #'R_Index_1_JJ','R_Index_2_JJ','R_Index_3_JJ',
                #'L_Middle_1_JJ','L_Middle_2_JJ','L_Middle_3_JJ',
                #'R_Middle_1_JJ','R_Middle_2_JJ','R_Middle_3_JJ',
                #'L_Ring_1_JJ','L_Ring_2_JJ','L_Ring_3_JJ',
                #'R_Ring_1_JJ','R_Ring_2_JJ','R_Ring_3_JJ',
                #'L_Pinky_1_JJ','L_Pinky_2_JJ','L_Pinky_3_JJ',
                #'R_Pinky_1_JJ','R_Pinky_2_JJ','R_Pinky_3_JJ',
                #'L_Thumb_0_JJ','L_Thumb__JJ','L_Thumb_3_JJ',
                #'R_Thumb_0_JJ','R_Thumb_1_JJ','R_Thumb_3_JJ',
                
                'L_Leg_JJ_Twist_0','L_Knee_JJ_Twist_0','L_Ankle_JJ','L_Ball_JJ',
                'R_Leg_JJ_Twist_0','R_Knee_JJ_Twist_0','R_Ankle_JJ','R_Ball_JJ']

for i in gameJoints:
    cmds.select(cl = True)
    try:
        if cmds.objExists(i):
            newJoint = cmds.joint(n = str(i)+'_Game')
        cmds.parentConstraint(i, newJoint, mo =False)
        cmds.setAttr(newJoint + '.segmentScaleCompensate',0)
    except:
        pass

cmds.select(cl = True)
cmds.joint(n = 'root')
cmds.setAttr('root.segmentScaleCompensate', 0)

try:
    cmds.parent('L_Index_0_JJ','L_Palm_Game')
except:
    pass
try:
    cmds.parent('L_Middle_0_JJ','L_Palm_Game')
except:
    pass
try:
    cmds.parent('L_Ring_0_JJ','L_Palm_Game')
except:
    pass
try:
    cmds.parent('L_Pinky_0_JJ','L_Palm_Game')
except:
    pass
try:
    cmds.parent('L_Thumb_0_JJ','L_Palm_Game')
except:
    pass


try:
    cmds.parent('R_Index_0_JJ','R_Palm_Game')
except:
    pass
try:
    cmds.parent('R_Middle_0_JJ','R_Palm_Game')
except:
    pass
try:
    cmds.parent('R_Ring_0_JJ','R_Palm_Game')
except:
    pass
try:
    cmds.parent('R_Pinky_0_JJ','R_Palm_Game')
except:
    pass
try:
    cmds.parent('R_Thumb_0_JJ','R_Palm_Game')
except:
    pass
    
cmds.parent('COG_Game','root')
    
cmds.parent('Spine_2_Game','Spine_1_Game')
cmds.parent('Spine_3_Game','Spine_2_Game')
cmds.parent('Spine_4_Game','Spine_3_Game')
cmds.parent('Head_Start_JJ_Game','Neck_Start_JJ_Game')
cmds.parent('Neck_Start_JJ_Game', 'Spine_4_Game')
  
cmds.parent('Spine_1_Game','COG_Game')
cmds.parent('ReverseSpine_JJ_Game','COG_Game')


cmds.parent('L_arm_1_Game','Spine_4_Game')  
cmds.parent('L_arm_2_Twist_0_Game','L_arm_1_Game')
cmds.parent('L_arm_3_Twist_0_Game','L_arm_2_Twist_0_Game')
cmds.parent('L_arm_3_Twist_2_Game','L_arm_3_Twist_0_Game')
cmds.parent('L_Palm_Game','L_arm_3_Twist_2_Game')
  
cmds.parent('R_arm_1_Game','Spine_4_Game')  
cmds.parent('R_arm_2_Twist_0_Game','R_arm_1_Game')
cmds.parent('R_arm_3_Twist_0_Game','R_arm_2_Twist_0_Game')
cmds.parent('R_arm_3_Twist_2_Game','R_arm_3_Twist_0_Game')
cmds.parent('R_Palm_Game','R_arm_3_Twist_2_Game')
    
    
cmds.parent('L_Leg_JJ_Twist_0_Game','ReverseSpine_JJ_Game')
cmds.parent('L_Knee_JJ_Twist_0_Game','L_Leg_JJ_Twist_0_Game')
cmds.parent('L_Ankle_JJ_Game','L_Knee_JJ_Twist_0_Game')
cmds.parent('L_Ball_JJ_Game','L_Ankle_JJ_Game')

cmds.parent('R_Leg_JJ_Twist_0_Game','ReverseSpine_JJ_Game')
cmds.parent('R_Knee_JJ_Twist_0_Game','R_Leg_JJ_Twist_0_Game')
cmds.parent('R_Ankle_JJ_Game','R_Knee_JJ_Twist_0_Game')
cmds.parent('R_Ball_JJ_Game','R_Ankle_JJ_Game')
 