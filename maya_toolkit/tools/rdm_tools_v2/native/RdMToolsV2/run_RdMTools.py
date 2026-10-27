from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import os
import sys
import maya.cmds as cmds

def RdM_Tools_Install():
    toolPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(toolPath)
    toolInfo = bundled_scripts_dir(usd=True) + 'RmdTools_Path.py'
    if os.path.isfile(toolInfo):
        os.remove(toolInfo)
    with open(toolInfo, 'w') as f:
        f.write('_RdMlocpath = "%s"' % toolPath)
    if toolPath not in sys.path:
        sys.path.append(toolPath)
    from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2 import ShowUI
    legacy_reload(ShowUI)
    RdMV2_ui = ShowUI.RdMV2UI()
    RdMV2_ui.show()


def run_script():
    exec(compile('RdM_Tools_Install()', __file__, "exec"), globals())
