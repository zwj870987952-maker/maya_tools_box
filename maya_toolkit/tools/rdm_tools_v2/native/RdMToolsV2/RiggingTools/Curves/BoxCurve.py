from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds


def run_script():
    exec(compile("Curve = cmds.curve(n='BoxCurve', d=1, p=[(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (-1, 1, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])\ncmds.setAttr('%s.overrideEnabled' % Curve, 1)\ncmds.setAttr('%s.overrideColor' % Curve, 16)", __file__, "exec"), globals())
