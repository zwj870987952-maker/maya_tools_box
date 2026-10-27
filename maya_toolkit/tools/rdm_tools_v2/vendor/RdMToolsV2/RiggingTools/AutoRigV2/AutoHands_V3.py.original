'''
12/09/18
RdMAutoHands v2.0
By Esteban Rodriguez

www.renderdemartes.com
info@renderdemartes.com

import RdMAutoHandsv2
reload (RdMAutoHandsv2)
'''
from maya import cmds
import RdMToolsV2

#Joints

def CreateJoints (ThumbCheckOn=1,IndexCheckOn=1,MiddleCheckOn=1,RingCheckOn=1,PinkyCheckOn=1, *args):
    
    cmds.undoInfo(openChunk=True)   
    
    cmds.select (cl = True)

    cmds.joint (n ='L_Palm')
    cmds.select (cl = True)
    


    def genericFinger (name, phalanges,x,y,z,mult):
        cmds.select ('L_Palm')
        for f in range(phalanges):
            cmds.joint (n ='L_' + str (name) + '_' + str (f) + '_JJ')
            cmds.move(f*mult,0,0)
            cmds.move (x,y,z, r = True)
            cmds.setAttr ('L_' + str (name) + '_' + str (f) + '_JJ'+'.segmentScaleCompensate', 0)
            
        cmds.select (cl = True)
        
        
          
    if IndexCheckOn == 1: 
        genericFinger ('Index', 5,3,0,5,3)
    
     
    if (MiddleCheckOn): 
        genericFinger ('Middle', 5,3,0,0,5)
        
       
    if (RingCheckOn): 
        genericFinger ('Ring', 5,3,0,-5,4)
        
    if (PinkyCheckOn): 
        genericFinger ('Pinky', 5,3,0,-10,3)
        
        
           
    if (ThumbCheckOn): 
        genericFinger ('Thumb', 4,0,0,10,3)
        cmds.setAttr ('L_Thumb_0_JJ.rotateY', -90)

    if cmds.objExists ('L_arm_4'):
        ParentPalm= cmds.pointConstraint ('L_arm_4', 'L_Palm', mo =False)
        cmds.delete(ParentPalm)

    cmds.undoInfo(closeChunk=True)   


#Controladores

def CreateControllers (GlobalMultVar, *args):

    cmds.undoInfo(openChunk=True)   
    
############################
    GlobalMult  = GlobalMultVar*0.5
    
    #Radio Controlador
    radio = 1* GlobalMult
    
    cmds.mirrorJoint ('L_Palm', sr = ('L_','R_'), myz = True, mb = True)
    cmds.select(clear = True)
    #cmds.select('L_Palm','L_Palm', hi = True)
    #cmds.joint(e= True, zso=True, oj= "xzy", sao = "zdown")
    cmds.select(clear = True)    
    L_GrupoMano = cmds.group(n = "L_Fingers", w = True, em = True)
    R_GrupoMano = cmds.group(n = "R_Fingers", w = True, em = True)    
    jointList = []
    controllers = []
    
    def FingerControl(finger):
        
        def ControllersCreator (side):
                        
            if cmds.objExists (str(side)+ str (finger)+'_0_JJ'):
                
                X = 0

                while cmds.objExists(str(side)+ str (finger)+'_'+ str(X)+ '_JJ'):
                                    
                    JointDedo = str(side)+ str (finger)+'_'+ str(X)+ '_JJ'
                    Circulo = cmds.circle(r = radio, n = str(side)+ str (finger)+'_'+ str(X)+ '_CC', nr = (1,0,0))
                    controllers.append(Circulo[0])
                    CirculoControl = cmds.group(Circulo , n = str(side)+ str (finger)+'_'+ str(X)+ '_GRP')
                    ParentSet = cmds.parentConstraint(JointDedo, CirculoControl, mo = False)
                    cmds.delete(ParentSet)
                    cmds.parentConstraint (Circulo, JointDedo)
                    
                    if side == 'L_':
                        cmds.setAttr (str(side)+ str (finger)+'_'+ str(X)+ '_CC'+'.overrideEnabled', 1)
                        cmds.setAttr (str(side)+ str (finger)+'_'+ str(X)+ '_CC'+'.overrideColor', 6)
                    if side == 'R_':
                        cmds.setAttr (str(side)+ str (finger)+'_'+ str(X)+ '_CC'+'.overrideEnabled', 1)
                        cmds.setAttr (str(side)+ str (finger)+'_'+ str(X)+ '_CC'+'.overrideColor', 13)
                        
                    if cmds.objExists(str(side)+ str (finger)+'_'+ str(X - 1)+ '_CC'):
                        cmds.parent (CirculoControl,str(side)+ str (finger)+'_'+ str(X - 1)+ '_CC')
                    
                    
                    jointList.append (JointDedo)
                    
                    X = X + 1
                    
                    
                #Grupo Dedos    
                Grupo = cmds.group(n = str(side)+ str (finger)+ '_Group', w = True, em = True)
                cmds.parent(str(side)+ str (finger)+'_'+ str(0)+ '_GRP', Grupo)
                
                #GrupoMano
                cmds.parent(Grupo, str(side)+ "Fingers")
                
                #Delete last Controllers
                X = X -1 
                cmds.delete (str(side)+ str (finger) +'_'+ str (X)+ '_GRP')
                jointList.remove(str(side)+ str (finger) +'_'+ str (X)+ '_JJ')
                 
                
                    
        ControllersCreator("L_") 
        ControllersCreator("R_") 
                           
                
    FingerControl('Index')        
    FingerControl('Middle')
    FingerControl('Ring')        
    FingerControl('Pinky')
    FingerControl('Thumb')
    
    cmds.parent(L_GrupoMano, "L_Palm")
    cmds.parent(R_GrupoMano, "R_Palm")
    
    if cmds.objExists('L_arm_4'):
        cmds.parent('L_Palm','L_arm_4')
    
    if cmds.objExists('R_arm_4'):
        cmds.parent('R_Palm','R_arm_4')
    
    #Create Set
    cmds.select(jointList)
    cmds.select('L_Palm', 'R_Palm', add = True)    
    cmds.sets (n= 'BindThisToHands')    


    #Clean and automate Fingers
        #Create handShape
    LockThisAttrFingers = ['scaleX','scaleY','scaleZ', 'visibility']
        
    for L in LockThisAttrFingers:
        for i in controllers:
            try:
                cmds.setAttr(str(i)+'.'+str(L),lock = True, keyable = False, channelBox = False)        
            except:
                 pass
    
    from RdMToolsV2.RiggingTools.Curves.curveOnSelection import curveOnSelectionFunc
    reload (RdMToolsV2.RiggingTools.Curves.curveOnSelection)  

    cmds.select('L_Palm')  
    curveOnSelectionFunc(mode = 'Hand',Constraint = False)
    cmds.select('R_Palm')  
    curveOnSelectionFunc(mode = 'Hand',Constraint = False)
    
    cmds.parent('L_Palm_CC', 'L_Palm')
    cmds.parent('R_Palm_CC', 'R_Palm')
    cmds.setAttr("R_Palm_CC.rotateZ", -180)
    
    LockThisAttrHand = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ', 'visibility']
        
    HandControllers = ['L_Palm_CC','R_Palm_CC']    
    for L in LockThisAttrHand:
        for i in HandControllers:
            try:
                cmds.setAttr(str(i)+'.'+str(L),lock = True, keyable = False, channelBox = False)        
            except:
                 pass
        
    #AutoClose
    from RdMToolsV2.RiggingTools.Curves.RootAuto import  offsetGrp
    reload (RdMToolsV2.RiggingTools.Curves.RootAuto)   
    
    for i in controllers:
        try:
            cmds.select(i)
            offsetGrp()
        except:
            pass

    if cmds.objExists('L_Thumb_0_JJ'):        
        closeAttr = cmds.addAttr('L_Palm_CC', ln="ThumbClose", dv=0, at='double')
        cmds.setAttr('L_Palm_CC.ThumbClose', e=1, keyable=True)
        cmds.addAttr('R_Palm_CC', ln="ThumbClose", dv=0, at='double')
        cmds.setAttr('R_Palm_CC.ThumbClose', e=1, keyable=True)    
        for i in range(1,3):
            cmds.connectAttr('L_Palm_CC.ThumbClose', 'L_Thumb_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
        
        for i in range(1,3):
            cmds.connectAttr('R_Palm_CC.ThumbClose', 'R_Thumb_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
            
    if cmds.objExists('L_Index_0_JJ'):        
        cmds.addAttr('L_Palm_CC', ln="IndexClose", dv=0, at='double')
        cmds.setAttr('L_Palm_CC.IndexClose', e=1, keyable=True)
        cmds.addAttr('R_Palm_CC', ln="IndexClose", dv=0, at='double')
        cmds.setAttr('R_Palm_CC.IndexClose', e=1, keyable=True)
        for i in range(1,4):
            cmds.connectAttr('L_Palm_CC.IndexClose', 'L_Index_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
        for i in range(1,4):
            cmds.connectAttr('R_Palm_CC.IndexClose', 'R_Index_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
    
    if cmds.objExists('L_Middle_0_JJ'):        
        cmds.addAttr('L_Palm_CC', ln="MiddleClose", dv=0, at='double')
        cmds.setAttr('L_Palm_CC.MiddleClose', e=1, keyable=True)
        cmds.addAttr('R_Palm_CC', ln="MiddleClose", dv=0, at='double')
        cmds.setAttr('R_Palm_CC.MiddleClose', e=1, keyable=True)
        for i in range(1,4):
            cmds.connectAttr('L_Palm_CC.MiddleClose', 'L_Middle_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
        for i in range(1,4):
            cmds.connectAttr('R_Palm_CC.MiddleClose', 'R_Middle_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
            
    if cmds.objExists('L_Ring_0_JJ'):        
        cmds.addAttr('L_Palm_CC', ln="RingClose", dv=0, at='double')
        cmds.setAttr('L_Palm_CC.RingClose', e=1, keyable=True)
        cmds.addAttr('R_Palm_CC', ln="RingClose", dv=0, at='double')
        cmds.setAttr('R_Palm_CC.RingClose', e=1, keyable=True)
        for i in range(1,4):
            cmds.connectAttr('L_Palm_CC.RingClose', 'L_Ring_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
        for i in range(1,4):
            cmds.connectAttr('R_Palm_CC.RingClose', 'R_Ring_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
    
    if cmds.objExists('L_Pinky_0_JJ'):        
        cmds.addAttr('L_Palm_CC', ln="PinkyClose", dv=0, at='double')
        cmds.setAttr('L_Palm_CC.PinkyClose', e=1, keyable=True)
        cmds.addAttr('R_Palm_CC', ln="PinkyClose", dv=0, at='double')
        cmds.setAttr('R_Palm_CC.PinkyClose', e=1, keyable=True)    
        for i in range(1,4):
            cmds.connectAttr('L_Palm_CC.PinkyClose', 'L_Pinky_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
        for i in range(1,4):
            cmds.connectAttr('R_Palm_CC.PinkyClose', 'R_Pinky_'+str(i)+'_CC_Offset_Grp.rotateZ', f = True)
                  
    if cmds.objExists('L_arm_IK_CC'):
        cmds.parent('L_Arm_FKIK_BlendShape','L_Palm_CC',s= True, add=True)
     

    if cmds.objExists('R_arm_IK_CC'):
        cmds.parent('R_Arm_FKIK_BlendShape','R_Palm_CC',s= True, add=True)
                   
                    
    
    
    cmds.select (cl = True)


    cmds.undoInfo(closeChunk=True)   

