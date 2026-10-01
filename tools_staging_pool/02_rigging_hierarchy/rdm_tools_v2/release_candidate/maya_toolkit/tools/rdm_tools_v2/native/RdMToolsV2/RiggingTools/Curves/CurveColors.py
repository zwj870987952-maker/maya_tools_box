from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def colorShape(Color=16, *args):
    cmds.undoInfo(openChunk=True)
    selection = cmds.ls(sl=True)
    for i in selection:
        cmds.setAttr('%s.overrideEnabled' % i, 1)
        cmds.setAttr('%s.overrideColor' % i, Color)
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
