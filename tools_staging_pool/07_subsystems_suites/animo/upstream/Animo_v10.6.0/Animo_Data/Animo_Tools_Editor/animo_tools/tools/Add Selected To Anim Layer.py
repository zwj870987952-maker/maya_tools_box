import maya.cmds as cmds


def add_selected_to_anim_layer():
    sel = cmds.ls(sl=True)

    if sel:
        try:
            animLayerName = cmds.treeView("AnimLayerTabanimLayerEditor", q=True, selectItem=True)[0]
            attrs = cmds.listAnimatable()

            for attr in attrs:
                cmds.animLayer(animLayerName, e=True, attribute=attr)
        except:
            pass


add_selected_to_anim_layer()
