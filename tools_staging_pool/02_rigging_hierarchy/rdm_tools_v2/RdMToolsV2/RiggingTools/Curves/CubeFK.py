from maya import cmds

selection =cmds.ls(sl = True)
firstJnt = selection [0]
lastJnt = selection [-1]
fisrtPos = cmds.xform(firstJnt, q = True, m =True,ws = True)
lastPos = cmds.xform(lastJnt, q = True, m =True,ws = True)

#Creating Cube variables
CustomName = 'Cube_FK'
cubeCurve = cmds.curve(n = firstJnt + '_Ctrl', p=[(0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], d=1)

leftVertex = (cubeCurve+'.cv[0:1]',cubeCurve+'.cv[4:8]',cubeCurve+'.cv[15]')
rightVertex = (cubeCurve+'.cv[2:3]',cubeCurve+'.cv[9:14]')

#Move the vertex to the correct position

cmds.xform(rightVertex, m = fisrtPos,ws = True)
cmds.xform(leftVertex, m = lastPos,ws = True)

