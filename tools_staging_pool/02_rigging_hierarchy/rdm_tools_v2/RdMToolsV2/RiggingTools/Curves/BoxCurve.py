from maya import cmds

Curve = cmds.curve(n="BoxCurve" , d=1, p=[(1, 1, 1),(1,1,-1) ,(1, -1, -1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, 1, 1) ,(1, 1, 1) ,(1, -1, 1) ,(-1, -1, 1) ,(-1, -1, -1) ,(-1, 1, -1) ,(1, 1, -1) ,(1, -1, -1) ,(-1, -1, -1) ,(-1, 1, -1) ,(-1, 1, 1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])


cmds.setAttr ('%s.overrideEnabled'%(Curve), 1)
cmds.setAttr ('%s.overrideColor'%(Curve), 16)

