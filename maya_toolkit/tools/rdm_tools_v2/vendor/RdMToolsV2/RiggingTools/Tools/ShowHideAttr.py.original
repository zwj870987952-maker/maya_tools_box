from maya import cmds

def hideSelection (hideT= True, hideR = True, hideS = True, hideV = True, *args):
    
    selection = cmds.ls(sl=True)
    cmds.undoInfo(openChunk=True)

    if (hideT):
        for T in selection:
            cmds.setAttr(str(T)+'.translateX',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(T)+'.translateY',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(T)+'.translateZ',lock = True, keyable = False, channelBox = False)

    if (hideR):
        for R in selection:
            cmds.setAttr(str(R)+'.rotateX',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(R)+'.rotateY',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(R)+'.rotateZ',lock = True, keyable = False, channelBox = False)

    if (hideS):
        for S in selection:
            cmds.setAttr(str(S)+'.scaleX',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(S)+'.scaleY',lock = True, keyable = False, channelBox = False)
            cmds.setAttr(str(S)+'.scaleZ',lock = True, keyable = False, channelBox = False)
        
    if (hideV):
        for V in selection:
            cmds.setAttr(str(V)+'.visibility',lock = True, keyable = False, channelBox = False)

    cmds.undoInfo(closeChunk=True)
    


def showAll(*args):
    
    import pymel.core as pm
    
    sel=pm.ls(long=1, sl=1)

    cmds.undoInfo(openChunk=True)
    
    for eachObj in sel:
    	ud=pm.listAttr(eachObj, ud=1)
    	pm.setAttr((str(eachObj) + ".tx"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".ty"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".tz"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".rx"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".ry"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".rz"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".sx"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".sy"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".sz"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".v"), 
    		k=True)
    	pm.setAttr((str(eachObj) + ".tx"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".ty"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".tz"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".rx"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".ry"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".rz"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".sx"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".sy"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".sz"), 
    		l=False)
    	pm.setAttr((str(eachObj) + ".v"), 
    		l=False)
    	for each in ud:
    		pm.setAttr((str(eachObj) + "." + str(each)), 
    			k=True)
    		pm.setAttr((str(eachObj) + "." + str(each)), 
    			l=False)
    cmds.undoInfo(closeChunk=True)
    		