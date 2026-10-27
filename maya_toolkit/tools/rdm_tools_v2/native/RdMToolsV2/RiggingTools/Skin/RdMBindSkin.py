from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def rdmBindSkin(final=False, *args):
    cmds.undoInfo(openChunk=True)
    selection = cmds.ls(sl=1)
    geo = selection[-1]
    if final == False:
        cmds.skinCluster(selection, tsb=True, sm=1, bm=0)
    else:
        customSkin = cmds.skinCluster(selection, tsb=True, sm=1, bm=3)
        cmds.geomBind(customSkin, gvp=(256, True))
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
