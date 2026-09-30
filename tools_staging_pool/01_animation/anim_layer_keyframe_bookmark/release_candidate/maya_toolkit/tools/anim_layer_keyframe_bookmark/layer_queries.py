"""Read-only layer-frame discovery and explicit per-frame command execution."""
import math
import maya.cmds as cmds


def get_scene_anim_layers():
    layers = cmds.ls(type='animLayer') or []
    return sorted(layers, key=lambda name: (name != 'BaseAnimation', name))


def get_active_anim_layer():
    if not cmds.about(batch=True) and cmds.treeView('AnimLayerTabanimLayerEditor', exists=True):
        selected = cmds.treeView('AnimLayerTabanimLayerEditor', query=True, selectItem=True) or []
        if selected and selected[0] in get_scene_anim_layers():
            return selected[0]
    selected = [layer for layer in get_scene_anim_layers() if cmds.animLayer(layer, query=True, selected=True)]
    return next((layer for layer in selected if layer != 'BaseAnimation'), 'BaseAnimation')


def get_layer_curves_for_objects(objects, layer_name):
    """Exact-plug lookup only; Base has a direct fallback only in layerless scenes."""
    result = set()
    layers = get_scene_anim_layers()
    for obj in objects:
        for plug in cmds.listAnimatable(obj) or []:
            if layer_name in layers:
                curves = cmds.animLayer(layer_name, query=True, findCurveForPlug=plug) or []
                if isinstance(curves, str):
                    curves = [curves]
            elif layer_name == 'BaseAnimation' and not layers:
                curves = cmds.listConnections(plug, source=True, destination=False, type='animCurve') or []
            else:
                curves = []
            for curve in curves:
                if cmds.objExists(curve) and cmds.nodeType(curve) in ('animCurveTA', 'animCurveTL', 'animCurveTU', 'animCurveTT'):
                    result.add(curve)
    return sorted(result)


def get_keyframes_from_layer(objects, layer='auto', only_in_playback=True):
    target_layer = get_active_anim_layer() if layer == 'auto' else layer
    layers = get_scene_anim_layers()
    if target_layer not in ('BaseAnimation', 'All') and target_layer not in layers:
        raise ValueError('Unknown animation layer: ' + target_layer)
    selected_layers = (layers or ['BaseAnimation']) if target_layer == 'All' else [target_layer]
    curves = sorted({c for layer_name in selected_layers for c in get_layer_curves_for_objects(objects, layer_name)})
    query = dict(query=True, timeChange=True)
    if only_in_playback:
        bounds = (float(cmds.playbackOptions(query=True, minTime=True)), float(cmds.playbackOptions(query=True, maxTime=True)))
        if not all(math.isfinite(t) for t in bounds) or bounds[0] > bounds[1]:
            raise ValueError('Invalid playback range')
        query['time'] = bounds
    times = cmds.keyframe(curves, **query) if curves else []
    if not all(math.isfinite(t) for t in times or []):
        raise ValueError('Non-finite keyframe time')
    unique = []
    for time in sorted({round(float(t), 4) for t in times or []}):
        if not unique or time != unique[-1]:
            unique.append(time)
    return unique, target_layer, curves
