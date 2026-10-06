import maya.cmds as cmds


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


cmds.undoInfo(openChunk=True)
try:
    add_selected_to_anim_layer()
except Exception:
    pass
finally:
    cmds.undoInfo(closeChunk=True)
