from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import maya.cmds as cmds


def run_script():
    exec(compile('sel = cmds.ls(sl=True)\njnts = cmds.skinCluster(sel, inf=True, q=True)\ncmds.select(jnts)\nprint(jnts)', __file__, "exec"), globals())
