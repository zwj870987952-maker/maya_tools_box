'''
11/10/18
RdMBindSkin v1.0
By Esteban Rodriguez

www.renderdemartes.com
info@renderdemartes.com

import RdMBindSkin
reload (RdMBindSkin)
'''

from maya import cmds

def BindSkin (*args):
    
    cmds.undoInfo(openChunk=True)   
   

    Geo = cmds.ls (sl = True) 
    
    if len(Geo) == 0:
        cmds.warning('Select GEO before continue')
    
    else:
        print Geo[0]

        if cmds.objExists('BindThisToSpine'):
            print 'Spine'  
            cmds.select ('BindThisToSpine', tgl = True)
        
        if cmds.objExists('BindThisToArms'):
            print 'Brazos'        
            cmds.select ('BindThisToArms', tgl = True)
            
        if cmds.objExists('BindThisToLegs'):
            print 'Piernas'        
            cmds.select ('BindThisToLegs', tgl = True)

        if cmds.objExists('BindThisToHands'):
            print 'Piernas'        
            cmds.select ('BindThisToHands', tgl = True)

        if cmds.objExists('BindThisToHead'):
            print 'Head' 
            cmds.select ('BindThisToHead', tgl = True)
            
            Joints = cmds.ls (sl = True)
            cmds.skinCluster (Joints, Geo, tsb = True, bm = 0, sm = 1, nw = 1)  
            

    cmds.undoInfo(closeChunk=True)   
    
     

