from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
import maya.mel as mel
import pymel.core as pm
jointsNum = 4

def LocatorsBtn(*args):
    cmds.undoInfo(openChunk=True)
    for X in range(jointsNum):
        cmds.select(clear=True)
        cmds.CreateLocator()
        cmds.move(2, 2.5 * X, 0)
        cmds.select(clear=True)
    cmds.rename('locator4', 'L_Leg_LOC')
    cmds.rename('locator3', 'L_Knee_LOC')
    cmds.rename('locator2', 'L_Ankle_LOC')
    cmds.rename('locator1', 'L_Heel_LOC')
    cmds.duplicate('L_Heel_LOC', n='L_EndFoot_LOC')
    cmds.duplicate('L_Heel_LOC', n='L_Ball_Loc')
    cmds.move(2, 0, 3, 'L_Ball_Loc')
    cmds.move(2, 0, 5, 'L_EndFoot_LOC')
    cmds.move(0, 0, 0.5, 'L_Knee_LOC', r=True)
    cmds.duplicate('L_Ball_Loc', n='L_InFoot_Loc')
    cmds.duplicate('L_Ball_Loc', n='L_OutFoot_Loc')
    cmds.move(-1, 0, 0, 'L_InFoot_Loc', r=True)
    cmds.move(1, 0, 0, 'L_OutFoot_Loc', r=True)
    cmds.select(clear=True)
    cmds.undoInfo(closeChunk=True)

def JointsBtn(*args):
    cmds.undoInfo(openChunk=True)
    try:
        cmds.rename('transform1', 'L_Transform1')
    except:
        pass
    try:
        cmds.rename('transform2', 'L_Transform2')
    except:
        pass
    cmds.select(clear=True)
    cmds.rename('L_Leg_LOC', 'locator1')
    cmds.rename('L_Knee_LOC', 'locator2')
    cmds.rename('L_Ankle_LOC', 'locator3')
    cmds.rename('L_Ball_Loc', 'locator4')
    cmds.rename('L_EndFoot_LOC', 'locator5')
    cmds.rename('L_Heel_LOC', 'locator6')
    cmds.select(cl=True)
    for X in range(1, jointsNum + 2):
        cmds.joint(n='L_leg_' + str(X))
        cmds.select('L_leg_' + str(X))
        cmds.pointConstraint('locator' + str(X), 'L_leg_' + str(X))
        cmds.delete('L_leg_' + str(X) + '_pointConstraint1')
    cmds.select(clear=True)
    for X in range(6, 2, -1):
        cmds.joint(n='Reverse_Foot_' + str(X))
        cmds.pointConstraint('locator' + str(X), 'Reverse_Foot_' + str(X))
        cmds.delete('Reverse_Foot_' + str(X) + '_pointConstraint1')
        cmds.delete('locator' + str(X))
    cmds.delete('locator1', 'locator2')
    cmds.rename('Reverse_Foot_6', 'L_RF_Heel')
    cmds.rename('Reverse_Foot_5', 'L_RF_Fingers')
    cmds.rename('Reverse_Foot_4', 'L_RF_Ball')
    cmds.rename('Reverse_Foot_3', 'L_RF_Ankle')
    cmds.rename('L_leg_1', 'L_Leg_JJ')
    cmds.rename('L_leg_2', 'L_Knee_JJ')
    cmds.rename('L_leg_3', 'L_Ankle_JJ')
    cmds.rename('L_leg_4', 'L_Ball_JJ')
    cmds.rename('L_leg_5', 'L_Fingers_JJ')
    cmds.select('L_Leg_JJ', 'L_Knee_JJ', 'L_Ankle_JJ', 'L_Ball_JJ', 'L_Fingers_JJ', 'L_RF_Ball')
    cmds.joint(e=True, zso=True, oj='xyz', sao='zdown')
    cmds.select(cl=True)
    In = cmds.joint(n='L_RF_InFoot')
    cmds.select(cl=True)
    Out = cmds.joint(n='L_RF_OutFoot')
    cmds.xform(In, m=cmds.xform('L_InFoot_Loc', q=True, m=True))
    cmds.xform(Out, m=cmds.xform('L_OutFoot_Loc', q=True, m=True))
    cmds.delete('L_InFoot_Loc', 'L_OutFoot_Loc')
    cmds.select('L_RF_Heel', 'L_RF_Fingers', 'L_RF_Ankle', 'L_RF_InFoot', 'L_RF_OutFoot')
    cmds.parent('L_RF_InFoot', 'L_RF_OutFoot')
    cmds.parent('L_RF_Heel', 'L_RF_InFoot')
    cmds.select(clear=True)
    cmds.undoInfo(closeChunk=True)

def IKFKLegs(LegsSize, Twist=False, Ribbon=False, *args):
    cmds.undoInfo(openChunk=True)
    cmds.select(clear=True)
    try:
        cmds.rename('transform1', 'L_Transform1')
    except:
        pass
    try:
        cmds.rename('transform2', 'L_Transform2')
    except:
        pass
    from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.AutoIKFK import RdM_IKFK
    legacy_reload(RdMToolsV2.RiggingTools.Tools.AutoIKFK)
    cmds.duplicate('L_Leg_JJ', n='R_Leg_JJ')
    cmds.duplicate('L_RF_OutFoot', n='R_RF_OutFoot')
    cmds.select('R_Leg_JJ')
    pm.mel.searchReplaceNames('L_', 'R_', 'hierarchy')
    cmds.select('R_RF_OutFoot')
    pm.mel.searchReplaceNames('L_', 'R_', 'hierarchy')
    cmds.parent('L_Ball_JJ', w=True)
    cmds.setAttr('L_Ankle_JJ.jointOrientZ', 0)
    cmds.parent('R_Ball_JJ', w=True)
    cmds.setAttr('R_Ankle_JJ.jointOrientZ', 0)
    cmds.select('L_Leg_JJ', 'L_Knee_JJ', 'L_Ankle_JJ')
    RdM_IKFK(CustomName='L_Leg', size=LegsSize, Color=6, pvMethod='v')
    cmds.select(cl=True)
    cmds.select('R_Leg_JJ', 'R_Knee_JJ', 'R_Ankle_JJ')
    RdM_IKFK(CustomName='R_Leg', size=LegsSize, Color=13, pvMethod='v')
    cmds.select(cl=True)
    cmds.parent('L_Ball_JJ', 'L_Ankle_JJ')
    cmds.parent('R_Ball_JJ', 'R_Ankle_JJ')

    def IkSquareOrient(side='L'):
        cmds.parent('%s_Ankle_JJ_IKIKrp' % side, '%s_Ankle_JJ_IK_Stretchy02' % side, '%s_Ankle_JJ_IK_CC' % side, w=True)
        cmds.setAttr('%s_Ankle_JJ_IK_CC.rotateX' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC.rotateY' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC.rotateZ' % side, 0)
        cmds.parent('%s_Ankle_JJ_IK_CC' % side, '%s_Ankle_JJ_IK_CC_GRP' % side)
        cmds.parent('%s_Ankle_JJ_IKIKrp' % side, '%s_Ankle_JJ_IK_Stretchy02' % side, '%s_Ankle_JJ_IK_CC' % side)
        cmds.group(em=True, n='%s_Ankle_JJ_IK_CC_Root' % side)
        cmds.parent('%s_Ankle_JJ_IK_CC_Root' % side, '%s_Ankle_JJ_IK_CC' % side)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.rotateX' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.rotateY' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.rotateZ' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.translateX' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.translateY' % side, 0)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.translateZ' % side, 0)
        cmds.parent('%s_Ankle_JJ_IK_CC_Root' % side, '%s_Ankle_JJ_IK_CC_GRP' % side)
        cmds.parent('%s_Ankle_JJ_IK_CC' % side, '%s_Ankle_JJ_IK_CC_Root' % side)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.scaleX' % side, 1)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.scaleY' % side, 1)
        cmds.setAttr('%s_Ankle_JJ_IK_CC_Root.scaleZ' % side, 1)
    IkSquareOrient(side='L')
    IkSquareOrient(side='R')
    LeftGroup = cmds.group('L_Leg_JJ', 'L_RF_OutFoot', 'L_Leg_JJ_IK_GRP', ' L_Leg_JJ_FK_GRP', n='L_Leg_GRP')
    RightGroup = cmds.group('R_Leg_JJ', 'R_RF_OutFoot', 'R_Leg_JJ_IK_GRP', ' R_Leg_JJ_FK_GRP', n='R_Leg_GRP')
    cmds.rename('NoXformConnected', 'NoXformConnectedLegs')
    cmds.group('L_Leg_GRP', 'R_Leg_GRP', 'NoXformConnectedLegs', n='RdM_AutoLEGS')
    cmds.parent('L_RF_OutFoot', 'L_Ankle_JJ_IK_CC')
    cmds.parent('L_Ankle_JJ_IKIKrp', 'L_RF_Ankle')
    cmds.parent('R_RF_OutFoot', 'R_Ankle_JJ_IK_CC')
    cmds.parent('R_Ankle_JJ_IKIKrp', 'R_RF_Ankle')

    def RFL(side, Color):
        print(side + '_RFL')
        cmds.duplicate(side + '_Ball_JJ', n=side + '_Ball_JJ_IK', rc=True)
        cmds.duplicate(side + '_Ball_JJ', n=side + '_Ball_JJ_FK', rc=True)
        cmds.rename(side + '_Fingers_JJ1', side + '_Fingers_IK')
        cmds.rename(side + '_Fingers_JJ2', side + '_Fingers_FK')
        cmds.parent(side + '_Ball_JJ_IK', side + '_Ankle_JJ_IK')
        cmds.parent(side + '_Ball_JJ_FK', side + '_Ankle_JJ_FK')
        cmds.parentConstraint(side + '_Ball_JJ_IK', side + '_Ball_JJ_FK', side + '_Ball_JJ', mo=True)
        cmds.parentConstraint(side + '_Fingers_IK', side + '_Fingers_FK', side + '_Fingers_JJ', mo=True)
        cmds.connectAttr('IKFKMinus1' + str(side) + '_Leg_JJ.output2D.output2Dx', str(side) + '_Ball_JJ_parentConstraint1.' + str(side) + '_Ball_JJ_FKW1')
        cmds.connectAttr('IKFKMinus1' + str(side) + '_Leg_JJ.output2D.output2Dx', str(side) + '_Fingers_JJ_parentConstraint1.' + str(side) + '_Fingers_FKW1')
        cmds.connectAttr(str(side) + '_Leg_FKIK_BlendShape.Blend_IKFK', str(side) + '_Ball_JJ_parentConstraint1.' + str(side) + '_Ball_JJ_IKW0')
        cmds.connectAttr(str(side) + '_Leg_FKIK_BlendShape.Blend_IKFK', str(side) + '_Fingers_JJ_parentConstraint1.' + str(side) + '_Fingers_IKW0')
        IkHandleAnkle = cmds.ikHandle(n=str(side) + '_Ankle_IKsc', sj=side + '_Ankle_JJ_IK', ee=side + '_Ball_JJ_IK', sol='ikSCsolver')
        IkHandleBall = cmds.ikHandle(n=str(side) + '_Ball_IKsc', sj=side + '_Ball_JJ_IK', ee=side + '_Fingers_IK', sol='ikSCsolver')
        cmds.parent(IkHandleAnkle[0], side + '_RF_Ball')
        cmds.parent(IkHandleBall[0], side + '_RF_Fingers')
        rflJoints = [str(side) + '_RF_OutFoot', str(side) + '_RF_InFoot', str(side) + '_RF_Heel', str(side) + '_RF_Fingers', str(side) + '_RF_Ball']
        for i in rflJoints:
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
            Circle = cmds.circle(n=str(i) + '_CC', r=LegsSize / 2)
            cmds.parent(str(Circle[0]) + 'Shape', i, s=True, r=True)
            cmds.delete(Circle[0])
            cmds.parent(str(side) + '_Ankle_JJ_IK_CC|' + str(side) + '_Leg_FKIK_BlendShape', i, add=1, s=1)
        cmds.select(str(side) + '_RF_Ball')
        Padre = cmds.listRelatives(i, p=1)
        Root = cmds.group(em=1, n=str(i) + '_Auto2')
        Contraint01 = cmds.parentConstraint(i, Root, mo=0)
        cmds.delete(Contraint01)
        cmds.parent(i, Root)
        if Padre:
            cmds.parent(Root, Padre)
        Circle = cmds.circle(n=str(side) + '_RF_Ball_CC2', r=LegsSize / 2, nr=(1, 0.7, 0))
        cmds.parent(str(Circle[0]) + 'Shape', str(Root), s=True, r=True)
        cmds.delete(Circle[0])
        cmds.parent(str(side) + '_Ball_IKsc', str(side) + '_RF_Ball_Auto2')
        cmds.parent(str(side) + '_RF_Ball', str(side) + '_RF_Ball_Auto')
        cmds.parent(str(side) + '_RF_Ball_Auto2', str(side) + '_RF_Ball_Root')
        GroupRoot = cmds.group(n=str(side) + '_RF_Ball_Auto_2', em=True)
        cmds.delete(cmds.pointConstraint(str(side) + '_RF_Ball_Root', GroupRoot))
        GroupAuto = cmds.group(n=str(side) + '_RF_Ball_Root_2')
        cmds.delete(cmds.pointConstraint(str(side) + '_RF_Ball', GroupAuto))
        cmds.parent(GroupAuto, str(side) + '_RF_Ball_Root')
        cmds.parent(str(side) + '_RF_Ball_Auto2', GroupRoot)
        cmds.rename(str(side) + '_RF_Ball_Auto2', str(side) + '_RF_Ball2')
        GRP = cmds.group(n=str(side) + '_RF_Ball_Zero', em=True)
        cmds.parent(GRP, str(side) + '_RF_Ball2')
        cmds.setAttr(str(GRP) + '.rotateX', 0)
        cmds.setAttr(str(GRP) + '.rotateY', 0)
        cmds.setAttr(str(GRP) + '.rotateZ', 0)
        cmds.setAttr(str(GRP) + '.translateX', 0)
        cmds.setAttr(str(GRP) + '.translateY', 0)
        cmds.setAttr(str(GRP) + '.translateZ', 0)
        cmds.parent(str(side) + '_Ball_IKsc', str(side) + '_RF_Ball_Auto_2')
        cmds.parent(GRP, str(side) + '_RF_Ball_Auto_2')
        cmds.parent(str(side) + '_RF_Ball2', GRP)
        cmds.parent(str(side) + '_Ball_IKsc', str(side) + '_RF_Ball2')
        Null = cmds.addAttr(str(side) + '_Ankle_JJ_IK_CC', ln='__________', at='enum', en=':.:')
        cmds.setAttr(str(side) + '_Ankle_JJ_IK_CC.__________', e=1, keyable=1)
        cmds.setAttr(str(side) + '_Ankle_JJ_IK_CC.__________', e=1, lock=True)
        LockThisAttrIK = ['sx', 'sy', 'sz', 'v', 'radi', 'tx', 'ty', 'tz']
        rflJoints.append(str(side) + '_RF_Ball2')
        controllers = rflJoints
        for L in LockThisAttrIK:
            for i in controllers:
                try:
                    cmds.setAttr(str(i) + '.' + str(L), lock=True, keyable=False, channelBox=False)
                except:
                    pass
        cmds.addAttr(str(side) + '_Ankle_JJ_IK_CC', ln='FootControllers', at='enum', en='Hiden:Show:')
        cmds.setAttr(str(side) + '_Ankle_JJ_IK_CC.FootControllers', e=True, channelBox=True)
        cmds.connectAttr(str(side) + '_Ankle_JJ_IK_CC.FootControllers', str(side) + '_RF_OutFoot_Auto.visibility')
        cmds.setAttr(str(side) + '_Ankle_JJ_IK_CC.FootControllers', 1)
        rflAttrs = ['RollFingers', 'PivotFingers', 'UpDownFingers', 'PivotBall', 'RollBall', 'PivotHeel', 'RollHeel', 'TiltOut', 'TiltIn']
        for i in rflAttrs:
            cmds.addAttr(str(side) + '_Ankle_JJ_IK_CC', ln=i, at='double', dv=0, keyable=1)
            cmds.setAttr(str(side) + '_Ankle_JJ_IK_CC.' + str(i), e=True, keyable=1)

        def connectWithRFL(attr1, attr2, axis):
            cmds.connectAttr(str(side) + '_Ankle_JJ_IK_CC.' + str(attr2), str(side) + '_RF_' + str(attr1) + '_Auto.rotate' + str(axis))
        connectWithRFL('InFoot', 'TiltIn', 'Z')
        connectWithRFL('OutFoot', 'TiltOut', 'Z')
        connectWithRFL('Heel', 'RollHeel', 'X')
        connectWithRFL('Heel', 'PivotHeel', 'Y')
        connectWithRFL('Ball', 'RollBall', 'Z')
        connectWithRFL('Ball', 'PivotBall', 'Y')
        connectWithRFL('Fingers', 'PivotFingers', 'Y')
        connectWithRFL('Fingers', 'RollFingers', 'X')
        cmds.connectAttr(str(side) + '_Ankle_JJ_IK_CC.UpDownFingers', str(side) + '_RF_Ball_Auto_2.rotateX')
        BallFK = cmds.circle(n=str(side) + '_Ball_JJ_FK_CC', nr=(1, 0, 0), r=LegsSize)
        GroupFK = cmds.group(n=str(side) + '_Ball_JJ_FK_GRP')
        ParentFK = cmds.parentConstraint(str(side) + '_Ball_JJ_FK', GroupFK, mo=False)
        cmds.delete(ParentFK)
        cmds.parent(GroupFK, str(side) + '_Ankle_JJ_FK_CC')
        cmds.parentConstraint(BallFK, str(side) + '_Ball_JJ_FK')
        LockThisAttrIK = ['sx', 'sy', 'sz', 'v']
        controllers = BallFK
        for L in LockThisAttrIK:
            cmds.setAttr(str(side) + '_Ball_JJ_FK_CC.' + str(L), lock=True, keyable=False, channelBox=False)
        cmds.parent(str(side) + '_Ankle_JJ_IK_CC|' + str(side) + '_Leg_FKIK_BlendShape', BallFK[0], add=1, s=1)
    RFL(side='L', Color=6)
    RFL(side='R', Color=13)
    from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.FootRollLegs import footRoll
    legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.FootRollLegs)
    footRoll()
    cmds.xform(RightGroup, rp=(0, 0, 0), sp=(0, 0, 0))
    cmds.setAttr(str(RightGroup) + '.rotateX', 180)
    cmds.setAttr(str(RightGroup) + '.scaleX', -1)
    cmds.setAttr(str(RightGroup) + '.scaleY', -1)
    cmds.setAttr(str(RightGroup) + '.scaleZ', -1)
    if Twist or Ribbon == True:
        print('TwistMethod ON')
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.AutoTwist import AutoTwistFunc
        legacy_reload(RdMToolsV2.RiggingTools.Tools.AutoTwist)
        cmds.select('L_Leg_JJ', 'L_Knee_JJ')
        AutoTwistFunc(Axis='X', SwitchVar=0)
        cmds.select('L_Knee_JJ', 'L_Ankle_JJ')
        AutoTwistFunc(Axis='X', SwitchVar=1)
        cmds.select('R_Leg_JJ', 'R_Knee_JJ')
        AutoTwistFunc(Axis='X', SwitchVar=0)
        cmds.select('R_Knee_JJ', 'R_Ankle_JJ')
        AutoTwistFunc(Axis='X', SwitchVar=1)
        FirstConnectionL = 'L_Knee_JJ'
        SecondConnectionL = 'L_Ankle_JJ'
        FirstConnectionR = 'R_Knee_JJ'
        SecondConnectionR = 'R_Ankle_JJ'
        LTwist1 = ['L_Leg_JJ_Twist_1', 'L_Leg_JJ_Twist_2', 'L_Leg_JJ_Twist_3']
        LTwist2 = ['L_Knee_JJ_Twist_1', 'L_Knee_JJ_Twist_2', 'L_Knee_JJ_Twist_3']
        RTwist1 = ['R_Leg_JJ_Twist_1', 'R_Leg_JJ_Twist_2', 'R_Leg_JJ_Twist_3']
        RTwist2 = ['R_Knee_JJ_Twist_1', 'R_Knee_JJ_Twist_2', 'R_Knee_JJ_Twist_3']
        MultDivide1 = cmds.shadingNode('multiplyDivide', asUtility=True)
        cmds.setAttr(str(MultDivide1) + '.operation', 2)
        cmds.setAttr(str(MultDivide1) + '.input2X', 3)
        cmds.setAttr(str(MultDivide1) + '.input2Y', 3)
        MultDivide2 = cmds.shadingNode('multiplyDivide', asUtility=True)
        cmds.setAttr(str(MultDivide2) + '.operation', 2)
        cmds.setAttr(str(MultDivide2) + '.input2X', 3)
        cmds.setAttr(str(MultDivide2) + '.input2Y', 3)
        cmds.connectAttr(FirstConnectionL + '.translateX.', str(MultDivide1) + '.input1X')
        cmds.connectAttr(SecondConnectionL + '.translateX.', str(MultDivide2) + '.input1X')
        cmds.connectAttr(FirstConnectionR + '.translateX.', str(MultDivide1) + '.input1Y')
        cmds.connectAttr(SecondConnectionR + '.translateX.', str(MultDivide2) + '.input1Y')
        for i in LTwist1:
            cmds.connectAttr(str(MultDivide1) + '.output.outputX', str(i) + '.translateX')
        for i in LTwist2:
            cmds.connectAttr(str(MultDivide2) + '.output.outputX', str(i) + '.translateX')
        for i in RTwist1:
            cmds.connectAttr(str(MultDivide1) + '.output.outputY', str(i) + '.translateX')
        for i in RTwist2:
            cmds.connectAttr(str(MultDivide2) + '.output.outputY', str(i) + '.translateX')
        cmds.pointConstraint('L_Leg_JJ', 'L_Leg_JJ_Twist_0', mo=True)
        cmds.pointConstraint('L_Knee_JJ', 'L_Knee_JJ_Twist_0', mo=True)
        cmds.pointConstraint('R_Leg_JJ', 'R_Leg_JJ_Twist_0', mo=True)
        cmds.pointConstraint('R_Knee_JJ', 'R_Knee_JJ_Twist_0', mo=True)
        cmds.select('L_Leg_JJ_Twist_0', 'L_Leg_JJ_Twist_1', 'L_Leg_JJ_Twist_2', 'L_Ankle_JJ', 'L_Knee_JJ_Twist_0', 'L_Knee_JJ_Twist_1', 'L_Knee_JJ_Twist_2', 'L_Ball_JJ')
        cmds.sets(n='BindThisTo_Twist_L_Leg')
        cmds.select('R_Leg_JJ_Twist_0', 'R_Leg_JJ_Twist_1', 'R_Leg_JJ_Twist_2', 'R_Ankle_JJ', 'R_Knee_JJ_Twist_0', 'R_Knee_JJ_Twist_1', 'R_Knee_JJ_Twist_2', 'R_Ball_JJ')
        cmds.sets(n='BindThisTo_Twist_R_Leg')
    if Ribbon == True:
        cmds.delete('BindThisTo_Twist_L_Leg', 'BindThisTo_Twist_R_Leg')
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.BendyRibbons import ribbonLimb
        legacy_reload(RdMToolsV2.RiggingTools.Tools.BendyRibbons)
        cmds.select('L_Leg_JJ', 'L_Knee_JJ', 'L_Ankle_JJ')
        ribbonLimb(customName='L_Leg', size=LegsSize)
        cmds.select('R_Leg_JJ', 'R_Knee_JJ', 'R_Ankle_JJ')
        ribbonLimb(customName='R_Leg', size=LegsSize)
        cmds.parentConstraint('L_Leg_JJ_Twist_0', 'L_LegRibbon_JC_1_GRP', mo=False)
        cmds.parentConstraint('L_Leg_JJ_Twist_1', 'L_LegRibbon_JC_2_GRP', mo=False)
        cmds.parentConstraint('L_Leg_JJ_Twist_2', 'L_LegRibbon_JC_3_GRP', mo=False)
        cmds.parentConstraint('L_Knee_JJ_Twist_0', 'L_LegRibbon_JC_4_GRP', mo=False)
        cmds.parentConstraint('L_Knee_JJ_Twist_1', 'L_LegRibbon_JC_5_GRP', mo=False)
        cmds.parentConstraint('L_Knee_JJ_Twist_2', 'L_LegRibbon_JC_6_GRP', mo=False)
        cmds.parentConstraint('L_Knee_JJ_Twist_3', 'L_LegRibbon_JC_7_GRP', mo=False)
        cmds.parentConstraint('R_Leg_JJ_Twist_0', 'R_LegRibbon_JC_1_GRP', mo=False)
        cmds.parentConstraint('R_Leg_JJ_Twist_1', 'R_LegRibbon_JC_2_GRP', mo=False)
        cmds.parentConstraint('R_Leg_JJ_Twist_2', 'R_LegRibbon_JC_3_GRP', mo=False)
        cmds.parentConstraint('R_Knee_JJ_Twist_0', 'R_LegRibbon_JC_4_GRP', mo=False)
        cmds.parentConstraint('R_Knee_JJ_Twist_1', 'R_LegRibbon_JC_5_GRP', mo=False)
        cmds.parentConstraint('R_Knee_JJ_Twist_2', 'R_LegRibbon_JC_6_GRP', mo=False)
        cmds.parentConstraint('R_Knee_JJ_Twist_3', 'R_LegRibbon_JC_7_GRP', mo=False)
        cmds.parent('L_Leg_RibbonGRP', 'R_Leg_RibbonGRP', 'RdM_AutoLEGS')
        cmds.sets('L_Ankle_JJ', edit=1, forceElement='BindThisTo_L_Leg_Ribbon')
        cmds.sets('R_Ankle_JJ', edit=1, forceElement='BindThisTo_R_Leg_Ribbon')
        pm.addAttr('|RdM_AutoLEGS|L_Leg_GRP|L_Leg_JJ_IK_GRP|L_Knee_JJ_IK_PV_GRP|L_Knee_JJ_IK_PV|L_Leg_FKIK_BlendShape', ln='ShowBendyControllers', en='Hide:Show:', at='enum')
        pm.setAttr('|RdM_AutoLEGS|L_Leg_GRP|L_Leg_JJ_IK_GRP|L_Knee_JJ_IK_PV_GRP|L_Knee_JJ_IK_PV|L_Leg_FKIK_BlendShape.ShowBendyControllers', e=1, channelBox=True)
        pm.addAttr('|RdM_AutoLEGS|R_Leg_GRP|R_Leg_JJ_IK_GRP|R_Knee_JJ_IK_PV_GRP|R_Knee_JJ_IK_PV|R_Leg_FKIK_BlendShape', ln='ShowBendyControllers', en='Hide:Show:', at='enum')
        pm.setAttr('|RdM_AutoLEGS|R_Leg_GRP|R_Leg_JJ_IK_GRP|R_Knee_JJ_IK_PV_GRP|R_Knee_JJ_IK_PV|R_Leg_FKIK_BlendShape.ShowBendyControllers', e=1, channelBox=True)
        pm.connectAttr('L_Knee_JJ_IK_PV|L_Leg_FKIK_BlendShape.ShowBendyControllers', 'L_LegRibbon_JC_GPR.visibility', f=1)
        pm.connectAttr('R_Knee_JJ_IK_PV|R_Leg_FKIK_BlendShape.ShowBendyControllers', 'R_LegRibbon_JC_GPR.visibility', f=1)
    else:
        pass
    oldNames = ['L_Ankle_JJ_IK_CC', 'R_Ankle_JJ_IK_CC', 'L_Knee_JJ_IK_PV', 'R_Knee_JJ_IK_PV', 'R_Leg_JJ_FK_CC', 'R_Knee_JJ_FK_CC', 'R_Ankle_JJ_FK_CC', 'R_Ball_JJ_FK_CC', 'L_Leg_JJ_FK_CC', 'L_Knee_JJ_FK_CC', 'L_Ankle_JJ_FK_CC', 'L_Ball_JJ_FK_CC']
    newNames = ['L_Leg_IK_CC', 'R_Leg_IK_CC', 'L_Knee_PV', 'R_Knee_PV', 'R_Leg_FK_CC', 'R_Knee_FK_CC', 'R_Ankle_FK_CC', 'R_Ball_FK_CC', 'L_Leg_FK_CC', 'L_Knee_FK_CC', 'L_Ankle_FK_CC', 'L_Ball_FK_CC']
    for i in range(0, 12):
        cmds.rename(oldNames[i], newNames[i])
    cmds.select(cl=True)
    LBlend = cmds.joint(n='L_BlendIK')
    RBlend = cmds.joint(n='R_BlendIK')
    cmds.delete(cmds.parentConstraint('L_Leg_IK_CC', LBlend, mo=False))
    cmds.delete(cmds.parentConstraint('R_Leg_IK_CC', RBlend, mo=False))
    cmds.parent(LBlend, 'L_Ankle_FK_CC')
    cmds.parent(RBlend, 'R_Ankle_FK_CC')
    LBlendRoll = cmds.joint(n='L_BlendIKRoll')
    RBlendRoll = cmds.joint(n='R_BlendIKRoll')
    cmds.delete(cmds.parentConstraint('L_RF_Ball2', LBlendRoll, mo=False))
    cmds.delete(cmds.parentConstraint('R_RF_Ball2', RBlendRoll, mo=False))
    cmds.parent(LBlendRoll, 'L_Ball_FK_CC')
    cmds.parent(RBlendRoll, 'R_Ball_FK_CC')
    '\n    Grupo sobre IKsc\n    Aim Constraint del control nuevo al joint\n    Switch del aim Constraint IK en , FK En 1\n    '
    NewFkGrpL = cmds.group('L_Leg_JJTwistIKrp', n='FKStretchyAimLLeg')
    NewFkGrpR = cmds.group('R_Leg_JJTwistIKrp', n='FKStretchyAimRLeg')
    cmds.xform(NewFkGrpL, rp=cmds.xform('L_Leg_JJ', q=True, rp=True))
    cmds.xform(NewFkGrpR, rp=cmds.xform('L_Leg_JJ', q=True, rp=True))
    cmds.aimConstraint('L_Knee_JJ', NewFkGrpL, weight=1, upVector=(0, 1, 0), mo=1, worldUpType='vector', aimVector=(1, 0, 0), worldUpVector=(0, 1, 0))
    cmds.aimConstraint('R_Knee_JJ', NewFkGrpR, weight=1, upVector=(0, 1, 0), mo=1, worldUpType='vector', aimVector=(1, 0, 0), worldUpVector=(0, 1, 0))
    try:
        cmds.delete('R_Knee_JJ_loc_orientConstraint1')
        cmds.orientConstraint('R_Ankle_JJ', 'R_Knee_JJ_loc', mo=False)
    except:
        pass
    cmds.undoInfo(closeChunk=True)
' \n                                \nLocatorsBtn()\nJointsBtn()\nIKFKLegs(LegsSize = 3, Twist = True, Ribbon = True)\n\n'


def run_script():
    exec(compile('jointsNum = 4', __file__, "exec"), globals())
