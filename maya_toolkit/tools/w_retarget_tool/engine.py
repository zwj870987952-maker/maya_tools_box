# Complete original CopyAnim matrix/constraint sampling, explicitly adapted.
import math
import time
from maya import cmds

def copy_anim(self, source, target, start_frame, end_frame, prefix, ValidObj=1, initTime=0):
    self.StartFrame = start_frame
    self.EndFrame = end_frame
    self.FrameTime = self.EndFrame - self.StartFrame
    if cmds.objExists(source):
        if cmds.objExists(target):
            "\n                decompMxMaster = cmds.shadingNode('decomposeMatrix',asUtility = 1, n = target +  'decompMx')\n                cmds.connectAttr(target + '.worldInverseMatrix[0]', decompMxMaster + '.inputMatrix' )\n                compMatrix = cmds.shadingNode('composeMatrix',asUtility = 1, n = target +  'compMx')\n                cmds.connectAttr(decompMxMaster + '.outputRotate', compMatrix + '.inputRotate')\n                holdMatrixTgt = cmds.shadingNode('holdMatrix', asUtility = True, n = target + 'holdMatrix')\n                cmds.connectAttr(compMatrix + '.outputMatrix',holdMatrixTgt + '.inMatrix', f = 1)\n                "
            cmds.currentTime(self.StartFrame)
            locGrpSrc1 = cmds.group(em=True, n=prefix + '_locGrpSrc1')
            locGrpSrc2 = cmds.group(locGrpSrc1, n=prefix + '_locGrpSrc2')
            cmds.delete(cmds.pointConstraint(source, locGrpSrc2))
            parents = cmds.listRelatives(source, parent=True, fullPath=True) or []
            if parents:
                sourceFather = parents[0]
                cmds.parentConstraint(sourceFather, locGrpSrc2, mo=True)
            cmds.parentConstraint(source, locGrpSrc1, mo=True)
            locGrpTgt1 = cmds.group(em=True, n=prefix + '_locGrpTgt1')
            locGrpTgt2 = cmds.group(locGrpTgt1, n=prefix + '_locGrpTgt2')
            cmds.delete(cmds.pointConstraint(target, locGrpTgt2))
            locGrpTgt3 = cmds.group(em=True, n=prefix + '_locGrpTgt3')
            cmds.delete(cmds.parentConstraint(target, locGrpTgt3))
            parents = cmds.listRelatives(target, parent=True, fullPath=True) or []
            if parents:
                sourceFatherTgt = parents[0]
                cmds.parent(locGrpTgt2, sourceFatherTgt)
                cmds.parent(locGrpTgt3, sourceFatherTgt)
            cmds.parentConstraint(locGrpTgt1, locGrpTgt3, mo=True)
            for i in range(self.StartFrame, self.EndFrame):
                startTime = time.time()
                cmds.currentTime(i)
                "\n                    if i == self.StartFrame:\n                        cmds.disconnectAttr(source + '.worldInverseMatrix[0]',holdMatrixSrc + '.inMatrix')\n                        cmds.disconnectAttr(compMatrix + '.outputMatrix',holdMatrixTgt + '.inMatrix')\n                    "
                multMatrix1 = cmds.shadingNode('multMatrix', asUtility=True, n=prefix + 'multMatrix')
                cmds.connectAttr(locGrpSrc1 + '.worldMatrix[0]', multMatrix1 + '.matrixIn[0]', f=1)
                cmds.connectAttr(locGrpSrc2 + '.worldInverseMatrix[0]', multMatrix1 + '.matrixIn[1]', f=1)
                "\n                    multMatrix2 = cmds.shadingNode('multMatrix', asUtility = True, n = source + 'multMatrix2')\n                    cmds.connectAttr(multMatrix1 + '.matrixSum',multMatrix2 + '.matrixIn[0]', f = 1)\n                    cmds.connectAttr(holdMatrixTgt + '.outMatrix',multMatrix2 + '.matrixIn[1]', f = 1)\n                    "
                decompMxMaster = cmds.shadingNode('decomposeMatrix', asUtility=1, n=prefix + 'decompMx')
                cmds.connectAttr(multMatrix1 + '.matrixSum', decompMxMaster + '.inputMatrix')
                cmds.connectAttr(decompMxMaster + '.outputRotate', locGrpTgt1 + '.r', f=1)
                cmds.connectAttr(decompMxMaster + '.outputTranslate', locGrpTgt1 + '.t', f=1)
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                    valueAttr = cmds.getAttr(locGrpTgt3 + '.' + attr)
                    if not math.isfinite(valueAttr):
                        raise ValueError('Non-finite sampled channel')
                    cmds.setKeyframe(target, attribute=attr, time=i, value=valueAttr)
                endTime = time.time()
                TotalEstimatedTime = self.FrameTime * (endTime - startTime) * ValidObj
                EstimatedRemainingTime = TotalEstimatedTime + initTime - endTime
                RemainingTimeLabel = 'Estimated remaining Time: ' + str(EstimatedRemainingTime) + ' seg'
                cmds.progressBar(self.ProgressControl, edit=True, step=1)
                '\n                    if i == 5:\n                        break\n                    '
            cmds.delete(locGrpSrc1)
            cmds.delete(locGrpSrc2)
            cmds.delete(locGrpTgt3)
            cmds.delete(locGrpTgt1)
            cmds.delete(locGrpTgt2)
            (print('Animation copied from: ' + source + ' to: ' + target + '\n'),)
            if ValidObj == 1:
                cmds.progressBar(self.ProgressControl, edit=True, endProgress=True)
        else:
            cmds.warning('No target Selected')
    else:
        cmds.warning('No source Selected')
