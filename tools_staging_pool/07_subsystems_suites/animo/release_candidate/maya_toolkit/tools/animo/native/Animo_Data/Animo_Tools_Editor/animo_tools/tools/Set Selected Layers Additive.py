import maya.cmds as cmds


def get_selected_anim_layers():
    root_layer = cmds.animLayer(q=True, root=True)
    selected_anim_layer = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True) or []

    if root_layer in selected_anim_layer:
        selected_anim_layer.remove(root_layer)

    if not selected_anim_layer:
        raise ValueError("Please select an animation layer")

    return selected_anim_layer


def set_selected_layers_additive():
    try:
        selectedLayers = get_selected_anim_layers()
    except ValueError as e:
        cmds.confirmDialog(title="Error", message=str(e))
        return

    for layer in selectedLayers:
        cmds.setAttr(layer + ".override", 0)

    cmds.inViewMessage(amg="Layers set to <hl>Additive</hl>", pos="topCenter", fade=True)


set_selected_layers_additive()
