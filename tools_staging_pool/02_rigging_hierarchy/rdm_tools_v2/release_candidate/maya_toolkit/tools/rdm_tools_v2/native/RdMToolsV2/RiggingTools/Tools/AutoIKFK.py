from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds, OpenMaya
import math
from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2

def RdM_IKFK(CustomName='RdM', size=3, Color=16, pvMethod='u'):
    cmds.undoInfo(openChunk=True)
    cmds.progressWindow(title='IK FK', progress=0, status='Starting', isInterruptable=True, maxValue=10)
    RadioSize = size
    JointsSel = cmds.ls(sl=1)
    if len(JointsSel) != 3:
        cmds.warning('Select Only 3 Joints without childres of parents')
    else:
        IKJoints = cmds.duplicate(JointsSel[0], rc=1)
        FKJoints = cmds.duplicate(JointsSel[0], rc=1)

        def CopyWithName(JointList, Ext):
            VarName = 0
            for i in JointList:
                NewName = cmds.rename(i, str(JointsSel[VarName]) + str(Ext))
                cmds.parentConstraint(NewName, str(JointsSel[VarName]), mo=True)
                VarName = VarName + 1
        CopyWithName(IKJoints, '_IK')
        CopyWithName(FKJoints, '_FK')
        cmds.select(str(JointsSel[0]) + '_IK', hi=True)
        IKJoints = cmds.ls(sl=1)
        cmds.select(str(JointsSel[0]) + '_FK', hi=True)
        FKJoints = cmds.ls(sl=1)
        cmds.progressWindow(edit=True, progress=1, status='Create FK')
        FKControllers = []

        def CreateFK(*args):
            Joints = cmds.ls(sl=True)
            for Joint in Joints:
                circulo = cmds.circle(n=str(Joint) + '_CC', nr=(1, 0, 0), r=RadioSize)
                FKControllers.append(circulo[0])
                grupo = cmds.group(circulo, n=str(Joint) + '_GRP')
                if 'X' in locals():
                    cmds.parent(grupo, X)
                parent01 = cmds.parentConstraint(Joint, grupo, mo=False)
                cmds.delete(parent01)
                parent02 = cmds.parentConstraint(circulo, Joint)
                if cmds.objExists(str(Joint) + '_CC'):
                    X = str(Joint) + '_CC'
                cmds.setAttr(str(circulo[0]) + '.overrideEnabled', 1)
                cmds.setAttr(str(circulo[0]) + '.overrideColor', Color)
        cmds.select(FKJoints)
        CreateFK()
        print(FKControllers)
        cmds.progressWindow(edit=True, progress=2, status='Create IK')
        CubeController = cmds.curve(n=str(IKJoints[-1]) + '_CC', d=1, p=[(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (-1, 1, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        GroupIKCube = cmds.group(n=str(IKJoints[-1]) + '_CC_GRP')
        cmds.setAttr(str(CubeController) + '.overrideEnabled', 1)
        cmds.setAttr(str(CubeController) + '.overrideColor', Color)
        ParentTemp = cmds.parentConstraint(IKJoints[-1], GroupIKCube, mo=0)
        cmds.delete(ParentTemp)
        cmds.xform(GroupIKCube, s=(RadioSize, RadioSize, RadioSize))
        IkHandle = cmds.ikHandle(n=str(IKJoints[-1] + 'IKrp'), sj=IKJoints[0], ee=IKJoints[-1], sol='ikRPsolver')
        cmds.parent(IkHandle[0], CubeController)
        cmds.progressWindow(edit=True, progress=3, status='Create PoleVector')
        CubeControllerPV = cmds.curve(n=str(IKJoints[1]) + '_PV', d=1, p=[(1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (-1, 1, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        GroupPVCube = cmds.group(n=str(IKJoints[1]) + '_PV_GRP')
        cmds.setAttr(str(CubeControllerPV) + '.overrideEnabled', 1)
        cmds.setAttr(str(CubeControllerPV) + '.overrideColor', Color)
        cmds.select(IKJoints[0], IKJoints[1], IKJoints[2])
        sel = cmds.ls(sl=1)
        start = cmds.xform(sel[0], q=1, ws=1, t=1)
        mid = cmds.xform(sel[1], q=1, ws=1, t=1)
        end = cmds.xform(sel[2], q=1, ws=1, t=1)
        startV = OpenMaya.MVector(start[0], start[1], start[2])
        midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
        endV = OpenMaya.MVector(end[0], end[1], end[2])
        startEnd = endV - startV
        startMid = midV - startV
        dotP = startMid * startEnd
        proj = float(dotP) / float(startEnd.length())
        startEndN = startEnd.normal()
        projV = startEndN * proj
        arrowV = startMid - projV
        arrowV *= 0.5
        finalV = arrowV + midV
        cross1 = startEnd ^ startMid
        cross1.normalize()
        cross2 = cross1 ^ arrowV
        cross2.normalize()
        arrowV.normalize()
        matrixV = [arrowV.x, arrowV.y, arrowV.z, 0, cross1.x, cross1.y, cross1.z, 0, cross2.x, cross2.y, cross2.z, 0, 0, 0, 0, 1]
        matrixM = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(matrixV, matrixM)
        matrixFn = OpenMaya.MTransformationMatrix(matrixM)
        rot = matrixFn.eulerRotation()
        loc = cmds.spaceLocator(n='nullLocPV')[0]
        cmds.xform(loc, ws=1, t=(finalV.x, finalV.y, finalV.z))
        cmds.xform(loc, ws=1, rotation=(rot.x / math.pi * 180.0, rot.y / math.pi * 180.0, rot.z / math.pi * 180.0))
        pvDistance = cmds.getAttr(str(IKJoints[1]) + '.translateX') * 1.5
        cmds.select(loc)
        cmds.move(pvDistance, 0, 0, r=1, os=1, wd=1)
        cmds.parentConstraint(loc, GroupPVCube, mo=False)
        cmds.delete(loc)
        cmds.poleVectorConstraint(CubeControllerPV, IkHandle[0])
        Null = cmds.addAttr(str(CubeControllerPV), ln='__________', at='enum', en=':.:')
        cmds.setAttr(str(CubeControllerPV) + '.__________', e=1, keyable=1)
        cmds.setAttr(str(CubeControllerPV) + '.__________', e=1, lock=True)
        AutoPV = cmds.addAttr(str(CubeControllerPV), ln='ParentMain', at='double', min=0, max=1)
        cmds.setAttr(str(CubeControllerPV) + '.ParentMain', e=1, keyable=1)
        cmds.parentConstraint(CubeController, GroupPVCube, mo=True)
        cmds.connectAttr(str(CubeControllerPV) + '.ParentMain', str(GroupPVCube) + '_parentConstraint1.' + str(CubeController) + 'W0')
        cmds.progressWindow(edit=True, progress=4, status='Switch Blend')
        BlendLocator = cmds.spaceLocator(n=str(CustomName) + '_FKIK_Blend')
        NewAttr = cmds.addAttr(str(BlendLocator[0] + 'Shape'), ln='RotateOrder', at='enum', en='XYZ:YZX:ZXY:XZY:YXZ:ZYX:')
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.RotateOrder', e=1, keyable=1)
        for i in JointsSel:
            cmds.connectAttr(str(BlendLocator[0]) + 'Shape.RotateOrder', str(i) + '.rotateOrder', f=1)
        for i in FKJoints:
            cmds.connectAttr(str(BlendLocator[0]) + 'Shape.RotateOrder', str(i) + '.rotateOrder', f=1)
        for i in IKJoints:
            cmds.connectAttr(str(BlendLocator[0]) + 'Shape.RotateOrder', str(i) + '.rotateOrder', f=1)
        NewAttr = cmds.addAttr(str(BlendLocator[0] + 'Shape'), ln='Blend_IKFK', at='double', min=0, max=1)
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', e=1, keyable=1)
        LockThisAttr = ('lpx', 'lpy', 'lpz', 'lsx', 'lsy', 'lsz')
        for L in LockThisAttr:
            cmds.setAttr(str(BlendLocator[0]) + 'Shape.' + str(L), lock=1, cb=0)
        cmds.parent(str(BlendLocator[0]) + 'Shape', CubeController, r=1, s=1)
        cmds.delete(BlendLocator)
        cmds.parent(str(BlendLocator[0]) + 'Shape', CubeControllerPV, add=1, s=1)
        for F in FKJoints:
            cmds.parent(str(BlendLocator[0]) + 'Shape', str(F) + '_CC', add=1, s=1)
        PlusMinusNode = cmds.shadingNode('plusMinusAverage', asUtility=1, n='IKFKMinus1' + str(JointsSel[0]))
        cmds.setAttr(str(PlusMinusNode) + '.operation', 2)
        cmds.setAttr(str(PlusMinusNode) + '.input2D[0].input2Dx', 1)
        cmds.setAttr(str(PlusMinusNode) + '.input2D[1].input2Dx', 0)
        cmds.connectAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', str(PlusMinusNode) + '.input2D[1].input2Dx')
        for C in JointsSel:
            cmds.connectAttr(str(PlusMinusNode) + '.output2D.output2Dx', str(C) + '_parentConstraint1.' + str(str(C) + '_FKW1'))
            cmds.connectAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', str(C) + '_parentConstraint1.' + str(str(C) + '_IKW0'))
        cmds.group(GroupPVCube, GroupIKCube, IKJoints[0], n=str(JointsSel[0]) + '_IK_GRP')
        cmds.rename(str(JointsSel[0]) + '_FK_GRP', str(JointsSel[0]) + '_FK_CVs')
        cmds.group(FKJoints[0], str(JointsSel[0]) + '_FK_CVs', n=str(JointsSel[0]) + '_FK_GRP')
        cmds.connectAttr(str(PlusMinusNode) + '.output2D.output2Dx', str(JointsSel[0]) + '_FK_GRP.visibility')
        cmds.connectAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', str(JointsSel[0]) + '_IK_GRP.visibility')
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', 1)
        cmds.progressWindow(edit=True, progress=5, status='Stretchy')
        firstPos = cmds.xform(IKJoints[0], q=True, t=True, ws=True)
        endPos = cmds.xform(IKJoints[-1], q=True, t=True, ws=True)
        StartLoc = cmds.spaceLocator(n=str(IKJoints[0]) + '_Stretchy01')
        cmds.xform(StartLoc, t=firstPos)
        cmds.setAttr(str(StartLoc[0]) + '.visibility', 0)
        EndLoc = cmds.spaceLocator(n=str(IKJoints[-1]) + '_Stretchy02')
        cmds.xform(EndLoc, t=endPos)
        cmds.setAttr(str(EndLoc[0]) + '.visibility', 0)
        Distance = cmds.distanceDimension(sp=firstPos, ep=endPos)
        Distance = cmds.rename(Distance, CustomName + '_Distance')
        cmds.parent(StartLoc, str(JointsSel[0]) + '_IK_GRP')
        cmds.parent(EndLoc, CubeController)
        null = cmds.group(em=True, n=CustomName + '_DistanceGrp')
        cmds.parent(Distance, null, r=1, s=1)
        cmds.parent(null, str(JointsSel[0]) + '_IK_GRP')
        try:
            cmds.delete('distanceDimension1')
        except:
            pass
        StartJoint = cmds.listConnections(IkHandle)
        jointDistance = cmds.listRelatives(StartJoint, ad=True, typ='joint')
        jointNum = 0
        totalDistance = 0
        for Joint in jointDistance:
            distanciaActual = cmds.getAttr(Joint + str('.translateX'))
            print(distanciaActual)
            totalDistance = totalDistance + distanciaActual
        if totalDistance < 0:
            totalDistance = totalDistance * -1
        else:
            pass
        Null = cmds.addAttr(str(BlendLocator[0] + 'Shape'), ln='__________', at='enum', en=':.:')
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.__________', e=1, keyable=1)
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.__________', e=1, lock=True)
        NewAttr = cmds.addAttr(str(BlendLocator[0] + 'Shape'), ln='IK_Stretchy', at='double', min=0, max=1)
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.IK_Stretchy', e=1, keyable=1)
        Null = cmds.addAttr(str(BlendLocator[0] + 'Shape'), ln='_________', at='enum', en=':.:')
        cmds.setAttr(str(BlendLocator[0]) + 'Shape._________', e=1, keyable=1)
        cmds.setAttr(str(BlendLocator[0]) + 'Shape._________', e=1, lock=True)
        Condition = cmds.shadingNode('condition', asUtility=True, n=CustomName + 'Condition')
        cmds.setAttr(str(Condition) + '.operation', 2)
        cmds.setAttr(str(Condition) + '.secondTerm', totalDistance)
        MultDivide = cmds.shadingNode('multiplyDivide', asUtility=True, n=CustomName + 'MultDiv')
        cmds.setAttr(str(MultDivide) + '.operation', 2)
        cmds.setAttr(str(MultDivide) + '.input2X', totalDistance)
        cmds.connectAttr(str(Distance) + '.distance', str(MultDivide) + '.input1X')
        cmds.connectAttr(str(MultDivide) + '.outputX', str(Condition) + '.colorIfTrueR')
        MultOut01 = cmds.shadingNode('multiplyDivide', asUtility=True, n=CustomName + '_MultDiv01')
        MultOut02 = cmds.shadingNode('multiplyDivide', asUtility=True, n=CustomName + '_MultDiv01')
        cmds.setAttr(str(MultOut01) + '.input2X', cmds.getAttr(str(IKJoints[1]) + '.translateX'))
        cmds.setAttr(str(MultOut02) + '.input2X', cmds.getAttr(str(IKJoints[2]) + '.translateX'))
        cmds.connectAttr(str(Condition) + '.outColorR', str(MultOut01) + '.input1X')
        cmds.connectAttr(str(Condition) + '.outColorR', str(MultOut02) + '.input1X')
        cmds.connectAttr(str(MultOut01) + '.outputX', str(IKJoints[1]) + '.translateX')
        cmds.connectAttr(str(MultOut02) + '.outputX', str(IKJoints[2]) + '.translateX')
        MultDivideStretchy = cmds.shadingNode('multiplyDivide', asUtility=True, n=CustomName + 'MultDiv00')
        cmds.connectAttr(str(Distance) + '.distance', str(MultDivideStretchy) + '.input1.input1X')
        cmds.connectAttr(str(MultDivideStretchy) + '.output.outputX', str(Condition) + '.firstTerm')
        cmds.connectAttr(str(BlendLocator[0]) + 'Shape.IK_Stretchy', str(MultDivideStretchy) + '.input2.input2X')
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.IK_Stretchy', 1)
        cmds.setAttr(str(null) + '.visibility', 0)
        cmds.setAttr(str(BlendLocator[0]) + 'Shape.visibility', 0)
        cmds.progressWindow(edit=True, progress=6, status='Connect with Line')

        def ConnectWIthLine(ColorCurve, Obj01, Obj02):
            Curve = cmds.curve(p=[(0, 0, 0), (0, 0, 1)], d=1, n=str(Obj01) + 'Line')
            cmds.setAttr('%s.overrideEnabled' % Curve, 1)
            cmds.setAttr('%s.overrideColor' % Curve, ColorCurve)
            Cluster01 = cmds.cluster(str(Curve) + '.cv[0]')
            Cluster02 = cmds.cluster(str(Curve) + '.cv[1]')
            cmds.parentConstraint(Obj01, Cluster01, mo=0)
            cmds.parentConstraint(Obj02, Cluster02, mo=0)
            if cmds.objExists('NoXformConnected'):
                print('Skip creating Group')
                Items = cmds.select(Curve, Cluster01, Cluster02, 'NoXformConnected')
                cmds.parent()
            else:
                cmds.group(Curve, Cluster01, Cluster02, n='NoXformConnected')
                cmds.setAttr('NoXformConnected.inheritsTransform', 0)
            cmds.setAttr(str(Curve) + '.inheritsTransform')
            cmds.setAttr(str(Cluster01[0]) + 'Handle.visibility', 0)
            cmds.setAttr(str(Cluster02[0]) + 'Handle.visibility', 0)
            cmds.connectAttr(str(BlendLocator[0]) + 'Shape.Blend_IKFK', str(Curve) + '.visibility')
            cmds.select(Curve)
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.ShowHideAttr import hideSelection
            legacy_reload(RdMToolsV2.RiggingTools.Tools.ShowHideAttr)
            hideSelection(hideT=True, hideR=True, hideS=True, hideV=True)
            cmds.setAttr(str(Curve) + '.template', 1)
        ConnectWIthLine(ColorCurve=Color, Obj01=CubeControllerPV, Obj02=IKJoints[1])
        LockThisAttrIK = ['sx', 'sy', 'sz', 'v']
        controllers = (CubeController, CubeControllerPV)
        for L in LockThisAttrIK:
            for i in controllers:
                cmds.setAttr(str(i) + '.' + str(L), lock=True, keyable=False, channelBox=False)
            for i in FKControllers:
                cmds.setAttr(str(i) + '.' + str(L), lock=True, keyable=False, channelBox=False)
        cmds.progressWindow(endProgress=1)
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
