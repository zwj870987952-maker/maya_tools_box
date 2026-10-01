from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

def RdMMirrorSkin(influenceAssociation1, influenceAssociation2, surfaceAssociation, *args):
    selection = cmds.ls(sl=True)
    item = selection[0]
    SkinCluster = mel.eval('findRelatedSkinCluster ' + item)
    pm.copySkinWeights(normalize=1, ss=SkinCluster, influenceAssociation=[influenceAssociation1, influenceAssociation2], surfaceAssociation=surfaceAssociation, ds=SkinCluster, mirrorMode='YZ')


def run_script():
    exec(compile('', __file__, "exec"), globals())
