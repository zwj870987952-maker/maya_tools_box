from maya import cmds

def colorShape(Color = 16, *args):
    cmds.undoInfo(openChunk=True)   
    
    selection = cmds.ls(sl=True)
    
    for i in selection:
        cmds.setAttr ('%s.overrideEnabled'%(i), 1)
        cmds.setAttr ('%s.overrideColor'%(i), Color)
    cmds.undoInfo(closeChunk=True)   
        
