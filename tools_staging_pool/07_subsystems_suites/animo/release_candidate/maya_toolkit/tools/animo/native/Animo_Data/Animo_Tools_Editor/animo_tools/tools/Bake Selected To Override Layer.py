import maya.cmds as cmds
import maya.mel as mel


def bake_selected_to_override_layer():
    sel = cmds.ls(sl=True)

    if not sel:
        cmds.confirmDialog(title="Error", message="Please select something!")
        return

    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = int(timeRange[0])
    EndRange = int(timeRange[1] - 1)

    if (EndRange - StartRange == 0):
        StartRange = cmds.playbackOptions(q=True, ast=True)
        EndRange = cmds.playbackOptions(q=True, aet=True)

    root_layer = cmds.animLayer(query=True, root=True) or []
    animLayers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []

    animLayerName = cmds.animLayer("animLayer", selected=True, override=True)

    for layer in animLayers:
        mel.eval('animLayerEditorOnSelect {0} 0;'.format(layer))

    eval_mode = cmds.evaluationManager(q=True, mode=True)

    try:
        cmds.waitCursor(state=True)
        cmds.refresh(suspend=True)
        cmds.evaluationManager(mode="off")

        cmds.bakeResults(sel, t=(StartRange, EndRange), sm=True, pok=True, destinationLayer=animLayerName)
    finally:
        cmds.waitCursor(state=False)
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode=eval_mode[0])


bake_selected_to_override_layer()
