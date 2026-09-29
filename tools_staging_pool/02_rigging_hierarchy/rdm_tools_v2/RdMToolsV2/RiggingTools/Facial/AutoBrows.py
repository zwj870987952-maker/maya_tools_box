#Convert polys to nurbs
import pymel.core as pm
from maya import cmds
import maya.mel as mel

import RdMToolsV2
from RdMToolsV2.RiggingTools.Curves.CurveColors import colorShape
from RdMToolsV2.RiggingTools.Tools.MirrorBehavior import mirrorParts
from RdMToolsV2.RiggingTools.Curves.RootAuto import rootAuto 

def polyToNurbs(Name = 'L_Brow', mirror = True):

    cmds.undoInfo(openChunk=True)   

    selFaces = cmds.ls(sl = True)
    print selFaces
    
    pm.mel.changeSelectMode('-component')
    pm.mel.changeSelectMode('-object')
    
    #Create New Faces
    selObj = cmds.ls(sl = True)
    print selObj
    originalName = selObj	
    print originalName[0]
    		
    DuplicateObj = cmds.duplicate(selObj, n = 'DuplicateGeo')
    tempName = cmds.rename(selObj, 'TempName')
    NewDuplicateName = cmds.rename(DuplicateObj, originalName )
    cmds.select(selFaces)
    
    
    cmds.polyChipOff(selFaces, ch = False, kft = 1, dup = 1, off = 0)
    pm.mel.polyPerformAction("polySeparate -rs 1", "o", 0)
    #cmds.select(selObj)
    Divide = pm.polySeparate(selObj, ch=1, rs=1)
    cmds.delete('polySurface1')
    cmds.delete('polySurface2', ch = True)
           
    ObjNew = cmds.rename(NewDuplicateName, NewDuplicateName + '_ToNurbs' )
    ObjFaces = cmds.rename('polySurface2', NewDuplicateName + '_ToNurbsPlane' )
    
    selObj = cmds.rename(tempName, originalName)
    
    #Create Nurbs From Selection
    
    cmds.select(ObjFaces)
    Subdiv = mel.eval('CreateSubdivSurface;')
    
    Nurbs = pm.subdToNurbs('polyToSubd1', ch=False, aut=True, ot=0)
    pm.pickWalk(d='down')
    Nurbs = cmds.ls(sl = True)
    cmds.parent(Nurbs, w = True)
    cmds.delete(ObjNew)
    Nurbs = cmds.rename(Nurbs[0], str(Name))
    
    cmds.xform(Nurbs, cp = 1)
    newNurb = cmds.rebuildSurface(Nurbs, rt=0, kc=0, fr=0, ch=1, end=1, sv=5, su=5, kr=0, dir=2, kcp=0, tol=1e-08, dv=3, du=3, rpo=1)
    cmds.select(newNurb)
    mel.eval('sets -e -forceElement initialShadingGroup;')


    if mirror:    
        newName = str(newNurb[0])
        correctSide = newName.replace('L_', 'R_')
        newNurb2 = cmds.duplicate(newNurb, n = str(correctSide))
        
        
        GroupVar =cmds.group(newNurb2, n = str(newNurb2[0])+'_Mirror')
    
        cmds.xform(GroupVar,rp=(0,0,0), sp=(0,0,0))
        
        cmds.setAttr(str(GroupVar)+'.rx', 180)
        cmds.setAttr(str(GroupVar)+'.sx', -1)
        cmds.setAttr(str(GroupVar)+'.sy', -1)
        cmds.setAttr(str(GroupVar)+'.sz', -1)
      
    print 'Done creating nurbs from selection'

    
    cmds.undoInfo(closeChunk=True)   

def createRibbons(bindJoints, controljoints, controllersSize, mode):
    
    cmds.undoInfo(openChunk=True)  

    ribbonsNameL = 'L_Brow'
    ribbonsNameR = 'R_Brow'
    
    def CreateRibbonFunc(name):
            
        cmds.select(name)
        if mode == 'u':
            pm.mel.createHair(1, bindJoints, 10, 0, 0, 0, 0, 5, 0, 1, 2, 1)
        else:
            pm.mel.createHair(bindJoints, 1, 10, 0, 0, 0, 0, 5, 0, 1, 2, 1)
            
        cmds.delete ('hairSystem1','pfxHair1','nucleus1')
    
        try:
            for C in range (1, bindJoints+1):
                cmds.delete ('curve' + str (C) )
        except:
            pass
            
        cmds.rename ('hairSystem1Follicles', name + 'Follicle_GRP')
        
        Follicles = cmds.ls (name + 'Follicle_GRP', dag = True, type = 'follicle')
    
        x=1
        BindSet = []
        for i in Follicles:
            newI = cmds.rename(i ,name + '_Follicle')  
            cmds.select(newI)
            cmds.joint(n = name + '_Bind_JJ'+str(x))  
            cmds.select(cl=True)
            BindSet.append(name + '_Bind_JJ'+str(x))
            x=x+1
        
        
    CreateRibbonFunc(name = ribbonsNameL)
    CreateRibbonFunc(name = ribbonsNameR)
    
    BindSet = ['L_Brow_Bind_JJ1', 'L_Brow_Bind_JJ2', 'L_Brow_Bind_JJ3', 'L_Brow_Bind_JJ4', 'L_Brow_Bind_JJ5']
    
    
    #Create Controllers 
    
    JointsControlL =[]
    for i in range(0,controljoints):
        print i
        cmds.select(cl = True)
        JC = cmds.joint(n = ribbonsNameL + '_Bind_JC_' + str(i+1))
        JointsControlL.append(ribbonsNameL + '_Bind_JC_' + str(i+1))
        cmds.setAttr(str(JC)+'.radius', 1.5 )
                
    #Position JC in JJ
    cmds.xform(JointsControlL[0], m = cmds.xform(BindSet[0],q = True, m =True, ws = True), ws = True)
    cmds.xform(JointsControlL[1], m = cmds.xform(BindSet[2],q = True, m =True, ws = True), ws = True)        
    cmds.xform(JointsControlL[2], m = cmds.xform(BindSet[-1],q = True, m =True, ws = True), ws = True)        

    JointsControlR = []
    for i in JointsControlL:
        cmds.select(cl = True)
        JC = cmds.duplicate(i, n = str(i).replace('L_','R_'))
        cmds.select(JC)
        mirrorParts(world = True)
        JointsControlR.append(JC[0])
    

    cmds.skinCluster(JointsControlL, ribbonsNameL, sm =0 , bm =0, tsb  = True )
    cmds.skinCluster(JointsControlR, ribbonsNameR, sm =0 , bm =0, tsb  = True )


    
    #Create Controllers for joints
    for c in JointsControlL:
        
        CC = cmds.curve(p=[(0, 1, 0), (-0.19509, 0.980785, -6.97697e-08), (-0.382683, 0.92388, -1.36858e-07), (-0.55557, 0.83147, -1.98687e-07), (-0.707107, 0.707107, -2.52881e-07), (-0.83147, 0.55557, -2.97357e-07), 
        (-0.92388, 0.382683, -3.30405e-07), (-0.980785, 0.19509, -3.50756e-07), (-1, 0, -3.57628e-07), (-0.980785, -0.19509, -3.50756e-07), (-0.92388, -0.382683, -3.30405e-07), (-0.83147, -0.55557, -2.97357e-07), 
        (-0.707107, -0.707107, -2.52881e-07), (-0.55557, -0.83147, -1.98687e-07), (-0.382683, -0.92388, -1.36858e-07), (-0.19509, -0.980785, -6.97697e-08), (0, -1, 0), (0.19509, -0.980785, 0), (0.382683, -0.92388, 0), 
        (0.55557, -0.83147, 0), (0.707107, -0.707107, 0), (0.83147, -0.55557, 0), (0.92388, -0.382683, 0), (0.980785, -0.19509, 0), (1, 0, 0), (0.980785, 0.19509, 0), (0.92388, 0.382683, 0), (0.83147, 0.55557, 0), 
        (0.707107, 0.707107, 0), (0.55557, 0.83147, 0), (0.382683, 0.92388, 0), (0.19509, 0.980785, 0), (0, 1, 0), (9.88405e-08, 0.980785, -0.19509), (1.93883e-07, 0.92388, -0.382683), (2.81474e-07, 0.83147, -0.55557), 
        (3.58248e-07, 0.707107, -0.707107), (4.21255e-07, 0.55557, -0.83147), (4.68074e-07, 0.382683, -0.923879), (4.96905e-07, 0.19509, -0.980785), (5.06639e-07, 0, -1), (4.96905e-07, -0.19509, -0.980785), 
        (4.68074e-07, -0.382683, -0.923879), (4.21255e-07, -0.55557, -0.83147), (3.58248e-07, -0.707107, -0.707107), (2.81474e-07, -0.83147, -0.55557), (1.93883e-07, -0.92388, -0.382683), (9.88405e-08, -0.980785, -0.19509), 
        (0, -1, 0), (-2.90707e-08, -0.980785, 0.19509), (-5.70243e-08, -0.92388, 0.382683), (-8.27864e-08, -0.83147, 0.55557), (-1.05367e-07, -0.707107, 0.707107), (-1.23899e-07, -0.55557, 0.83147), (-1.37669e-07, -0.382683, 0.92388), 
        (-1.46148e-07, -0.19509, 0.980785), (-1.49012e-07, 0, 1), (-1.46148e-07, 0.19509, 0.980785), (-1.37669e-07, 0.382683, 0.92388), (-1.23899e-07, 0.55557, 0.83147), (-1.05367e-07, 0.707107, 0.707107), (-8.27864e-08, 0.83147, 0.55557), 
        (-5.70243e-08, 0.92388, 0.382683), (-2.90707e-08, 0.980785, 0.19509), (0, 1, 0), (-2.90707e-08, 0.980785, 0.19509), (-5.70243e-08, 0.92388, 0.382683), (-8.27864e-08, 0.83147, 0.55557), (-1.05367e-07, 0.707107, 0.707107), 
        (-1.23899e-07, 0.55557, 0.83147), (-1.37669e-07, 0.382683, 0.92388), (-1.46148e-07, 0.19509, 0.980785), (-1.49012e-07, 0, 1), (-0.382684, 0, 0.923879), (-0.707107, 0, 0.707107), (-0.92388, 0, 0.382683), (-1, 0, -3.57628e-07), 
        (-0.923879, 0, -0.382684), (-0.707106, 0, -0.707107), (-0.382683, 0, -0.92388), (5.06639e-07, 0, -1), (0.382684, 0, -0.923879), (0.707107, 0, -0.707106), (0.92388, 0, -0.382683), (1, 0, 0), (0.92388, 0, 0.382683), (0.707107, 0, 0.707107), 
        (0.382683, 0, 0.92388), (-1.49012e-07, 0, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88], d=1,n = str(c)[0] + '_Brow_CC_'+str(c)[-1])
        colorShape(Color = 6)
        rootAuto()
        cmds.xform(str(c)[0] + '_Brow_CC_'+str(c)[-1]+'_Root', m = cmds.xform(c,q = True, m =True, ws = True), ws = True)        
        cmds.parent(c, CC)
         
    for c in JointsControlR:
        
        CC = cmds.curve(p=[(0, 1, 0), (-0.19509, 0.980785, -6.97697e-08), (-0.382683, 0.92388, -1.36858e-07), (-0.55557, 0.83147, -1.98687e-07), (-0.707107, 0.707107, -2.52881e-07), (-0.83147, 0.55557, -2.97357e-07), 
        (-0.92388, 0.382683, -3.30405e-07), (-0.980785, 0.19509, -3.50756e-07), (-1, 0, -3.57628e-07), (-0.980785, -0.19509, -3.50756e-07), (-0.92388, -0.382683, -3.30405e-07), (-0.83147, -0.55557, -2.97357e-07), 
        (-0.707107, -0.707107, -2.52881e-07), (-0.55557, -0.83147, -1.98687e-07), (-0.382683, -0.92388, -1.36858e-07), (-0.19509, -0.980785, -6.97697e-08), (0, -1, 0), (0.19509, -0.980785, 0), (0.382683, -0.92388, 0), 
        (0.55557, -0.83147, 0), (0.707107, -0.707107, 0), (0.83147, -0.55557, 0), (0.92388, -0.382683, 0), (0.980785, -0.19509, 0), (1, 0, 0), (0.980785, 0.19509, 0), (0.92388, 0.382683, 0), (0.83147, 0.55557, 0), 
        (0.707107, 0.707107, 0), (0.55557, 0.83147, 0), (0.382683, 0.92388, 0), (0.19509, 0.980785, 0), (0, 1, 0), (9.88405e-08, 0.980785, -0.19509), (1.93883e-07, 0.92388, -0.382683), (2.81474e-07, 0.83147, -0.55557), 
        (3.58248e-07, 0.707107, -0.707107), (4.21255e-07, 0.55557, -0.83147), (4.68074e-07, 0.382683, -0.923879), (4.96905e-07, 0.19509, -0.980785), (5.06639e-07, 0, -1), (4.96905e-07, -0.19509, -0.980785), 
        (4.68074e-07, -0.382683, -0.923879), (4.21255e-07, -0.55557, -0.83147), (3.58248e-07, -0.707107, -0.707107), (2.81474e-07, -0.83147, -0.55557), (1.93883e-07, -0.92388, -0.382683), (9.88405e-08, -0.980785, -0.19509), 
        (0, -1, 0), (-2.90707e-08, -0.980785, 0.19509), (-5.70243e-08, -0.92388, 0.382683), (-8.27864e-08, -0.83147, 0.55557), (-1.05367e-07, -0.707107, 0.707107), (-1.23899e-07, -0.55557, 0.83147), (-1.37669e-07, -0.382683, 0.92388), 
        (-1.46148e-07, -0.19509, 0.980785), (-1.49012e-07, 0, 1), (-1.46148e-07, 0.19509, 0.980785), (-1.37669e-07, 0.382683, 0.92388), (-1.23899e-07, 0.55557, 0.83147), (-1.05367e-07, 0.707107, 0.707107), (-8.27864e-08, 0.83147, 0.55557), 
        (-5.70243e-08, 0.92388, 0.382683), (-2.90707e-08, 0.980785, 0.19509), (0, 1, 0), (-2.90707e-08, 0.980785, 0.19509), (-5.70243e-08, 0.92388, 0.382683), (-8.27864e-08, 0.83147, 0.55557), (-1.05367e-07, 0.707107, 0.707107), 
        (-1.23899e-07, 0.55557, 0.83147), (-1.37669e-07, 0.382683, 0.92388), (-1.46148e-07, 0.19509, 0.980785), (-1.49012e-07, 0, 1), (-0.382684, 0, 0.923879), (-0.707107, 0, 0.707107), (-0.92388, 0, 0.382683), (-1, 0, -3.57628e-07), 
        (-0.923879, 0, -0.382684), (-0.707106, 0, -0.707107), (-0.382683, 0, -0.92388), (5.06639e-07, 0, -1), (0.382684, 0, -0.923879), (0.707107, 0, -0.707106), (0.92388, 0, -0.382683), (1, 0, 0), (0.92388, 0, 0.382683), (0.707107, 0, 0.707107), 
        (0.382683, 0, 0.92388), (-1.49012e-07, 0, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88], d=1,n = str(c)[0] + '_Brow_CC_'+str(c)[-1])
        colorShape(Color = 13)
        rootAuto()
        cmds.xform(str(c)[0] + '_Brow_CC_'+str(c)[-1]+'_Root', m = cmds.xform(c,q = True, m =True, ws = True), ws = True)        
        cmds.parent(c, CC)
                     
                     
                     
    #Order everything
        
    cmds.delete('R_Brow_Bind_JC_1_Mirror','R_Brow_Bind_JC_2_Mirror','R_Brow_Bind_JC_3_Mirror')
    cmds.group('R_Brow_Mirror','L_Brow',n = 'Brow_Nurbs_GRP')
    cmds.group('L_BrowFollicle_GRP','R_BrowFollicle_GRP',n = 'Brow_Follicle_GRP')    
    cmds.group('L_Brow_CC_1_Root','L_Brow_CC_2_Root','L_Brow_CC_3_Root',n = 'L_Brow_GRP')    
    cmds.group('R_Brow_CC_1_Root','R_Brow_CC_2_Root','R_Brow_CC_3_Root',n = 'R_Brow_GRP')    
    cmds.group('Brow_Nurbs_GRP','Brow_Follicle_GRP','L_Brow_GRP','R_Brow_GRP',n = 'Brows_RdMAutoRig_GRP')  
    
    #All Brows Ctrl
    for i in ['L_Brow_GRP', 'R_Brow_GRP']:
        CC = cmds.curve(n = i + "_CC" , d=1, p=[(1, 1, 1),(1,1,-1) ,(1, -1, -1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, 1, 1) ,(1, 1, 1) ,(1, -1, 1) ,
        (-1, -1, 1) ,(-1, -1, -1) ,(-1, 1, -1) ,(1, 1, -1) ,(1, -1, -1) ,(-1, -1, -1) ,(-1, 1, -1) ,(-1, 1, 1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
        cmds.delete(cmds.parentConstraint(i,CC, mo =False))
        cmds.parent(i , CC)
        cmds.parent(CC, 'Brows_RdMAutoRig_GRP')
        colorShape(Color = 16)
        cmds.select(CC)
        rootAuto()

    #Create Sets
    bindJoints = []
    for i in range(0,5):
        bindJoints.append('L_Brow_Bind_JJ'+str(i+1))  
        bindJoints.append('R_Brow_Bind_JJ'+str(i+1))
      
    cmds.select(bindJoints)
    cmds.sets(n = 'BindThisToBrows')


    #Connect to Head
    if cmds.objExists('Head_CC'):
        cmds.parentConstraint('Head_CC','L_Brow_GRP_CC_Root', mo =True)
        cmds.scaleConstraint('Head_CC','L_Brow_GRP_CC_Root', mo =True)
        cmds.parentConstraint('Head_CC','R_Brow_GRP_CC_Root', mo =True)
        cmds.scaleConstraint('Head_CC','R_Brow_GRP_CC_Root', mo =True)

    if cmds.objExists('Facial_RdM_Autorig'):
        pass
    else:
        cmds.select(cl = True)
        cmds.group(n = 'Facial_RdM_Autorig', em = True)

    cmds.parent('Facial_RdM_Autorig','Brows_RdMAutoRig_GRP')
    cmds.setAttr('Brow_Nurbs_GRP.visibility',0)

    cmds.undoInfo(closeChunk=True)  
  
'''    

polyToNurbs(Name = 'L_Brow', mirror = True)    


'''

#createRibbons(bindJoints = 5, controljoints = 3, controllersSize = 1, mode = 'v')




