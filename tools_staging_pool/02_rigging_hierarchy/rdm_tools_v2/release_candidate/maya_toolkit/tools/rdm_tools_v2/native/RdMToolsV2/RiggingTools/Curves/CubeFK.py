from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
CustomName = 'Cube_FK'


def run_script():
    exec(compile("selection = cmds.ls(sl=True)\nfirstJnt = selection[0]\nlastJnt = selection[-1]\nfisrtPos = cmds.xform(firstJnt, q=True, m=True, ws=True)\nlastPos = cmds.xform(lastJnt, q=True, m=True, ws=True)\nCustomName = 'Cube_FK'\ncubeCurve = cmds.curve(n=firstJnt + '_Ctrl', p=[(0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], d=1)\nleftVertex = (cubeCurve + '.cv[0:1]', cubeCurve + '.cv[4:8]', cubeCurve + '.cv[15]')\nrightVertex = (cubeCurve + '.cv[2:3]', cubeCurve + '.cv[9:14]')\ncmds.xform(rightVertex, m=fisrtPos, ws=True)\ncmds.xform(leftVertex, m=lastPos, ws=True)", __file__, "exec"), globals())
