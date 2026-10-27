from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
import pymel.core as pm
import maya.mel as mel
from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.RdMSimpleFK import SimpleFKFunc
from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.GlobalAttr import globalControl, deleteGlobal
from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.CurveColors import colorShape

def LocatorsChickenHead(*args):
    cmds.undoInfo(openChunk=True)
    for X in range(0, 3):
        cmds.select(clear=True)
        cmds.CreateLocator()
        cmds.move(0, 2.5 * X, 0)
        cmds.select(clear=True)
    cmds.rename('locator1', 'Neck_Start_LOC')
    cmds.rename('locator2', 'Head_Start_LOC')
    cmds.rename('locator3', 'Head_End_LOC')
    if cmds.objExists('SpineEnd_JC'):
        cmds.parent('Head_End_LOC', 'Head_Start_LOC')
        cmds.parent('Head_Start_LOC', 'Neck_Start_LOC')
        cmds.pointConstraint('SpineEnd_JC', 'Neck_Start_LOC', mo=False)
        cmds.delete('Neck_Start_LOC' + '_pointConstraint1')
        cmds.parent('Head_End_LOC', w=True)
        cmds.parent('Head_Start_LOC', w=True)
        cmds.select(cl=True)
    cmds.setAttr('Neck_Start_LOC.visibility', 0)
    cmds.undoInfo(closeChunk=True)

def JointsChickenHead(*args):
    cmds.undoInfo(openChunk=True)
    cmds.select(clear=True)
    cmds.rename('Neck_Start_LOC', 'locator0')
    cmds.rename('Head_Start_LOC', 'locator1')
    cmds.rename('Head_End_LOC', 'locator2')
    for X in range(3):
        cmds.joint(n='Joint' + str(X))
        cmds.pointConstraint('locator' + str(X), 'Joint' + str(X))
        cmds.delete('Joint' + str(X) + '_pointConstraint1')
        cmds.delete('locator' + str(X))
    cmds.select('Joint0', 'Joint1', 'Joint2')
    cmds.joint(e=True, zso=True, oj='xyz', sao='zup', ch=True)
    cmds.rename('Joint0', 'Neck_Start_JJ')
    cmds.rename('Joint1', 'Head_Start_JJ')
    cmds.rename('Joint2', 'Head_End_JE')
    cmds.select(cl=True)
    cmds.undoInfo(closeChunk=True)

def ChickenHead(GlobalMultVar, Neck=1, *args):
    cmds.undoInfo(openChunk=True)
    GlobalMult = GlobalMultVar
    cmds.rename('Neck_Start_JJ', 'Neck_JJ')
    cmds.rename('Head_Start_JJ', 'Head_JJ')
    try:
        cmds.parentConstraint('Spine_JntEnd', 'Neck_JJ', mo=True)
    except:
        cmds.parentConstraint('Spine_ConnectToArms', 'Neck_JJ', mo=True)
    if Neck == 1:
        cmds.duplicate('Head_JJ', n='Neck_Mid_JJ', po=True)
        cmds.setAttr('Neck_Mid_JJ.translateX', cmds.getAttr('Neck_Mid_JJ.translateX') / 2)
        cmds.parent('Head_JJ', 'Neck_Mid_JJ')
    cmds.select('Neck_JJ', 'Neck_Mid_JJ', 'Head_JJ')
    Joints = cmds.ls(sl=True)
    for Joint in Joints:
        if Joint == 'Head_JJ':
            circulo = cmds.circle(n=str(Joint) + '_CC', nr=(0, 0, 1), r=GlobalMult * cmds.getAttr('Head_End_JE.translateX'))
        else:
            circulo = cmds.circle(n=str(Joint) + '_CC', nr=(0, 1, 0), r=GlobalMult * cmds.getAttr('Head_End_JE.translateX'))
        grupo = cmds.group(circulo, n=str(Joint) + '_GRP')
        if 'X' in locals():
            cmds.parent(grupo, X)
        parent01 = cmds.pointConstraint(Joint, grupo, mo=False)
        cmds.delete(parent01)
        parent02 = cmds.parentConstraint(circulo, Joint, mo=True)
        if cmds.objExists(str(Joint) + '_CC'):
            X = str(Joint) + '_CC'
        cmds.setAttr(str(circulo[0]) + '.overrideEnabled', 1)
        cmds.setAttr(str(circulo[0]) + '.overrideColor', 16)
    cmds.select('Neck_JJ_GRP')
    pm.mel.searchReplaceNames('_JJ', '', 'hierarchy')
    try:
        cmds.parentConstraint('Spine_JntEnd', 'Neck_GRP', mo=True)
    except:
        cmds.parentConstraint('Spine_ConnectToArms', 'Neck_GRP', mo=True)
    cmds.spaceLocator(n='ChickenHeadAttrs_loc')
    cmds.setAttr('ChickenHeadAttrs_locShape.lpx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('ChickenHeadAttrs_locShape.lpy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('ChickenHeadAttrs_locShape.lpz', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('ChickenHeadAttrs_locShape.lsx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('ChickenHeadAttrs_locShape.lsy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('ChickenHeadAttrs_locShape.lsz', lock=True, channelBox=False, keyable=False)
    globalControl(method='Left', CC='Head_CC', GlobalCC='COG_CC', AttrName='IsolateHead', AttrPosition='ChickenHeadAttrs_locShape')
    cmds.parent('ChickenHeadAttrs_locShape', 'Head_CC', r=1, s=1)
    cmds.parent('ChickenHeadAttrs_locShape', 'Neck_CC', add=1, s=1)
    cmds.parent('ChickenHeadAttrs_locShape', 'Neck_Mid_CC', add=1, s=1)
    cmds.delete('ChickenHeadAttrs_loc')
    cmds.setAttr('ChickenHeadAttrs_locShape.visibility', 0)
    cmds.setAttr('Head_CC_locIsolateHead.visibility', 0)
    cmds.group('Neck_GRP', 'Neck_JJ', n='RdM_ChickenHead')
    cmds.rotate(0, 0, 90, 'Head_CCShape.cv[0:7]')
    cmds.move(0, cmds.getAttr('Head_End_JE.translateX'), 0, 'Head_CCShape.cv[0:7]', r=True)
    cmds.setAttr('Head_CC.sx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_CC.sx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Head_CC.sy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_CC.sy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Head_CC.sz', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_CC.sz', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Head_CC.v', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_CC.v', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_Mid_CC.sx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_Mid_CC.sy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_Mid_CC.sz', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('Neck_Mid_CC.v', lock=True, channelBox=False, keyable=False)
    cmds.select('Neck_CC', 'Head_CC')
    colorShape(Color=18)
    cmds.select('Neck_JJ', 'Head_JJ')
    cmds.delete('Neck_JJ_parentConstraint1')
    cmds.parent('Neck_JJ', 'Neck_CC')
    cmds.setAttr('ChickenHeadAttrs_locShape.IsolateHead', 0)
    cmds.select('Head_JJ', 'Neck_Mid_JJ', 'Neck_JJ')
    cmds.sets(n='BindThisToHead')
    cmds.undoInfo(closeChunk=True)
'\n\nLocatorsChickenHead()\nJointsChickenHead()\nChickenHead (GlobalMultVar = 3)\n\n\n\n'


def run_script():
    exec(compile('legacy_reload(RdMToolsV2.RiggingTools.Tools.RdMSimpleFK)\nlegacy_reload(RdMToolsV2.RiggingTools.Tools.GlobalAttr)', __file__, "exec"), globals())
