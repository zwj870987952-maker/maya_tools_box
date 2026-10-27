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
    cmds.undoInfo(openChunk=True)   
 
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

    #lock Attr
    LockThisAttrIK = ['sx','sy','sz', 'v']
    controllers = [str (Character) + '_MoveControl']     
    for L in LockThisAttrIK:
        for i in controllers:
            cmds.setAttr(str(i)+'.'+str(L),lock = True, keyable = False, channelBox = False)
           
    cmds.undoInfo(closeChunk=True)   
        
#Parent to MASTER CONTROL

        
def ConnectSpine (CharacterNameVar,*args):
    
    cmds.undoInfo(openChunk=True)   
      
    if cmds.objExists ('RdM_AutoSPINE'):
        Character = CharacterNameVar
        cmds.parent ('RdM_AutoSPINE', str (Character) + '_MoveControl') 


    def MultiplyDiveNode(Name, mode, *args):
        cmds.shadingNode('multiplyDivide', asUtility=True, name=Name)
        cmds.setAttr(str(Name)+'.operation', mode)
    
   

    #Curve info


    if cmds.objExists('Spine_CV'):
        Curveinfonode = cmds.shadingNode('curveInfo', asUtility=True, name= 'CurveInfoSpine') 
        cmds.connectAttr ('Spine_CV.worldSpace[0]', str(Curveinfonode)+'.inputCurve', f = True)
        ArcLenght = cmds.arclen( 'Spine_CV' )
        print ArcLenght   
    elif cmds.objExists('curveShape1'):
        Curveinfonode = cmds.shadingNode('curveInfo', asUtility=True, name= 'CurveInfoSpine') 
        cmds.connectAttr ('curveShape1.worldSpace[0]', str(Curveinfonode)+'.inputCurve', f = True)
        ArcLenght = cmds.arclen( 'curveShape1' )
        print ArcLenght
         
    #Normalize
    
    NormalizeDiv = MultiplyDiveNode('NomralizeDivNode', 2)
    cmds.connectAttr ('CurveInfoSpine.arcLength', 'NomralizeDivNode.input1X.', f = True)
    cmds.connectAttr (str(Character) + '_MasterControl.scaleX', 'NomralizeDivNode.input2X.', f = True)
    
    print 'DoneNormalize'         
    
    
    #StretchyDiv
        
    StretchyDiv = MultiplyDiveNode('StretchyDivNode', 2)
    cmds.shadingNode('floatConstant', asUtility=True, name='ArcLenghtNode')
    cmds.setAttr ('ArcLenghtNode.inFloat', ArcLenght)
    cmds.connectAttr ('NomralizeDivNode.outputX', 'StretchyDivNode.input1X.', f = True)
    cmds.connectAttr ('ArcLenghtNode.outFloat', 'StretchyDivNode.input2X.', f = True)
    
    print 'DoneStretchyDiv'         
    
 
    #Squash Inv Power 
    
    SquashInvPower = MultiplyDiveNode('SquashInvPower', 3)
    cmds.connectAttr ('StretchyDivNode.outputX', 'SquashInvPower.input1X.', f = True)
    cmds.shadingNode('floatConstant', asUtility=True, name='05invPower')
    cmds.setAttr ('invPower.inFloat', 0.5)
    cmds.connectAttr ('invPower.outFloat', 'SquashInvPower.input2X.', f = True)
     
    print 'DoneInvPower'         
    
    
    #Squash Div
    
    SquashDiv = MultiplyDiveNode('SquashDiv', 2)
    cmds.connectAttr ('SquashInvPower.outputX', 'SquashDiv.input2X.', f = True)
    cmds.shadingNode('floatConstant', asUtility=True, name='SquashConstantDiv')
    cmds.setAttr ('SquashConstantDiv.inFloat', 1)
    cmds.connectAttr ('SquashConstantDiv.outFloat', 'SquashDiv.input1X', f = True)
     
    print 'DoneSquashDiv'         
     
    #ConnectStretchy to Joints
    if cmds.objExists('Spine_1'):  #Renaming in autoSpine v2
        X = 1
    elif cmds.objExists('Spine_1_Belly'):
        X = 2
        
    while cmds.objExists('Spine_'+str(X)):
        cmds.connectAttr('StretchyDivNode.outputX', 'Spine_'+str(X)+'.scaleX')
        cmds.connectAttr('SquashDiv.outputX', 'Spine_'+str(X)+'.scaleY')
        cmds.connectAttr('SquashDiv.outputX', 'Spine_'+str(X)+'.scaleZ')
        X = X+1
    
    print 'Done'         

    cmds.undoInfo(closeChunk=True)   

              
def ConnectLegs (CharacterNameVar,*args):   
   
    cmds.undoInfo(openChunk=True)   
    
    if cmds.objExists ('RdM_AutoLEGS'):
        Character = CharacterNameVar
        
        try :
            cmds.parent ('RdM_AutoLEGS', str (Character) + '_MoveControl' )    
        except:
            pass
        cmds.parentConstraint ('ReverseSpine_JE','L_Leg_JJ_FK_GRP', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','R_Leg_JJ_FK_GRP', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','L_Leg_JJ_IK', mo = True)    
        cmds.parentConstraint ('ReverseSpine_JE','R_Leg_JJ_IK', mo = True)  
        cmds.parentConstraint ('ReverseSpine_JE','L_Leg_JJ_IK_Stretchy01', mo = True)  
        cmds.parentConstraint ('ReverseSpine_JE','R_Leg_JJ_IK_Stretchy01', mo = True)  
        
        
        if cmds.objExists ('L_Leg_Bind_Jnt1'):
            for i in range(1,14):
                    cmds.connectAttr(str(Character) + '_MasterControl.scale','L_Leg_Bind_Jnt'+str(i)+'.scale', f = True)    
            for i in range(1,14):
                    cmds.connectAttr(str(Character) + '_MasterControl.scale','R_Leg_Bind_Jnt'+str(i)+'.scale', f = True)    

    NormalizeL = cmds.shadingNode('multiplyDivide', asUtility=True, n='L_Leg_normalize_MultDiv')
    cmds.setAttr('L_Leg_normalize_MultDiv.operation', 2)

    cmds.connectAttr(str(Character) + '_MasterControl.scaleX','L_Leg_normalize_MultDiv.input2X')
    
    cmds.connectAttr('L_Leg_Distance.distance','L_Leg_normalize_MultDiv.input1X', f= True)     
    cmds.connectAttr('L_Leg_normalize_MultDiv.outputX','L_LegMultDiv.input1X', f= True)     
    cmds.connectAttr('L_Leg_normalize_MultDiv.outputX','L_LegMultDiv00.input1X', f= True)     

    NormalizeR = cmds.shadingNode('multiplyDivide', asUtility=True, n='R_Leg_normalize_MultDiv')
    cmds.setAttr('R_Leg_normalize_MultDiv.operation', 2)

    cmds.connectAttr(str(Character) + '_MasterControl.scaleX','R_Leg_normalize_MultDiv.input2X')
    
    cmds.connectAttr('R_Leg_Distance.distance','R_Leg_normalize_MultDiv.input1X', f= True)     
    cmds.connectAttr('R_Leg_normalize_MultDiv.outputX','R_LegMultDiv.input1X', f= True)     
    cmds.connectAttr('R_Leg_normalize_MultDiv.outputX','R_LegMultDiv00.input1X', f= True)     
       
    cmds.undoInfo(closeChunk=True)   

                  
def ConnectArms (CharacterNameVar,*args):          
    cmds.undoInfo(openChunk=True)   

    if cmds.objExists ('RdM_AutoARMS'):
        Character = CharacterNameVar
        
        try:
            cmds.parent ('RdM_AutoARMS', str(Character) + '_MoveControl' )  
        except:
            pass
        cmds.parentConstraint ('Spine_ConnectToArms','L_Clavicule_CC_GRP' , mo = True)    
        cmds.parentConstraint ('Spine_ConnectToArms','R_Clavicule_CC_GRP' , mo = True)
  
  
        if cmds.objExists ('L_Arm_Bind_Jnt1'):  
            for i in range(1,14):
                cmds.connectAttr(str(Character) + '_MasterControl.scale','L_Arm_Bind_Jnt'+str(i)+'.scale', f = True)    
            for i in range(1,14):
                cmds.connectAttr(str(Character) + '_MasterControl.scale','R_Arm_Bind_Jnt'+str(i)+'.scale', f = True)                        
   
    Normalize0L = cmds.shadingNode('multiplyDivide', asUtility=True, n='L_Arm_normalize_MultDiv')
    cmds.setAttr('L_Arm_normalize_MultDiv.operation', 2)

    cmds.connectAttr(str(Character) + '_MasterControl.scaleX','L_Arm_normalize_MultDiv.input2X')

    cmds.connectAttr('L_Arm_Distance.distance','L_Arm_normalize_MultDiv.input1X', f= True)     
    cmds.connectAttr('L_Arm_normalize_MultDiv.outputX','L_ArmMultDiv.input1X', f= True)     
    cmds.connectAttr('L_Arm_normalize_MultDiv.outputX','L_ArmMultDiv00.input1X', f= True)     

    Normalize0R = cmds.shadingNode('multiplyDivide', asUtility=True, n='R_Arm_normalize_MultDiv')
    cmds.setAttr('R_Arm_normalize_MultDiv.operation', 2)

    cmds.connectAttr(str(Character) + '_MasterControl.scaleX','R_Arm_normalize_MultDiv.input2X')

    cmds.connectAttr('R_Arm_Distance.distance','R_Arm_normalize_MultDiv.input1X', f= True)     
    cmds.connectAttr('R_Arm_normalize_MultDiv.outputX','R_ArmMultDiv.input1X', f= True)     
    cmds.connectAttr('R_Arm_normalize_MultDiv.outputX','R_ArmMultDiv00.input1X', f= True)     
  
   
    cmds.undoInfo(closeChunk=True)   
     
  
def ConnectHead (CharacterNameVar,*args):     
    cmds.undoInfo(openChunk=True)   
   
    if cmds.objExists ('RdM_ChickenHead'):
            Character = CharacterNameVar 
            cmds.parent ('RdM_ChickenHead', str (Character) + '_MoveControl' )   

    cmds.undoInfo(closeChunk=True)   

