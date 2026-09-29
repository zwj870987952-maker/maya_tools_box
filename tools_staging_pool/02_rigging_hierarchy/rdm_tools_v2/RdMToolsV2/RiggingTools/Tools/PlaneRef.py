from maya import cmds

def RefPlane():
    cmds.undoInfo(openChunk=True)   

    sel = cmds.ls(sl = True)
    refPlane = cmds.polyPlane(n = str(sel[0])+'_RefPlane', sh = 1, sw = 1)[0]
    
    cmds.move(-0.5, 0, 0, str(refPlane)+'.scalePivot', str(refPlane)+'.rotatePivot')
    cmds.manipPivot(o=(-90, 0, 90))
    
    cmds.matchTransform(refPlane, sel[0])
    edge = cmds.select(str(refPlane)+'.e[2]')
    
    Cluster = cmds.cluster(n = str(sel[1])+'_cluster')
    cmds.delete(cmds.pointConstraint(sel[1], Cluster, mo =False))    
    cmds.delete(refPlane, ch = True)

    cmds.undoInfo(closeChunk=True)   
    
'''

RefPlane()

'''