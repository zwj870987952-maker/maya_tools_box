from maya import cmds

if cmds.getAttr("Head_CC.IsolateHead") == 0:
    
    #Crear locator en posicion de la cabeza
    LocatorTemp= cmds.spaceLocator(n='HeadlocTemp')
    LocatorTempParent=cmds.parentConstraint ('Head_CC', LocatorTemp,mo=0)
    cmds.delete(LocatorTempParent)
    
    #Cambiar Isolate a 1
    cmds.setAttr("Head_CC.IsolateHead",1)

    #Posicionar la cabeza
    HeadParentTemp= cmds.parentConstraint(LocatorTemp, 'Head_CC',mo=0)
    cmds.delete(HeadParentTemp,LocatorTemp)
    
else: 

    #Crear locator en posicion de la cabeza y cuello
    LocatorTempHead= cmds.spaceLocator(n='HeadlocTemp')
    LocatorTempParent=cmds.parentConstraint ('Head_CC', LocatorTempHead,mo=0)
    cmds.delete(LocatorTempParent)
    
    LocatorTempNeck= cmds.spaceLocator(n='NecklocTemp')
    LocatorTempParent=cmds.parentConstraint ('Neck_CC', LocatorTempNeck,mo=0)
    cmds.delete(LocatorTempParent)
    
    #Cambiar Isolate a 0
    cmds.setAttr("Head_CC.IsolateHead",0)   
    
    #Posicionar la cabeza
    NeckParentTemp= cmds.parentConstraint(LocatorTempNeck, 'Neck_CC',mo=0)
    cmds.delete(NeckParentTemp,LocatorTempNeck)
    HeadParentTemp= cmds.parentConstraint(LocatorTempHead, 'Head_CC',mo=0)
    cmds.delete(HeadParentTemp,LocatorTempHead)     
