from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds


def run_script():
    exec(compile("Curve = cmds.circle(n='PringleCurve', r=2, nr=(0, 1, 0))\ncmds.select('PringleCurve.cv[7]', 'PringleCurve.cv[3]')\ncmds.move(0, -2, 0, r=True)\ncmds.setAttr('%s.overrideEnabled' % Curve[0], 1)\ncmds.setAttr('%s.overrideColor' % Curve[0], 16)\ncmds.select(Curve)", __file__, "exec"), globals())
