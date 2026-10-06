import maya.cmds as cmds
import maya.mel as mel


def get_time_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return start_range, end_range


def get_selected_anim_layers():
    root_layer = cmds.animLayer(query=True, root=True)
    selected_layers = cmds.treeView('AnimLayerTabanimLayerEditor', query=True, selectItem=True) or []
    
    if root_layer in selected_layers:
        selected_layers.remove(root_layer)
    
    return selected_layers


def get_objects_from_anim_layers(anim_layers):
    objects = []
    for anim_layer in anim_layers:
        attributes = cmds.animLayer(anim_layer, query=True, attribute=True)
        if attributes:
            for attr in attributes:
                obj = attr.split('.')[0]
                if obj not in objects:
                    objects.append(obj)
    return objects


def smart_merge_selected_anim_layers():
    root_layer = cmds.animLayer(query=True, root=True)
    selected_layers = get_selected_anim_layers()
    
    if not selected_layers:
        return
    
    muted_layers = []
    for layer in selected_layers[:]:
        if cmds.animLayer(layer, query=True, mute=True):
            muted_layers.append(layer)
            selected_layers.remove(layer)
    
    if muted_layers:
        cmds.delete(muted_layers)
    
    if not selected_layers:
        return
    
    objects_to_bake = get_objects_from_anim_layers(selected_layers)
    
    if not objects_to_bake:
        return
    
    cmds.select(objects_to_bake)
    
    all_anim_layers = cmds.ls(type='animLayer')
    if root_layer in all_anim_layers:
        all_anim_layers.remove(root_layer)
    if 'BaseAnimation' in all_anim_layers:
        all_anim_layers.remove('BaseAnimation')
    
    layers_on = []
    for layer in all_anim_layers:
        if not cmds.animLayer(layer, query=True, mute=True):
            layers_on.append(layer)
    
    for layer in selected_layers:
        if layer in layers_on:
            layers_on.remove(layer)
    
    non_selected_layers = [layer for layer in all_anim_layers if layer not in selected_layers]
    
    for layer in selected_layers:
        cmds.animLayer(layer, edit=True, selected=True)
    
    if root_layer:
        cmds.animLayer(root_layer, edit=True, selected=False)
    
    for layer in non_selected_layers:
        cmds.animLayer(layer, edit=True, mute=True)
    
    start_range, end_range = get_time_range()
    min_time = cmds.playbackOptions(query=True, animationStartTime=True)
    max_time = cmds.playbackOptions(query=True, animationEndTime=True)
    
    cmds.refresh(suspend=True)
    cmds.evaluationManager(mode='off')
    
    try:
        if end_range - start_range == 0:
            cmds.bakeResults(
                simulation=True,
                preserveOutsideKeys=True,
                smart=(True,),
                time=(min_time, max_time)
            )
        else:
            cmds.bakeResults(
                simulation=True,
                preserveOutsideKeys=True,
                smart=(True,),
                time=(start_range, end_range)
            )
    
    except Exception:
        pass
    
    finally:
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode='parallel')
        
        for layer in non_selected_layers:
            if cmds.objExists(layer):
                cmds.animLayer(layer, edit=True, mute=False, lock=False)
        
        for layer in layers_on:
            if cmds.objExists(layer):
                cmds.animLayer(layer, edit=True, mute=False, lock=False)
        
        for layer in selected_layers:
            if cmds.objExists(layer):
                cmds.delete(layer)


smart_merge_selected_anim_layers()
