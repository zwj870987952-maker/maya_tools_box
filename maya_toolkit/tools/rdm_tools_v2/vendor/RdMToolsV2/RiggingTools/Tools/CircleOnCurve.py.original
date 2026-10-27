from maya import cmds

if cmds.window ("RdMCircleOnSelection", exists = True):
    cmds.deleteUI ("RdMCircleOnSelection")



def CurveOnSelection(*args):

    Selection = cmds.ls(sl=1)


    if len (Selection) == 0:
        cmds.warning('Hey select someting pleaaaaaseeee')
        
    else:
        
        radio = cmds.floatSliderGrp (RadioControls, q = True, value = 2)
        Color = cmds.intSliderGrp (ColorControl, q = True, value = 2)
        #Grupo = cmds.textFieldGrp (NameControls, q = True)
        
        
        
        for i in Selection:
            
            
            Circle01 = cmds.circle(n = str(i+'_Control'), nr = (0,0,1), r =radio)
            GroupCircle = cmds.group (Circle01, n =str(i+'_Offset') )
            ParentTemp = cmds.parentConstraint(i, GroupCircle, mo = 0)
            cmds.delete(ParentTemp)
            cmds.parentConstraint(Circle01, i, mo = 0)
            cmds.setAttr(Circle01[0]+'.overrideEnabled', 1)
            cmds.setAttr(Circle01[0]+'.overrideColor', Color)
            cmds.select(cl=1)   
            
        
            


cmds.window( "RdMCircleOnSelection", title="RdMCircleOnSelection" )




cmds.setParent('..')
cmds.columnLayout( adjustableColumn=True )

cmds.separator (h=25) 


#NameControls = cmds.textFieldGrp (l = 'Name:', tx = 'Control')
ColorControl = cmds.intSliderGrp (l = 'Color:', min = 1 , max = 31, field = True, v = 16)

RadioControls = cmds.floatSliderGrp (l = 'Size:', min = 1 , max = 100, field = True, v = 20, hlc = (0,0.2,0.5))

cmds.separator (h=25) 

cmds.button( label='Circle Where?', command= CurveOnSelection )


cmds.text( label='By: Render de Martes' )
cmds.text( label='info@renderdemartes.com' )
cmds.showWindow("RdMCircleOnSelection")
