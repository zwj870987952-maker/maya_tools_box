#want name of skin cluster on  selection
import maya.cmds as cmds
import maya.mel as mel

def moveJoints(mode = True, *args):
    selection = cmds.ls(sl=True)
    item= selection[0]
    Skin = mel.eval('findRelatedSkinCluster '+item)

    if (mode):
        cmds.skinCluster(Skin, edit = True, mjm = True)
        
    else:
        cmds.skinCluster(Skin, edit = True, mjm = False)