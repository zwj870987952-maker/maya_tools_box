from maya import cmds


def createFol(addJoint = True, NewName = 'FollicleName'):
    originalName = NewName
    y = 0
    for i in cmds.ls(sl = True):
        cmds.select(i)
        
        NewName = str(NewName)+ str(y)
        
        face = cmds.ls(sl = True)
        
        
        cmds.undoInfo(openChunk=True)    
        
        null = cmds.group(em=True, n = NewName)
        
        Loc = cmds.spaceLocator(n = NewName + '_LOC')
    
        cmds.parent(str(Loc[0]) + 'Shape', null, r = True, s= True)
        cmds.delete(Loc)
    
        cmds.select(face, null)
        cmds.pointOnPolyConstraint(weight=1, offset=(0, 0, 0))
       
        if addJoint == True:
            cmds.select(null)
            cmds.joint(n = str(NewName)+ '_Jnt' )   
               
        cmds.undoInfo(closeChunk=True)    
        NewName = originalName
        y = y  + 1    
  
#createFol(addJoint = False, NewName = 'Foll')

