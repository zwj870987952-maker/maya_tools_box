import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui2
import maya.api.OpenMayaRender as omr2
import maya.api.OpenMayaAnim as oma2
import json

_parsedCacheStore = {}


def maya_useNewAPI():
    pass


class TracifyNode(omui2.MPxLocatorNode):
    TYPE_NAME = "tracifyNode"
    TYPE_ID = om2.MTypeId(0x0012cb01)
    DRAW_CLASSIFY = "drawdb/geometry/tracifyNode"
    DRAW_REGISTRANT = "tracifyPlugin"
    
    aTimeInput = None
    aFrameRange = None
    aPointSize = None
    aLineWidth = None
    aLineColorR = None
    aLineColorG = None
    aLineColorB = None
    aKeyColorR = None
    aKeyColorG = None
    aKeyColorB = None
    aCacheData = None
    aSourceWorldMatrix = None
    aColorMode = None
    aCameraSpace = None
    aCameraWorldMatrix = None
    aOutput = None
    
    def __init__(self):
        omui2.MPxLocatorNode.__init__(self)
    
    @staticmethod
    def creator():
        return TracifyNode()
    
    @staticmethod
    def initialize():
        nFn = om2.MFnNumericAttribute()
        tFn = om2.MFnTypedAttribute()
        uFn = om2.MFnUnitAttribute()
        mFn = om2.MFnMatrixAttribute()
        
        TracifyNode.aTimeInput = uFn.create("timeInput", "ti", om2.MFnUnitAttribute.kTime, 0.0)
        uFn.storable = False
        uFn.writable = True
        uFn.hidden = True
        TracifyNode.addAttribute(TracifyNode.aTimeInput)
        
        TracifyNode.aSourceWorldMatrix = mFn.create("sourceWorldMatrix", "swm")
        mFn.storable = False
        mFn.writable = True
        mFn.hidden = True
        TracifyNode.addAttribute(TracifyNode.aSourceWorldMatrix)
        
        TracifyNode.aFrameRange = nFn.create("frameRange", "fr", om2.MFnNumericData.kInt, 18)
        nFn.storable = True
        nFn.keyable = True
        TracifyNode.addAttribute(TracifyNode.aFrameRange)
        
        TracifyNode.aPointSize = nFn.create("pointSize", "ps", om2.MFnNumericData.kFloat, 5.0)
        nFn.storable = True
        nFn.keyable = True
        TracifyNode.addAttribute(TracifyNode.aPointSize)
        
        TracifyNode.aLineWidth = nFn.create("lineWidth", "lw", om2.MFnNumericData.kFloat, 4.0)
        nFn.storable = True
        nFn.keyable = True
        TracifyNode.addAttribute(TracifyNode.aLineWidth)
        
        TracifyNode.aLineColorR = nFn.create("lineColorR", "lcr", om2.MFnNumericData.kFloat, 1.0)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aLineColorR)
        
        TracifyNode.aLineColorG = nFn.create("lineColorG", "lcg", om2.MFnNumericData.kFloat, 1.0)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aLineColorG)
        
        TracifyNode.aLineColorB = nFn.create("lineColorB", "lcb", om2.MFnNumericData.kFloat, 0.3)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aLineColorB)
        
        TracifyNode.aKeyColorR = nFn.create("keyColorR", "kcr", om2.MFnNumericData.kFloat, 1.0)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aKeyColorR)
        
        TracifyNode.aKeyColorG = nFn.create("keyColorG", "kcg", om2.MFnNumericData.kFloat, 0.9)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aKeyColorG)
        
        TracifyNode.aKeyColorB = nFn.create("keyColorB", "kcb", om2.MFnNumericData.kFloat, 0.15)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aKeyColorB)
        
        TracifyNode.aColorMode = nFn.create("colorMode", "cm", om2.MFnNumericData.kInt, 0)
        nFn.storable = True
        TracifyNode.addAttribute(TracifyNode.aColorMode)
        
        TracifyNode.aCameraSpace = nFn.create("cameraSpace", "cs", om2.MFnNumericData.kBoolean, False)
        nFn.storable = True
        nFn.keyable = True
        TracifyNode.addAttribute(TracifyNode.aCameraSpace)
        
        TracifyNode.aCameraWorldMatrix = mFn.create("cameraWorldMatrix", "cwm")
        mFn.storable = False
        mFn.writable = True
        mFn.hidden = True
        TracifyNode.addAttribute(TracifyNode.aCameraWorldMatrix)
        
        TracifyNode.aCacheData = tFn.create("cacheData", "cd", om2.MFnData.kString)
        tFn.storable = True
        tFn.hidden = True
        TracifyNode.addAttribute(TracifyNode.aCacheData)
        
        TracifyNode.aOutput = nFn.create("output", "out", om2.MFnNumericData.kFloat, 0.0)
        nFn.storable = False
        nFn.writable = False
        nFn.hidden = True
        TracifyNode.addAttribute(TracifyNode.aOutput)
        
        TracifyNode.attributeAffects(TracifyNode.aTimeInput, TracifyNode.aOutput)
        TracifyNode.attributeAffects(TracifyNode.aCacheData, TracifyNode.aOutput)
        TracifyNode.attributeAffects(TracifyNode.aCameraSpace, TracifyNode.aOutput)
        TracifyNode.attributeAffects(TracifyNode.aCameraWorldMatrix, TracifyNode.aOutput)
    
    def isBounded(self):
        return True
    
    def boundingBox(self):
        return om2.MBoundingBox(om2.MPoint(-1e6, -1e6, -1e6), om2.MPoint(1e6, 1e6, 1e6))


class TracifyDrawData(om2.MUserData):
    def __init__(self):
        om2.MUserData.__init__(self, False)
        self.frameRange = 18
        self.pointSize = 5.0
        self.lineWidth = 4.0
        self.colorR = 1.0
        self.colorG = 1.0
        self.colorB = 0.3
        self.keyColorR = 1.0
        self.keyColorG = 0.9
        self.keyColorB = 0.15
        self.colorMode = 0
        self.currentFrame = 0
        self.points = []
        self.keyframes = set()
        self.cameraSpace = False
        self.cameraWorldMatrix = om2.MMatrix()


class TracifyDrawOverride(omr2.MPxDrawOverride):
    
    def __init__(self, obj):
        omr2.MPxDrawOverride.__init__(self, obj, None, True)
    
    @staticmethod
    def creator(obj):
        return TracifyDrawOverride(obj)
    
    def supportedDrawAPIs(self):
        return omr2.MRenderer.kAllDevices
    
    def hasUIDrawables(self):
        return True
    
    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        data = oldData if isinstance(oldData, TracifyDrawData) else TracifyDrawData()
        data.points = []
        data.keyframes = set()
        
        node = objPath.node()
        if node.isNull():
            return data
        
        fn = om2.MFnDependencyNode(node)
        
        data.frameRange = fn.findPlug("frameRange", False).asInt()
        data.pointSize = fn.findPlug("pointSize", False).asFloat()
        data.lineWidth = fn.findPlug("lineWidth", False).asFloat()
        data.colorR = fn.findPlug("lineColorR", False).asFloat()
        data.colorG = fn.findPlug("lineColorG", False).asFloat()
        data.colorB = fn.findPlug("lineColorB", False).asFloat()
        data.keyColorR = fn.findPlug("keyColorR", False).asFloat()
        data.keyColorG = fn.findPlug("keyColorG", False).asFloat()
        data.keyColorB = fn.findPlug("keyColorB", False).asFloat()
        data.colorMode = fn.findPlug("colorMode", False).asInt()
        data.currentFrame = int(oma2.MAnimControl.currentTime().value)
        data.cameraSpace = fn.findPlug("cameraSpace", False).asBool()
        
        try:
            camMatrixObj = fn.findPlug("cameraWorldMatrix", False).asMObject()
            data.cameraWorldMatrix = om2.MFnMatrixData(camMatrixObj).matrix()
        except:
            data.cameraWorldMatrix = om2.MMatrix()
        
        cacheStr = fn.findPlug("cacheData", False).asString()
        if not cacheStr:
            return data
        
        nodeName = fn.name()
        cached = _parsedCacheStore.get(nodeName)
        if cached and cached[0] == cacheStr:
            cache = cached[1]
        else:
            try:
                cache = json.loads(cacheStr)
                _parsedCacheStore[nodeName] = (cacheStr, cache)
            except:
                return data
        
        positions = cache.get("positions", {})
        cameraPositions = cache.get("cameraPositions", {})
        data.keyframes = set(cache.get("keyframes", []))
        cacheStart = cache.get("start", 0)
        cacheEnd = cache.get("end", 0)
        
        displayStart = max(data.currentFrame - data.frameRange, cacheStart)
        displayEnd = min(data.currentFrame + data.frameRange, cacheEnd)
        
        sourcePositions = cameraPositions if (data.cameraSpace and cameraPositions) else positions
        useFlatten = data.cameraSpace and bool(cameraPositions)
        
        referenceDepth = None
        if useFlatten:
            currentLocal = cameraPositions.get(str(data.currentFrame))
            if currentLocal is not None:
                referenceDepth = currentLocal[2]
            else:
                for offset in range(1, data.frameRange + 1):
                    left = cameraPositions.get(str(data.currentFrame - offset))
                    if left is not None:
                        referenceDepth = left[2]
                        break
                    right = cameraPositions.get(str(data.currentFrame + offset))
                    if right is not None:
                        referenceDepth = right[2]
                        break
        
        if useFlatten and referenceDepth is None:
            return data
        
        for frame in range(displayStart, displayEnd + 1):
            key = str(frame)
            if key in sourcePositions:
                p = sourcePositions[key]
                if useFlatten:
                    dz = p[2]
                    if abs(dz) > 1e-6:
                        scale = referenceDepth / dz
                    else:
                        scale = 1.0
                    localPoint = om2.MPoint(p[0] * scale, p[1] * scale, referenceDepth)
                else:
                    localPoint = om2.MPoint(p[0], p[1], p[2])
                point = localPoint
                if useFlatten:
                    point = point * data.cameraWorldMatrix
                data.points.append((frame, point))
        
        return data
    
    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        if not isinstance(data, TracifyDrawData) or len(data.points) < 2:
            return
        
        lineColor = om2.MColor([data.colorR, data.colorG, data.colorB, 1.0])
        colCurrent = om2.MColor([1.0, 0.2, 0.2, 1.0])
        colDots = om2.MColor([data.keyColorR, data.keyColorG, data.keyColorB, 1.0])
        
        currentPt = None
        currentIdx = -1
        keyPts = om2.MPointArray()
        inbetweenPts = om2.MPointArray()
        keyIndices = []
        inbetweenIndices = []
        
        for idx, (frame, pt) in enumerate(data.points):
            if frame == data.currentFrame:
                currentPt = pt
                currentIdx = idx
            elif frame in data.keyframes:
                keyPts.append(pt)
                keyIndices.append(idx)
            else:
                inbetweenPts.append(pt)
                inbetweenIndices.append(idx)
        
        numPoints = len(data.points)
        useGradient = data.colorMode > 0
        
        drawManager.beginDrawInXray()
        drawManager.setLineWidth(data.lineWidth)
        
        for i in range(numPoints - 1):
            frame1, pt1 = data.points[i]
            frame2, pt2 = data.points[i + 1]
            if frame2 - frame1 <= 3:
                if useGradient:
                    t = i / max(1, numPoints - 2)
                    color = self._getGradientColor(t, data.colorMode, data.currentFrame)
                    drawManager.setColor(om2.MColor([color[0], color[1], color[2], 1.0]))
                else:
                    drawManager.setColor(lineColor)
                drawManager.line(pt1, pt2)
        
        drawManager.endDrawInXray()
        
        drawManager.beginDrawInXray()
        
        if useGradient:
            drawManager.setPointSize(data.pointSize)
            for idx in inbetweenIndices:
                t = idx / max(1, numPoints - 1)
                color = self._getGradientColor(t, data.colorMode, data.currentFrame)
                whiteColor = (0.7 + color[0] * 0.3, 0.7 + color[1] * 0.3, 0.7 + color[2] * 0.3)
                drawManager.setColor(om2.MColor([whiteColor[0], whiteColor[1], whiteColor[2], 1.0]))
                drawManager.point(data.points[idx][1])
            
            for idx in keyIndices:
                t = idx / max(1, numPoints - 1)
                color = self._getGradientColor(t, data.colorMode, data.currentFrame)
                whiteColor = (0.7 + color[0] * 0.3, 0.7 + color[1] * 0.3, 0.7 + color[2] * 0.3)
                drawManager.setColor(om2.MColor([whiteColor[0], whiteColor[1], whiteColor[2], 1.0]))
                drawManager.point(data.points[idx][1])
        else:
            if len(inbetweenPts) > 0:
                drawManager.setPointSize(data.pointSize)
                drawManager.setColor(colDots)
                drawManager.points(inbetweenPts, False)
            
            if len(keyPts) > 0:
                drawManager.setPointSize(data.pointSize)
                drawManager.setColor(colDots)
                drawManager.points(keyPts, False)
        
        if currentPt:
            drawManager.setPointSize(data.pointSize * 1.8)
            drawManager.setColor(colCurrent)
            drawManager.point(currentPt)
        
        drawManager.endDrawInXray()
    
    def _getGradientColor(self, t, mode, currentFrame=0):
        if mode == 1:
            return self._hsvToRgb(t * 0.85, 0.9, 1.0)
        elif mode == 2:
            # Fire/Temperature - animate based on currentFrame
            # More gradual color stops for smoother transitions
            colors = [
                (0.9, 0.1, 0.05),   # Deep red
                (0.95, 0.2, 0.05),  # Red-orange
                (1.0, 0.35, 0.0),   # Orange
                (1.0, 0.5, 0.0),    # Orange-gold
                (1.0, 0.65, 0.05),  # Gold
                (1.0, 0.8, 0.15),   # Light gold
                (1.0, 0.9, 0.3),    # Yellow-gold
                (1.0, 0.8, 0.15),   # Light gold
                (1.0, 0.65, 0.05),  # Gold
                (1.0, 0.5, 0.0),    # Orange-gold
                (0.95, 0.35, 0.0),  # Orange
                (0.9, 0.2, 0.05),   # Red-orange
            ]
            # Offset t based on currentFrame to create animation effect
            offset = (currentFrame * 0.04) % 1.0
            animT = (t - offset) % 1.0
            return self._lerpColors(colors, animT)
        elif mode == 3:
            colors = [(0.0, 0.2, 0.6), (0.0, 0.4, 0.8), (0.0, 0.6, 0.9), (0.0, 0.8, 0.85), (0.2, 0.9, 0.8)]
            return self._lerpColors(colors, t)
        elif mode == 4:
            colors = [(1.0, 0.85, 0.92), (1.0, 0.6, 0.8), (1.0, 0.4, 0.7), (0.9, 0.3, 0.75), (0.75, 0.35, 0.9)]
            return self._lerpColors(colors, t)
        return (1.0, 1.0, 1.0)
    
    def _lerpColors(self, colors, t):
        n = len(colors) - 1
        idx = t * n
        i = int(idx)
        if i >= n:
            return colors[-1]
        f = idx - i
        c1, c2 = colors[i], colors[i + 1]
        return (c1[0] + (c2[0] - c1[0]) * f, c1[1] + (c2[1] - c1[1]) * f, c1[2] + (c2[2] - c1[2]) * f)
    
    def _hsvToRgb(self, h, s, v):
        if s == 0.0:
            return (v, v, v)
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)
        return (v, v, v)


def initializePlugin(obj):
    plugin = om2.MFnPlugin(obj, "Tracify", "1.0")
    plugin.registerNode(
        TracifyNode.TYPE_NAME,
        TracifyNode.TYPE_ID,
        TracifyNode.creator,
        TracifyNode.initialize,
        omui2.MPxLocatorNode.kLocatorNode,
        TracifyNode.DRAW_CLASSIFY
    )
    omr2.MDrawRegistry.registerDrawOverrideCreator(
        TracifyNode.DRAW_CLASSIFY,
        TracifyNode.DRAW_REGISTRANT,
        TracifyDrawOverride.creator
    )


def uninitializePlugin(obj):
    plugin = om2.MFnPlugin(obj)
    omr2.MDrawRegistry.deregisterDrawOverrideCreator(
        TracifyNode.DRAW_CLASSIFY,
        TracifyNode.DRAW_REGISTRANT
    )
    plugin.deregisterNode(TracifyNode.TYPE_ID)