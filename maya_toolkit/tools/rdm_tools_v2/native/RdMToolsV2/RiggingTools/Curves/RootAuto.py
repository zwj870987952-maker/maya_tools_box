from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def rootAuto():
    cmds.undoInfo(openChunk=True)
    Selection = cmds.ls(sl=1)
    for i in Selection:
        if cmds.objExists(str(i) + '_Auto'):
            cmds.warning('rename it before please')
        elif cmds.objExists(str(i) + '_Root'):
            cmds.warning('rename it before please')
        else:
            Padre = cmds.listRelatives(i, p=1)
            Root = cmds.group(em=1, n=str(i) + '_Auto')
            Contraint01 = cmds.parentConstraint(i, Root, mo=0)
            cmds.delete(Contraint01)
            cmds.parent(i, Root)
            if Padre:
                cmds.parent(Root, Padre)
            Auto = cmds.group(em=1, n=str(i) + '_Root')
            Contraint01 = cmds.parentConstraint(Root, Auto, mo=0)
            cmds.delete(Contraint01)
            cmds.parent(Root, Auto)
            if Padre:
                cmds.parent(Auto, Padre)
    cmds.undoInfo(closeChunk=True)

def offsetGrp():
    cmds.undoInfo(openChunk=True)
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
            if Padre:
                cmds.parent(Root, Padre)
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
