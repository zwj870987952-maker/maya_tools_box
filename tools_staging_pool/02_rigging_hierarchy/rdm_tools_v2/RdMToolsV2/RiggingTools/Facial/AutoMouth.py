from maya import cmds
import maya.mel as mel
import pymel.core as pm

import RdMToolsV2
from RdMToolsV2.RiggingTools.Facial.EdgeToCurve import edgeToCv
from RdMToolsV2.RiggingTools.Tools.MirrorBehavior import mirrorParts
from RdMToolsV2.RiggingTools.Curves.RootAuto import rootAuto 
from RdMToolsV2.RiggingTools.Curves.CurveColors import colorShape


def LipNurbs(size, Name):
    cmds.undoInfo(openChunk=True) 

    upperLipLoop = cmds.ls(sl=True)
    Curve = edgeToCv(cvs = 5, customName = Name + '01')
    Curve2 = cmds.duplicate(Name + '01_CV', n =  Name + '02_CV')
    
    #Create Nurbs Plane
    CornerPos = cmds.pointPosition( Name + '01_CV.cv[0]')
    print CornerPos    
    cmds.move(0,0,size, Name + '01_CV')
    cmds.move(0,0,-size, Name + '02_CV')
    Plane = cmds.loft(Name + '02_CV', Name + '01_CV', c=0, ch=0, d=3, ss=1, rsn=True, ar=1, u=1, rn=0, po=0, n = Name)
    
    #GetCorner Position


    
    cmds.delete(Name + '01_CV', Name + '02_CV')

    #Create Follicles
   
    follicles = pm.mel.createHair(5, 1, 10, 0, 0, 0, 0, 5, 0, 1, 2, 1)
    deleteList = ('hairSystem1','pfxHair1','nucleus1','hairSystem2','pfxHair2','nucleus2' )
    for i in deleteList:
        
        try:
            cmds.delete(i)
            
        except:
            pass
            
       
    cmds.rename ('hairSystem1Follicles', Name + '_Follicle_GRP')
    
    Follicles = cmds.ls (Name + '_Follicle_GRP', dag = True, type = 'follicle')

    x=1
    BindSet = []
    for i in Follicles:
        cmds.select(i)
        cmds.pickWalk(d='up')
        newI = cmds.rename(Name + '_Follicle')  
        cmds.select(newI)
        cmds.joint(n = Name + '_Bind_JJ'+str(x))  
        cmds.delete(cmds.pickWalk(d='left'))

        cmds.select(cl=True)
        BindSet.append(Name + '_Bind_JJ'+str(x))
        x=x+1

    cmds.delete(BindSet[3],BindSet[4]) 
    
    
    #GetCorner Locator
    if cmds.objExists('L_corner_loc'):
        pass
    else:
        Loc = cmds.spaceLocator(n = 'L_corner_loc')
        cmds.xform(Loc, t = CornerPos) 
        cmds.setAttr("L_corner_loc.rotateY", -90)
        cmds.setAttr("L_corner_loc.rotateX", -90)

        
    #Turn on symmetry
    pm.mel.reflectionBuildMenu('StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|symmetryIcons|symModelingBtn|popupMenu9')
    pm.mel.reflectionSetMode('objectx')

    #If it goes to right instead on left
    if cmds.xform(Name + '_Bind_JJ1', q = True, t = True, ws = True)[0] > 0:
        print 'positive'
    else:
        print 'negative'
        cmds.setAttr(Name + '.scaleX' , -1)
        cmds.makeIdentity(Name, s = True)

    
    cmds.undoInfo(closeChunk=True)      
'''
cmds.select('Body.e[5799]', 'Body.e[5872]', 'Body.e[5877]', 'Body.e[6267]', 'Body.e[6271]', 'Body.e[6275]', 'Body.e[6279]', 'Body.e[6283]', 'Body.e[6323]', 'Body.e[6327]', 'Body.e[13550]', 'Body.e[13623]', 'Body.e[13628]', 'Body.e[14025]', 'Body.e[14029]', 'Body.e[14033]', 'Body.e[14037]', 'Body.e[14041]', 'Body.e[14081]', 'Body.e[14085]', add=1)
LipNurbs(size = 1, Name = 'upperLip')

mel.eval('select Body.e[7141] Body.e[7156] Body.e[7159] Body.e[7163] Body.e[7169:7170] Body.e[7186:7187] Body.e[7192:7193] Body.e[7196] Body.e[14887] Body.e[14902] Body.e[14905] Body.e[14909] Body.e[14915:14916] Body.e[14932:14933] Body.e[14938:14939] Body.e[14942] ;')
LipNurbs(size = 1, Name = 'lowerLip')
'''

def LipsSystem(Scale):

    cmds.undoInfo(openChunk=True)  

    cmds.progressWindow(title='Mouth', progress=0, status='Starting', isInterruptable=True ,maxValue=10)


    
    if cmds.objExists('upperLip_Bind_JJ1') == False:
        cmds.error('Do the first step first :D', n = False)
    
    #Turn off symmetry
    pm.mel.reflectionBuildMenu('StatusLine|MainStatusLineLayout|formLayout4|flowLayout1|symmetryIcons|symModelingBtn|popupMenu9')
    pm.mel.reflectionSetMode('none')
    
    upLip = ['upperLip_Bind_JJ1', 'upperLip_Bind_JJ2', 'upperLip_Bind_JJ3']
    lowLip = ['lowerLip_Bind_JJ1', 'lowerLip_Bind_JJ2', 'lowerLip_Bind_JJ3']
    BindJoints = upLip + lowLip
    LeftJoints = upLip + lowLip
    
    #Clean the Joints
    for i in upLip and lowLip:
        cmds.makeIdentity(i, n=0, s=1, r=1, t=1, apply=True, pn=1)
        cmds.select(i)
        rootAuto()

        
    #Other Side Joints
    newNames = ['upperLip_Bind_JJ5','upperLip_Bind_JJ4','lowerLip_Bind_JJ5','lowerLip_Bind_JJ4']
    parents = ['upperLip_Follicle4','upperLip_Follicle3','lowerLip_Follicle4','lowerLip_Follicle3']
    x=0
    
    for i in upLip[0],upLip[1],lowLip[0],lowLip[1]:
        cmds.select(cl = True)
        Joint = cmds.joint(n = newNames[x])
        cmds.makeIdentity(i, n=0, s=1, r=1, t=1, apply=True, pn=1)
        cmds.delete(cmds.parentConstraint(i , Joint, mo = False))
        cmds.select(Joint)
        rootAuto()
        
        cmds.select(str(Joint)+'_Root')
        mirrorParts(world = True)
        
        cmds.parent(str(Joint)+'_Root_Mirror', parents[x])
        x = x+1
        BindJoints.append(Joint)
        cmds.makeIdentity(Joint, n=0, s=1, r=1, t=1, apply=True, pn=1)
    
    print BindJoints
    
    cmds.progressWindow(edit=True, progress=1, status='Create Controllers')
    
    #CreateControllers
    for c in LeftJoints:
        CCName = str(c).replace('JJ', 'CC')
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
         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88], d=1,n = CCName)
        
        
        cmds.delete(cmds.parentConstraint(c, CC, mo = False))
        cmds.select(CC)
        colorShape(Color = 17 if str(CC)[0] == 'u' else 14)
        rootAuto()
        
        
   
    MirrorCC = ['upperLip_Bind_CC1','upperLip_Bind_CC2','lowerLip_Bind_CC1','lowerLip_Bind_CC2']
    NewNamesCC = ['upperLip_Bind_CC5','upperLip_Bind_CC4','lowerLip_Bind_CC5','lowerLip_Bind_CC4']    
    x = 0
    for c in MirrorCC:
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
         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88], d=1,n = NewNamesCC[x])
        
        cmds.delete(cmds.parentConstraint(c, CC, mo = False))
        cmds.select(CC)
        colorShape(Color = 17 if str(CC)[0] == 'u' else 14)
        rootAuto()
        cmds.select(str(CC)+'_Root')
        Mirror = mirrorParts(world = True)     
        cmds.select(cl = True)
        x = x+1

    cmds.progressWindow(edit=True, progress=2, status='Adjust Hy')
    
    #Change Herarchy and groups
    cmds.group('upperLip','lowerLip',n ='Mouth_Nurbs_GRP') 
    cmds.group('upperLip_Bind_CC1_Root','upperLip_Bind_CC2_Root','upperLip_Bind_CC3_Root','upperLip_Bind_CC4_Root_Mirror','upperLip_Bind_CC5_Root_Mirror',n ='upper_Mouth_GRP') 
    cmds.group('lowerLip_Bind_CC1_Root','lowerLip_Bind_CC2_Root','lowerLip_Bind_CC3_Root','lowerLip_Bind_CC4_Root_Mirror','lowerLip_Bind_CC5_Root_Mirror',n ='lower_Mouth_GRP') 
    cmds.group('Mouth_Nurbs_GRP','upperLip_Follicle_GRP','lowerLip_Follicle_GRP','upper_Mouth_GRP','lower_Mouth_GRP',n ='Mouth_RdMAutoRig_GRP') 
    cmds.group('upperLip_Follicle_GRP','lowerLip_Follicle_GRP',n ='Mouth_Follicles_GRP') 
    cmds.setAttr('Mouth_Nurbs_GRP.visibility', 0)
        
    #Bind Joints
    jointHere = ['L_corner_loc','upperLip_Bind_JJ3','lowerLip_Bind_JJ3']
    nameHere = ['L_MouthCorner_JC','MouthUp_JC','MouthDown_JC']
    
    y = 0
    for i in jointHere:
        cmds.select(cl=True)
        JJ = cmds.joint(n = nameHere[y], rad = 1.5)
        matrix = cmds.xform(jointHere[y], q = True, m = True, ws = True)
        cmds.xform(JJ, m = matrix)
        cmds.makeIdentity(JJ, n=0, s=1, r=1, t=1, apply=True, pn=1)
        rootAuto()        
        y = y + 1
    
    #Create other Corner Joint
    cmds.select(cl = True)
    JJ = cmds.joint(n = 'R_MouthCorner_JC', rad = 1.5)
    cmds.xform(JJ, m =cmds.xform('L_MouthCorner_JC', q = True , m = True, ws = True), ws = True)
    rootAuto()
    cmds.select(str(JJ)+'_Root')
    mirrorParts(world = True)  
    
    #Group and Bind
    GRP = cmds.group('L_MouthCorner_JC_Root','MouthUp_JC_Root','MouthDown_JC_Root','R_MouthCorner_JC_Root_Mirror', n='Mouth_Bind_JC_GRP')
    cmds.parent(GRP, 'Mouth_RdMAutoRig_GRP')
    cmds.delete('L_corner_loc') 
    

    cmds.progressWindow(edit=True, progress=3, status='Bind Ribbon')    
    
    ribbonsName1 = 'upperLip'
    ribbonsName2 = 'lowerLip'
    JointsControl1 = ['L_MouthCorner_JC','R_MouthCorner_JC','MouthUp_JC']
    JointsControl2 = ['L_MouthCorner_JC','R_MouthCorner_JC','MouthDown_JC']
   
    
    #Square Controllers for Ribbon
    AllJC = JointsControl1 + ['MouthDown_JC']
    def cubeCurve(Name):
        cmds.curve(n=str(Name) + "_CC" , d=1, p=[(1, 1, 1),(1,1,-1) ,(1, -1, -1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, 1, 1) ,(1, 1, 1) ,(1, -1, 1) ,
        (-1, -1, 1) ,(-1, -1, -1) ,(-1, 1, -1) ,(1, 1, -1) ,(1, -1, -1) ,(-1, -1, -1) ,(-1, 1, -1) ,(-1, 1, 1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

    for i in 'L_MouthCorner_JC','MouthDown_JC','MouthUp_JC':
        CC = cubeCurve(Name = str(i).replace('_JC',''))             
        cmds.xform(CC, m = cmds.xform(i, q = True, m = True, ws = True), ws = True)
        rootAuto()
        colorShape(Color = 16)
    
    CC = cubeCurve(Name = 'R_MouthCorner')
    cmds.xform(CC, m = cmds.xform('L_MouthCorner_CC', q = True, m = True, ws = True), ws = True)
    rootAuto()
    cmds.select('R_MouthCorner_CC_Root')
    mirrorParts(world = True)  
    colorShape(Color = 16)

    #Extra Controllers
    
    cmds.group('MouthDown_CC_Root','MouthUp_CC_Root', n = 'Mid_MouthCtrl_GRP', r = True)
    cmds.group('L_MouthCorner_CC_Root','R_MouthCorner_CC_Root_Mirror','Mid_MouthCtrl_GRP', n = 'All_MouthCtrl_GRP', r = True)
    cmds.group('MouthUp_JC_Root','MouthDown_JC_Root', n = 'Mid_Mouth_JC_GRP')
    
    for i in 'All_MouthCtrl_GRP', 'Mid_MouthCtrl_GRP': 
        if str(i)[0] == 'M':
            CC = cmds.curve(n = str(i).replace('GRP','CC') ,p=[(0.5, 0.0111736, -0.5), (0.5, -0.0111736, 0.5), (-0.5, -0.0111736, 0.5), (-0.5, 0.0111736, -0.5), (0.5, 0.0111736, -0.5)], k=[0, 1, 2, 3, 4], d=1)
        else: 
            CC = cmds.curve(n = str(i).replace('GRP','CC'),p=[(0.467843, 0.00379908, 0.490368), (0.467843, 0.00379908, 1.679979), (1.082301, 0.00379921, 1.376763), (-0.0321573, 0.0037986, 3.615697), (-1.146616, 0.00379921, 1.376763), (-0.532157, 0.00379908, 1.679979), (-0.534007, 0.00379908, 0.5), (-1.712137, 0.00379908, 0.5), (-1.408921, 0.00379921, 1.114459), (-3.647855, 0.0037986, 5.96046e-08), (-1.408921, 0.00379921, -1.114459), (-1.712137, 0.00379908, -0.5), (-0.532157, 0.00379908, -0.495999), (-0.532157, 0.00379908, -1.679979), (-1.146616, 0.00379921, -1.376763), (-0.0321574, 0.0037986, -3.615697), (1.082301, 0.00379921, -1.376763), (0.467843, 0.00379908, -1.679979), (0.467355, 0.00379908, -0.5), (1.647822, 0.00379908, -0.5), (1.344606, 0.00379921, -1.114459), (3.58354, 0.0037986, -5.96046e-08), (1.344606, 0.00379921, 1.114459), (1.647822, 0.00379908, 0.5), (0.467843, 0.00379908, 0.490368)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], d=1)
           
        cmds.delete(cmds.pointConstraint(i, CC, mo =False))
        rootAuto() 
        colorShape(Color = 9)        
                     
        
        if str(i)[0] == 'M':
            cmds.setAttr(str(CC)+ '_Root.translateZ', cmds.getAttr('upperLip_Bind_CC2_Root.translateX')+cmds.getAttr(str(CC)+ '_Root.translateZ'))    
        else: 
            cmds.setAttr(str(CC)+ '_Root.translateZ', cmds.getAttr('upperLip_Bind_CC2_Root.translateX')+cmds.getAttr(str(CC)+ '_Root.translateZ')*1.1)    
    
    
    #Connect Everything
    This = ['All_MouthCtrl_CC','Mid_MouthCtrl_CC','L_MouthCorner_CC','R_MouthCorner_CC','MouthUp_CC','MouthDown_CC',
    'upperLip_Bind_CC1','upperLip_Bind_CC2','upperLip_Bind_CC3','upperLip_Bind_CC4','upperLip_Bind_CC5',
    'lowerLip_Bind_CC1','lowerLip_Bind_CC2','lowerLip_Bind_CC3','lowerLip_Bind_CC4','lowerLip_Bind_CC5']
    
    That = ['Mouth_Bind_JC_GRP','Mid_Mouth_JC_GRP','L_MouthCorner_JC','R_MouthCorner_JC','MouthUp_JC','MouthDown_JC',
    'upperLip_Bind_JJ1','upperLip_Bind_JJ2','upperLip_Bind_JJ3','upperLip_Bind_JJ4','upperLip_Bind_JJ5',
    'lowerLip_Bind_JJ1','lowerLip_Bind_JJ2','lowerLip_Bind_JJ3','lowerLip_Bind_JJ4','lowerLip_Bind_JJ5']
    
    x = 0
    for i in This:
        cmds.connectAttr(str(i)+'.translate', str(That[x])+'.translate', f = True)
        cmds.connectAttr(str(i)+'.rotate', str(That[x])+'.rotate', f = True)
        cmds.connectAttr(str(i)+'.scale', str(That[x])+'.scale', f = True)
        x = x + 1   
   
    cmds.select('All_MouthCtrl_CC.cv[0:24]')
    cmds.rotate(90,0,0)
    cmds.scale(0.5,0.5,0.5)
    cmds.select('Mid_MouthCtrl_CC.cv[0:4]')
    cmds.rotate(90,0,0)   
    #Group and Clean
    GRP = cmds.group('upper_Mouth_GRP','lower_Mouth_GRP','All_MouthCtrl_GRP','All_MouthCtrl_CC_Root','Mid_MouthCtrl_CC_Root', n = 'MoveThis_Mouth_Ctrl_GRP')      
    cmds.parent(GRP , 'Mouth_RdMAutoRig_GRP')  
    
    #Create Bind Set
    cmds.select(BindJoints)
    cmds.sets(n = 'BindThisToMouth')

    #Skin the ribbon
    ribbonsName1 = 'upperLip'
    ribbonsName2 = 'lowerLip'
    JointsControl1 = ['L_MouthCorner_JC','R_MouthCorner_JC','MouthUp_JC']
    JointsControl2 = ['L_MouthCorner_JC','R_MouthCorner_JC','MouthDown_JC']
    
    cmds.skinCluster(JointsControl1, ribbonsName1, sm =0 , bm =0, tsb  = True )
    cmds.skinCluster(JointsControl2, ribbonsName2, sm =0 , bm =0, tsb  = True )



    cmds.progressWindow(edit=True, progress=4, status='End')
    cmds.progressWindow(endProgress=1)
    #
    print 'Done'

    cmds.undoInfo(closeChunk=True)   
      
'''      

LipsSystem(Scale = 1)  


'''

  

    
    
    
    