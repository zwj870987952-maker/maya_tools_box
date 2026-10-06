import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.utils as mutils
import os
import json
import sys

FRAME_RANGE = 18
POINT_SIZE = 5.0
LINE_WIDTH = 4.0
GROUP_NAME = "Tracify"
COLORS = [(0.85, 0.12, 0.11), (1.0, 0.4, 0.7), (1.0, 0.9, 0.15), (0.7, 0.3, 0.9), (0.3, 0.6, 1.0)]
KEY_COLOR = (0.95, 0.45, 0.45)
CAMERA_SPACE = False
FILL_BATCH_SIZE = 1

_colorIndex = 0
_trackers = {}
_cache = {}
_cameraTransforms = {}
_jobs = []
_attrJobs = []
_cameraDirty = set()
_cameraCheckJob = None
_checkJob = None


def _loadPlugin():
    pluginName = "tracify_node.py"
    try:
        if cmds.pluginInfo(pluginName, query=True, loaded=True):
            return True
    except:
        pass
    thisDir = os.path.dirname(os.path.abspath(__file__))
    pluginPath = os.path.join(thisDir, pluginName)
    if not os.path.exists(pluginPath):
        cmds.error("Tracify: Cannot find " + pluginPath)
        return False
    try:
        cmds.loadPlugin(pluginPath)
        return True
    except Exception as e:
        cmds.error("Tracify: Failed to load plugin - " + str(e))
        return False


def _isPluginLoaded():
    try:
        return cmds.pluginInfo("tracify_node.py", query=True, loaded=True)
    except:
        return False


def _getNextColor():
    global _colorIndex
    color = COLORS[_colorIndex % len(COLORS)]
    _colorIndex += 1
    return color


def _getAnimRange():
    return int(oma2.MAnimControl.animationStartTime().value), int(oma2.MAnimControl.animationEndTime().value)


def _getPlaybackRange():
    return int(oma2.MAnimControl.minTime().value), int(oma2.MAnimControl.maxTime().value)


def _getCurrentFrame():
    return int(oma2.MAnimControl.currentTime().value)


def _getWorldPivotPoint(objName, frame=None):
    try:
        if frame is None:
            translate = cmds.getAttr(objName + ".translate")[0]
            pivotTranslate = cmds.getAttr(objName + ".rotatePivotTranslate")[0]
            pivot = cmds.getAttr(objName + ".rotatePivot")[0]
            parentMatrixVals = cmds.getAttr(objName + ".parentMatrix[0]")
        else:
            translate = cmds.getAttr(objName + ".translate", time=frame)[0]
            pivotTranslate = cmds.getAttr(objName + ".rotatePivotTranslate", time=frame)[0]
            pivot = cmds.getAttr(objName + ".rotatePivot", time=frame)[0]
            parentMatrixVals = cmds.getAttr(objName + ".parentMatrix[0]", time=frame)
        uiToInternal = om2.MDistance.uiToInternal(1.0)
        localPoint = om2.MPoint(
            (translate[0] + pivotTranslate[0] + pivot[0]) * uiToInternal,
            (translate[1] + pivotTranslate[1] + pivot[1]) * uiToInternal,
            (translate[2] + pivotTranslate[2] + pivot[2]) * uiToInternal
        )
        worldPoint = localPoint * om2.MMatrix(parentMatrixVals)
        return [worldPoint.x, worldPoint.y, worldPoint.z]
    except:
        return None


def _getCameraWorldMatrix(camTransform, frame=None):
    try:
        if frame is None:
            return cmds.getAttr(camTransform + ".worldMatrix[0]")
        return cmds.getAttr(camTransform + ".worldMatrix[0]", time=frame)
    except:
        return None


def _getActiveCameraTransform():
    cam = None
    try:
        panel = cmds.getPanel(withFocus=True)
        if panel and cmds.getPanel(typeOf=panel) == "modelPanel":
            cam = cmds.modelPanel(panel, query=True, camera=True)
    except:
        cam = None
    if not cam:
        try:
            panels = cmds.getPanel(type="modelPanel") or []
            for p in panels:
                try:
                    candidate = cmds.modelPanel(p, query=True, camera=True)
                except:
                    candidate = None
                if candidate:
                    cam = candidate
                    break
        except:
            pass
    if not cam:
        return None
    try:
        if cmds.objExists(cam) and cmds.nodeType(cam) == "camera":
            parents = cmds.listRelatives(cam, parent=True, fullPath=True) or []
            if parents:
                return parents[0]
            return None
        camList = cmds.ls(cam, long=True)
        if camList:
            return camList[0]
    except:
        pass
    return None


def _getPositionsAt(objName, camTransform, frame=None):
    worldPoint = _getWorldPivotPoint(objName, frame)
    if worldPoint is None:
        return None, None
    cameraPoint = None
    if camTransform:
        camMatrixVals = _getCameraWorldMatrix(camTransform, frame)
        if camMatrixVals is not None:
            try:
                camMatrix = om2.MMatrix(camMatrixVals)
                invCamMatrix = camMatrix.inverse()
                p = om2.MPoint(worldPoint[0], worldPoint[1], worldPoint[2])
                localPoint = p * invCamMatrix
                cameraPoint = [localPoint.x, localPoint.y, localPoint.z]
            except:
                cameraPoint = None
    return worldPoint, cameraPoint


def _getKeyframes(objName, start, end):
    keyframes = set()
    sel = om2.MSelectionList()
    try:
        sel.add(objName)
        dagPath = sel.getDagPath(0)
        node = dagPath.node()
        itDG = om2.MItDependencyGraph(node, om2.MFn.kAnimCurve, om2.MItDependencyGraph.kUpstream, om2.MItDependencyGraph.kDepthFirst, om2.MItDependencyGraph.kNodeLevel)
        while not itDG.isDone():
            curve = oma2.MFnAnimCurve(itDG.currentNode())
            for i in range(curve.numKeys):
                f = int(curve.input(i).value)
                if start <= f <= end:
                    keyframes.add(f)
            itDG.next()
    except:
        pass
    return list(keyframes)



def _buildVisibleCache(nodeName, srcObj):
    global _cache
    playStart, playEnd = _getAnimRange()
    camTransform = _cameraTransforms.get(nodeName)
    worldPositions = {}
    cameraPositions = {}
    for f in range(playStart, playEnd + 1):
        worldPoint, cameraPoint = _getPositionsAt(srcObj, camTransform, f)
        if worldPoint is not None:
            worldPositions[str(f)] = worldPoint
        if cameraPoint is not None:
            cameraPositions[str(f)] = cameraPoint
    keyframes = _getKeyframes(srcObj, playStart, playEnd)
    _cache[nodeName] = {
        "positions": worldPositions,
        "cameraPositions": cameraPositions,
        "cameraTransform": camTransform,
        "keyframes": keyframes,
        "start": playStart,
        "end": playEnd,
        "cameraSpace": bool(camTransform)
    }
    _syncCache(nodeName)


def _buildFillOrder(winStart, winEnd, currentFrame):
    order = []
    seen = set()

    def addOffset(off):
        f = currentFrame + off
        if f < winStart or f > winEnd or f in seen:
            return False
        seen.add(f)
        order.append(f)
        return True

    addOffset(0)
    leftStep = 0
    rightStep = 0
    while True:
        roundLefts = []
        roundRights = []
        for _ in range(3):
            leftStep += 1
            roundLefts.append(-leftStep)
        for _ in range(2):
            rightStep += 1
            roundRights.append(rightStep)
        interleaved = [roundLefts[0], roundRights[0], roundLefts[1], roundRights[1], roundLefts[2]]
        addedAny = False
        for off in interleaved:
            if addOffset(off):
                addedAny = True
        if not addedAny:
            break
    return order


_fillPending = {}
_fillJob = False


def _queueFill(nodeName, frames):
    global _fillPending
    if not frames:
        return
    _fillPending[nodeName] = frames
    _scheduleFill()


def _scheduleFill():
    global _fillJob
    if not _fillJob and _fillPending:
        _fillJob = True
        mutils.executeDeferred(_processFill)


def _processFill():
    global _fillJob, _fillPending
    _fillJob = False
    if not _fillPending:
        return
    needsRefresh = False
    for nodeName in list(_fillPending.keys()):
        if nodeName not in _cache or not cmds.objExists(nodeName):
            _fillPending.pop(nodeName, None)
            continue
        srcObj = _trackers.get(nodeName)
        if not srcObj or not cmds.objExists(srcObj):
            _fillPending.pop(nodeName, None)
            continue
        frames = _fillPending.get(nodeName) or []
        if not frames:
            _fillPending.pop(nodeName, None)
            continue
        camTransform = _cameraTransforms.get(nodeName)
        cache = _cache[nodeName]
        batch = frames[:FILL_BATCH_SIZE]
        remaining = frames[FILL_BATCH_SIZE:]
        positions = cache["positions"]
        cameraPositions = cache.setdefault("cameraPositions", {})
        for f in batch:
            worldPoint, cameraPoint = _getPositionsAt(srcObj, camTransform, f)
            if worldPoint is not None:
                positions[str(f)] = worldPoint
            if cameraPoint is not None:
                cameraPositions[str(f)] = cameraPoint
        if remaining:
            _fillPending[nodeName] = remaining
        else:
            _fillPending.pop(nodeName, None)
        _syncCache(nodeName)
        needsRefresh = True
    if needsRefresh:
        cmds.refresh(cv=True)
    if _fillPending:
        _scheduleFill()


def _clearFillQueue():
    global _fillPending, _fillJob
    _fillPending = {}
    _fillJob = False


def _syncCache(nodeName):
    if nodeName in _cache and cmds.objExists(nodeName):
        undoState = cmds.undoInfo(q=True, state=True)
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            cmds.setAttr(nodeName + ".cacheData", json.dumps(_cache[nodeName], separators=(',', ':')), type="string")
        except:
            pass
        cmds.undoInfo(stateWithoutFlush=undoState)


def _getNodeFrameRange(nodeName):
    try:
        return cmds.getAttr(nodeName + ".frameRange")
    except:
        return FRAME_RANGE


def _getNodeWindow(nodeName, cache, currentFrame):
    frameRange = _getNodeFrameRange(nodeName)
    start = cache.get("start", currentFrame)
    end = cache.get("end", currentFrame)
    winStart = max(currentFrame - frameRange, start)
    winEnd = min(currentFrame + frameRange, end)
    return winStart, winEnd


def _rebuildSourceDeferred(nodeName):
    srcObj = _trackers.get(nodeName)
    if not srcObj:
        return
    if not cmds.objExists(nodeName) or not cmds.objExists(srcObj):
        return
    cache = _cache.get(nodeName)
    if cache is None:
        _buildVisibleCache(nodeName, srcObj)
        cmds.refresh()
        return
    currentFrame = _getCurrentFrame()
    start = cache.get("start", currentFrame)
    end = cache.get("end", currentFrame)
    order = _buildFillOrder(start, end, currentFrame)
    _queueFill(nodeName, order)


def _onSourceAttrChanged(nodeName):
    mutils.executeDeferred(_rebuildSourceDeferred, nodeName)


def _onTimeChange():
    if not _trackers:
        return
    currentFrame = _getCurrentFrame()
    for nodeName, srcObj in list(_trackers.items()):
        if not cmds.objExists(nodeName) or not cmds.objExists(srcObj):
            continue
        cache = _cache.get(nodeName)
        if cache is None:
            continue
        winStart, winEnd = _getNodeWindow(nodeName, cache, currentFrame)
        order = _buildFillOrder(winStart, winEnd, currentFrame)
        positions = cache["positions"]
        missing = [f for f in order if str(f) not in positions]
        if missing:
            _queueFill(nodeName, missing)


def _checkPositions():
    global _checkJob
    _checkJob = None
    if not _trackers:
        _scheduleCheck()
        return
    currentFrame = _getCurrentFrame()
    for nodeName, srcObj in list(_trackers.items()):
        if not cmds.objExists(nodeName) or not cmds.objExists(srcObj):
            continue
        cache = _cache.get(nodeName)
        if cache is None:
            continue
        camTransform = _cameraTransforms.get(nodeName)
        currentWorldPos, currentCameraPos = _getPositionsAt(srcObj, camTransform, None)
        if not currentWorldPos:
            continue
        isDirty = False
        cachedPos = cache["positions"].get(str(currentFrame))
        if cachedPos:
            dx = abs(currentWorldPos[0] - cachedPos[0])
            dy = abs(currentWorldPos[1] - cachedPos[1])
            dz = abs(currentWorldPos[2] - cachedPos[2])
            if dx >= 0.0001 or dy >= 0.0001 or dz >= 0.0001:
                isDirty = True
        else:
            isDirty = True
        if not isDirty and camTransform and currentCameraPos is not None:
            cachedCameraPos = cache.get("cameraPositions", {}).get(str(currentFrame))
            if cachedCameraPos:
                cdx = abs(currentCameraPos[0] - cachedCameraPos[0])
                cdy = abs(currentCameraPos[1] - cachedCameraPos[1])
                cdz = abs(currentCameraPos[2] - cachedCameraPos[2])
                if cdx >= 0.0001 or cdy >= 0.0001 or cdz >= 0.0001:
                    isDirty = True
            else:
                isDirty = True
        if not isDirty:
            continue
        start = cache.get("start", currentFrame)
        end = cache.get("end", currentFrame)
        order = _buildFillOrder(start, end, currentFrame)
        _queueFill(nodeName, order)
    _scheduleCheck()


def _scheduleCheck():
    global _checkJob
    if _checkJob is None:
        _checkJob = cmds.scriptJob(event=["idle", _checkPositions], runOnce=True)


def _setupJobs():
    global _jobs
    _clearJobs()
    _jobs.append(cmds.scriptJob(event=["timeChanged", _onTimeChange], protected=True))
    _jobs.append(cmds.scriptJob(event=["SceneOpened", clear], protected=True))
    _jobs.append(cmds.scriptJob(event=["NewSceneOpened", clear], protected=True))
    _jobs.append(cmds.scriptJob(event=["Undo", _onUndoRedo], protected=True))
    _jobs.append(cmds.scriptJob(event=["Redo", _onUndoRedo], protected=True))
    _setupAttrJobs()
    _scheduleCheck()


def _hasUpstreamAnimation(objName):
    sel = om2.MSelectionList()
    try:
        sel.add(objName)
        dagPath = sel.getDagPath(0)
        node = dagPath.node()
        itDG = om2.MItDependencyGraph(node, om2.MFn.kAnimCurve, om2.MItDependencyGraph.kUpstream, om2.MItDependencyGraph.kDepthFirst, om2.MItDependencyGraph.kNodeLevel)
        if not itDG.isDone():
            return True
    except:
        pass
    try:
        conns = cmds.listConnections(objName, source=True, destination=False) or []
        for c in conns:
            try:
                nType = cmds.nodeType(c)
            except:
                continue
            if nType in ("parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "expression", "motionPath"):
                return True
    except:
        pass
    parents = cmds.listRelatives(objName, parent=True, fullPath=True) or []
    for p in parents:
        if _hasUpstreamAnimation(p):
            return True
    return False


def _onCameraTransformChanged(camTransform):
    global _cameraDirty, _cameraCheckJob
    _cameraDirty.add(camTransform)
    if _cameraCheckJob is None:
        _cameraCheckJob = cmds.scriptJob(event=["idle", _rebuildDirtyCameras], runOnce=True)


def _rebuildDirtyCameras():
    global _cameraDirty, _cameraCheckJob, _trackers, _cache, _cameraTransforms
    _cameraCheckJob = None
    dirty = _cameraDirty
    _cameraDirty = set()
    if not dirty or not _trackers:
        return
    currentFrame = _getCurrentFrame()
    for nodeName, srcObj in list(_trackers.items()):
        camTransform = _cameraTransforms.get(nodeName)
        if not camTransform or camTransform not in dirty:
            continue
        if not cmds.objExists(nodeName) or not cmds.objExists(srcObj):
            continue
        cache = _cache.get(nodeName)
        if cache is None:
            _buildVisibleCache(nodeName, srcObj)
            continue
        start = cache.get("start", currentFrame)
        end = cache.get("end", currentFrame)
        order = _buildFillOrder(start, end, currentFrame)
        _queueFill(nodeName, order)


def _setupAttrJobs():
    global _attrJobs
    _clearAttrJobs()
    camTransforms = set()
    for camTransform in _cameraTransforms.values():
        if camTransform and cmds.objExists(camTransform):
            camTransforms.add(camTransform)
    staticCamTransforms = set(ct for ct in camTransforms if not _hasUpstreamAnimation(ct))
    for camTransform in staticCamTransforms:
        try:
            cmds.getAttr(camTransform + ".worldMatrix[0]")
        except:
            pass
        try:
            job = cmds.scriptJob(
                attributeChange=[camTransform + ".worldMatrix[0]", lambda ct=camTransform: _onCameraTransformChanged(ct)],
                protected=True
            )
            _attrJobs.append(job)
        except:
            pass
    for nodeName, srcObj in _trackers.items():
        if not srcObj or not cmds.objExists(srcObj):
            continue
        try:
            cmds.getAttr(srcObj + ".worldMatrix[0]")
        except:
            pass
        try:
            job = cmds.scriptJob(
                attributeChange=[srcObj + ".worldMatrix[0]", lambda nn=nodeName: _onSourceAttrChanged(nn)],
                protected=True
            )
            _attrJobs.append(job)
        except:
            pass


def _clearAttrJobs():
    global _attrJobs, _cameraCheckJob, _cameraDirty
    for j in _attrJobs:
        try:
            if cmds.scriptJob(exists=j):
                cmds.scriptJob(kill=j, force=True)
        except:
            pass
    _attrJobs = []
    if _cameraCheckJob is not None:
        try:
            if cmds.scriptJob(exists=_cameraCheckJob):
                cmds.scriptJob(kill=_cameraCheckJob, force=True)
        except:
            pass
        _cameraCheckJob = None
    _cameraDirty = set()


def _onUndoRedo():
    global _trackers, _cache
    if not _trackers:
        return
    for nodeName, srcObj in list(_trackers.items()):
        if cmds.objExists(nodeName) and cmds.objExists(srcObj):
            _buildVisibleCache(nodeName, srcObj)
    cmds.refresh()


def _clearJobs():
    global _jobs, _checkJob
    _clearAttrJobs()
    _clearFillQueue()
    for j in _jobs:
        try:
            if cmds.scriptJob(exists=j):
                cmds.scriptJob(kill=j, force=True)
        except:
            pass
    _jobs = []
    if _checkJob is not None:
        try:
            if cmds.scriptJob(exists=_checkJob):
                cmds.scriptJob(kill=_checkJob, force=True)
        except:
            pass
        _checkJob = None


def create(objects=None):
    global _colorIndex, _trackers, _cache, _cameraTransforms
    if not _loadPlugin():
        return
    if objects is None:
        objects = cmds.ls(sl=True, long=True)
    if not objects:
        cmds.warning("Tracify: Select at least one object")
        return
    _colorIndex = 0
    camTransform = _getActiveCameraTransform() if CAMERA_SPACE else None
    cmds.waitCursor(state=True)
    try:
        if not cmds.objExists(GROUP_NAME):
            cmds.createNode("transform", name=GROUP_NAME, skipSelect=True)
            cmds.setAttr(GROUP_NAME + ".useOutlinerColor", True)
            cmds.setAttr(GROUP_NAME + ".outlinerColor", 1.0, 0.4, 0.7)
            cmds.setAttr(GROUP_NAME + ".hiddenInOutliner", True)
            for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
                cmds.setAttr(GROUP_NAME + "." + attr, lock=True, keyable=False, channelBox=False)
        for obj in objects:
            srcObj = cmds.ls(obj, long=True)[0]
            shortName = obj.lstrip("|").replace("|", "_").replace(":", "_")
            nodeName = "tracify_" + shortName
            if cmds.objExists(nodeName):
                cmds.delete(nodeName)
            _cache.pop(nodeName, None)
            _cameraTransforms.pop(nodeName, None)
            _clearParsedDrawCache(nodeName)
            node = cmds.createNode("tracifyNode", name=nodeName, parent=GROUP_NAME, skipSelect=True)
            cmds.setAttr(node + ".useOutlinerColor", True)
            cmds.setAttr(node + ".outlinerColor", 1.0, 0.4, 0.7)
            cmds.connectAttr("time1.outTime", node + ".timeInput", force=True)
            cmds.connectAttr(srcObj + ".worldMatrix[0]", node + ".sourceWorldMatrix", force=True)
            color = _getNextColor()
            cmds.setAttr(node + ".frameRange", FRAME_RANGE)
            cmds.setAttr(node + ".pointSize", POINT_SIZE)
            cmds.setAttr(node + ".lineWidth", LINE_WIDTH)
            cmds.setAttr(node + ".lineColorR", color[0])
            cmds.setAttr(node + ".lineColorG", color[1])
            cmds.setAttr(node + ".lineColorB", color[2])
            cmds.setAttr(node + ".keyColorR", KEY_COLOR[0])
            cmds.setAttr(node + ".keyColorG", KEY_COLOR[1])
            cmds.setAttr(node + ".keyColorB", KEY_COLOR[2])
            if camTransform and cmds.objExists(camTransform):
                try:
                    cmds.connectAttr(camTransform + ".worldMatrix[0]", node + ".cameraWorldMatrix", force=True)
                    cmds.setAttr(node + ".cameraSpace", True)
                    _cameraTransforms[nodeName] = camTransform
                except:
                    _cameraTransforms[nodeName] = None
            else:
                try:
                    cmds.setAttr(node + ".cameraSpace", False)
                except:
                    pass
                _cameraTransforms[nodeName] = None
            _trackers[nodeName] = srcObj
        _setupJobs()
        for panel in cmds.getPanel(type="modelPanel") or []:
            try:
                cmds.modelEditor(panel, edit=True, locators=True)
            except:
                pass
        cmds.select(objects)
        _initTrackers()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        cmds.waitCursor(state=False)


def _initTrackers():
    for nodeName, srcObj in list(_trackers.items()):
        if cmds.objExists(nodeName) and cmds.objExists(srcObj):
            _buildVisibleCache(nodeName, srcObj)
    cmds.refresh()


def _clearParsedDrawCache(nodeName=None):
    mod = sys.modules.get("tracify_node")
    if mod is None:
        return
    try:
        if nodeName is None:
            mod._parsedCacheStore.clear()
        else:
            mod._parsedCacheStore.pop(nodeName, None)
    except:
        pass


def clear():
    global _trackers, _cache, _cameraTransforms
    cmds.waitCursor(state=True)
    try:
        _clearJobs()
        _trackers = {}
        _cache = {}
        _cameraTransforms = {}
        for grp in cmds.ls("tracify_grp_*", type="transform") or []:
            if cmds.objExists(grp):
                try:
                    cmds.delete(grp)
                except:
                    pass
        if cmds.objExists(GROUP_NAME):
            cmds.delete(GROUP_NAME)
        if _isPluginLoaded():
            for node in cmds.ls(type="tracifyNode") or []:
                if cmds.objExists(node):
                    cmds.delete(node)
        _clearParsedDrawCache()
        cmds.refresh()
    finally:
        cmds.waitCursor(state=False)


def toggle(objects=None):
    cmds.undoInfo(openChunk=True, chunkName="Tracify")
    try:
        if cmds.objExists(GROUP_NAME) or (cmds.ls(type="tracifyNode") if _isPluginLoaded() else False):
            clear()
        else:
            create(objects)
    finally:
        cmds.undoInfo(closeChunk=True)


def refresh():
    global _trackers, _cache, _cameraTransforms
    if not _isPluginLoaded():
        return
    _trackers = {}
    _cache = {}
    _cameraTransforms = {}
    validEntries = []
    for nodeName in cmds.ls(type="tracifyNode") or []:
        if not cmds.objExists(nodeName):
            continue
        conns = cmds.listConnections(nodeName + ".sourceWorldMatrix", source=True, destination=False) or []
        if conns:
            srcObj = cmds.ls(conns[0], long=True)
            if srcObj and cmds.objExists(srcObj[0]):
                validEntries.append((nodeName, srcObj[0]))
    for nodeName, srcObj in validEntries:
        _trackers[nodeName] = srcObj
        camEnabled = False
        try:
            camEnabled = cmds.getAttr(nodeName + ".cameraSpace")
        except:
            camEnabled = False
        camTransform = None
        if camEnabled:
            camConns = cmds.listConnections(nodeName + ".cameraWorldMatrix", source=True, destination=False) or []
            if camConns:
                camList = cmds.ls(camConns[0], long=True)
                if camList and cmds.objExists(camList[0]):
                    camTransform = camList[0]
        _cameraTransforms[nodeName] = camTransform
        _buildVisibleCache(nodeName, srcObj)
    if _trackers:
        _setupJobs()
    cmds.refresh()


def reinit():
    refresh()


def setRange(value):
    global FRAME_RANGE
    FRAME_RANGE = value
    if not _isPluginLoaded():
        return
    currentFrame = _getCurrentFrame()
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".frameRange", value)
        srcObj = _trackers.get(node)
        cache = _cache.get(node)
        if srcObj and cache and cmds.objExists(srcObj):
            winStart, winEnd = _getNodeWindow(node, cache, currentFrame)
            order = _buildFillOrder(winStart, winEnd, currentFrame)
            positions = cache["positions"]
            missing = [f for f in order if str(f) not in positions]
            if missing:
                _queueFill(node, missing)
    cmds.refresh()


def setPointSize(value):
    global POINT_SIZE
    POINT_SIZE = value
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".pointSize", value)
    cmds.refresh()


def setLineWidth(value):
    global LINE_WIDTH
    LINE_WIDTH = value
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".lineWidth", value)
    cmds.refresh()


def setColorMode(mode):
    if not _isPluginLoaded():
        return
    for node in cmds.ls(type="tracifyNode") or []:
        cmds.setAttr(node + ".colorMode", mode)
    cmds.refresh()


def setRainbowMode(enabled):
    setColorMode(1 if enabled else 0)


def setCameraSpace(enabled):
    global CAMERA_SPACE, _cameraTransforms, _cache
    CAMERA_SPACE = bool(enabled)
    if not _isPluginLoaded():
        return
    targetCamera = _getActiveCameraTransform() if CAMERA_SPACE else None
    currentFrame = _getCurrentFrame()
    for nodeName in cmds.ls(type="tracifyNode") or []:
        if not cmds.objExists(nodeName):
            continue
        if not CAMERA_SPACE or not targetCamera or not cmds.objExists(targetCamera):
            try:
                cmds.setAttr(nodeName + ".cameraSpace", False)
            except:
                pass
            existingConns = cmds.listConnections(nodeName + ".cameraWorldMatrix", source=True, destination=False, plugs=True) or []
            for conn in existingConns:
                try:
                    cmds.disconnectAttr(conn, nodeName + ".cameraWorldMatrix")
                except:
                    pass
            _cameraTransforms[nodeName] = None
            cache = _cache.get(nodeName)
            if cache is not None:
                cache["cameraPositions"] = {}
                cache["cameraTransform"] = None
            continue
        assignedCamera = _cameraTransforms.get(nodeName)
        cache = _cache.get(nodeName)
        hasCameraCache = bool(cache and cache.get("cameraPositions"))
        if assignedCamera != targetCamera:
            existingConns = cmds.listConnections(nodeName + ".cameraWorldMatrix", source=True, destination=False, plugs=True) or []
            for conn in existingConns:
                try:
                    cmds.disconnectAttr(conn, nodeName + ".cameraWorldMatrix")
                except:
                    pass
            try:
                cmds.connectAttr(targetCamera + ".worldMatrix[0]", nodeName + ".cameraWorldMatrix", force=True)
            except:
                pass
            _cameraTransforms[nodeName] = targetCamera
            hasCameraCache = False
        try:
            cmds.setAttr(nodeName + ".cameraSpace", True)
        except:
            pass
        if not hasCameraCache:
            srcObj = _trackers.get(nodeName)
            if srcObj is None:
                conns = cmds.listConnections(nodeName + ".sourceWorldMatrix", source=True, destination=False) or []
                if conns:
                    srcList = cmds.ls(conns[0], long=True)
                    if srcList:
                        srcObj = srcList[0]
            if srcObj and cmds.objExists(srcObj):
                cache = _cache.get(nodeName)
                if cache is None:
                    _buildVisibleCache(nodeName, srcObj)
                else:
                    winStart, winEnd = _getNodeWindow(nodeName, cache, currentFrame)
                    order = _buildFillOrder(winStart, winEnd, currentFrame)
                    _queueFill(nodeName, order)
    _setupAttrJobs()
    cmds.refresh()


r = refresh
t = toggle