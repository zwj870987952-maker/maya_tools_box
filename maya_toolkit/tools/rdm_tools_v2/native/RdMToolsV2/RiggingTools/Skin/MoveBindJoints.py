from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import maya.cmds as cmds
import maya.mel as mel

def moveJoints(mode=True, *args):
    selection = cmds.ls(sl=True)
    item = selection[0]
    Skin = mel.eval('findRelatedSkinCluster ' + item)
    if mode:
        cmds.skinCluster(Skin, edit=True, mjm=True)
    else:
        cmds.skinCluster(Skin, edit=True, mjm=False)


def run_script():
    exec(compile('', __file__, "exec"), globals())
