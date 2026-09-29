'''
22/10/18
RdMSimpleFK
By Esteban Rodriguez

www.renderdemartes.com
info@renderdemartes.com

import RdMSimpleFK
reload (RdMSimpleFK)
'''


from maya import cmds

def SimpleFKFunc (scale = 1):   

    cmds.undoInfo(openChunk=True)   
    
    Joints = cmds.ls(sl = True)

    for Joint in Joints:
	    circulo = cmds.circle(n=str(Joint)+'_CC',nr = (1,0,0), r = scale)
	    grupo = cmds.group (circulo, n = str(Joint) + '_GRP')
	    
	    if 'X' in locals():
	        cmds.parent(grupo, X)
	        
	    parent01=cmds.parentConstraint (Joint, grupo,mo=False )
	    cmds.delete(parent01)
	    parent02=cmds.parentConstraint (circulo, Joint)
	    
	    if cmds.objExists (str(Joint)+'_CC'):
	        X = str(Joint)+'_CC'
	    
	    cmds.setAttr (str(circulo[0])+'.overrideEnabled', 1)
	    cmds.setAttr (str(circulo[0])+'.overrideColor', 16)


    cmds.undoInfo(closeChunk=True)   

    
print 'SimpleFK'
