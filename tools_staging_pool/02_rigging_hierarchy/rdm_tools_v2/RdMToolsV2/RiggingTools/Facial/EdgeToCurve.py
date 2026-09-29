from maya import cmds

def edgeToCv(cvs = 2, customName = 'EdgeToCurve'):

    cmds.undoInfo(openChunk=True)  
    
    cv = cmds.polyToCurve(conformToSmoothMeshPreview=1, degree=3, form=2, n = customName + '_CV')
    newCv = cmds.rebuildCurve(cv, rt=0, ch=1, end=1, d=2, kr=0, s=cvs, kcp=0, tol=0.01, kt=0, rpo=1, kep=1)[0]
    cmds.delete(cv, ch=True)
    cmds.xform(newCv, cp=1)

    cmds.undoInfo(closeChunk=True)  

def locOnCurve(amount = 3, customName = 'locatorName'):

    cmds.undoInfo(openChunk=True)      
    locs = []
    Paths = []
    
    for i in range(amount):
        loc = cmds.spaceLocator(n = customName + '_0' + str(i+1))[0]
        locs.append(loc) 
        cmds.joint(n =  customName + '_0' + str(i+1)+'_Jnt')
        
        Path = cmds.pathAnimation (loc, customName + '_CV')
        Path = cmds.rename(Path, customName + '_0' + str(i+1)+'_Jnt' )
        Paths.append(Path)
        
        attr = str(Path)+'.u' 
        maya.mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\""%attr)   
        cmds.orientConstraint(customName + '_CV', loc, mo=True)
      
    #position in the correct length of the cv
      
    if len(locs) == 3:
        cmds.setAttr(str(Paths[0])+'.uValue', 0)
        cmds.setAttr(str(Paths[1])+'.uValue', 0.5)
        cmds.setAttr(str(Paths[2])+'.uValue', 1)

    if len(locs) == 5:
        cmds.setAttr(str(Paths[0])+'.uValue', 0)
        cmds.setAttr(str(Paths[1])+'.uValue', 0.25)
        cmds.setAttr(str(Paths[2])+'.uValue', 0.5)
        cmds.setAttr(str(Paths[3])+'.uValue', 0.75)
        cmds.setAttr(str(Paths[4])+'.uValue', 1)

     
    cmds.undoInfo(closeChunk=True)      
'''

edgeToCv(cvs = 5, customName = 'L_Brow')
locOnCurve(amount = 5, customName = 'L_Brow')

'''

