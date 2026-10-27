from maya import cmds
Curve = cmds.circle (n= 'PringleCurve', r = 2,nr =(0,1,0) )
cmds.select ('PringleCurve.cv[7]','PringleCurve.cv[3]')
cmds.move (0, -2 ,0, r = True)

cmds.setAttr ('%s.overrideEnabled'%(Curve[0]), 1)
cmds.setAttr ('%s.overrideColor'%(Curve[0]), 16)

cmds.select(Curve)