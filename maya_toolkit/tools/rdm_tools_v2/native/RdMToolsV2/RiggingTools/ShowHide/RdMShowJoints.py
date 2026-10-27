from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds


def run_script():
    exec(compile("joints = cmds.ls(typ='joint')\nfor item in joints:\n    cmds.setAttr(str(item) + '.drawStyle', 0)\nprint('Show Joints')", __file__, "exec"), globals())
