def locOnVertex():

    cmds.undoInfo(openChunk=True)  
    
    selList = getSelection()
    for c in selList:
    
        cmds.select(cl=1)
        # make a joint at the position of each selected vertex
        cmds.joint(n="joint#", p=cmds.pointPosition(c), rad=.25)
    cmds.undoInfo(closeChunk=True)      
        
def getSelection():
    cmds.undoInfo(openChunk=True)  
    components = cmds.ls(sl=1)
    selList = []
    objName = components[0][0:components[0].index(".")]
    # go through every component in the list. If it is a single component ("pCube1.vtx[1]"), add it to the list. Else,
    # add each component in the index ("pCube1.vtx[1:5]") to the list
    for c in components:
        if ":" not in c:
            selList.append(c)
        else:
            print c
            startComponent = int(c[c.index("[") + 1: c.index(":")])
            endComponent = int(c[c.index(":") + 1:c.index("]")])
            componentType = c[c.index(".") + 1:c.index("[")]
            while startComponent <= endComponent:
                selList.append(objName + "." + componentType + "[" + str(startComponent) + "]")
                startComponent += 1

    return selList
    cmds.undoInfo(closeChunk=True)  
'''

locOnVertex()

'''