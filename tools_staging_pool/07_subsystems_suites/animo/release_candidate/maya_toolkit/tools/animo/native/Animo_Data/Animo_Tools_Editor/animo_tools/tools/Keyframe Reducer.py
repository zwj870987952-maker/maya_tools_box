import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2


def _get_anim_curve_fn(curve_name):
    sel = om2.MSelectionList()
    sel.add(curve_name)
    mobj = sel.getDependNode(0)
    return oma2.MFnAnimCurve(mobj)


def _sample_curve(fn_curve, t0, t1, samples_per_frame):
    n = max(2, int(round((t1 - t0) * samples_per_frame)))
    unit = om2.MTime.uiUnit()
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * (float(i) / n)
        v = fn_curve.evaluate(om2.MTime(t, unit))
        pts.append((t, v))
    return pts


def _line_value(t, t0, v0, t1, v1):
    if t1 == t0:
        return v0
    frac = (t - t0) / (t1 - t0)
    return v0 + frac * (v1 - v0)


def _max_deviation(fine_pts, t0, v0, t1, v1):
    max_dev = 0.0
    max_t = None
    for t, v in fine_pts:
        if t < t0 or t > t1:
            continue
        dev = abs(v - _line_value(t, t0, v0, t1, v1))
        if dev > max_dev:
            max_dev = dev
            max_t = t
    return max_dev, max_t


def _sign(d, eps):
    if d > eps:
        return 1
    if d < -eps:
        return -1
    return 0


def _find_extrema(candidates):
    protected = set()
    n = len(candidates)
    values = [v for _, v in candidates]
    value_range = max(values) - min(values)
    eps = max(value_range * 1e-4, 1e-6)
    for i in range(1, n - 1):
        slope_in = _sign(candidates[i][1] - candidates[i - 1][1], eps)
        slope_out = _sign(candidates[i + 1][1] - candidates[i][1], eps)
        if slope_in != slope_out:
            protected.add(i)
    return protected


def _greedy_reduce(candidates, fine_pts, tolerance, protected):
    n = len(candidates)
    if n < 3:
        return set(range(n))

    alive = list(range(n))
    while len(alive) >= 3:
        best_pos, best_err = None, None
        for pos in range(1, len(alive) - 1):
            if alive[pos] in protected:
                continue
            t0, v0 = candidates[alive[pos - 1]]
            t1, v1 = candidates[alive[pos + 1]]
            err, _ = _max_deviation(fine_pts, t0, v0, t1, v1)
            if best_err is None or err < best_err:
                best_err, best_pos = err, pos
        if best_err is not None and best_err <= tolerance:
            del alive[best_pos]
        else:
            break
    return set(alive)


def smart_reduce_keys(tolerance=0.05, samples_per_frame=4,
                       escalate=True, escalate_factor=1.5,
                       max_tolerance=None, max_attempts=12):
    curves = list(set(cmds.keyframe(query=True, selected=True, name=True) or []))
    if not curves:
        cmds.inViewMessage(
            amg='<span style="color:#ffffff;">Please select keys in the Graph Editor</span>',
            pos='midCenter',
            fade=True
        )
        return

    cmds.undoInfo(openChunk=True)
    try:
        for curve in curves:
            sel_times = cmds.keyframe(curve, query=True, selected=True, timeChange=True)
            if not sel_times:
                continue
            sel_times = sorted(set(sel_times))
            if len(sel_times) < 3:
                continue

            candidates = []
            for t in sel_times:
                v = cmds.keyframe(curve, time=(t, t), query=True, valueChange=True)[0]
                candidates.append((t, v))

            fn_curve = _get_anim_curve_fn(curve)
            fine_pts = _sample_curve(fn_curve, sel_times[0], sel_times[-1], samples_per_frame)
            protected = _find_extrema(candidates)

            t_cur = tolerance
            remove_times = []
            attempts = 0
            while attempts < max_attempts:
                alive = _greedy_reduce(candidates, fine_pts, t_cur, protected)
                keep_times_set = set(candidates[i][0] for i in alive)
                remove_times = [t for t in sel_times if t not in keep_times_set]

                if remove_times or not escalate:
                    break
                if max_tolerance is not None and t_cur >= max_tolerance:
                    break
                t_cur *= escalate_factor
                attempts += 1

            for t in remove_times:
                cmds.cutKey(curve, time=(t, t))
    finally:
        cmds.undoInfo(closeChunk=True)


smart_reduce_keys(tolerance=0.05)