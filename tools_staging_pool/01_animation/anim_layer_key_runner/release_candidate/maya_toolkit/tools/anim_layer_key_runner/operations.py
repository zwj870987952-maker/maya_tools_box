"""Read-only layer-frame discovery and explicit per-frame command execution."""
import math
import sys
import maya.cmds as cmds
import maya.mel as mel


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
        if not unique or abs(time - unique[-1]) > 0.001:
            unique.append(time)
    return unique, target_layer, curves


def run_frames(objects, frames, layer, command, language, continue_on_error=True):
    """Execute explicitly supplied code; no claim that arbitrary code is undoable."""
    original_time = cmds.currentTime(query=True)
    original_selection = cmds.ls(selection=True, long=True) or []
    selection_ids = [(item, None if '.' in item else (cmds.ls(item, uuid=True) or [None])[0]) for item in original_selection]
    # Resolve renamed targets between frames. Commands cannot mutate the scheduler's list.
    identities = [cmds.ls(obj, uuid=True)[0] for obj in objects]
    scheduled = tuple(frames)
    errors, completed = [], []
    namespace = dict(cmds=cmds, mel=mel, sys=sys, frames=list(scheduled), layer=layer,
                     resolved_layer=layer, command=command, language=language,
                     __name__='anim_layer_key_runner_command')
    compiled = compile(command, '<anim_layer_key_runner command>', 'exec') if language == 'python' else None
    try:
        for frame in scheduled:
            try:
                live_objects = []
                for identity in identities:
                    nodes = cmds.ls(identity, long=True) or []
                    if len(nodes) != 1:
                        raise RuntimeError('Target was deleted or no longer resolves uniquely')
                    live_objects.append(nodes[0])
                cmds.currentTime(frame, edit=True)
                cmds.select(live_objects, replace=True)
                namespace.update(f=frame, frame=frame, objects=list(live_objects))
                if language == 'python':
                    exec(compiled, namespace, namespace)
                else:
                    mel.eval(command)
                completed.append(frame)
            except Exception as error:
                errors.append({'frame': frame, 'error': str(error)})
                if not continue_on_error:
                    break
    finally:
        try:
            cmds.currentTime(original_time, edit=True)
        except Exception as error:
            errors.append({'stage': 'restore_time', 'error': str(error)})
        try:
            surviving = []
            for name, identity in selection_ids:
                nodes = cmds.ls(identity, long=True) or [] if identity else []
                if nodes:
                    surviving.append(nodes[0])
                elif cmds.objExists(name):
                    surviving.append(name)
            cmds.select(surviving, replace=True) if surviving else cmds.select(clear=True)
        except Exception as error:
            errors.append({'stage': 'restore_selection', 'error': str(error)})
    return dict(layer=layer, frames=list(scheduled), completed_frames=completed,
                count=len(completed), total=len(scheduled), errors=errors)
