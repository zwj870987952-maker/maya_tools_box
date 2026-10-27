from maya import cmds

def BindSkin (*args):
    
    cmds.undoInfo(openChunk=True)   
   

    Geo = cmds.ls (sl = True) 
    
    if len(Geo) == 0:
        cmds.warning('Select GEO before continue')
    
    else:
        print Geo[0]

        if cmds.objExists('BindThisToSpine'):
            cmds.select ('BindThisToSpine', tgl = True)
        
        if cmds.objExists('BindThisToArms'):
            cmds.select ('BindThisToArms', tgl = True)
            
        if cmds.objExists('BindThisToLegs'):
            cmds.select ('BindThisToLegs', tgl = True)

        if cmds.objExists('BindThisToHands'):
            cmds.select ('BindThisToHands', tgl = True)

        if cmds.objExists('BindThisToHead'):
            cmds.select ('BindThisToHead', tgl = True)
            
            
        if cmds.objExists('BindThisTo_Twist_L_Arm'):
            cmds.select ('BindThisTo_Twist_L_Arm', tgl = True)
        if cmds.objExists('BindThisTo_Twist_R_Arm'):
            cmds.select ('BindThisTo_Twist_R_Arm', tgl = True)                        
        if cmds.objExists('BindThisTo_L_Arm_Ribbon'):
            cmds.select ('BindThisTo_L_Arm_Ribbon', tgl = True)
        if cmds.objExists('BindThisTo_R_Arm_Ribbon'):
            cmds.select ('BindThisTo_R_Arm_Ribbon', tgl = True)                        

        if cmds.objExists('BindThisTo_Twist_L_Leg'):
            cmds.select ('BindThisTo_Twist_L_Leg', tgl = True)
        if cmds.objExists('BindThisTo_Twist_R_Leg'):
            cmds.select ('BindThisTo_Twist_R_Leg', tgl = True)                        
        if cmds.objExists('BindThisTo_L_Leg_Ribbon'):
            cmds.select ('BindThisTo_L_Leg_Ribbon', tgl = True)
        if cmds.objExists('BindThisTo_R_Leg_Ribbon'):
            cmds.select ('BindThisTo_R_Leg_Ribbon', tgl = True)    
                       
            
        Joints = cmds.ls (sl = True)
        cmds.skinCluster (Joints, Geo, tsb = True, bm = 0, sm = 1, nw = 1)  
            

    cmds.undoInfo(closeChunk=True)   
    
     

