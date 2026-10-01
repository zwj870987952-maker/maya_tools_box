from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def ChangeHead(*args):
    if cmds.getAttr('Head_CC.ChickenHead') == 0:
        LocatorTemp = cmds.spaceLocator(n='HeadlocTemp')
        LocatorTempParent = cmds.parentConstraint('Head_CC', LocatorTemp, mo=0)
        cmds.delete(LocatorTempParent)
        cmds.setAttr('Head_CC.ChickenHead', 1)
        HeadParentTemp = cmds.parentConstraint(LocatorTemp, 'Head_CC', mo=0)
        cmds.delete(HeadParentTemp, LocatorTemp)
        cmds.select('Head_CC')
    else:
        LocatorTempHead = cmds.spaceLocator(n='HeadlocTemp')
        LocatorTempParent = cmds.parentConstraint('Head_CC', LocatorTempHead, mo=0)
        cmds.delete(LocatorTempParent)
        LocatorTempNeck = cmds.spaceLocator(n='NecklocTemp')
        LocatorTempParent = cmds.parentConstraint('Neck_CC', LocatorTempNeck, mo=0)
        cmds.delete(LocatorTempParent)
        cmds.setAttr('Head_CC.ChickenHead', 0)
        NeckParentTemp = cmds.parentConstraint(LocatorTempNeck, 'Neck_CC', mo=0)
        cmds.delete(NeckParentTemp, LocatorTempNeck)
        HeadParentTemp = cmds.parentConstraint(LocatorTempHead, 'Head_CC', mo=0)
        cmds.delete(HeadParentTemp, LocatorTempHead)
        cmds.select('Head_CC')


def run_script():
    exec(compile('', __file__, "exec"), globals())
