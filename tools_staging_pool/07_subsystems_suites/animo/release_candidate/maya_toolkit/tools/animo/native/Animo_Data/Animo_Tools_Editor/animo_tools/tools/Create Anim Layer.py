import maya.cmds as cmds
import maya.mel as mel
import sys


def create_simple_anim_layer():
    sel = cmds.ls(sl=True)

    if sel:
        root_layer = cmds.animLayer(query=True, root=True) or []
        animLayers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []
        cmds.waitCursor(state=True)
        animLayerName = cmds.animLayer("animLayer", selected=True)
        for layer in animLayers:
            mel.eval('animLayerEditorOnSelect {0} 0;'.format(layer))

        min = cmds.playbackOptions(q=True, ast=True)
        max = cmds.playbackOptions(q=True, aet=True)

        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        StartRange = timeRange[0]
        EndRange = timeRange[1] - 1
        StartRange = int(StartRange)
        EndRange = int(EndRange)
        attrs = cmds.listAnimatable()

        for attr in attrs:
            cmds.animLayer(animLayerName, e=True, attribute=attr)
        cmds.waitCursor(state=False)

    else:
        cmds.confirmDialog(title="Error", message="Please select something!")


create_simple_anim_layer()
