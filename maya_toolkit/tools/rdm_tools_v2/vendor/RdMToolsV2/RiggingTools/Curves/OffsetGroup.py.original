from maya import cmds

#Conseguir la seleccion para ejecutarle un loop
def offsetGrp():
    
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
        

        
