'''
12/9/18
RdMAutoComplete v1.0
By Esteban Rodriguez

www.renderdemartes.com
info@renderdemartes.com

import RdMAutoComplete
reload (RdMAutoComplete)
'''

from maya import cmds



#Create Maser Controllers

def MasterControl (CharacterNameVar, ControlScaleVar,*args):   
 
    Character = CharacterNameVar
    ControlScale = ControlScaleVar
    
    cmds.circle (nr = (0,1,0), n = str (Character) + '_MasterControl', r = ControlScale)
    cmds.group (str (Character) + '_MasterControl' ,n = str (Character) + '_MasterControl_GRP')
    cmds.circle (nr = (0,1,0), n = str (Character) + '_MoveControl', r = ControlScale/1.5)
    cmds.group (str (Character) + '_MoveControl' ,n = str (Character) + '_MoveControl_GRP')
    cmds.group (str (Character) + '_MasterControl_GRP', n = Character + '_RdM Autorig')
    cmds.parent (str (Character) + '_MoveControl_GRP', str (Character) + '_MasterControl')
    cmds.setAttr(str (Character) + '_MoveControl'  + "Shape.overrideEnabled", True )
    cmds.setAttr(str (Character) + '_MoveControl'+ "Shape.overrideColor", 17 )
    cmds.setAttr(str (Character) + '_MasterControl' + "Shape.overrideEnabled", True )
    cmds.setAttr(str (Character) + '_MasterControl' + "Shape.overrideColor", 16 )

        
#Parent to MASTER CONTROL

        
def ConnectSpine (CharacterNameVar,*args):      
    if cmds.objExists ('RdM_AutoSPINE'):
        Character = CharacterNameVar
        cmds.parent ('RdM_AutoSPINE', str (Character) + '_MoveControl') 
          
def ConnectLegs (CharacterNameVar,*args):      
    if cmds.objExists ('RdM_AutoLEGS'):
        Character = CharacterNameVar
        if cmds.objExists ('IK_FK_CC'):
            Character = CharacterNameVar
            Papa = cmds.listRelatives ('IK_FK_CC',c= True, p = True)
            if Papa < 1:
                cmds.parent ('IK_FK_CC', str (Character) + '_MoveControl' )
                
        cmds.parent ('RdM_AutoLEGS', str (Character) + '_MoveControl' )    
        cmds.parentConstraint ('ReverseSpine_JE','L_Leg_FK_CCGRP', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','R_Leg_FK_CCGRP', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','L_Leg_IK', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','R_Leg_IK', mo = True)  
                  
def ConnectArms (CharacterNameVar,*args):          
    if cmds.objExists ('RdM_AutoARMS'):
        Character = CharacterNameVar
        if cmds.objExists ('IK_FK_CC'):
            Character = CharacterNameVar
            Papa = cmds.listRelatives ('IK_FK_CC',c= True, p = True)
            if Papa < 1:
                cmds.parent ('IK_FK_CC', str (Character) + '_MoveControl' )
                
        cmds.parent ('RdM_AutoARMS', str (Character) + '_MoveControl' )  
        cmds.parentConstraint ('Spine_ConnectToArms','L_clavicule_01_GRP' , mo = True)    
        cmds.parentConstraint ('Spine_ConnectToArms','R_clavicule_01_GRP' , mo = True)
  
def ConnectHead (CharacterNameVar,*args):     
    if cmds.objExists ('RdM_ChickenHead'):
            Character = CharacterNameVar 
            cmds.parent ('RdM_ChickenHead', str (Character) + '_MoveControl' )   


