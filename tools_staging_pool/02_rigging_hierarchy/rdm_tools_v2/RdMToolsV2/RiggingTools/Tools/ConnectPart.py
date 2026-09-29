from maya import cmds

   
cmds.undoInfo(openChunk=True)   
Color = 16


Objects = cmds.ls(sl=1)
Obj01 = Objects[0]    
Obj02 = Objects[-1]
print (Obj01, Obj02)


Curve = cmds.curve( p=[(0, 0, 0), (0, 0, 1)], d = 1 )
cmds.setAttr ('%s.overrideEnabled'%(Curve), 1)
cmds.setAttr ('%s.overrideColor'%(Curve), Color)

Cluster01 =cmds.cluster(str(Curve)+'.cv[0]')
Cluster02 =cmds.cluster(str(Curve)+'.cv[1]')

cmds.parentConstraint(Obj01, Cluster01, mo =0)
cmds.parentConstraint(Obj02, Cluster02, mo =0)

if cmds.objExists('NoXformConnected'):
    print 'Skip creating Group'
    Items = cmds.select(Curve,Cluster01,Cluster02,'NoXformConnected')
    cmds.parent()
    
else:
    cmds.group(Curve, Cluster01, Cluster02, n = 'NoXformConnected')
    cmds.setAttr('NoXformConnected.inheritsTransform', 0)
    
cmds.setAttr(str(Curve)+'.inheritsTransform')
cmds.setAttr(str(Cluster01[0])+'Handle.visibility', 0)
cmds.setAttr(str(Cluster02[0])+'Handle.visibility', 0)


cmds.undoInfo(closeChunk=True)   
       
