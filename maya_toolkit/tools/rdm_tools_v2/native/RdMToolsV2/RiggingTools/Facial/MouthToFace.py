from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
import maya.mel as mel
from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.FollicleOnPositionAlt import createFol
mouthControllers = ['upperLip_Bind_CC1', 'upperLip_Bind_CC2', 'upperLip_Bind_CC3', 'upperLip_Bind_CC4', 'upperLip_Bind_CC5', 'lowerLip_Bind_CC1', 'lowerLip_Bind_CC2', 'lowerLip_Bind_CC3', 'lowerLip_Bind_CC4', 'lowerLip_Bind_CC5', 'L_MouthCorner_CC', 'R_MouthCorner_CC', 'MouthUp_CC', 'MouthDown_CC']


def run_script():
    exec(compile("mouthControllers = ['upperLip_Bind_CC1', 'upperLip_Bind_CC2', 'upperLip_Bind_CC3', 'upperLip_Bind_CC4', 'upperLip_Bind_CC5', 'lowerLip_Bind_CC1', 'lowerLip_Bind_CC2', 'lowerLip_Bind_CC3', 'lowerLip_Bind_CC4', 'lowerLip_Bind_CC5', 'L_MouthCorner_CC', 'R_MouthCorner_CC', 'MouthUp_CC', 'MouthDown_CC']\nfor i in mouthControllers:\n    negGrp = cmds.group(em=True, n=str(i) + '_Neg')\n    cmds.xform(negGrp, m=cmds.xform(i, q=True, m=True, ws=True), ws=True)\n    cmds.parent(negGrp, str(i) + '_Root')\n    cmds.parent(str(i) + '_Auto', negGrp)\n    MultDivide = cmds.shadingNode('multiplyDivide', asUtility=True, n=i + '_MultDiv')\n    cmds.setAttr(str(MultDivide) + '.input2X', -1)\n    cmds.setAttr(str(MultDivide) + '.input2Y', -1)\n    cmds.setAttr(str(MultDivide) + '.input2Z', -1)\n    cmds.connectAttr(str(i) + '.translate', str(MultDivide) + '.input1')\n    cmds.connectAttr(str(MultDivide) + '.output', str(negGrp) + '.translate')\nupMouthFaces = cmds.ls(sl=True)\ncmds.select(cl=True)\ndwMouthFaces = cmds.ls(sl=True)\ncornerFaces = cmds.ls(sl=True)\nallFaces = upMouthFaces\ncmds.group(em=True, n='MouthPointsOnPolys')\nfor i in allFaces:\n    cmds.select(i)\n    createFol(addJoint=False, NewName=i + 'Follicle')\n    cmds.parent(i + 'Follicle', 'MouthPointsOnPolys')", __file__, "exec"), globals())
