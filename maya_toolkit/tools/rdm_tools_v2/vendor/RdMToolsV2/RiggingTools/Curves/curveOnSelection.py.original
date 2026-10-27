from maya import cmds
from RdMToolsV2.RiggingTools.Curves.RootAuto import rootAuto 

def curveOnSelectionFunc(mode = 'Cube',Constraint = False, offset = False, *args):
    
    cmds.undoInfo(openChunk=True)   

    selection = cmds.ls(sl = True)
    if len(selection) == 0:
        selection = cmds.spaceLocator(n = str(mode))           
    
    for p in selection:
        
        cmds.select(p)
        Selection = cmds.ls(sl = True)
        
        if len(Selection) == 0:
            Selection = str(mode)
        else:
            print Selection
            Selection = Selection[0]
            object = Selection
            print object
    
        if mode == 'Joint':
            cmds.select(cl = True)
            Curve = cmds.joint(n=str(Selection)+ "_Jnt" )
            cmds.select(Curve)
    
        if mode == 'Locator':
            cmds.select(cl = True)
            Curve = cmds.spaceLocator(n = str(Selection)+ "_Loc" )
            cmds.select(Curve)
    
        if mode == 'CircleX': 
            cmds.select(cl = True)
            Curve = cmds.circle(n=str(Selection)+ "_CC" , nr =(1,0,0))[0]
            cmds.select(Curve)
    
        if mode == 'CircleY':
            cmds.select(cl = True)
            Curve = cmds.circle(n=str(Selection)+ "_CC" , nr =(0,1,0))[0]
            cmds.select(Curve)
    
        if mode == 'CircleZ':
            cmds.select(cl = True)
            Curve = cmds.circle(n=str(Selection)+ "_CC" , nr =(0,0,1))[0]
            cmds.select(Curve)
    
        if mode == 'Sphere':
            x = 1
            while cmds.objExists(str(Selection) + '_Sphere_CC'):
                try :
                    Selection = Selection + 1
                except:
                    Selection = Selection + '1'
        
                          
            Curve = cmds.circle(n=str(Selection) + '_Sphere_CC' , nr =(0,0,1))
            Curve1 = cmds.circle(n=str(Selection) + '_Sphere_CC1' , nr =(0,1,0))
            Curve2 = cmds.circle(n=str(Selection) + '_Sphere_CC2' , nr =(1,0,0))
            cmds.parent(str(Curve1[0])  + 'Shape', Curve[0], r = True, s = True)
            cmds.parent(str(Curve2[0])  + 'Shape', Curve[0], r = True, s = True)
            cmds.delete(Curve1, Curve2)       
            cmds.select(Curve)
    
    
        if mode == 'Cube': 
            Curve = cmds.curve(n=str(Selection) + "_CC" , d=1, p=[(1, 1, 1),(1,1,-1) ,(1, -1, -1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, 1, 1) ,(1, 1, 1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, -1, -1) ,(-1, 1, -1) ,(1, 1, -1) ,(1, -1, -1) ,(-1, -1, -1) ,(-1, 1, -1) ,(-1, 1, 1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
            cmds.select(Curve)
        
        if mode == 'Hand':
            Curve = cmds.curve(n=str(Selection) + "_CC",  p =[[0.7982363549443874, -0.03312381394884196, 0.0], [0.246083465367747, -0.033123657085117816, 0.0], [-0.48278001289794936, -0.033123343357669525, 0.0], [-1.4825557066778388, 0.5726820184225275, 0.0], [-2.663688492765169, 2.7115049577573838, 0.0], [-3.1247693147700715, 3.254010024815882, 0.0], [-2.9412817125285353, 4.002830167445566, 0.0], [-2.1107110753984024, 4.085517598961959, 0.0], [-1.6908599024451583, 3.2224952161058953, 0.0], [-1.400467277219339, 2.647682334618429, 0.0], [-1.4004692670294752, 3.684792092308598, 0.0], [-1.400469267047782, 6.998794103871373, 0.0], [-0.9042252110773584, 7.137820711521537, 0.0], [-0.5228261595994259, 6.998789620250499, 0.0], [-0.5228279292069075, 5.403915926958552, 0.0], [-0.5228269979544187, 4.040448049933847, 0.0], [-0.3949846246752978, 4.040447831591451, 0.0], [-0.2180932090311397, 4.040446899463086, 0.0], [-0.21809354465088623, 5.715454672546393, 0.0], [-0.21809463304598897, 7.722113943947256, 0.0], [0.2451357512230513, 7.86113752895071, 0.0], [0.7066220583909373, 7.722113750990215, 0.0], [0.7066211505481725, 5.718312802074311, 0.0], [0.7066208961515005, 4.103016801105229, 0.0], [0.8410525122559298, 4.103020532229875, 0.0], [0.9966602778711925, 4.103016937008975, 0.0], [0.9966606415822326, 6.035575008902293, 0.0], [0.9966592015876571, 7.2635999499324635, 0.0], [1.4554726059774596, 7.455477082045534, 0.0], [1.9192120582357546, 7.243737117292962, 0.0], [1.9192106877909976, 5.966376670979836, 0.0], [1.9192103009877264, 3.9213588887276174, 0.0], [2.0230261830917007, 3.9213617215842027, 0.0], [2.116209263686871, 3.921358867869387, 0.0], [2.116209263692829, 5.380122221504778, 0.0], [2.1162073135002957, 6.246227931950929, 0.0], [2.596313005782029, 6.606062906787962, 0.0], [3.1196265628959137, 6.307385007325626, 0.0], [3.1196245993664937, 5.135493774335305, 0.0], [3.1196258860212227, 3.878459031126682, 0.0], [3.119624932673482, 2.571691249639972, 0.0], [3.158803975933098, 1.1030508178821383, 0.0], [2.169119497585999, -0.0331236473135145, 0.0], [1.4655497485583755, -0.0331235106546292, 0.0], [0.7982362310698355, -0.03312344232518655, 0.0]],
            per = False, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44])
                        
            Curve = cmds.rebuildCurve(ch=0, rpo=1, rt=1, end = 1, kr =0, kcp =1, kep=1, kt=0,s=20,d=3,tol=0.01)
            cmds.select(Curve)
    
       
        if mode == 'Foot':
            Curve = cmds.curve(n=str(Selection) + "_CC", p =[[1.3484978854098617, 0.002162300000000264, 0.6510500531154664], [0.031939100000000095, 0.002162300000000293, -0.26168952655773037], [-1.476254185409861, -0.010811499999999735, 0.3957070531154665], [-1.3998607784989097, 0.002162300000000183, 2.42006135898006], [0.12644282473547985, 0.002162300000000065, 3.9004625425857276], [-1.2688091752645207, 0.0021622999999999348, 6.0319814574142745], [-1.5161647784989087, 0.002162299999999817, 7.952413641019943], [-0.5349241854098623, 0.0021622999999997357, 9.281393946884535], [0.7433230999999996, 0.0021622999999997066, 9.755701526557736], [1.983494385409861, 0.0021622999999997357, 8.917633946884537], [2.4626899784989105, 0.002162299999999817, 7.952413641019945], [2.673610375264521, 0.0021622999999999348, 6.031981457414275], [2.4349003752645206, 0.002162300000000065, 3.9004625425857284], [1.8967769784989115, 0.002162300000000183, 1.9800303589800583], [1.348,0.00216,0.651]],
            per = False, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,14])
                
            Curve = cmds.rebuildCurve(ch=0, rpo=1, rt=1, end = 1, kr =0, kcp =1, kep=1, kt=0,s=20,d=3,tol=0.01)
            cmds.select(Curve)


        if mode == 'Pyramids':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(-0.5, -0.5, -0.5), (0, 0.5, 0), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (0, 0.5, 0), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], d=1)
                
            cmds.select(Curve)

        if mode == 'Square':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(0.5, 0.0111736, -0.5), (0.5, -0.0111736, 0.5), (-0.5, -0.0111736, 0.5), (-0.5, 0.0111736, -0.5), (0.5, 0.0111736, -0.5)], k=[0, 1, 2, 3, 4], d=1)
            cmds.select(Curve)


        if mode == 'Arrow':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(0.5, 0.00379908, 0.5), (-0.5, 0.00379908, 0.5), (-0.195663, 0.00379921, 0.937632), (-1.629296, 0.0037986, 5.96046e-08), (-0.195663, 0.00379921, -0.937632), (-0.5, 0.00379908, -0.5), (0.5, 0.00379908, -0.5), (0.5, 0.00379908, 0.5)], k=[0, 1, 2, 3, 4, 5, 6, 7], d=1)
            
            
            cmds.select(Curve)

        if mode == 'MultipleArrows':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(0.467843, 0.00379908, 0.490368), (0.467843, 0.00379908, 1.679979), (1.082301, 0.00379921, 1.376763), (-0.0321573, 0.0037986, 3.615697), (-1.146616, 0.00379921, 1.376763), (-0.532157, 0.00379908, 1.679979), (-0.534007, 0.00379908, 0.5), (-1.712137, 0.00379908, 0.5), (-1.408921, 0.00379921, 1.114459), (-3.647855, 0.0037986, 5.96046e-08), (-1.408921, 0.00379921, -1.114459), (-1.712137, 0.00379908, -0.5), (-0.532157, 0.00379908, -0.495999), (-0.532157, 0.00379908, -1.679979), (-1.146616, 0.00379921, -1.376763), (-0.0321574, 0.0037986, -3.615697), (1.082301, 0.00379921, -1.376763), (0.467843, 0.00379908, -1.679979), (0.467355, 0.00379908, -0.5), (1.647822, 0.00379908, -0.5), (1.344606, 0.00379921, -1.114459), (3.58354, 0.0037986, -5.96046e-08), (1.344606, 0.00379921, 1.114459), (1.647822, 0.00379908, 0.5), (0.467843, 0.00379908, 0.490368)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], d=1)
            
            
            cmds.select(Curve)

        if mode == 'SideArrows':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(-0.735589, 0.00379908, 0.5), (-0.213927, 0.00379921, 0.937632), (-2.671307, 0.0037986, 5.96046e-08), (-0.213927, 0.00379921, -0.937632), (-0.735589, 0.00379908, -0.5), (0.978503, 0.00379908, -0.5), (0.468925, 0.00379921, -0.937632), (2.926305, 0.0037986, -5.96046e-08), (0.468925, 0.00379921, 0.937632), (0.990587, 0.00379908, 0.5), (-0.735589, 0.00379908, 0.5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], d=1)
            
            
            cmds.select(Curve)

        if mode == 'LineArrow':
            Curve = cmds.curve(n=str(Selection) + "_CC",p=[(0, 0, -1.529415), (0.5, 0, -0.529415), (0.0440401, 0, -0.532721), (0.0440401, 0, 2.560786), (0.361761, -0.00575372, 2.684397), (0.511607, -0.00575372, 3.046158), (0.361761, -0.00575372, 3.407919), (0, 0.00575372, 3.557765), (-0.361761, 0.00575372, 3.407919), (-0.511607, 0.00575372, 3.046158), (-0.361761, 0.00575372, 2.684397), (-0.0440401, 0, 2.560786), (-0.0440401, 0, -0.532721), (-0.5, 0, -0.529415), (0, 0, -1.529415)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], d=1)
            
            cmds.select(Curve)

    
        if mode == 'EyeVisor':
            #Visor Basico
            LCircle=cmds.circle(n = str(Selection) + 'L_Eye', nr = (0,0,1))
            LCircleGRP=cmds.group(LCircle, n = str(Selection)+'L_Eye_GRP')            
            RCircle=cmds.circle(n = str(Selection)+'R_Eye', nr = (0,0,1))
            RCircleGRP =cmds.group(RCircle, n = str(Selection)+ 'R_Eye_GRP')
            Curve=cmds.circle(n = str(Selection) + '_Visor', nr = (0,0,1))[0]
            
            cmds.xform(Curve, s = (2.5,1.7,2.5))
    
            cmds.parent(LCircleGRP, Curve, a = True)
            cmds.parent(RCircleGRP, Curve, a = True)
            #VisorPosition
            cmds.setAttr('%s.translateX'%(LCircle[0]) , 1.1)
            cmds.setAttr('%s.translateX'%(RCircle[0]) , -1.1)
            cmds.select(Curve)
                
    
        if mode == 'Pringle':
                #Turn off Mirror X
            cmds.symmetricModelling(symmetry=False)
            cmds.softSelect(sse=0)   
            Curve = cmds.circle (n=str(Selection) + "_CC", r = 2,nr =(0,1,0) )[0]
            cmds.select ('%s.cv[5]'%(Curve),'%s.cv[1]'%(Curve))
            cmds.move (0, -1 ,0, r = True)
            cmds.select(Curve)
    
        try: 
            cmds.setAttr ('%s.overrideEnabled'%(Curve), 1)
            cmds.setAttr ('%s.overrideColor'%(Curve), 16)
        except: 
            pass
        try: 
            cmds.setAttr ('%s.overrideEnabled'%(Curve[0]), 1)
            cmds.setAttr ('%s.overrideColor'%(Curve[0]), 16)
        except: 
            pass 
        try:
            cmds.matchTransform(Curve, object)
        except: 
            pass
    
        if Constraint == True:
            cmds.parentConstraint(Curve,object, mo = True)
        
        cmds.select(Curve)     
        ''' 
        try:
            newName = str(Curve).replace('_JJ','')
            cmds.rename(Curve, newName)
            Curve = newName
        except:
            pass    
        '''
        if offset == True:
            cmds.select(Curve)
            rootAuto()

    try:
        cmds.delete(str(mode))
        
    except:
        pass      
       
   
        
    cmds.undoInfo(closeChunk=True)   
    
    
'''
curveOnSelectionFunc(mode = 'Joint',Constraint = False)

curveOnSelectionFunc(mode = 'Locator',Constraint = False)

curveOnSelectionFunc(mode = 'EyeVisor',Constraint = False)

curveOnSelectionFunc(mode = 'Hand',Constraint = False)

curveOnSelectionFunc(mode = 'Foot',Constraint = False)

curveOnSelectionFunc(mode = 'Cube',Constraint = False)

curveOnSelectionFunc(mode = 'Sphere',Constraint = False)

curveOnSelectionFunc(mode = 'CircleX',Constraint = False)

curveOnSelectionFunc(mode = 'CircleY',Constraint = False)

curveOnSelectionFunc(mode = 'CircleZ',Constraint = False)

curveOnSelectionFunc(mode = 'Pringle', offset = 1,Constraint = False)

'''