from maya import cmds

def extraJointsFace(GlobalMult = 1):

    cmds.undoInfo(openChunk=True)      
    ##############
    #Add extra Joints 'Jaw, Eyes, Nose, Ears, Upper Head, Lower Head'
 
    bindJoints = []
    def jointMiddle(jointName, p01='Head_JJ', p02='Head_End_JE', Xmov=0, Ymov=0, Zmov=0, bind = True):
        cmds.select(cl = True)
        newjoint = cmds.joint(n = jointName)
        cmds.delete(cmds.pointConstraint(p01, p02, newjoint, mo =False))
        cmds.move(Xmov*GlobalMult,Ymov*GlobalMult,Zmov*GlobalMult, r = True)    
        if bind == True:
            bindJoints.append(newjoint)
    
    HeadDw=jointMiddle(jointName = 'Head_Down_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = -0.1)
    HeadUp=jointMiddle(jointName = 'Head_Up_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = 0.1)
    Jaw = jointMiddle(jointName = 'Jaw_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = -0.2, Zmov = 1)
    JawEnd = jointMiddle(jointName = 'Jaw_JE', p01='Head_JJ', p02='Head_End_JE', Ymov = -1, Zmov = 3, bind = False)

    Nose=jointMiddle(jointName = 'Nose_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = 0.1, Zmov = 2)
    L_Nose=jointMiddle(jointName = 'L_Nose_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = 0.1, Zmov = 2.2, Xmov = 0.15)

    L_Eye=jointMiddle(jointName = 'L_Eye_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = 0.5, Zmov = 1.2, Xmov = 0.4)
    L_Ear=jointMiddle(jointName = 'L_Ear_JJ', p01='Head_JJ', p02='Head_End_JE', Ymov = 0.7, Zmov = 0, Xmov = 1)
 
    cmds.parent('Head_Up_JJ', 'Head_JJ')
    cmds.parent('Head_Down_JJ', 'Head_JJ')

    cmds.parent('Jaw_JE', 'Jaw_JJ')
    cmds.parent('Jaw_JJ', 'Head_Down_JJ')
    cmds.parent('L_Nose_JJ', 'Nose_JJ')
    cmds.parent('Nose_JJ', 'Head_Up_JJ')
    cmds.parent('L_Eye_JJ', 'Head_Up_JJ')
    cmds.parent('L_Ear_JJ', 'Head_Up_JJ')

    cmds.delete('BindThisToHead')
    
    for i in bindJoints:
        cmds.select(i, add = True)
    
    cmds.sets(n = 'BindThisToHead')  

    cmds.undoInfo(closeChunk=True)          

def extraControlJointsFace(GlobalMult = 1):

    cmds.undoInfo(openChunk=True)  

    cmds.select('L_Ear_JJ')
    cmds.mirrorJoint(mirrorYZ=1, mirrorBehavior=1, searchReplace=("L_", "R_"))
    cmds.select('L_Nose_JJ')
    cmds.mirrorJoint(mirrorYZ=1, mirrorBehavior=1, searchReplace=("L_", "R_"))
    cmds.select('L_Eye_JJ')
    cmds.mirrorJoint(mirrorYZ=1, mirrorBehavior=1, searchReplace=("L_", "R_"))
                
    
    facialJoints = cmds.select('BindThisToHead')  
      
    for i in cmds.ls(sl = True):
        
        print i
        Controller = cmds.circle(n = str(i) + '_CC', r = GlobalMult , nr = (0,1,0) if i == 'Head_Up_JJ' else (0,1,0) if i == 'Head_Down_JJ' else (0,0,1))
        Grp = cmds.group(n = str(i) + '_GRP')
        cmds.delete(cmds.parentConstraint(i, Grp, mo =False))
        cmds.parentConstraint(Controller, i, mo = True)
        
        LockThisAttrIK = ['sx','sy','sz', 'v']
        
        for L in LockThisAttrIK:
            cmds.setAttr(str(i)+'_CC.'+str(L),lock = True, keyable = False, channelBox = False)        
        
        cmds.setAttr (str(Controller[0])+'.overrideEnabled', 1)
        cmds.setAttr (str(Controller[0])+'.overrideColor', 16)    
        
        
    cmds.parent('L_Nose_JJ_GRP', 'Nose_JJ_CC')
    cmds.parent('R_Nose_JJ_GRP', 'Nose_JJ_CC')
    cmds.parent('Nose_JJ_GRP', 'Head_Up_JJ_CC')
    cmds.parent('R_Ear_JJ_GRP', 'Head_Up_JJ_CC')
    cmds.parent('L_Ear_JJ_GRP', 'Head_Up_JJ_CC')
    cmds.parent('L_Eye_JJ_GRP', 'Head_Up_JJ_CC')
    cmds.parent('R_Eye_JJ_GRP', 'Head_Up_JJ_CC')
    cmds.parent('Jaw_JJ_GRP', 'Head_Down_JJ_CC')
    cmds.parent('Head_Down_JJ_GRP', 'Head_CC')
    cmds.parent('Head_Up_JJ_GRP', 'Head_CC')

    cmds.undoInfo(closeChunk=True)  

def basicBlendShapes():

    cmds.undoInfo(openChunk=True)  
    
    mainGeo = cmds.ls(sl = True)
    Happy = cmds.duplicate(mainGeo, n = 'HappyShape')
    Sad = cmds.duplicate(mainGeo, n = 'SadShape')
    Wide = cmds.duplicate(mainGeo, n = 'WideShape')
    Narrow = cmds.duplicate(mainGeo, n = 'NarrowShape')
    Narrow = cmds.duplicate(mainGeo, n = 'NarrowShape')
    LipsRollIn = cmds.duplicate(mainGeo, n = 'RollIn')
    LipsRollOut = cmds.duplicate(mainGeo, n = 'RollOut')

    Down = cmds.duplicate(mainGeo, n = 'HappyShape')
    Up = cmds.duplicate(mainGeo, n = 'SadShape')
    InUp = cmds.duplicate(mainGeo, n = 'InUpShape')
    InDown = cmds.duplicate(mainGeo, n = 'InDownShape')
    OutUp = cmds.duplicate(mainGeo, n = 'OutUpShape')
    OutDown = cmds.duplicate(mainGeo, n = 'OutDownShape')
    Frown = cmds.duplicate(mainGeo, n = 'WideShape')
        
    
    cmds.blendShape(Happy,Sad,Wide,Narrow,LipsRollIn,LipsRollOut, mainGeoDown,Up,Frown,InUp,InDown,OutUp,OutDown,mainGeo, n = 'FacialBS')
    cmds.undoInfo(closeChunk=True)       
            
'''
extraJointsFace(GlobalMult = 2)
extraControlJointsFace(GlobalMult = 2)

basicBlendShapes()

'''