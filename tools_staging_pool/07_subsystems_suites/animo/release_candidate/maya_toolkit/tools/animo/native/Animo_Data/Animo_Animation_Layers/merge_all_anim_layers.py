import maya.cmds as cmds
import maya.mel as mel


def get_time_range():
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start_range = int(time_range[0])
    end_range = int(time_range[1] - 1)
    return start_range, end_range


def get_frame_range():
    shot_nodes = cmds.ls(type='shot')
    start_time = cmds.playbackOptions(query=True, animationStartTime=True)
    end_time = cmds.playbackOptions(query=True, animationEndTime=True)
    
    if shot_nodes:
        for shot_node in shot_nodes:
            start_frame = cmds.getAttr(shot_node + '.startFrame')
            if start_frame <= start_time:
                start_time = start_frame
            end_frame = cmds.getAttr(shot_node + '.endFrame')
            if end_frame >= end_time:
                end_time = end_frame
    
    return start_time, end_time


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


def merge_all_anim_layers():
    anim_layers = cmds.ls(type='animLayer')
    
    if 'BaseAnimation' in anim_layers:
        anim_layers.remove('BaseAnimation')
    
    if not anim_layers:
        return
    
    objects_to_bake = get_objects_from_anim_layers(anim_layers)
    
    if not objects_to_bake:
        return
    
    start_range, end_range = get_time_range()
    start_time, end_time = get_frame_range()
    
    cmds.refresh(suspend=True)
    cmds.evaluationManager(mode='off')
    
    try:
        if end_range - start_range == 0:
            cmds.bakeResults(
                objects_to_bake,
                time=(start_time, end_time),
                simulation=True,
                animation='keysOrObjects',
                removeBakedAttributeFromLayer=True,
                preserveOutsideKeys=True
            )
        else:
            cmds.bakeResults(
                objects_to_bake,
                time=(start_range, end_range),
                simulation=True,
                animation='keysOrObjects',
                removeBakedAttributeFromLayer=True,
                preserveOutsideKeys=True
            )
        
        cmds.delete(anim_layers)
        
        root_layer = cmds.animLayer(query=True, root=True)
        if root_layer:
            cmds.delete(root_layer)
    
    except Exception:
        pass
    
    finally:
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode='parallel')


merge_all_anim_layers()
