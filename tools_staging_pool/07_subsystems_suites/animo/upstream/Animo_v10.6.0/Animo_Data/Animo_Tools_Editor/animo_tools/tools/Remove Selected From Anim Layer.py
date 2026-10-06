import maya.cmds as cmds


def remove_selected_from_anim_layer():
    sel = cmds.ls(sl=True)

    if sel:
        try:
            animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)[0]
            attrs = cmds.listAnimatable()

            for attr in attrs:
                cmds.animLayer(animLayerName, e=True, removeAttribute=attr)
        except:
            pass


remove_selected_from_anim_layer()
