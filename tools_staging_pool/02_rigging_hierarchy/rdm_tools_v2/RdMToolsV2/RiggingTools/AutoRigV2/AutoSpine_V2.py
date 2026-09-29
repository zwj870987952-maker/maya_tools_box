from maya import cmds

###JOINTS LOCATORSz

def LocatorsBtn(jointsNumVar=5):

    cmds.undoInfo(openChunk=True)   

    cmds.select(cl = True)
    
    cmds.spaceLocator(n = 'Pelvis Loc')
    cmds.move (0, -2.5, 0)

    jointsNum = jointsNumVar
    
    for X in range (jointsNum):
    
        cmds.select (clear = True)        
        cmds.CreateLocator ()
        cmds.move (0, 2.5*X, 0)
        cmds.select (clear = True)           
        cmds.rename ("locator1", "Spine_0" + str (X + 1) + "_LOC")


    cmds.rename('Spine_01_LOC', 'COG_LOC')
    cmds.rename('Spine_0%s_LOC'%(jointsNum), 'Spine_END_LOC')
    cmds.rename('Spine_0%s_LOC'%(jointsNum-1), 'Spine_CHEST_LOC')

    try:
        for i in range(jointsNum-2):
            cmds.rename('Spine_0%s_LOC'%(i+2),'Belly_0%s_LOC'%(i+1) )
        print 'rename %s'%(i)
        
    except:
        pass
                
    cmds.select (clear = True)

    cmds.undoInfo(closeChunk=True)   

    
def JointsBtn(jointsNumVar = 5):

    cmds.undoInfo(openChunk=True)   
    jointsNum = jointsNumVar
    
    cmds.select(cl = True)
    
    #Rename to old version
    v = 1
    
    while cmds.objExists('Belly_0'+str(v)+'_LOC'):
        cmds.rename('Belly_0'+str(v)+'_LOC', 'Spine_0'+str(v+1)+'_LOC')
        v = v + 1 

    
    cmds.rename('COG_LOC','Spine_01_LOC')
    cmds.rename('Spine_END_LOC','Spine_0%s_LOC'%(jointsNum))
    cmds.rename('Spine_CHEST_LOC','Spine_0%s_LOC'%(jointsNum-1))

  
    #ORIGINAL STUFF
    
    cmds.select (clear = True)  

    for X in range (jointsNum):
        cmds.rename ("Spine_0" + str (X + 1) + "_LOC", 'locator' + str (X + 1) )      
          
    for X in range (1, jointsNum + 1):  
                
        cmds.joint (n = "Spine_" + str(X))
        cmds.pointConstraint ("locator" + str (X) , "Spine_" + str(X))
        cmds.delete ("Spine_" + str(X) + "_pointConstraint1")
        cmds.delete ("locator" + str (X))
     
    cmds.select (clear = True)
    
    whileX = 1
    
    while cmds.objExists("Spine_" + str(whileX)):
        
        cmds.select ('Spine_' + str(whileX), add = True, tgl = True)
        whileX = whileX +1
   
      
    cmds.joint(e= True, zso=True, oj= "xyz", sao = "zup") 
    
    cmds.select (clear = True)   

    #COG

    cmds.duplicate ('Spine_1', n = 'COG')
    cmds.delete  ('COG|Spine_2')
    cmds.setAttr ("COG.radius", 2)
    
    cmds.parent('Spine_1', 'COG')
    
    cmds.select(cl = True)
    
    
    #Last Joint
    LastOne = cmds.duplicate('Spine_%s'%(jointsNumVar))
    cmds.parent(LastOne, 'Spine_%s'%(jointsNumVar))
    cmds.setAttr('%s.translateY'%(LastOne[0]),10 )
    cmds.select('Spine_%s'%(jointsNumVar))
    cmds.joint(e= True, zso=True, oj= "xyz", sao = "zup") 
    cmds.delete(LastOne[0])

    cmds.select(cl = True)
    PelvisJnt = cmds.joint(n = 'Pelvis_Jnt')
    cmds.delete(cmds.parentConstraint('Pelvis_Loc',PelvisJnt, mo = False))
    cmds.delete('Pelvis_Loc')
    cmds.parent(PelvisJnt, 'COG')
    
    cmds.undoInfo(closeChunk=True)   


#***********************************************************************************************************************
def SpineBtn(jointsNumVar,GlobalMultVar): 

    print jointsNumVar
    #Turn off Mirror X
    cmds.symmetricModelling(symmetry=False)
    cmds.softSelect(sse=0)   
    
    cmds.undoInfo(openChunk=True)   

    cmds.progressWindow(title='Spine Rig v2', progress=0, status='Starting', isInterruptable=True,maxValue=3)
    
    cmds.parent('Spine_1', w = True)
        
    IkSystem = cmds.ikHandle(sj ='Spine_1', ee= 'Spine_%s'%(jointsNumVar),  sol= 'ikSplineSolver', n = 'Spine_IK', ns = jointsNumVar) 
    IKHandle = IkSystem[0]    
    Curve = cmds.rename(IkSystem[2], 'Spine_CV')   
      
    cmds.parent('Spine_1', Curve, 'COG')    
    
    #IK System
    radio = cmds.getAttr('Spine_2.translateX')*2*GlobalMultVar
    
    
    IKJoints = []

    def SpineCircle(name, p01, p02, mode, Color):
        
        controllerIK = cmds.circle(n = name + '_CC' , r = radio, nr = (0,1,0))
        if mode == 'IK':
            Joint = cmds.duplicate('Spine_1', n = name + '_JC')
            cmds.delete(name+'_JC|Spine_2')
            IKJoints.append (Joint[0])
            
        controllerGRP = cmds.group(controllerIK, n = name + '_GRP')      
        pConstraint = cmds.pointConstraint(p01,p02,controllerGRP)


                       
        #Put it in the middle
        try:
            if mode== 'IK':
                cmds.setAttr('%s_parentConstraint1.%sW1'%(controllerGRP, p02),2)
            cmds.delete(pConstraint)
        except:
            cmds.delete(pConstraint)
        
        #Shape and Color
        size = -radio/2
        if mode == 'IK':
            cmds.select(name + '_CC.cv[3]',name + '_CC.cv[7]')
            cmds.move(0, size, 0, r =True)
        cmds.select(cl = True)
        cmds.setAttr ('%s.overrideEnabled'%(controllerIK[0]), 1)
        cmds.setAttr ('%s.overrideColor'%(controllerIK[0]), Color)
        
        #Put the joint in Position
        if mode == 'IK':
            cmds.delete(cmds.pointConstraint(controllerIK[0],name + '_JC', mo =False))
            cmds.parent(name + '_JC', controllerIK[0])
        

    cmds.progressWindow(edit=True, progress=2, status='Create FK')
    
    #FK

    SpineCircle(name = 'Spine_FK_01', p01 = 'Spine_1',p02='Spine_1', mode = 'FK', Color = 9)  
    SpineCircle(name = 'Spine_FK_03', p01 = 'Spine_%s'%(jointsNumVar-1),p02='Spine_%s'%(jointsNumVar-1), mode = 'FK', Color = 9)    
    SpineCircle(name = 'Spine_FK_02', p01 = 'Spine_FK_03_CC',p02='Spine_FK_01_CC', mode = 'FK', Color = 9)    


    cmds.progressWindow(edit=True, progress=3, status='Completing')

    #IK
    cmds.progressWindow(edit=True, progress=1, status='Create IK')
        
    SpineCircle(name = 'Spine_IK_01', p01 = 'Spine_1',p02='Spine_1', mode = 'IK', Color = 14)    
    SpineCircle(name = 'Spine_IK_02', p01 = 'Spine_2',p02='Spine_2', mode = 'IK',Color = 14)    
    SpineCircle(name = 'Spine_IK_03', p01 = 'Spine_3',p02='Spine_3', mode = 'IK',Color = 14)    
    SpineCircle(name = 'Spine_IK_04', p01 = 'Spine_%s'%(jointsNumVar),p02='Spine_%s'%(jointsNumVar), mode = 'IK',Color = 14)    


    #Create hierarchy
    cmds.parent('Spine_IK_02_GRP', 'Spine_FK_01_CC')
    cmds.parent('Spine_IK_04_GRP', 'Spine_FK_03_CC')
    cmds.parent('Spine_IK_03_GRP', 'Spine_FK_02_CC')
    cmds.parent('Spine_FK_03_GRP', 'Spine_FK_02_CC')
    cmds.parent('Spine_FK_02_GRP', 'Spine_FK_01_CC')

    #Twist
    cmds.setAttr("Spine_IK.dTwistControlEnable", 1)
    cmds.setAttr("Spine_IK.dWorldUpType", 4)
    cmds.connectAttr ("Spine_FK_01_CC.worldMatrix[0]", "Spine_IK.dWorldUpMatrix", f=True)
    cmds.connectAttr ("Spine_FK_03_CC.worldMatrix[0]" , "Spine_IK.dWorldUpMatrixEnd", f=True )
    
    cmds.setAttr("Spine_IK.dForwardAxis", 0)
    cmds.setAttr("Spine_IK.dWorldUpAxis", 4)
    cmds.setAttr("Spine_IK.dWorldUpVectorZ", -1)
    cmds.setAttr("Spine_IK.dWorldUpVectorEndX", 0)
    cmds.setAttr("Spine_IK.dWorldUpVectorEndZ", -1)
    cmds.setAttr("Spine_IK.dWorldUpVectorX", 0)
    cmds.setAttr("Spine_IK.dWorldUpVectorY", 0)
    cmds.setAttr("Spine_IK.dWorldUpVectorEndY", 0)
    #COG
    
    cmds.nurbsSquare (n= 'COG_CC', nr = (0,1,0))
    cmds.parent ('leftCOG_CCShape','bottomCOG_CCShape','rightCOG_CCShape','topCOG_CC', r= True, s = True)
    cmds.rename ('COG_CC', 'COG_GRP')
    cmds.rename ('topCOG_CC', 'COG_CC')
    cmds.delete ('leftCOG_CC','bottomCOG_CC','rightCOG_CC')
    cmds.pointConstraint ('COG', 'COG_GRP')
    cmds.delete ('COG_GRP_pointConstraint1')
    cmds.parentConstraint ('COG_CC', 'COG' , mo =True)
    cmds.scale (radio*3,radio*3,radio*3, 'COG_GRP')
    cmds.setAttr ('COG_CC.overrideEnabled', 1)
    cmds.setAttr ('COG_CC.overrideColor', 16)
    cmds.parent('Spine_IK_01_GRP','Spine_FK_01_GRP','COG_CC') 
         
    #Boind to curve
    cmds.parent('Spine_CV', w=True)
    cmds.setAttr('Spine_CV.inheritsTransform', 0)      
    cmds.skinCluster(IKJoints,Curve, tsb= True,  nw=1, wd = 0, mi = 5, omi = True, dr = 4, rui = True)

    #Organize
    cmds.group('COG', 'Spine_IK' ,'COG_GRP', 'Spine_CV',n ='RdM_AutoSPINE')
    
    #Clean Attrs
    LockThisAttrIK = ['sx','sy','sz', 'v']
    controllersIK = ('Spine_IK_01_CC','Spine_IK_02_CC','Spine_IK_03_CC','Spine_IK_04_CC')
    controllersFK = ('Spine_FK_01_CC','Spine_FK_02_CC','Spine_FK_03_CC')
        
    for L in LockThisAttrIK:
        for i in controllersIK:
            cmds.setAttr(str(i)+'.'+str(L),lock = True, keyable = False, channelBox = False)
        for i in controllersFK:
            cmds.setAttr(str(i)+'.'+str(L),lock = True, keyable = False, channelBox = False)
        cmds.setAttr('COG_CC.'+str(L),lock = True, keyable = False, channelBox = False)

    
    #Reverse Spine for AutoConnect
    cmds.select('Spine_IK_01_JC')
    cmds.joint(n = 'ReverseSpine_JE')
    cmds.delete(cmds.parentConstraint('Pelvis_Jnt','ReverseSpine_JE'))
    cmds.delete('Pelvis_Jnt')
    
    #Joint name for head
    cmds.rename('Spine_IK_04_JC','SpineEnd_JC')

    cmds.progressWindow(endProgress=1)

   #Fixes
    cmds.parent('SpineEnd_JC', 'Spine_FK_03_CC' )
    cmds.delete('Spine_IK_04_GRP')
    
    cmds.rename('Spine_%s'%(jointsNumVar), 'Spine_JntEnd')
    cmds.rename('Spine_%s'%(jointsNumVar-1), 'Spine_JntChest')


    #Cahnge pivot info
    cmds.addAttr('Spine_IK_01_CC', ln="_____",at='enum', en =  ".:")
    cmds.setAttr('Spine_IK_01_CC._____', e=1, keyable=False, cb = True)
    cmds.addAttr('Spine_IK_01_CC', ln="ChangePivot", dv=0, at='double')
    cmds.setAttr('Spine_IK_01_CC.ChangePivot', e=1, keyable=True)
    cmds.connectAttr('Spine_IK_01_CC.ChangePivot', 'Spine_IK_01_CC.rotatePivotY', f=1)
    cmds.setAttr('Spine_IK_01_CC.ChangePivot', cmds.getAttr('ReverseSpine_JE.translateX'))    

    #Set
    cmds.select('Spine_FK_03_CC')
    cmds.joint(n = 'Spine_ConnectToArms' )
    
    cmds.select(cl = True)
    x = 1 
    while cmds.objExists('Spine_%s'%(x)):
        cmds.select('Spine_%s'%(x), tgl = True)
        x = x + 1
        
    cmds.select('Spine_JntChest','ReverseSpine_JE',add = True)
    
    cmds.sets(n = 'BindThisToSpine')
    
    
    cmds.undoInfo(closeChunk=True)   
    
'''
    
LocatorsBtn(jointsNumVar = 5)
    
JointsBtn(jointsNumVar = 5)
   
SpineBtn(jointsNumVar = 5, GlobalMultVar = 1)


'''
