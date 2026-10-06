import maya.cmds as cmds
import maya.mel as mel
import sys

Min = cmds.playbackOptions(q=True, min=True)
Max = cmds.playbackOptions(q=True, max=True)
pnl = cmds.getPanel(up=True)
curveSel = cmds.keyframe(q=True, sl=True)
selCurve = cmds.keyframe(q=True, selected=True)

if pnl == 'graphEditor1':
    if selCurve:
        mel.eval('bakeResults -sampleBy 1 -oversamplingRate 1 -preserveOutsideKeys 1 -sparseAnimCurveBake 0;')

else:
    if selCurve:
        cmds.selectKey(cl=True)
    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = timeRange[0]
    EndRange = timeRange[1] - 1
    StartRange = int(StartRange)
    EndRange = int(EndRange)
    selection = cmds.ls(sl=True)
    
    if selection:
        cmds.waitCursor(state=True)
        cmds.refresh(suspend=True)
        cmds.evaluationManager(mode="off")
        CBsel = cmds.channelBox("mainChannelBox", q=True, sma=True)
        mods = cmds.getModifiers()
    
        if CBsel:
            if EndRange-StartRange==0:
                cmds.bakeResults(sm=True, pok=True, t=(Min, Max), at=CBsel, sb="1")
            else:
                cmds.bakeResults(sm=True, pok=True, t=(StartRange, EndRange), at=CBsel, sb="1")
        else:
            if EndRange-StartRange==0:
                cmds.bakeResults(sm=True, pok=True, t=(Min, Max), sb="1")
            else:
                cmds.bakeResults(sm=True, pok=True, t=(StartRange, EndRange), sb="1")
        cmds.waitCursor(state=False)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode="parallel")
        mel.eval("paneLayout -e -manage true $gMainPane")