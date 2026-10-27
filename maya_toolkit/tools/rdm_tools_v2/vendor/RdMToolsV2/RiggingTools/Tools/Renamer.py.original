from maya import cmds


def RenameThis(NewName, NumCheck = True, *args):

    
    Selection = cmds.ls(sl=True)

    cmds.undoInfo(openChunk=True)    

    if (NumCheck):
	 	var = 0

 	

    for i in Selection:
        cmds.rename(i, NewName + '_' + str(var) if (NumCheck) == True else NewName)
        

        if (NumCheck):
 	    	var = var + 1

    cmds.undoInfo(closeChunk=True)    


def JointSufix(sufix = '_JJ', *args):

    
    Selection = cmds.ls(sl=True)
    
    cmds.undoInfo(openChunk=True)    

    for i in Selection:
        cmds.rename(i, str(i) + '_'+ str(sufix))
        
    cmds.undoInfo(closeChunk=True)    


def AddPrefix (side = 'L', *args):
    
    Selection = cmds.ls(sl=True)
    
    cmds.undoInfo(openChunk=True)    

    for i in Selection:
        cmds.rename(i, str(side)+'_'+str(i))

    cmds.undoInfo(closeChunk=True)    

def SearchReplace(Search = 'L_', Replace = 'R_',*args):
    
    Selection = cmds.ls(sl = True)

    cmds.undoInfo(openChunk=True)    

    for i in Selection:  
        oldName = str(i)
        newName = oldName.replace(Search, Replace)
        print newName
        cmds.rename(i, str(newName))
    
    cmds.undoInfo(closeChunk=True)    
    
    
def SearchReplaceHerarchy(Search = 'L_', Replace = 'R_',*args):

    cmds.undoInfo(openChunk=True)    
       
    import pymel.core as pm
    pm.mel.searchReplaceNames(Search, Replace, "hierarchy")
    
    cmds.undoInfo(closeChunk=True)  
    
def AddCustomPrefix (customText, *args):
    
    Selection = cmds.ls(sl=True)
    
    cmds.undoInfo(openChunk=True)    

    for i in Selection:
        cmds.rename(i, str(customText)+'_'+str(i))

    cmds.undoInfo(closeChunk=True)        
    
def AddCustomSufix (customText, *args):
    
    Selection = cmds.ls(sl=True)
    
    cmds.undoInfo(openChunk=True)    

    for i in Selection:
        cmds.rename(i,str(i)+'_'+str(customText))

    cmds.undoInfo(closeChunk=True)        