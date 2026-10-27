#pm.copySkinWeights(normalize=1, ss='skinCluster1', influenceAssociation=['closestJoint', 'oneToOne'], surfaceAssociation='closestComponent', ds='skinCluster1', mirrorMode='YZ')
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def RdMMirrorSkin(influenceAssociation1,influenceAssociation2,surfaceAssociation, *args):

    selection = cmds.ls(sl=True)
    item= selection[0]
    SkinCluster = mel.eval('findRelatedSkinCluster '+item)


    pm.copySkinWeights(normalize=1, ss=SkinCluster, influenceAssociation=[influenceAssociation1,influenceAssociation2], surfaceAssociation = surfaceAssociation, ds=SkinCluster, mirrorMode='YZ')
