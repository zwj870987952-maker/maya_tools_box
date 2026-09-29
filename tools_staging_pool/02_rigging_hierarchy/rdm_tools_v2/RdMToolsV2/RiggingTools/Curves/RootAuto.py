from maya import cmds

def rootAuto():
    
    cmds.undoInfo(openChunk=True)   

    #Conseguir la seleccion para ejecutarle un loop
    Selection = cmds.ls(sl=1)
    
    for i in Selection:
        if cmds.objExists(str(i) + '_Auto'):
            cmds.warning('rename it before please')
 
        elif cmds.objExists(str(i) + '_Root'):
            cmds.warning('rename it before please')
                    
        else:
            #Cual es el papa de la seleccion?
            Padre = cmds.listRelatives(i, p =1)
            #print Padre
            
            #Grupo Nullo en posicion de la selccion
            Root = cmds.group(em=1, n = str(i) + '_Auto')
            Contraint01 = cmds.parentConstraint(i, Root, mo =0)
            cmds.delete(Contraint01)
            
            #Meter Sleccion dentro del grupo y luego grupo dentro del padre
            cmds.parent(i,Root)
            if Padre:
                cmds.parent(Root, Padre)    
         
            #Crear lo mismo para el Auto
            Auto = cmds.group(em=1, n = str(i) + '_Root')
            Contraint01 = cmds.parentConstraint(Root, Auto, mo =0)
            cmds.delete(Contraint01)
            
            #Meter Sleccion dentro del grupo y luego grupo dentro del padre
            cmds.parent(Root, Auto)
            if Padre:
                cmds.parent(Auto, Padre) 

    cmds.undoInfo(closeChunk=True)   
    
def offsetGrp():
    
    cmds.undoInfo(openChunk=True)   

    
    Selection = cmds.ls(sl=1)
    
    for i in Selection:
        
        if cmds.objExists(str(i) + '_Offset_Grp'):
            
            cmds.warning('rename it before please')
        
        else:
            #Cual es el papa de la seleccion?
            Padre = cmds.listRelatives(i, p =1)
            print Padre
            
            #Grupo Nullo en posicion de la selccion
            Root = cmds.group(em=1, n = str(i) + '_Offset_Grp')
            Contraint01 = cmds.parentConstraint(i, Root, mo =0)
            cmds.delete(Contraint01)
            
            #Meter Seleccion dentro del grupo y luego grupo dentro del padre
            cmds.parent(i,Root)
        
            if Padre:
                cmds.parent(Root, Padre)    
    cmds.undoInfo(closeChunk=True)   
        
            
