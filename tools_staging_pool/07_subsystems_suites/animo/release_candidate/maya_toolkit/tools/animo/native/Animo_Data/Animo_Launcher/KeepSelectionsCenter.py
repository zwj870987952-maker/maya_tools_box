from maya import cmds
import math

ANCHOR_DATA_NODE = "pivotAnchorDataHolder"

def terminateWatchers():
    if not cmds.objExists(ANCHOR_DATA_NODE):
        return
    
    try:
        watcherStr = cmds.getAttr("{}.watcherIds".format(ANCHOR_DATA_NODE))
        if watcherStr:
            watcherList = [int(x) for x in watcherStr.split(',') if x.strip()]
            
            for wid in watcherList:
                if cmds.scriptJob(exists=wid):
                    cmds.scriptJob(kill=wid)
        
        cmds.setAttr("{}.watcherIds".format(ANCHOR_DATA_NODE), "", type="string")
    except:
        pass

def persistWatcherIds(idList):
    if not cmds.objExists(ANCHOR_DATA_NODE):
        cmds.createNode("network", name=ANCHOR_DATA_NODE)
        cmds.addAttr(ANCHOR_DATA_NODE, longName="watcherIds", dataType="string")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="cachedRotateMode", attributeType="bool")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="modeEngaged", attributeType="bool")
    
    idStr = ','.join(str(x) for x in idList)
    cmds.setAttr("{}.watcherIds".format(ANCHOR_DATA_NODE), idStr, type="string")

def checkPivotModeState():
    if not cmds.objExists(ANCHOR_DATA_NODE):
        return False
    
    try:
        return cmds.getAttr("{}.modeEngaged".format(ANCHOR_DATA_NODE))
    except:
        return False

def updatePivotModeState(engaged):
    if not cmds.objExists(ANCHOR_DATA_NODE):
        cmds.createNode("network", name=ANCHOR_DATA_NODE)
        cmds.addAttr(ANCHOR_DATA_NODE, longName="watcherIds", dataType="string")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="cachedRotateMode", attributeType="bool")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="modeEngaged", attributeType="bool")
    
    cmds.setAttr("{}.modeEngaged".format(ANCHOR_DATA_NODE), engaged)

def cacheDefaultRotation(val):
    if not cmds.objExists(ANCHOR_DATA_NODE):
        cmds.createNode("network", name=ANCHOR_DATA_NODE)
        cmds.addAttr(ANCHOR_DATA_NODE, longName="watcherIds", dataType="string")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="cachedRotateMode", attributeType="bool")
        cmds.addAttr(ANCHOR_DATA_NODE, longName="modeEngaged", attributeType="bool")
    
    cmds.setAttr("{}.cachedRotateMode".format(ANCHOR_DATA_NODE), val)

def fetchDefaultRotation():
    if not cmds.objExists(ANCHOR_DATA_NODE):
        return None
    
    try:
        return cmds.getAttr("{}.cachedRotateMode".format(ANCHOR_DATA_NODE))
    except:
        return None

def calculateScaleFactor():
    scaleMap = {
        "mm": 0.1,
        "cm": 1.0,
        "m": 100.0,
        "in": 2.54,
        "ft": 30.48,
        "yd": 91.44
    }
    
    activeUnit = cmds.currentUnit(query=True, linear=True)
    return scaleMap.get(activeUnit, 1.0)

def refreshCameraAnchor():
    picked = cmds.ls(selection=True)
    
    if not picked:
        return
    
    targetObj = picked[-1]
    validTypes = ["transform", "joint"]
    
    if cmds.nodeType(targetObj) not in validTypes:
        return
    
    scaleFactor = calculateScaleFactor()
    
    meshDescendants = cmds.listRelatives(targetObj, allDescendents=True, 
                                         noIntermediate=True, type="mesh")
    hasMesh = meshDescendants is not None
    
    if hasMesh:
        bounds = cmds.xform(targetObj, query=True, boundingBox=True, ws=True)
        px = (bounds[0] + bounds[3]) / 2.0
        py = (bounds[1] + bounds[4]) / 2.0
        pz = (bounds[2] + bounds[5]) / 2.0
    else:
        coords = cmds.xform(targetObj, query=True, ws=True, rotatePivot=True)
        px, py, pz = coords[0], coords[1], coords[2]
    
    px *= scaleFactor
    py *= scaleFactor
    pz *= scaleFactor
    
    allCameras = cmds.ls(dag=True, cameras=True)
    
    cmds.undoInfo(stateWithoutFlush=False)
    
    for cam in allCameras:
        try:
            cmds.setAttr("{}.tumblePivot".format(cam), px, py, pz)
        except:
            pass
    
    cmds.undoInfo(stateWithoutFlush=True)

def activateCenterPivot():
    savedMode = cmds.tumbleCtx("tumbleContext", query=True, localTumble=True)
    cacheDefaultRotation(savedMode)
    
    cmds.tumbleCtx("tumbleContext", edit=True, localTumble=0)
    
    w1 = cmds.scriptJob(runOnce=False, killWithScene=False, 
                        event=('DragRelease', refreshCameraAnchor))
    w2 = cmds.scriptJob(runOnce=False, killWithScene=False, 
                        event=('SelectionChanged', refreshCameraAnchor))
    w3 = cmds.scriptJob(runOnce=False, killWithScene=False, 
                        event=('timeChanged', refreshCameraAnchor))
    
    persistWatcherIds([w1, w2, w3])
    updatePivotModeState(True)
    
    refreshCameraAnchor()

def deactivateCenterPivot():
    terminateWatchers()
    
    savedMode = fetchDefaultRotation()
    if savedMode is not None:
        cmds.tumbleCtx("tumbleContext", edit=True, localTumble=savedMode)
    
    updatePivotModeState(False)

def switchPivotBehavior():
    if checkPivotModeState():
        deactivateCenterPivot()
    else:
        activateCenterPivot()

if __name__ == "__main__":
    switchPivotBehavior()
else:
    switchPivotBehavior()