from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def setAxisDisplay(display=False):
    cmds.undoInfo(openChunk=True)
    'if no joints are selected, do it for all the joints in the scene'
    if len(cmds.ls(sl=1, type='joint')) == 0:
        jointList = cmds.ls(type='joint')
    else:
        jointList = cmds.ls(sl=1, type='joint')
    ' set the displayLocalAxis attribute to what the user specifies'
    for jnt in jointList:
        cmds.setAttr(jnt + '.displayLocalAxis', display)
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
