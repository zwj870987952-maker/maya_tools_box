from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds, mel
'\nskinClusterInfluence 1 " -dr 4 -lw true -wt 0";\nskinCluster -e  -dr 4 -lw true -wt 0 -ai joint3 skinCluster1;\n'


def run_script():
    exec(compile("selection = cmds.ls(sl=True)\nitem = selection[0]\nSkinCluster = mel.eval('findRelatedSkinCluster ' + item)\njoints = cmds.ls(sl=True, type='joint')\ncmds.skinCluster(SkinCluster, e=True, lw=True, ai=joints)", __file__, "exec"), globals())
