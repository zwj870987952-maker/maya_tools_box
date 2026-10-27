from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def DisplaySize(value, *args):
    cmds.jointDisplayScale(value)


def run_script():
    exec(compile('', __file__, "exec"), globals())
