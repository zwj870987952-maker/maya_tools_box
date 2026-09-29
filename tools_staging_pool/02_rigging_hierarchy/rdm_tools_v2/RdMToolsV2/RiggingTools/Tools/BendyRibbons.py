from maya import cmds
import pymel.core as pm

'''
Order the mess

'''

def ribbonLimb(customName, size ,  *args):
    
    cmds.undoInfo(openChunk=True)   

    Divisions = 13

    cmds.progressWindow(title='IK FK', progress=0, status='Starting', isInterruptable=True,maxValue=6)
    cmds.progressWindow(edit=True, progress=1, status='Create Plane in Pos')
    
    Joints = cmds.ls(sl=True)
    firstJoint = Joints[0]
    middleJoint = Joints[1]
    lastJoint = Joints[-1]
    

    
    ribbonPlane =cmds.nurbsPlane(ch=1, d=1, v=1, p=(0, 0, 0), u=2, w=1, ax=(0, 0, 1), lr=1, n = customName)
    cluster01 = cmds.cluster(customName + '.cv[0][0:1]')
    cluster02 = cmds.cluster(customName + '.cv[1][0:1]')
    cluster03 = cmds.cluster(customName + '.cv[2][0:1]')
    cmds.setAttr(str(ribbonPlane[0])+'.visibility', 0)
    
    cmds.delete(cmds.parentConstraint(firstJoint, cluster01, mo=False))
    cmds.delete(cmds.parentConstraint(middleJoint, cluster02, mo=False))
    cmds.delete(cmds.parentConstraint(lastJoint, cluster03, mo=False))

    cmds.delete(ribbonPlane,ch=True)

    cmds.rebuildSurface(ribbonPlane[0], rt=0, kc=0, fr=0, end=1, sv=1, su=Divisions, kr=0, dir=2, kcp=0, tol=0.01, dv=1, du=3, rpo=1)

    cmds.progressWindow(edit=True, progress=2, status='Create Follicles')
    
    #Follicles on Plane
    cmds.progressWindow(edit=True, progress=2, status='Folicles On Plane')

    cmds.select(ribbonPlane[0])
    pm.mel.createHair(Divisions, 1, 10, 0, 0, 0, 0, 5, 0, 1, 2, 1)
    cmds.delete ('hairSystem1','pfxHair1','nucleus1')
    cmds.setAttr(str (customName)+'.inheritsTransform', 0)
    
    for C in range (1, Divisions+1):
        cmds.delete ('curve' + str (C) )
    cmds.rename ('hairSystem1Follicles', customName + 'Follicle_GRP')
    
    Follicles = cmds.ls (customName + 'Follicle_GRP', dag = True, type = 'follicle')

    x=1
    BindSet = []
    for i in Follicles:
        newI = cmds.rename(i ,customName + '_Follicle')  
        cmds.select(newI)
        cmds.joint(n = customName + '_Bind_Jnt'+str(x))  
        cmds.select(cl=True)
        BindSet.append(customName + '_Bind_Jnt'+str(x))
        x=x+1


    #New joints to Bind Skin
    cmds.progressWindow(edit=True, progress=3, status='Joints Controlling the plane')

    newJoints01 = cmds.duplicate(Joints[0], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_1')
    newJoints02 = cmds.duplicate(Joints[0], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_2')
    newJoints03 = cmds.duplicate(Joints[0], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_3')
   
    newJoints04 = cmds.duplicate(Joints[1], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_4')
    newJoints05 = cmds.duplicate(Joints[1], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_5')
    newJoints06 = cmds.duplicate(Joints[1], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_6')

    newJoints07 = cmds.duplicate(Joints[2], rc = True, ic = False, po = True, n = customName+ 'Ribbon_JC_7')
    
    JointsControllers = (newJoints01[0],newJoints02[0],newJoints03,newJoints04,newJoints05,newJoints06,newJoints07)
    #cmds.parent(newJoints05,newJoints06,w=True)
    
    BindJoints = []
    
    RibbonGroups = []
    
    for i in range(1,8):
        GRP = cmds.group(em=1, n = customName+ 'Ribbon_JC_'+str(i) + '_GRP')
        cmds.delete(cmds.parentConstraint(customName+ 'Ribbon_JC_'+str(i), GRP, mo =0))
        Control = cmds.circle(nr = (1,0,0),n = customName+ 'Ribbon_JC_'+str(i) + '_CC', r= size*0.75)[0]
        cmds.delete(cmds.parentConstraint(GRP, Control, mo =0))
        cmds.parent(Control, GRP)
        cmds.parent(customName+ 'Ribbon_JC_'+str(i), Control)
        BindJoints.append(customName+ 'Ribbon_JC_'+str(i))
        RibbonGroups.append(GRP)
        
        cmds.setAttr(str(Control)+'.overrideEnabled',  1)
        cmds.setAttr(str(Control)+'.overrideColor',  16)
    
    print RibbonGroups 
        
    #Put them in the middle
    cmds.progressWindow(edit=True, progress=4, status='Everything in the middle')

    point1= cmds.pointConstraint(customName+ 'Ribbon_JC_1_GRP',customName+ 'Ribbon_JC_4_GRP', customName+ 'Ribbon_JC_2_GRP', mo = False)
    point2= cmds.pointConstraint(customName+ 'Ribbon_JC_1_GRP',customName+ 'Ribbon_JC_4_GRP', customName+ 'Ribbon_JC_3_GRP', mo = False)
    point3= cmds.pointConstraint(customName+ 'Ribbon_JC_4_GRP',customName+ 'Ribbon_JC_7_GRP', customName+ 'Ribbon_JC_5_GRP', mo = False)
    point4= cmds.pointConstraint(customName+ 'Ribbon_JC_4_GRP',customName+ 'Ribbon_JC_7_GRP', customName+ 'Ribbon_JC_6_GRP', mo = False)
    cmds.setAttr(customName + 'Ribbon_JC_2_GRP_pointConstraint1.'+customName+'Ribbon_JC_1_GRPW0',2)
    cmds.setAttr(customName + 'Ribbon_JC_3_GRP_pointConstraint1.'+customName+'Ribbon_JC_4_GRPW1',2)
    cmds.setAttr(customName + 'Ribbon_JC_5_GRP_pointConstraint1.'+customName+'Ribbon_JC_4_GRPW0',2)
    cmds.setAttr(customName + 'Ribbon_JC_6_GRP_pointConstraint1.'+customName+'Ribbon_JC_7_GRPW1',2)
    
    cmds.delete(point1 ,point2, point3, point4)
    
    #Parent the JJ to the Ribbon
    cmds.progressWindow(edit=True, progress=5, status='Nurbs Plane Bind Skin')

    cmds.skinCluster(BindJoints, ribbonPlane[0], sm =0 , bm =0, tsb  = True )


    #Clean the mess
    cmds.progressWindow(edit=True, progress=6, status='Cleaning')
    
    GroupJC= cmds.group(RibbonGroups, n = customName + 'Ribbon_JC_GPR') 
    AllGRP = cmds.group(GroupJC, customName + 'Follicle_GRP', n = customName + '_RibbonGRP')
    cmds.setAttr( customName + 'Follicle_GRP.inheritsTransform', 0)
    
    cmds.select (BindSet)
    cmds.sets (n= 'BindThisTo_' + customName + '_Ribbon')  
    
    cmds.parent(customName,AllGRP) 

                
    cmds.progressWindow(endProgress=1)

    cmds.undoInfo(closeChunk=True)   

#ribbonLimb(customName= 'Ribbon', size = 3)

