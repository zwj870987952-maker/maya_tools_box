import maya.cmds as cmds


def select_objects_in_selected_anim_layer():
    selected_anim_layers = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)
    if not selected_anim_layers:
        return
    objects = []
    for anim_layer in selected_anim_layers:
        anim_layer_attrs = cmds.animLayer(anim_layer, query=True, attribute=True)
        if anim_layer_attrs:
            for attr in anim_layer_attrs:
                obj = attr.split('.')[0]
                objects.append(obj)
    if objects:
        objects = list(set(objects))
        cmds.select(objects)


cmds.undoInfo(openChunk=True)
try:
    select_objects_in_selected_anim_layer()
except Exception:
    pass
finally:
    cmds.undoInfo(closeChunk=True)
