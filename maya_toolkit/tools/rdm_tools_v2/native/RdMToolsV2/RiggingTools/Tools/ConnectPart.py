from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
Color = 16


def run_script():
    exec(compile("cmds.undoInfo(openChunk=True)\nColor = 16\nObjects = cmds.ls(sl=1)\nObj01 = Objects[0]\nObj02 = Objects[-1]\nprint((Obj01, Obj02))\nCurve = cmds.curve(p=[(0, 0, 0), (0, 0, 1)], d=1)\ncmds.setAttr('%s.overrideEnabled' % Curve, 1)\ncmds.setAttr('%s.overrideColor' % Curve, Color)\nCluster01 = cmds.cluster(str(Curve) + '.cv[0]')\nCluster02 = cmds.cluster(str(Curve) + '.cv[1]')\ncmds.parentConstraint(Obj01, Cluster01, mo=0)\ncmds.parentConstraint(Obj02, Cluster02, mo=0)\nif cmds.objExists('NoXformConnected'):\n    print('Skip creating Group')\n    Items = cmds.select(Curve, Cluster01, Cluster02, 'NoXformConnected')\n    cmds.parent()\nelse:\n    cmds.group(Curve, Cluster01, Cluster02, n='NoXformConnected')\n    cmds.setAttr('NoXformConnected.inheritsTransform', 0)\ncmds.setAttr(str(Curve) + '.inheritsTransform')\ncmds.setAttr(str(Cluster01[0]) + 'Handle.visibility', 0)\ncmds.setAttr(str(Cluster02[0]) + 'Handle.visibility', 0)\ncmds.undoInfo(closeChunk=True)", __file__, "exec"), globals())
