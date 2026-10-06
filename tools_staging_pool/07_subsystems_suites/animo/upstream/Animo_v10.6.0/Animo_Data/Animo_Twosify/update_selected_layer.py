import maya.cmds as cmds
import maya.mel as mel


def add_selected_to_anim_layer():
    sel = cmds.ls(sl=True)
    if sel:
        try:
            animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)[0]
            attrs = cmds.listAnimatable()
            for attr in attrs:
                cmds.animLayer(animLayerName, e=True, attribute=attr)
        except Exception:
            pass


def convert_to_twos():
    animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
    if animLayerName:
        animLayerName = animLayerName[0]
    else:
        return
    rootLayer = cmds.animLayer(q=True, root=True)
    animLayers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
    min_time = cmds.playbackOptions(q=True, min=True)
    max_time = cmds.playbackOptions(q=True, max=True)
    sel = cmds.ls(sl=True)
    try:
        cmds.selectKey(cl=True)
    except Exception:
        pass
    if sel:
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        StartRange = timeRange[0]
        EndRange = timeRange[1] - 1
        StartRange = int(StartRange)
        EndRange = int(EndRange)
        if (EndRange - StartRange == 0):
            if animLayers[0] == rootLayer:
                cmds.confirmDialog(title='Error', message='Please make sure to have an animLayer selected!', button="Got it!")
            else:
                cmds.animLayer(animLayerName, edit=True, override=True)
                cmds.animLayer(animLayerName, e=True, weight=0)
                curTime = cmds.currentTime(q=True)
                keys = cmds.keyframe(q=True, t=(min_time, max_time))
                if keys:
                    cmds.waitCursor(state=True)
                    keys = list(set(keys))
                    keys.sort()
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.setKeyframe()
                    cmds.currentTime(curTime)
                    cmds.refresh(suspend=False)
                    cmds.animLayer(animLayerName, e=True, weight=1)
                    cmds.keyTangent(ott="step", itt="auto")
                    cmds.waitCursor(state=False)
                else:
                    cmds.confirmDialog(title='Error', message='Please set some keys!', button="Got it!")
        else:
            if animLayers[0] == rootLayer:
                cmds.confirmDialog(title='Error', message='Please make sure to have an animLayer selected!', button="Got it!")
            else:
                cmds.animLayer(animLayerName, edit=True, override=True)
                cmds.animLayer(animLayerName, e=True, weight=0)
                curTime = cmds.currentTime(q=True)
                keys = cmds.keyframe(q=True, t=(StartRange, EndRange))
                if keys:
                    cmds.waitCursor(state=True)
                    keys = list(set(keys))
                    keys.sort()
                    for key in keys:
                        cmds.currentTime(key)
                        cmds.setKeyframe()
                    cmds.currentTime(curTime)
                    cmds.refresh(suspend=False)
                    cmds.animLayer(animLayerName, e=True, weight=1)
                    cmds.keyTangent(ott="step", itt="step")
                    cmds.waitCursor(state=False)
                else:
                    cmds.confirmDialog(title='Error', message='Please set some keys!', button="Got it!")
    else:
        cmds.confirmDialog(title='Error', message='Please select something!', button="Got it!")


cmds.undoInfo(openChunk=True)
try:
    add_selected_to_anim_layer()
    convert_to_twos()
except Exception:
    pass
finally:
    cmds.undoInfo(closeChunk=True)
