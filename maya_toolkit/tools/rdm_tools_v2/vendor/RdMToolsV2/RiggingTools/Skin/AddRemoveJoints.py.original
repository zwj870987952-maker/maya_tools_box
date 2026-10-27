from maya import cmds
'''
skinClusterInfluence 1 " -dr 4 -lw true -wt 0";
skinCluster -e  -dr 4 -lw true -wt 0 -ai joint3 skinCluster1;
'''

selection = cmds.ls(sl=True)
item= selection[0]
SkinCluster = mel.eval('findRelatedSkinCluster '+item)

joints = cmds.ls(sl = True, type='joint')

cmds.skinCluster=(e = True, lw=True, ai = joints, SkinCluster)
