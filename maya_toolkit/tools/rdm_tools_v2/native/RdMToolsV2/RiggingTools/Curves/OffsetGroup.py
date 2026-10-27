from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def offsetGrp():
    Selection = cmds.ls(sl=1)
    for i in Selection:
        if cmds.objExists(str(i) + '_Offset_Grp'):
            cmds.warning('rename it before please')
        else:
            Padre = cmds.listRelatives(i, p=1)
            print(Padre)
            Root = cmds.group(em=1, n=str(i) + '_Offset_Grp')
            Contraint01 = cmds.parentConstraint(i, Root, mo=0)
            cmds.delete(Contraint01)
            cmds.parent(i, Root)


def run_script():
    exec(compile('', __file__, "exec"), globals())
