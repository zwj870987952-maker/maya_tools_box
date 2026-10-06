import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds
import math


def maya_useNewAPI():
    pass


class SmoothKeysCmd(om.MPxCommand):
    kPluginCmdName = "smoothKeysAPI"
    kStrengthFlag = "-st"
    kStrengthFlagLong = "-strength"
    kIterationsFlag = "-it"
    kIterationsFlagLong = "-iterations"
    
    def __init__(self):
        om.MPxCommand.__init__(self)
        self.curveChanges = None
        self.strength = 0.5
        self.iterations = 1
    
    @staticmethod
    def creator():
        return SmoothKeysCmd()
    
    @staticmethod
    def createSyntax():
        syntax = om.MSyntax()
        syntax.addFlag(SmoothKeysCmd.kStrengthFlag, SmoothKeysCmd.kStrengthFlagLong, om.MSyntax.kDouble)
        syntax.addFlag(SmoothKeysCmd.kIterationsFlag, SmoothKeysCmd.kIterationsFlagLong, om.MSyntax.kLong)
        return syntax
    
    def isUndoable(self):
        return True
    
    def parseArguments(self, args):
        argData = om.MArgDatabase(self.syntax(), args)
        
        if argData.isFlagSet(SmoothKeysCmd.kStrengthFlag):
            self.strength = argData.flagArgumentDouble(SmoothKeysCmd.kStrengthFlag, 0)
        
        if argData.isFlagSet(SmoothKeysCmd.kIterationsFlag):
            self.iterations = argData.flagArgumentInt(SmoothKeysCmd.kIterationsFlag, 0)
    
    def getAnimCurveFunction(self, curveName):
        selectionList = om.MSelectionList()
        selectionList.add(curveName)
        dependNode = selectionList.getDependNode(0)
        return oma.MFnAnimCurve(dependNode)
    
    def isRotationCurve(self, animCurveFn):
        curveType = animCurveFn.animCurveType
        rotationTypes = [
            oma.MFnAnimCurve.kAnimCurveTA,
            oma.MFnAnimCurve.kAnimCurveUA
        ]
        return curveType in rotationTypes
    
    def gatherKeyData(self, animCurveFn):
        keyCount = animCurveFn.numKeys
        keyData = []
        isRotation = self.isRotationCurve(animCurveFn)
        
        for i in range(keyCount):
            timeVal = animCurveFn.input(i).value
            valueVal = animCurveFn.value(i)
            
            if isRotation:
                valueVal = math.degrees(valueVal)
            
            keyData.append([timeVal, valueVal])
        
        return keyData, isRotation
    
    def computeLaplacianSmoothedValue(self, keyData, index):
        totalKeys = len(keyData)
        
        if index < 1 or index >= totalKeys - 1:
            return keyData[index][1]
        
        tPrev, vPrev = keyData[index - 1]
        tCurr, vCurr = keyData[index]
        tNext, vNext = keyData[index + 1]
        
        blend = (tCurr - tPrev) / (tNext - tPrev)
        vInterpolated = vPrev + (vNext - vPrev) * blend
        
        return vCurr + (vInterpolated - vCurr) * self.strength
    
    def doIt(self, args):
        self.parseArguments(args)
        self.curveChanges = oma.MAnimCurveChange()
        self.redoIt()
    
    def redoIt(self):
        animCurveNames = cmds.keyframe(q=True, name=True)
        
        if not animCurveNames:
            return
        
        for curveName in animCurveNames:
            selectedFrames = cmds.keyframe(curveName, q=True, sl=True, timeChange=True)
            
            if not selectedFrames:
                continue
            
            for iteration in range(self.iterations):
                animCurveFn = self.getAnimCurveFunction(curveName)
                keyData, isRotation = self.gatherKeyData(animCurveFn)
                
                timeToIndex = {data[0]: idx for idx, data in enumerate(keyData)}
                
                for frame in selectedFrames:
                    if frame not in timeToIndex:
                        continue
                    
                    keyIndex = timeToIndex[frame]
                    smoothedValue = self.computeLaplacianSmoothedValue(keyData, keyIndex)
                    
                    if isRotation:
                        smoothedValue = math.radians(smoothedValue)
                    
                    animCurveFn.setValue(keyIndex, smoothedValue, self.curveChanges)
                    keyData[keyIndex][1] = math.degrees(smoothedValue) if isRotation else smoothedValue
    
    def undoIt(self):
        if self.curveChanges:
            self.curveChanges.undoIt()


def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin, "SmoothKeys", "1.0")
    pluginFn.registerCommand(SmoothKeysCmd.kPluginCmdName, SmoothKeysCmd.creator, SmoothKeysCmd.createSyntax)


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    pluginFn.deregisterCommand(SmoothKeysCmd.kPluginCmdName)