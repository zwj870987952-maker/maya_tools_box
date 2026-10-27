from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

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
    cmds.joint(e=True, zso=True, oj='yxz', sao='zup', ch=True)
    cmds.rename('Joint0', 'Neck_Start_JJ')
    cmds.rename('Joint1', 'Head_Start_JJ')
    cmds.rename('Joint2', 'Head_End_JE')
    cmds.undoInfo(closeChunk=True)

def ChickenHead(GlobalMultVar, *args):
    cmds.undoInfo(openChunk=True)
    GlobalMult = GlobalMultVar
    cmds.parent('Head_End_JE', w=True)
    cmds.parent('Head_Start_JJ', w=True)
    cmds.duplicate('Head_Start_JJ', n='Neck_End_JE')
    cmds.group('Neck_Start_JJ', n='Neck_GRP')
    cmds.parent('Neck_End_JE', 'Neck_Start_JJ')
    cmds.parent('Head_End_JE', 'Head_Start_JJ')
    ControlRadius = cmds.getAttr('Neck_End_JE.translateY')
    cmds.circle(n='Neck_CC', r=ControlRadius * 2 * GlobalMult, nr=(0, 1, 0))
    cmds.parentConstraint('Neck_Start_JJ', 'Neck_CC', mo=False)
    cmds.delete('Neck_CC_parentConstraint1')
    cmds.circle(n='Head_CC', r=ControlRadius * 1.5 * GlobalMult, nr=(1, 0, 0))
    cmds.parentConstraint('Head_Start_JJ', 'Head_CC', mo=False)
    cmds.delete('Head_CC_parentConstraint1')
    cmds.parent('Neck_CC', 'Neck_GRP')
    cmds.orientConstraint('Head_CC', 'Head_Start_JJ', mo=True)
    cmds.orientConstraint('Neck_CC', 'Neck_Start_JJ', mo=True)
    cmds.group('Head_CC', 'Head_Start_JJ', n='Head_GRP')
    try:
        cmds.parentConstraint('Spine_ConnectToArms', 'Neck_GRP', mo=True)
    except:
        pass
    cmds.pointConstraint('Neck_End_JE', 'Head_GRP', mo=True)
    cmds.spaceLocator(n='headspace_NECK_LOC')
    cmds.spaceLocator(n='headspace_TORSO_LOC')
    if cmds.objExists('COG'):
        cmds.parentConstraint('COG', 'headspace_TORSO_LOC', mo=False)
        cmds.delete('headspace_TORSO_LOC_parentConstraint1')
    cmds.parentConstraint('Neck_End_JE', 'headspace_NECK_LOC', mo=False)
    cmds.delete('headspace_NECK_LOC_parentConstraint1')
    cmds.makeIdentity('Head_CC', a=True, t=1, r=1)
    cmds.makeIdentity('headspace_TORSO_LOC', a=True, t=1, r=1)
    cmds.makeIdentity('headspace_NECK_LOC', a=True, t=1, r=1)
    if cmds.objExists('COG'):
        cmds.parentConstraint('COG_GRP', 'headspace_TORSO_LOC', mo=True)
    else:
        cmds.spaceLocator(n='COG_loc')
        cmds.parentConstraint('COG_loc', 'headspace_TORSO_LOC', mo=True)
    cmds.parent('headspace_NECK_LOC', 'Neck_End_JE')
    cmds.orientConstraint('headspace_NECK_LOC', 'headspace_TORSO_LOC', 'Head_GRP', mo=True)
    '\n    new Locator add s\n    switch with nodes\n    '
    switchloc = cmds.spaceLocator(n='HeadTorsoBlend')
    cmds.setAttr('HeadTorsoBlendShape.lpx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('HeadTorsoBlendShape.lpy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('HeadTorsoBlendShape.lpz', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('HeadTorsoBlendShape.lsx', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('HeadTorsoBlendShape.lsy', lock=True, channelBox=False, keyable=False)
    cmds.setAttr('HeadTorsoBlendShape.lsz', lock=True, channelBox=False, keyable=False)
    cmds.addAttr('HeadTorsoBlendShape', ln='NeckTorso', max=1, dv=0, at='double', min=0)
    cmds.setAttr('HeadTorsoBlendShape.NeckTorso', e=1, keyable=True)
    cmds.parent('HeadTorsoBlendShape', 'Neck_CC', r=True, s=True)
    cmds.parent('HeadTorsoBlendShape', 'Head_CC', add=True, s=True)
    cmds.delete('HeadTorsoBlend')
    cmds.setAttr('Neck_CC|HeadTorsoBlendShape.visibility', 0)
    PlusMinusNode = cmds.shadingNode('plusMinusAverage', asUtility=1, n='IKFKMinusHead')
    cmds.setAttr(str(PlusMinusNode) + '.operation', 2)
    cmds.setAttr(str(PlusMinusNode) + '.input2D[0].input2Dx', 1)
    cmds.setAttr(str(PlusMinusNode) + '.input2D[1].input2Dx', 0)
    cmds.connectAttr(str(switchloc[0]) + 'Shape.NeckTorso', str(PlusMinusNode) + '.input2D[1].input2Dx')
    cmds.connectAttr(str(switchloc[0]) + 'Shape.NeckTorso', 'Head_GRP_orientConstraint1.headspace_NECK_LOCW0')
    cmds.connectAttr('IKFKMinusHead.output2Dx', 'Head_GRP_orientConstraint1.headspace_TORSO_LOCW1', f=1)
    cmds.group('Neck_GRP', 'Head_GRP', 'headspace_TORSO_LOC', n='RdM ChickenHead')
    cmds.select('Head_Start_JJ', 'Neck_Start_JJ')
    cmds.sets(n='BindThisToHead')
    cmds.select('Neck_CC')
    HandItems = cmds.ls(selection=True)
    GroupName = 'OffsetGroup'
    for CC in HandItems:
        while cmds.objExists(CC + str(GroupName)):
            GroupName = str(GroupName) + str(GroupName)
        cmds.group(n=CC + str(GroupName), r=True, em=True)
        cmds.pointConstraint(CC, CC + str(GroupName))
        cmds.orientConstraint(CC, CC + str(GroupName))
        cmds.delete(CC + str(GroupName) + str('_pointConstraint1'))
        cmds.delete(CC + str(GroupName) + str('_orientConstraint1'))
        cmds.select(CC)
        Papa = cmds.listRelatives(c=True, p=True)
        cmds.parent(CC, CC + str(GroupName))
        if Papa > 1:
            cmds.parent(CC + str(GroupName), Papa)
    cmds.setAttr('Neck_CC.overrideEnabled', 1)
    cmds.setAttr('Neck_CC' + '.overrideColor', 18)
    cmds.setAttr('Head_CC.overrideEnabled', 1)
    cmds.setAttr('Head_CC' + '.overrideColor', 18)
    cmds.select('Neck_CC')
    IK = cmds.ls(sl=True)
    for T in IK:
        cmds.setAttr(str(T) + '.translateX', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.translateY', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.translateZ', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.scaleX', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.scaleY', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.scaleZ', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.visibility', lock=True, keyable=False, channelBox=False)
    cmds.select('Head_CC')
    IK = cmds.ls(sl=True)
    for T in IK:
        cmds.setAttr(str(T) + '.scaleX', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.scaleY', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.scaleZ', lock=True, keyable=False, channelBox=False)
        cmds.setAttr(str(T) + '.visibility', lock=True, keyable=False, channelBox=False)
    cmds.pointConstraint('Head_CC', 'Head_Start_JJ', mo=True)
    "\n    \n    cmds.select('Head_GRP')\n    AutoGRP = cmds.group(n = 'Head_GRP_AUTO')\n    cmds.xform(AutoGRP, cp=1)\n    \n    cmds.parentConstraint(cmds.spaceLocator(n = 'null_loc'),'Neck_GRP', AutoGRP,mo = True)\n    cmds.parent('null_loc', 'RdM_ChickenHead')\n    \n    #Neck = 1 // parentNeck = 1\n    #Neck = 0 / Null = 1\n    \n    cmds.connectAttr('HeadTorsoBlendShape.NeckTorso', 'Head_GRP_AUTO_parentConstraint1.Neck_GRPW1', f=1)\n    cmds.connectAttr('IKFKMinusHead.output2Dx', 'Head_GRP_AUTO_parentConstraint1.null_locW0', f=1)\n\n    \n    "
    cmds.undoInfo(closeChunk=True)
'\n\nLocatorsChickenHead()\nJointsChickenHead()\nChickenHead (GlobalMultVar = 3)\n\n\n\n'


def run_script():
    exec(compile('', __file__, "exec"), globals())
