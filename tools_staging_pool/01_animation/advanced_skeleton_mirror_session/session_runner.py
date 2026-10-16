"""Session-only AS 5.740 mirror adaptation, kept in staging.

Uses the repository's original asMirror procedure, then resolves world-space
controls against the rig's captured build pose. No production registration.
Requires the explicit, inspected mtb_mirror_session state in the live Maya.
"""
import math
import time

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

from maya_toolkit.core.context import UndoChunkContext


def pair(node):
    if node.endswith('_L'):
        return node[:-2] + '_R'
    if node.endswith('_R'):
        return node[:-2] + '_L'
    return node


def sample(start, end):
    import mtb_mirror_session as s
    reflection = om.MMatrix([-1, 0, 0, 0, 0, 1, 0, 0,
                             0, 0, 1, 0, 0, 0, 0, 1])
    begin = time.perf_counter()
    old_time = cmds.currentTime(q=True)
    errors = []
    try:
        cmds.refresh(suspend=True)
        for frame in range(start, end + 1):
            cmds.currentTime(frame)
            original = {p: cmds.getAttr(p) for p in s.plugs}
            before = {n: cmds.xform(n, q=True, ws=True, t=True)
                      for n in s.check_nodes}
            expected = {
                pair(n): om.MMatrix(s.rest[pair(n)]) * reflection
                * om.MMatrix(s.rest[n]).inverse()
                * om.MMatrix(cmds.xform(n, q=True, ws=True, m=True))
                * reflection for n in s.world_nodes
            }
            try:
                with UndoChunkContext('MTB Mirror Sampling'):
                    mel.eval('mtbASMirrorCalibrated mtbMirrorSessionUI;')
                    # AS 5.740 assumes local X for every IK control. A hybrid
                    # spine uses local Z. Build-pose calibration also resolves
                    # the original procedure's dependent-control write order.
                    for _ in range(3):
                        for node in s.world_nodes:
                            matrix = expected[node]
                            rot = om.MTransformationMatrix(matrix).rotation()
                            rot.reorderIt(cmds.getAttr(node + '.rotateOrder'))
                            cmds.xform(node, ws=True, t=list(matrix)[12:15],
                                       ro=[math.degrees(x) for x in rot])
                    values = {p: cmds.getAttr(p) for p in s.plugs}
                    after = {n: cmds.xform(n, q=True, ws=True, t=True)
                             for n in s.check_nodes}
                    worst = max(math.dist(after[n], [-before[pair(n)][0],
                                    before[pair(n)][1], before[pair(n)][2]])
                                for n in s.check_nodes)
                    if worst > 0.001:
                        raise RuntimeError('Mirror geometry mismatch at %s: %s cm'
                                           % (frame, worst))
                    errors.append(worst)
            finally:
                cmds.undo()
            for plug, value in original.items():
                if abs(cmds.getAttr(plug) - value) > 1e-7:
                    raise RuntimeError('Sampling undo did not restore ' + plug)
            s.frames[frame] = values
            s.original_frames[frame] = original
            s.expected_positions[frame] = after
        return {'sampled': [start, end], 'total': len(s.frames),
                'max_error_cm': max(errors),
                'seconds': time.perf_counter() - begin}
    finally:
        cmds.currentTime(old_time)
        cmds.refresh(suspend=False)


def cleanup():
    import mtb_mirror_session as s
    for name, value in s.options.items():
        if value is None:
            cmds.optionVar(remove=name)
        else:
            cmds.optionVar(sv=(name, value))
    cmds.autoKeyframe(state=s.autokey)
    cmds.currentTime(s.original_time)
    if cmds.window(s.window, exists=True):
        cmds.deleteUI(s.window)


def sample_eye_targets():
    """AS's original asMirror skips Aim controls; include this rig's eyes.

    Captured build-pose matrices show world-aligned axes for the three aim
    controls. Reflection therefore negates local tx/ry/rz and swaps L/R.
    Their evaluated world positions are checked during the final bake.
    """
    import mtb_mirror_session as s
    nodes = [s.ns + n for n in ('AimEye_M', 'AimEye_L', 'AimEye_R')]
    plugs = [n + '.' + a for n in nodes
             for a in (cmds.listAttr(n, k=True, scalar=True) or [])
             if cmds.getAttr(n + '.' + a, settable=True)]
    for frame in range(241):
        cmds.currentTime(frame)
        values = {p: cmds.getAttr(p) for p in plugs}
        positions = {n: cmds.xform(n, q=True, ws=True, t=True) for n in nodes}
        for plug in plugs:
            node, attr = plug.rsplit('.', 1)
            source = pair(node) + '.' + attr
            sign = -1 if attr in ('translateX', 'rotateY', 'rotateZ') else 1
            s.frames[frame][plug] = values[source] * sign
            s.original_frames[frame][plug] = values[plug]
        for node in nodes:
            pos = positions[pair(node)]
            s.expected_positions[frame][node] = [-pos[0], pos[1], pos[2]]
    s.plugs.extend(p for p in plugs if p not in s.plugs)
    s.check_nodes.extend(n for n in nodes if n not in s.check_nodes)
    cmds.currentTime(s.original_time)


def apply_sampled():
    import json
    import os
    import tempfile
    import mtb_mirror_session as s
    if set(s.frames) != set(range(241)):
        raise RuntimeError('Expected all frames 0..240')
    changed = [p for p in s.plugs if any(
        abs(s.frames[f][p] - s.original_frames[f][p]) > 1e-6
        for f in range(241))]
    outside_times = [-1, 241, 250, 280, 310]
    outside = {p: [cmds.getAttr(p, time=t) for t in outside_times]
               for p in changed}
    original_keys = {}
    for p in changed:
        curves = cmds.listConnections(p, s=True, d=False, type='animCurve') or []
        original_keys[p] = {
            'curves': curves,
            'value': cmds.getAttr(p),
            'times': cmds.keyframe(p, q=True, tc=True) or [],
            'values': cmds.keyframe(p, q=True, vc=True) or [],
            'in_tangent': cmds.keyTangent(p, q=True, itt=True) or [],
            'out_tangent': cmds.keyTangent(p, q=True, ott=True) or [],
            'in_angle': cmds.keyTangent(p, q=True, ia=True) or [],
            'out_angle': cmds.keyTangent(p, q=True, oa=True) or [],
            'in_weight': cmds.keyTangent(p, q=True, iw=True) or [],
            'out_weight': cmds.keyTangent(p, q=True, ow=True) or [],
        }
    backup_dir = tempfile.mkdtemp(prefix='maya_GuanCha_mirror_')
    s.backup_path = os.path.join(backup_dir, 'original_animation.json')
    with open(s.backup_path, 'w', encoding='utf-8') as stream:
        json.dump({'scene': cmds.file(q=True, sn=True), 'range': [0, 240],
                   'original_animation': original_keys}, stream)
    cmds.refresh(suspend=True)
    try:
        with UndoChunkContext('Mirror GuanCha 0-240'):
            for p in changed:
                data = original_keys[p]
                for guard in (-1, 241):
                    if guard not in data['times']:
                        if data['curves']:
                            cmds.setKeyframe(p, time=guard, insert=True)
                        else:
                            cmds.setKeyframe(p, time=guard, value=data['value'])
                cmds.cutKey(p, time=(0, 240), clear=True)
                discrete = cmds.getAttr(p, type=True) in ('bool', 'enum', 'long', 'short', 'byte')
                previous = None
                for frame in range(241):
                    value = s.frames[frame][p]
                    if p.rsplit('.', 1)[1] in ('rotateX', 'rotateY', 'rotateZ'):
                        if previous is not None:
                            value += 360 * round((previous - value) / 360)
                        previous = value
                    cmds.setKeyframe(p, time=frame, value=value,
                                     inTangentType='linear',
                                     outTangentType='step' if discrete else 'linear')
            worst = 0.0
            for frame in (0, 30, 60, 90, 120, 150, 180, 210, 240):
                cmds.currentTime(frame)
                for node in s.check_nodes:
                    worst = max(worst, math.dist(
                        cmds.xform(node, q=True, ws=True, t=True),
                        s.expected_positions[frame][node]))
            if worst > 0.001:
                raise RuntimeError('Baked pose differs from sampled mirror: %s cm' % worst)
            outside_error = max(abs(cmds.getAttr(p, time=t) - outside[p][i])
                                for p in changed for i, t in enumerate(outside_times))
            if outside_error > 1e-5:
                raise RuntimeError('Outside-range animation changed: %s' % outside_error)
            cmds.currentTime(s.original_time)
        s.result = {'range': [0, 240], 'changed_channels': len(changed),
                    'changed_controls': len(set(p.rsplit('.', 1)[0] for p in changed)),
                    'bake_error_cm': worst, 'outside_error': outside_error,
                    'backup_path': s.backup_path}
        return s.result
    except Exception:
        cmds.undo()
        raise
    finally:
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            cmds.currentTime(s.original_time)
            cmds.refresh(suspend=False)
        finally:
            cmds.undoInfo(stateWithoutFlush=True)
