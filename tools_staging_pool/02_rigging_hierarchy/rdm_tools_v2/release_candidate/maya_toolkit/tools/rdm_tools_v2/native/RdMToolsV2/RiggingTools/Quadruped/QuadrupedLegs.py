from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds, OpenMaya
import math

def create_locator(side):
    loc = cmds.spaceLocator(n='{}_upper_Leg_loc'.format(side))
    cmds.delete(cmds.parentConstraint('{}_Leg_JJ'.format(side), loc))
    cmds.move(0, 5, 0, loc, r=True)

def create_upper_leg():
    Rloc = cmds.spaceLocator(n='R_upper_Leg_loc')
    cmds.delete(cmds.parentConstraint('L_upper_Leg_loc', Rloc))
    mirror_grp = cmds.group(em=True)
    cmds.parent(Rloc, mirror_grp)
    cmds.setAttr('{}.scaleX'.format(mirror_grp), -1)

    def jointSwitch(side):
        cmds.select(cl=True)
        upper_joint = cmds.joint(n='{}_upperLeg_JJ'.format(side))
        cmds.delete(cmds.parentConstraint('{}_upper_Leg_loc'.format(side), upper_joint), '{}_upper_Leg_loc'.format(side))
        ik_joint = cmds.duplicate(upper_joint, n='{}_IK_JC'.format(upper_joint))
        cmds.makeIdentity(t=1, r=1, jo=1)
        fk_joint = cmds.duplicate(upper_joint, n='{}_FK_JC'.format(upper_joint))
        cmds.makeIdentity(t=1, r=1, jo=1)
        cmds.parentConstraint(ik_joint, fk_joint, upper_joint)
        cmds.connectAttr('{}_Leg_FKIK_BlendShape.Blend_IKFK'.format(side), '{}_upperLeg_JJ_parentConstraint1.{}_upperLeg_JJ_IK_JCW0'.format(side, side))
        mel.eval('shadingNode -asUtility reverse -n {}_upperLeg_reverse'.format(side))
        mel.eval('connectAttr -f {}_upperLeg_reverse.outputX {}_upperLeg_JJ_parentConstraint1.{}_upperLeg_JJ_FK_JCW1;'.format(side, side, side))
        mel.eval('connectAttr -f {}_Leg_FKIK_BlendShape.Blend_IKFK {}_upperLeg_reverse.inputX;'.format(side, side))
    jointSwitch(side='L')
    jointSwitch(side='R')
    cmds.parent('L_Leg_JJ_IK', 'L_upperLeg_JJ_IK_JC')
    cmds.parent('L_upperLeg_JJ_IK_JC', 'L_Leg_JJ_IK_GRP')
    cmds.parent('R_Leg_JJ_IK', 'R_upperLeg_JJ_IK_JC')
    cmds.parent('R_upperLeg_JJ_IK_JC', 'R_Leg_JJ_IK_GRP')
    "\n    IkHandleL = cmds.ikHandle (n='L_upper_leg_IKrp', sj='L_upperLeg_JJ_IK_JC', ee= 'L_Knee_JJ_IK', sol = 'ikRPsolver')\n    IkHandleR = cmds.ikHandle (n='R_upper_leg_IKrp', sj='R_upperLeg_JJ_IK_JC', ee= 'R_Knee_JJ_IK', sol = 'ikRPsolver')\n    \n    #delete old IK and create a new one\n    cmds.delete('L_Ankle_JJ_IKIKrp')    \n    cmds.delete('R_Ankle_JJ_IKIKrp')    \n\n    IkHandleL2 = cmds.ikHandle (n='L_Ankle_JJ_IKIKrp', sj='L_Leg_JJ_IK', ee= 'L_Ankle_JJ_IK', sol = 'ikRPsolver')\n    IkHandleR2 = cmds.ikHandle (n='R_Ankle_JJ_IKIKrp', sj='R_Leg_JJ_IK', ee= 'R_Ankle_JJ_IK', sol = 'ikRPsolver')\n    cmds.poleVectorConstraint('L_Knee_PV', IkHandleL2[0])\n    cmds.poleVectorConstraint('R_Knee_PV', IkHandleR2[0])\n\n    #parent All Ik Stuff\n    cmds.parent(IkHandleL[0],'L_Leg_IK_CC')\n    cmds.parent(IkHandleR[0],'R_Leg_IK_CC')\n    cmds.parent(IkHandleL2[0],'L_RF_Ankle')\n    cmds.parent(IkHandleR2[0],'R_RF_Ankle')\n\n\n    #Thanks to >>> https://vimeo.com/66015036\n    cmds.select('L_upperLeg_JJ_IK_JC','L_Leg_JJ_IK','L_Knee_JJ_IK')\n    sel = cmds.ls(sl = 1)\n    start = cmds.xform(sel[0] ,q= 1 ,ws = 1,t =1 )\n    mid = cmds.xform(sel[1] ,q= 1 ,ws = 1,t =1 )\n    end = cmds.xform(sel[2] ,q= 1 ,ws = 1,t =1 )\n    startV = OpenMaya.MVector(start[0] ,start[1],start[2])\n    midV = OpenMaya.MVector(mid[0] ,mid[1],mid[2])\n    endV = OpenMaya.MVector(end[0] ,end[1],end[2])\n    startEnd = endV - startV\n    startMid = midV - startV\n    dotP = startMid * startEnd\n    proj = float(dotP) / float(startEnd.length())\n    startEndN = startEnd.normal()\n    projV = startEndN * proj\n    arrowV = startMid - projV\n    arrowV*= 0.5\n    finalV = arrowV + midV\n    cross1 = startEnd ^ startMid\n    cross1.normalize()\n    cross2 = cross1 ^ arrowV\n    cross2.normalize()\n    arrowV.normalize()\n    matrixV = [arrowV.x , arrowV.y , arrowV.z , 0 ,\n    cross1.x ,cross1.y , cross1.z , 0 ,\n    cross2.x , cross2.y , cross2.z , 0,\n    0,0,0,1]\n    matrixM = OpenMaya.MMatrix()\n    OpenMaya.MScriptUtil.createMatrixFromList(matrixV , matrixM)\n    matrixFn = OpenMaya.MTransformationMatrix(matrixM)\n    rot = matrixFn.eulerRotation()\n    loc = cmds.spaceLocator(n = 'nullLocPV')[0]\n    cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z))\n    cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0),\n    (rot.y/math.pi*180.0),\n    (rot.z/math.pi*180.0)))    \n        \n    pvDistance = cmds.getAttr('L_Leg_JJ_IK.translateY')*1.5    \n    cmds.select(loc)     \n\n    cmds.move(-pvDistance/2, 0, 0, r=1, os=1, wd=1) \n\n    cmds.poleVectorConstraint(loc, IkHandleL[0])\n    cmds.rename(loc, 'L_PV_loc')\n    \n    #duplciate to right side\n    Rloc = cmds.spaceLocator(n = 'R_PV_loc')\n    cmds.delete(cmds.parentConstraint('L_PV_loc',Rloc))\n    mirror_grp = cmds.group(em = True)\n    cmds.parent(Rloc, mirror_grp)\n    cmds.setAttr('{}.scaleX'.format(mirror_grp),-1)\n    cmds.poleVectorConstraint(Rloc, IkHandleR[0])\n        \n    "
    ctrl = cmds.circle(n='L_upper_leg_Fk_CC', r=cmds.getAttr('L_Leg_JJ_FK.translateY') / 2, nr=(1, 0, 0))
    offset = cmds.group(ctrl, n='{}_OffsetGrp'.format(ctrl[0]))
    cmds.delete(cmds.parentConstraint('L_upperLeg_JJ_FK_JC', offset, mo=False))
    cmds.parentConstraint(ctrl, 'L_upperLeg_JJ_FK_JC')
    cmds.parent('L_Leg_JJ_FK_GRP', 'L_upperLeg_JJ_FK_JC')
    cmds.parent('L_upperLeg_JJ_FK_JC', ctrl)
    cmds.parent(offset, 'L_Leg_GRP')
    ctrl = cmds.circle(n='R_upper_leg_Fk_CC', r=cmds.getAttr('R_Leg_JJ_FK.translateY') / 2, nr=(1, 0, 0))
    offset = cmds.group(ctrl, n='{}_OffsetGrp'.format(ctrl[0]))
    cmds.delete(cmds.parentConstraint('R_upperLeg_JJ_FK_JC', offset, mo=False))
    cmds.parentConstraint(ctrl, 'R_upperLeg_JJ_FK_JC')
    cmds.parent('R_Leg_JJ_FK_GRP', 'R_upperLeg_JJ_FK_JC')
    cmds.parent('R_upperLeg_JJ_FK_JC', ctrl)
    cmds.parent(offset, 'R_Leg_GRP')


def run_script():
    exec(compile("create_locator(side='L')\ncreate_upper_leg()", __file__, "exec"), globals())
