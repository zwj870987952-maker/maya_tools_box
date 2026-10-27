'''
09/10/18
RdMAutoLegs v1.0
By Esteban Rodriguez

www.renderdemartes.com
info@renderdemartes.com

import RdMAutoLegs
reload (RdMAutoLegs)
'''

from maya import cmds 

  

###JOINTS LOCATORS

jointsNum = 4

def LocatorsBtn(*args):

    cmds.undoInfo(openChunk=True)   

    for X in range (jointsNum):
    
        cmds.select (clear = True)        
        cmds.CreateLocator ()
        cmds.move (0,2.5*X, 0)
        cmds.select (clear = True)
           
    cmds.rename ("locator4","L_Leg_LOC")
    cmds.rename ("locator3","L_Knee_LOC")
    cmds.rename ("locator2","L_Ankle_LOC")
    cmds.rename ("locator1","L_Heel_LOC")
    
    cmds.duplicate ('L_Heel_LOC', n= 'L_EndFoot_LOC')
    cmds.duplicate ('L_Heel_LOC', n= 'L_Ball_Loc')
    cmds.move (0,0,3, 'L_Ball_Loc' )
    cmds.move (0,0,5, 'L_EndFoot_LOC' )
    cmds.move (0,5,0.3, 'L_Knee_LOC')

         
    cmds.select (clear = True)  
    
    cmds.undoInfo(closeChunk=True)   
             
    
def JointsBtn(*args):  

    cmds.undoInfo(openChunk=True)   


    cmds.rename ("L_Leg_LOC","locator1")
    cmds.rename ("L_Knee_LOC","locator2")
    cmds.rename ("L_Ankle_LOC","locator3")
    cmds.rename ("L_Ball_Loc","locator4")
    cmds.rename ("L_EndFoot_LOC","locator5")
    cmds.rename ("L_Heel_LOC","locator6")

    
    
    cmds.select (cl=True)
    for X in range (1,jointsNum + 2):  
                
        cmds.joint (n = "L_leg_" + str(X))
        cmds.select ("L_leg_" + str(X))
        cmds.pointConstraint ("locator" + str (X) , "L_leg_" + str(X))
        cmds.delete ("L_leg_" + str(X) + "_pointConstraint1")
        cmds.setAttr ("L_leg_" + str(X) + ".displayLocalAxis", 1)
        

        
    cmds.select (clear = True)
        
    for X in range (6,2,-1):  
        
        cmds.joint (n = "Reverse_Foot_" + str(X))
        cmds.pointConstraint ("locator" + str (X) , "Reverse_Foot_" + str(X))
        cmds.delete ("Reverse_Foot_" + str(X) + "_pointConstraint1")
        cmds.delete ("locator" + str (X))
      
          
    cmds.delete ('locator1','locator2') 
     
    cmds.rename ('Reverse_Foot_6','L_RF_Heel')
    cmds.rename ('Reverse_Foot_5','L_RF_Fingers') 
    cmds.rename ('Reverse_Foot_4','L_RF_Ball') 
    cmds.rename ('Reverse_Foot_3','L_RF_Ankle') 
    
    cmds.rename ('L_leg_1','L_Leg_JJ')
    cmds.rename ('L_leg_2','L_Knee_JJ') 
    cmds.rename ('L_leg_3','L_Ankle_JJ') 
    cmds.rename ('L_leg_4','L_Ball_JJ') 
    cmds.rename ('L_leg_5','L_Fingers_JJ')
    
    cmds.select ('L_Leg_JJ', 'L_Knee_JJ', 'L_Ankle_JJ', 'L_Ball_JJ', 'L_Fingers_JJ','L_RF_Ball')
    cmds.joint(e= True, zso=True, oj= "yxz", sao = "zup", ch=True) 
    
    cmds.select ( 'L_RF_Heel', 'L_RF_Fingers', 'L_RF_Ankle')
    cmds.joint(e= True, zso=True, oj= "xyz", sao = "zup", ch=True)     
       
    cmds.select (clear = True)
    

    cmds.undoInfo(closeChunk=True)   
		
    
def IKFK(GlobalMultVar, *args):  

    cmds.undoInfo(openChunk=True)   

    #Mirror Joints
    cmds.select ( 'L_RF_Heel', 'L_RF_Fingers', 'L_RF_Ankle', 'L_Leg_JJ', 'L_Knee_JJ', 'L_Ankle_JJ', 'L_Ball_JJ', 'L_Fingers_JJ','L_RF_Ball')    
    HideAxis = cmds.ls( selection=True )
    
    for jnt in HideAxis:

        cmds.setAttr (jnt + ".displayLocalAxis", 0)
     
     
    cmds.duplicate ("L_Leg_JJ", rc = True)
    cmds.duplicate ("L_Leg_JJ", rc = True)
    
    cmds.rename ("L_Leg_JJ1", "L_Leg_FK")
    cmds.rename ("L_Knee_JJ1", "L_Knee_FK")
    cmds.rename ("L_Ankle_JJ1", "L_Ankle_FK")
    cmds.rename ("L_Ball_JJ1", "L_Ball_FK")
    cmds.rename ("L_Fingers_JJ1", "L_Fingers_FK")
      
    
    cmds.rename ("L_Leg_JJ2", "L_Leg_IK")
    cmds.rename ("L_Knee_JJ2", "L_Knee_IK")
    cmds.rename ("L_Ankle_JJ2", "L_Ankle_IK")
    cmds.rename ("L_Ball_JJ2", "L_Ball_IK")
    cmds.rename ("L_Fingers_JJ2", "L_Fingers_IK")
      
    
    cmds.mirrorJoint ('L_Leg_JJ',mirrorYZ = True, mirrorBehavior = True, searchReplace=('L_', 'R_'))
    cmds.mirrorJoint ('L_RF_Heel',mirrorYZ = True, mirrorBehavior = True, searchReplace=('L_', 'R_'))
    cmds.mirrorJoint ('L_Leg_FK',mirrorYZ = True, mirrorBehavior = True, searchReplace=('L_', 'R_'))
    cmds.mirrorJoint ('L_Leg_IK',mirrorYZ = True, mirrorBehavior = True, searchReplace=('L_', 'R_'))
   
   
    #IK
    GlobalMult  = GlobalMultVar * 2
    radio =  GlobalMult 
    
        
    cmds.ikHandle (n="L_LegIKrp", sj="L_Leg_IK", ee= "L_Ankle_IK", sol='ikRPsolver')
    cmds.ikHandle (n="L_AnkleIKsch", sj="L_Ankle_IK", ee= "L_Ball_IK", sol = 'ikSCsolver')
    cmds.ikHandle (n="L_BallIKsch", sj="L_Ball_IK", ee= "L_Fingers_IK", sol = 'ikSCsolver')

    cmds.ikHandle (n="R_LegIKrp", sj="R_Leg_IK", ee= "R_Ankle_IK", sol='ikRPsolver')
    cmds.ikHandle (n="R_AnkleIKsch", sj="R_Ankle_IK", ee= "R_Ball_IK", sol = 'ikSCsolver')
    cmds.ikHandle (n="R_BallIKsch", sj="R_Ball_IK", ee= "R_Fingers_IK", sol = 'ikSCsolver')
    
    cmds.curve(n="L_LegIK_CC" , d=1, p=[(1, 1, 1),(1,1,-1) ,(1, -1, -1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, 1, 1) ,(1, 1, 1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, -1, -1) ,(-1, 1, -1) ,(1, 1, -1) ,(1, -1, -1) ,(-1, -1, -1) ,(-1, 1, -1) ,(-1, 1, 1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
    cmds.group ("L_LegIK_CC", n= "L_LegIK_GRP")
    cmds.pointConstraint ("L_Ball_JJ", "L_LegIK_GRP")
    cmds.delete ("L_LegIK_GRP_pointConstraint1")
    cmds.orientConstraint ("L_Ball_JJ", "L_LegIK_GRP")
    cmds.delete ("L_LegIK_GRP_orientConstraint1")  
      
    cmds.duplicate ('L_LegIK_CC',n='R_LegIK_CC')
    cmds.group ("R_LegIK_CC", n= "R_LegIK_GRP")
    cmds.parent ('R_LegIK_GRP', w = True)
    cmds.group(n = 'R_LegIK_GRP2', em = True)
    cmds.parent ('R_LegIK_GRP','R_LegIK_GRP2')
    cmds.setAttr('R_LegIK_GRP2.scaleX',-1)

     
    cmds.scale(GlobalMult,GlobalMult,GlobalMult,'L_LegIK_GRP', r = True)
    cmds.scale(GlobalMult,GlobalMult,GlobalMult,'R_LegIK_GRP', r = True)

    cmds.setAttr ("L_LegIK_CC.overrideEnabled", 1)
    cmds.setAttr ("R_LegIK_CC.overrideEnabled", 1)

    cmds.setAttr ("L_LegIK_CC.overrideColor", 6)
    cmds.setAttr ("R_LegIK_CC.overrideColor", 13)   

    #FK
    GlobalMult  = GlobalMult
    radio =  GlobalMult
    
    cmds.select ( 'L_Leg_FK', 'L_Knee_FK', 'L_Ankle_FK', 'R_Leg_FK', 'R_Knee_FK' ,'R_Ankle_FK','L_Ball_FK','R_Ball_FK')    
    FKCircle = cmds.ls( selection=True )
    
    for FK in FKCircle:    
     
        cmds.circle (n= FK + str ('_CC'), r= radio, nr=(0, 1, 0))
        cmds.group (n= FK + str ('_CC') + str ('GRP'))
        cmds.pointConstraint (FK, FK + str ('_CC') + str ('GRP'), mo= False)
        cmds.orientConstraint (FK, FK + str ('_CC') + str ('GRP'), mo= False)
        cmds.delete (FK + str ('_CC') + str ('GRP')+str('_pointConstraint1'))
        cmds.delete (FK + str ('_CC') + str ('GRP')+str('_orientConstraint1'))
        cmds.orientConstraint (FK + str ('_CC'),FK , mo= True)
        cmds.pointConstraint (FK + str ('_CC'),FK , mo= True)
        cmds.setAttr (FK + str ('_CC')+ str ('Shape.overrideEnabled'), 1)
        cmds.setAttr (FK + str ('_CC')+ str ('Shape.overrideColor'), 6)
        
    cmds.setAttr ('R_Leg_FK_CCShape.overrideColor',13)
    cmds.setAttr ('R_Knee_FK_CCShape.overrideColor',13)
    cmds.setAttr ('R_Ankle_FK_CCShape.overrideColor',13)
    cmds.setAttr ('R_Ball_FK_CCShape.overrideColor',13)
    
    cmds.parent ('L_Knee_FK_CCGRP','L_Leg_FK_CC')
    cmds.parent ('L_Ankle_FK_CCGRP','L_Knee_FK_CC')
    cmds.parent ('L_Ball_FK_CCGRP','L_Ankle_FK_CC')
    cmds.parent ('R_Knee_FK_CCGRP','R_Leg_FK_CC')
    cmds.parent ('R_Ankle_FK_CCGRP','R_Knee_FK_CC')
    cmds.parent ('R_Ball_FK_CCGRP','R_Ankle_FK_CC')
                
    #ReverseFoot
    
    cmds.parent ('L_RF_Heel','L_LegIK_CC')
    cmds.parent ('L_LegIKrp','L_RF_Ankle')   
    cmds.parent ('L_AnkleIKsch','L_RF_Ball')
    cmds.parent ('L_BallIKsch','L_RF_Fingers')
    
    cmds.parent ('R_RF_Heel','R_LegIK_CC')
    cmds.parent ('R_LegIKrp','R_RF_Ankle')   
    cmds.parent ('R_AnkleIKsch','R_RF_Ball')
    cmds.parent ('R_BallIKsch','R_RF_Fingers')
        
    cmds.addAttr ('L_LegIK_CC', ln= 'RollHeel', at= 'double' , dv = 0 )
    cmds.setAttr ('L_LegIK_CC.RollHeel', k = True)  
    cmds.connectAttr ('L_LegIK_CC.RollHeel','L_RF_Heel.rotateZ')  
    cmds.addAttr ('L_LegIK_CC', ln= 'TwistHeel', at= 'double' , dv = 0 )
    cmds.setAttr ('L_LegIK_CC.TwistHeel', k = True)
    cmds.connectAttr ('L_LegIK_CC.TwistHeel','L_RF_Heel.rotateY')  
    cmds.addAttr ('L_LegIK_CC', ln= 'RollBall', at= 'double' , dv = 0 )
    cmds.setAttr ('L_LegIK_CC.RollBall', k = True)
    cmds.connectAttr ('L_LegIK_CC.RollBall','L_RF_Ball.rotateZ')  
    cmds.addAttr ('L_LegIK_CC', ln= 'TwistBall', at= 'double' , dv = 0 )
    cmds.setAttr ('L_LegIK_CC.TwistBall', k = True)
    cmds.connectAttr ('L_LegIK_CC.TwistBall','L_RF_Ball.rotateY')  
    cmds.addAttr ('L_LegIK_CC', ln= 'RollToe', at= 'double' , dv = 0 )
    cmds.setAttr ('L_LegIK_CC.RollToe', k = True)
    cmds.connectAttr ('L_LegIK_CC.RollToe','L_RF_Fingers.rotateZ')  
    
    
    cmds.addAttr ('R_LegIK_CC', ln= 'RollHeel', at= 'double' , dv = 0 )
    cmds.setAttr ('R_LegIK_CC.RollHeel', k = True)  
    cmds.connectAttr ('R_LegIK_CC.RollHeel','R_RF_Heel.rotateZ')  
    cmds.addAttr ('R_LegIK_CC', ln= 'TwistHeel', at= 'double' , dv = 0 )
    cmds.setAttr ('R_LegIK_CC.TwistHeel', k = True)
    cmds.connectAttr ('R_LegIK_CC.TwistHeel','R_RF_Heel.rotateY')  
    cmds.addAttr ('R_LegIK_CC', ln= 'RollBall', at= 'double' , dv = 0 )
    cmds.setAttr ('R_LegIK_CC.RollBall', k = True)
    cmds.connectAttr ('R_LegIK_CC.RollBall','R_RF_Ball.rotateZ')  
    cmds.addAttr ('R_LegIK_CC', ln= 'TwistBall', at= 'double' , dv = 0 )
    cmds.setAttr ('R_LegIK_CC.TwistBall', k = True)
    cmds.connectAttr ('R_LegIK_CC.TwistBall','R_RF_Ball.rotateY')  
    cmds.addAttr ('R_LegIK_CC', ln= 'RollToe', at= 'double' , dv = 0 )
    cmds.setAttr ('R_LegIK_CC.RollToe', k = True)
    cmds.connectAttr ('R_LegIK_CC.RollToe','R_RF_Fingers.rotateZ')  
    
    #Pole Vector
    
    cmds.polyPlane (n="LLeg_PV_Plane", sh = 1, sw= 1)
    
    cmds.delete ("LLeg_PV_Plane.vtx[3]")
    cmds.cluster ("LLeg_PV_Plane.vtx[0]", n= "LegCluster")
    cmds.cluster ("LLeg_PV_Plane.vtx[1]" ,n= "KneeCluster")
    cmds.cluster ("LLeg_PV_Plane.vtx[2]", n= "AnkleCluster")
    
    cmds.pointConstraint ("L_Leg_JJ","LegClusterHandle")
    cmds.pointConstraint ("L_Knee_JJ","KneeClusterHandle")
    cmds.pointConstraint ("L_Ankle_JJ","AnkleClusterHandle")
    
    P01X = cmds.getAttr("L_Leg_JJ.translateX")
    P01Y = cmds.getAttr("L_Leg_JJ.translateY")
    P01Z = cmds.getAttr("L_Leg_JJ.translateZ")    
    
    P02X = cmds.getAttr("L_Knee_JJ.translateX") + P01X
    P02Y = cmds.getAttr("L_Knee_JJ.translateY") + P01Y
    P02Z = cmds.getAttr("L_Knee_JJ.translateZ") + P01Z
    
    P03X = cmds.getAttr("L_Ankle_JJ.translateX") + P02X
    P03Y = cmds.getAttr("L_Ankle_JJ.translateY") + P02Y
    P03Z = cmds.getAttr("L_Ankle_JJ.translateZ") + P02Z
    
    P04X = cmds.getAttr("L_Fingers_JJ.translateX") + P03X
    P04Y = cmds.getAttr("L_Fingers_JJ.translateY") + P03Y
    P04Z = cmds.getAttr("L_Fingers_JJ.translateZ") + P03Z
    
    cmds.moveVertexAlongDirection ("LLeg_PV_Plane.vtx[1]", v= P02X+(P02X/2))
    PVposition = cmds.pointPosition ("LLeg_PV_Plane.vtx[1]") 
    
    cmds.circle (n="LLeg_PV01",nr=(0, 0, 1),r = radio/2)
    cmds.circle (n="LLeg_PV02",nr=(0, 1, 0),r = radio/2)
    cmds.circle (n="LLeg_PV03",nr=(1, 0, 0),r = radio/2)
    
    cmds.parent ("LLeg_PV02Shape","LLeg_PV01",r= True, s= True)
    cmds.parent ("LLeg_PV03Shape","LLeg_PV01",r= True, s= True)
    cmds.delete ("LLeg_PV02","LLeg_PV03")
    cmds.select ("LLeg_PV01")
    cmds.group (n= "LLeg_PV01_GRP", r= True)
    cmds.xform (t=PVposition)
    cmds.duplicate ("LLeg_PV01_GRP", n= "RLeg_PV_GRP")
    cmds.rename ("RLeg_PV_GRP|LLeg_PV01", "RLeg_PV01")
    cmds.rename ("LLeg_PV01_GRP", "LLeg_PV0_GRP")
    cmds.move(0, 0, 0, ".scalePivot",".rotatePivot", absolute=True)
    cmds.setAttr ("RLeg_PV_GRP.scaleX", -1)
    
    
    cmds.select ("LLeg_PV01","L_LegIKrp")
    cmds.PoleVectorConstraint ()
    
    cmds.select ("RLeg_PV01","R_LegIKrp")
    cmds.PoleVectorConstraint ()
           
    cmds.setAttr("RLeg_PV01Shape.overrideEnabled", True )
    cmds.setAttr("RLeg_PV01Shape.overrideColor", 13 )
    cmds.setAttr("RLeg_PV02Shape1.overrideEnabled", True )
    cmds.setAttr("RLeg_PV02Shape1.overrideColor", 13 )     
    cmds.setAttr("RLeg_PV03Shape1.overrideEnabled", True )
    cmds.setAttr("RLeg_PV03Shape1.overrideColor", 13 )
    
    cmds.setAttr("LLeg_PV01Shape.overrideEnabled", True )
    cmds.setAttr("LLeg_PV01Shape.overrideColor", 6 )
    cmds.setAttr("LLeg_PV02Shape.overrideEnabled", True )
    cmds.setAttr("LLeg_PV02Shape.overrideColor", 6 )     
    cmds.setAttr("LLeg_PV03Shape.overrideEnabled", True )
    cmds.setAttr("LLeg_PV03Shape.overrideColor", 6 )    
    
    cmds.group ("LLeg_PV_Plane","LegClusterHandle","KneeClusterHandle","AnkleClusterHandle", n= "ExtrasAutoLegs")
    cmds.setAttr ("ExtrasAutoLegs.visibility", 0)
 
    #Switch IK FK
    
    if cmds.objExists ("IK_FK_CC"):
        print "CurveControl IKFK  Exists"
        
    else:
        if cmds.objExists('makeTextCurves1'):
            cmds.rename ('makeTextCurves1','makeTextCurves1LOL')
        Texto = 'IK-FK'
        Color = 16
        Text = cmds.textCurves (n= Texto, t = Texto, o = True)    
        Lista= cmds.listRelatives (Text, ad = True)
        Shape = Lista[1]
        
        cmds.delete ('makeTextCurves1')
        
        for Curva in Lista:
            if cmds.objectType(str(Curva), isType='nurbsCurve'):
                curvaPapa = cmds.listRelatives(Curva, p = True)
                curvaAbuelo = cmds.listRelatives(curvaPapa, p = True)
                DobleCurva = cmds.listRelatives(curvaAbuelo)
                if len(DobleCurva)==2:
                    LetrasDobles.append (Curva)
                else:   
                    if not Shape == curvaPapa[0]:
                        cmds.makeIdentity (curvaAbuelo, a = True, t = True , r = True)
                        cmds.parent (Curva, Shape, r = True, s = True)
                    #Colores
                    cmds.setAttr (Curva+'.overrideEnabled', 1)
                    cmds.setAttr (Curva+'.overrideColor', Color)
                    
        cmds.parent (Shape,w=True)
        cmds.rename(Shape, 'IK_FK_CC')
        cmds.setAttr ("IK_FK_CC.overrideEnabled", 1)
        cmds.setAttr ("IK_FK_CC.overrideColor", 16)
        cmds.setAttr ('IK_FK_CC.rotateX', -90)
        cmds.xform(cp= True)
        cmds.setAttr ('IK_FK_CC.scaleX', GlobalMult)
        cmds.setAttr ('IK_FK_CC.scaleY', GlobalMult)
        cmds.setAttr ('IK_FK_CC.scaleZ', GlobalMult)
        cmds.makeIdentity(a=True, t = True, r = True, s=True)
        
    cmds.select ("IK_FK_CC")
    cmds.addAttr (ln= "LeftLegIKFK", min=0, max=1)
    cmds.setAttr ("IK_FK_CC.LeftLegIKFK", keyable = True)
    
    cmds.select ("IK_FK_CC")
    cmds.addAttr (ln= "RightLegIKFK", min=0, max=1)
    cmds.setAttr ("IK_FK_CC.RightLegIKFK", keyable = True)

    cmds.expression (n="L_Leg_Switch", s = "L_Leg_JJ.rotateX = (L_Leg_FK.rotateX* IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.rotateX*(1- IK_FK_CC.LeftLegIKFK)); \nL_Leg_JJ.rotateY = (L_Leg_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Leg_JJ.rotateZ = (L_Leg_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.rotateX = (L_Knee_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.rotateY = (L_Knee_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.rotateZ = (L_Knee_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.rotateX = (L_Ankle_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.rotateY = (L_Ankle_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.rotateZ = (L_Ankle_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.rotateX = (L_Ball_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.rotateY = (L_Ball_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.rotateZ = (L_Ball_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.rotateX = (L_Fingers_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.rotateY = (L_Fingers_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.rotateZ = (L_Fingers_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \n  \nL_Leg_JJ.translateX = (L_Leg_FK.translateX* IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.translateX*(1- IK_FK_CC.LeftLegIKFK)); \nL_Leg_JJ.translateY = (L_Leg_FK.translateY*IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Leg_JJ.translateZ = (L_Leg_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( L_Leg_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.translateX = (L_Knee_FK.translateX*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.translateY = (L_Knee_FK.translateY*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Knee_JJ.translateZ = (L_Knee_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( L_Knee_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.translateX = (L_Ankle_FK.translateX*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.translateY = (L_Ankle_FK.translateY*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ankle_JJ.translateZ = (L_Ankle_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( L_Ankle_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.translateX = (L_Ball_FK.translateX*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.translateY = (L_Ball_FK.translateY*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Ball_JJ.translateZ = (L_Ball_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( L_Ball_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.translateX = (L_Fingers_FK.translateX*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.translateY = (L_Fingers_FK.translateY*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nL_Fingers_JJ.translateZ = (L_Fingers_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( L_Fingers_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \n  \n  \nL_Leg_FK_CC.visibility = IK_FK_CC.LeftLegIKFK; \nL_LegIK_CC.visibility = (1-IK_FK_CC.LeftLegIKFK); \nLLeg_PV01.visibility = (1-IK_FK_CC.LeftLegIKFK);"  )
    cmds.expression (n="R_Leg_Switch", s = "R_Leg_JJ.rotateX = (R_Leg_FK.rotateX* IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.rotateX*(1- IK_FK_CC.LeftLegIKFK)); \nR_Leg_JJ.rotateY = (R_Leg_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Leg_JJ.rotateZ = (R_Leg_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.rotateX = (R_Knee_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.rotateY = (R_Knee_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.rotateZ = (R_Knee_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.rotateX = (R_Ankle_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.rotateY = (R_Ankle_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.rotateZ = (R_Ankle_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.rotateX = (R_Ball_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.rotateY = (R_Ball_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.rotateZ = (R_Ball_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.rotateX = (R_Fingers_FK.rotateX*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.rotateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.rotateY = (R_Fingers_FK.rotateY*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.rotateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.rotateZ = (R_Fingers_FK.rotateZ*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.rotateZ*(1-IK_FK_CC.LeftLegIKFK)); \n  \nR_Leg_JJ.translateX = (R_Leg_FK.translateX* IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.translateX*(1- IK_FK_CC.LeftLegIKFK)); \nR_Leg_JJ.translateY = (R_Leg_FK.translateY*IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Leg_JJ.translateZ = (R_Leg_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( R_Leg_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.translateX = (R_Knee_FK.translateX*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.translateY = (R_Knee_FK.translateY*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Knee_JJ.translateZ = (R_Knee_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( R_Knee_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.translateX = (R_Ankle_FK.translateX*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.translateY = (R_Ankle_FK.translateY*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ankle_JJ.translateZ = (R_Ankle_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( R_Ankle_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.translateX = (R_Ball_FK.translateX*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.translateY = (R_Ball_FK.translateY*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Ball_JJ.translateZ = (R_Ball_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( R_Ball_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.translateX = (R_Fingers_FK.translateX*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.translateX*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.translateY = (R_Fingers_FK.translateY*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.translateY*(1-IK_FK_CC.LeftLegIKFK)); \nR_Fingers_JJ.translateZ = (R_Fingers_FK.translateZ*IK_FK_CC.LeftLegIKFK)+( R_Fingers_IK.translateZ*(1-IK_FK_CC.LeftLegIKFK)); \n  \n  \nR_Leg_FK_CC.visibility = IK_FK_CC.RightLegIKFK; \nR_LegIK_CC.visibility = (1-IK_FK_CC.RightLegIKFK); \nRLeg_PV01.visibility = (1-IK_FK_CC.RightLegIKFK);"  )

    # Grouping and Organizing
    
    
    cmds.group ('L_Leg_JJ', 'L_Leg_FK', 'L_Leg_IK ','L_Leg_FK_CCGRP', n = 'L_Leg_Joints')
    cmds.group ('R_Leg_JJ', 'R_Leg_FK', 'R_Leg_IK ','R_Leg_FK_CCGRP', n = 'R_Leg_Joints')
    cmds.group ("L_LegIK_GRP", "LLeg_PV0_GRP", n="L_IKLeg_GRP")
    cmds.group ("R_LegIK_GRP", "RLeg_PV_GRP", n="R_IKLeg_GRP")
    cmds.group ("L_IKLeg_GRP", "R_IKLeg_GRP",'L_Leg_Joints','R_Leg_Joints',n= "Connect this to the rest of the rig")
    cmds.group ('ExtrasAutoLegs',"Connect_this_to_the_rest_of_the_rig", n="RdM_AutoLEGS" )

    cmds.select ('L_Ball_JJ', 'L_Ankle_JJ', 'L_Knee_JJ', 'L_Leg_JJ','R_Ball_JJ', 'R_Leg_JJ', 'R_Knee_JJ', 'R_Ankle_JJ')
    cmds.sets (n= 'BindThisToLegs')  
    cmds.delete('R_LegIK_GRP2') 
    
    
    #Locking Attr
    
    #FK
   
    cmds.select ('R_Leg_FK_CC','R_Knee_FK_CC','R_Ankle_FK_CC','R_Ball_FK_CC','L_Leg_FK_CC','L_Knee_FK_CC','L_Ankle_FK_CC','L_Ball_FK_CC')
    FK = cmds.ls(sl=True)
   
    for T in FK:            
        cmds.setAttr(str(T)+'.translateX',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.translateY',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.translateZ',lock = True, keyable = False, channelBox = False)     
       
        cmds.setAttr(str(T)+'.scaleX',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleY',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleZ',lock = True, keyable = False, channelBox = False)

       
        cmds.setAttr(str(T)+'.visibility',lock = True, keyable = False, channelBox = False)
   
   #IK, Clavicule
   
    cmds.select ('L_LegIK_CC', 'R_LegIK_CC')
    IK = cmds.ls(sl=True)
   
    for T in IK:            

        cmds.setAttr(str(T)+'.scaleX',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleY',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleZ',lock = True, keyable = False, channelBox = False)

       
        cmds.setAttr(str(T)+'.visibility',lock = True, keyable = False, channelBox = False)
   
   
   #Pole Vector   

    cmds.select ('LLeg_PV01', 'RLeg_PV01')
    PV = cmds.ls(sl=True)   

    for T in PV:   
             
        cmds.setAttr(str(T)+'.rotateX',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.rotateY',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.rotateZ',lock = True, keyable = False, channelBox = False)     
       
        cmds.setAttr(str(T)+'.scaleX',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleY',lock = True, keyable = False, channelBox = False)
        cmds.setAttr(str(T)+'.scaleZ',lock = True, keyable = False, channelBox = False)

       
        cmds.setAttr(str(T)+'.visibility',lock = True, keyable = False, channelBox = False)
    
    print ('Legs DONE')

    cmds.undoInfo(closeChunk=True)   

