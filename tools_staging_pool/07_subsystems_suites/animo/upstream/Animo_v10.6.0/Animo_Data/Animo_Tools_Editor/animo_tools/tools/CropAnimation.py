import maya.cmds as cmds
import maya.mel as mel
import builtins

try:
    int = builtins.int
except:
    pass


def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
        return False
    except:
        return False


def get_graph_editor_selection():
    if not is_graph_editor_active():
        return None

    selected_keys = cmds.keyframe(q=True, sl=True)
    if not selected_keys:
        return None

    if not isinstance(selected_keys, (list, tuple)):
        selected_keys = [selected_keys]

    sorted_keys = sorted(selected_keys)
    startRange = int(sorted_keys[0])
    endRange = int(sorted_keys[-1])

    if endRange - startRange <= 0:
        return None

    objects = cmds.ls(selection=True) or []
    plugs = []

    for obj in objects:
        attrs = cmds.listAttr(obj, keyable=True, scalar=True) or []
        for attr in attrs:
            plug = obj + '.' + attr
            try:
                attr_keys = cmds.keyframe(plug, q=True, sl=True)
            except:
                attr_keys = None
            if attr_keys:
                plugs.append(plug)

    if not plugs:
        return None

    return startRange, endRange, plugs


def get_timeline_range():
    try:
        playBackSlider = mel.eval('$tmp=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, q=True, rangeArray=True)
    except:
        timeRange = None

    if timeRange is None:
        return None

    startRange = int(timeRange[0])
    endRange = int(timeRange[1]) - 1

    if endRange - startRange > 0:
        return startRange, endRange
    return None


def crop_plugs(plugs, startRange, endRange):
    ct = cmds.currentTime(q=True)

    cmds.waitCursor(state=True)
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)

    try:
        cmds.selectKey(clear=True)
    except:
        pass

    cmds.currentTime(startRange)
    cmds.setKeyframe(plugs, insert=True)
    cmds.currentTime(endRange)
    cmds.setKeyframe(plugs, insert=True)

    cmds.cutKey(plugs, time=(-999999, startRange - 1))
    cmds.cutKey(plugs, time=(endRange + 1, 999999))

    cmds.currentTime(ct)

    try:
        cmds.selectKey(plugs, replace=True)
    except:
        pass

    cmds.waitCursor(state=False)
    cmds.evaluationManager(mode="parallel")
    cmds.refresh(suspend=False)


def crop_objects(startRange, endRange):
    ct = cmds.currentTime(q=True)

    cmds.waitCursor(state=True)
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)

    try:
        cmds.selectKey(clear=True)
    except:
        pass

    cmds.currentTime(startRange)
    cmds.setKeyframe(insert=True)
    cmds.currentTime(endRange)
    cmds.setKeyframe(insert=True)

    cmds.cutKey(time=(-999999, startRange - 1))
    cmds.cutKey(time=(endRange + 1, 999999))

    cmds.currentTime(ct)

    cmds.waitCursor(state=False)
    cmds.evaluationManager(mode="parallel")
    cmds.refresh(suspend=False)


def crop_animation():
    graph_selection = get_graph_editor_selection()

    if graph_selection:
        startRange, endRange, plugs = graph_selection
        crop_plugs(plugs, startRange, endRange)
        return

    cropRange = get_timeline_range()
    if cropRange is None:
        return

    startRange, endRange = cropRange
    crop_objects(startRange, endRange)


crop_animation()