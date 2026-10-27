from maya import cmds
import maya.mel as mel


def TextToCurve(Textisimo = 'Name',font = 'Arial', *args):   

    cmds.undoInfo(openChunk=True)    

    #Im deleting one node so if theres one already in the scene i dont want to delete it
    if cmds.objExists('makeTextCurves1'):
        cmds.rename ('makeTextCurves1','makeTextCurves1LOL')
        
    #Lets Create some curves    
    Texto = '_'+ Textisimo
    Color = 16

    LetrasDobles = []
    
    Text = cmds.textCurves (n= Texto, t = Texto, o = True, f = font)    
    Lista= cmds.listRelatives (Text, ad = True)
    
    #print Lista
    Shape = Lista[1]
    #print Shape
    
    cmds.delete ('makeTextCurves1')

    for Curva in Lista:
        if cmds.objectType(str(Curva), isType='nurbsCurve'):
            #print Curva
            #Get Parents
            curvaPapa = cmds.listRelatives(Curva, p = True)
            #print 'Curva papa ' + str(curvaPapa)
            curvaAbuelo = cmds.listRelatives(curvaPapa, p = True)
            #print 'curva Abuelo '+(curvaAbuelo[0])
    
            #letters like e and o have 2 curves instead of 1
            DobleCurva = cmds.listRelatives(curvaAbuelo)
            
            if len(DobleCurva)==2:
                                
                #print 'DobleCurva ' + str(DobleCurva)
                LetrasDobles.append (Curva)
                            
            else:   
                     
                #parent to first shape
                if not Shape == curvaPapa[0]:
                    cmds.makeIdentity (curvaAbuelo, a = True, t = True , r = True)
                    cmds.parent (Curva, Shape, r = True, s = True)
                                                        
                #Colores
                cmds.setAttr (Curva+'.overrideEnabled', 1)
                cmds.setAttr (Curva+'.overrideColor', Color)
                      
    #Do stuff for the Double Letters
        #print LetrasDobles
    for dl in LetrasDobles:
        dlPapa = cmds.listRelatives (dl, p = True)
        dlAbuelo = cmds.listRelatives (dlPapa, p = True)
        cmds.makeIdentity (dlAbuelo, a = True, t = True , r = True)
        cmds.parent(dl, Shape, r = True, s = True)
        cmds.setAttr (dl+'.overrideEnabled', 1)
        cmds.setAttr (dl+'.overrideColor', Color)
                   
    #Organizing
    cmds.parent (Shape, w = True)       
    cmds.rename (Shape, Texto + str('_CV')) 
    cmds.delete(Text[0])
    cmds.delete (Texto + str('_CVShape'))
    cmds.move (-0.5,0,0, r = True)
    cmds.xform(cp= True)
    cmds.rename(Textisimo + '_CV')
    
    cmds.undoInfo(closeChunk=True)    
    
        

         
            