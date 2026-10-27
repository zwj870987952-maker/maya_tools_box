from functools import wraps

_ACTIVE = False
_CURVES = set()
_UI = None


def mc():
    from maya import cmds
    return cmds


def suitable(curve):
    c = mc()
    try:
        if c.nodeType(curve) not in ('animCurveTL', 'animCurveTA', 'animCurveTU') or c.referenceQuery(curve, isNodeReferenced=True) or c.lockNode(curve, query=True, lock=True)[0]:
            return False
        frames = c.keyframe(curve, query=True, timeChange=True) or []
        if len(frames) < 2:
            return False
        for source in c.listConnections(curve + '.input', source=True, destination=False) or []:
            if c.nodeType(source) != 'time':
                return False
        if any(kind in ('step', 'stepnext') for key in ('inTangentType', 'outTangentType') for kind in c.keyTangent(curve, query=True, **{key: True}) or []):
            return False
        outputs = c.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
        if len(outputs) != 1:
            return False
        plug = outputs[0]
        node = plug.split('.', 1)[0]
        if c.nodeType(node) not in ('transform', 'joint') or c.referenceQuery(node, isNodeReferenced=True) or c.lockNode(node, query=True, lock=True)[0] or c.getAttr(plug, lock=True):
            return False
        return True
    except Exception:
        return False


def selection_curves():
    c = mc()
    curves = set()
    for node in c.ls(selection=True) or []:
        if c.nodeType(node).startswith('animCurve'):
            curves.add(node)
        else:
            curves.update(c.listConnections(node, source=True, destination=False, type='animCurve') or [])
    return sorted(curves)


def reduce_bridge(function):
    @wraps(function)
    def call(self, *args, **kwargs):
        if _ACTIVE:
            return function(self, *args, **kwargs)
        if args:
            raise ValueError('候选标准桥只接受命名参数')
        from .tool import KeyframeReductionTool
        result = KeyframeReductionTool().run(curves=[self.path], **kwargs)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['results'][0]['rate']
    return call


def run_ui(widget):
    from .tool import KeyframeReductionTool
    curves = widget.filter.getAnimationCurves()
    result = KeyframeReductionTool().run(curves=curves, **widget.settings.getSettings()) if curves else None
    if result is None:
        mc().warning('没有选中可精简曲线')
        return
    if not result.success:
        raise RuntimeError(result.message)
    widget.progress.setRange(0, len(curves))
    widget.progress.setValue(len(curves))
    widget.progress.setFormat('Completed %d curves' % len(curves))
    return result.data


def execute(args):
    global _ACTIVE, _CURVES, _UI
    c = mc()
    if args['action'] == 'open_ui':
        from .native import ui
        if _UI is not None:
            try:
                _UI.close()
                _UI.deleteLater()
            except RuntimeError:
                pass
        _UI = ui.show()
        return {'window': 'Keyframe Reduction'}
    if args['action'] == 'inspect':
        return {'curves': [{'curve': n, 'key_count': c.keyframe(n, query=True, keyframeCount=True), 'frames': c.keyframe(n, query=True, timeChange=True)} for n in args['curves']]}
    from .native.classes.keyframeReduction import KeyframeReduction
    auto = c.autoKeyframe(query=True, state=True)
    _ACTIVE, _CURVES = True, {c.ls(n, uuid=True)[0] for n in args['curves']}
    try:
        c.autoKeyframe(state=False)
        settings = {k: v for k, v in args.items() if k not in ('action', 'curves')}
        rows = []
        for curve in args['curves']:
            before = c.keyframe(curve, query=True, keyframeCount=True)
            rate = KeyframeReduction(curve).reduce(**settings)
            rows.append({'curve': curve, 'before': before, 'after': c.keyframe(curve, query=True, keyframeCount=True), 'rate': rate})
        return {'results': rows}
    finally:
        try:
            c.autoKeyframe(state=auto)
        finally:
            _ACTIVE, _CURVES = False, set()
