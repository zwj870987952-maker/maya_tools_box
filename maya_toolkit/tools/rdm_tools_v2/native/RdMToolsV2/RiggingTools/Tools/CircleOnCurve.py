from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def CurveOnSelection(*args):
    Selection = cmds.ls(sl=1)
    if len(Selection) == 0:
        cmds.warning('Hey select someting pleaaaaaseeee')
    else:
        radio = cmds.floatSliderGrp(RadioControls, q=True, value=2)
        Color = cmds.intSliderGrp(ColorControl, q=True, value=2)
        for i in Selection:
            Circle01 = cmds.circle(n=str(i + '_Control'), nr=(0, 0, 1), r=radio)
            GroupCircle = cmds.group(Circle01, n=str(i + '_Offset'))
            ParentTemp = cmds.parentConstraint(i, GroupCircle, mo=0)
            cmds.delete(ParentTemp)
            cmds.parentConstraint(Circle01, i, mo=0)
            cmds.setAttr(Circle01[0] + '.overrideEnabled', 1)
            cmds.setAttr(Circle01[0] + '.overrideColor', Color)
            cmds.select(cl=1)


def run_script():
    exec(compile("if cmds.window('RdMCircleOnSelection', exists=True):\n    cmds.deleteUI('RdMCircleOnSelection')\ncmds.window('RdMCircleOnSelection', title='RdMCircleOnSelection')\ncmds.setParent('..')\ncmds.columnLayout(adjustableColumn=True)\ncmds.separator(h=25)\nColorControl = cmds.intSliderGrp(l='Color:', min=1, max=31, field=True, v=16)\nRadioControls = cmds.floatSliderGrp(l='Size:', min=1, max=100, field=True, v=20, hlc=(0, 0.2, 0.5))\ncmds.separator(h=25)\ncmds.button(label='Circle Where?', command=CurveOnSelection)\ncmds.text(label='By: Render de Martes')\ncmds.text(label='info@renderdemartes.com')\ncmds.showWindow('RdMCircleOnSelection')", __file__, "exec"), globals())
