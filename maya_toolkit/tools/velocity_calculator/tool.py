import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def get_linear_distance(start_pos, end_pos):
    """计算两点之间的直线距离（完整保留原公式）"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(start_pos, end_pos)))


def normalize(**kwargs):
    if set(kwargs) - {'objects', 'mode', 'start_frame', 'end_frame', 'frame', 'sample_step', 'show_result'}:
        raise ValueError('Unknown arguments')
    p = dict(mode='average', sample_step=1., show_result=False)
    p.update(kwargs)
    if p['mode'] not in ('average', 'instant') or type(p['show_result']) is not bool:
        raise ValueError('mode must be average/instant; show_result boolean')
    for key in ('start_frame', 'end_frame', 'frame', 'sample_step'):
        if key in p and (type(p[key]) not in (int, float) or not math.isfinite(p[key]) or abs(p[key]) > 10000000):
            raise ValueError('Finite bounded frames/sample_step required')
    if p['sample_step'] <= 0:
        raise ValueError('sample_step must be positive')
    if p['mode'] == 'average' and ('frame' in kwargs or 'sample_step' in kwargs):
        raise ValueError('frame/sample_step apply only to instant mode')
    if p['mode'] == 'instant' and ('start_frame' in p or 'end_frame' in p):
        raise ValueError('start/end apply only to average mode')
    if 'objects' in p and (not isinstance(p['objects'], list) or not p['objects'] or any(not isinstance(x, str) or not x for x in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Supply nonempty unique whole transform paths')
    return p


def preflight(p):
    from maya import cmds
    import maya.api.OpenMaya as om
    names = p.get('objects', (cmds.ls(selection=True, long=True) or [])[:1])
    if not names:
        raise ValueError('Select a whole transform or supply objects')
    objects = []
    for value in names:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Expected unique whole transform: ' + value)
        if found[0] in objects:
            raise ValueError('Duplicate node aliases')
        objects.append(found[0])
    if p['mode'] == 'average':
        start = p.get('start_frame', cmds.playbackOptions(query=True, minTime=True))
        end = p.get('end_frame', cmds.playbackOptions(query=True, maxTime=True))
    else:
        end = p.get('frame', cmds.currentTime(query=True))
        start = end - p['sample_step']
    if not all(math.isfinite(x) and abs(x) <= 10000000 for x in (start, end)) or end <= start:
        raise ValueError('Measurement interval must have positive duration')
    duration = om.MTime(end - start, om.MTime.uiUnit()).asUnits(om.MTime.kSeconds)
    if duration <= 0:
        raise ValueError('Positive Maya time duration is required')
    if p['show_result'] and cmds.about(batch=True):
        raise ValueError('inViewMessage needs interactive Maya; use structured output in batch')
    return {'objects': objects, 'mode': p['mode'], 'start_frame': start, 'end_frame': end, 'duration_seconds': duration, 'linear_unit': cmds.currentUnit(query=True, linear=True), 'time_unit': cmds.currentUnit(query=True, time=True), 'quantity': 'endpoint_displacement_per_second' if p['mode'] == 'average' else 'backward_finite_difference_per_second', 'sampling': 'read-only worldMatrix plug with MDGContext; current timeline unchanged', 'gui_acceptance': 'not_run'}


def position_at(path, frame):
    import maya.api.OpenMaya as om
    selection = om.MSelectionList()
    selection.add(path)
    dag = selection.getDagPath(0)
    node = om.MFnDependencyNode(dag.node())
    plug = node.findPlug('worldMatrix', False).elementByLogicalIndex(dag.instanceNumber())
    context = om.MDGContext(om.MTime(frame, om.MTime.uiUnit()))
    matrix = om.MFnMatrixData(plug.asMObject(context)).matrix()
    # API world matrices use internal centimeters, not UI linear-unit labels.
    return [om.MDistance(matrix[12 + i], om.MDistance.kCentimeters).asUnits(om.MDistance.uiUnit()) for i in range(3)]


class VelocityCalculatorTool(BaseMayaTool):
    tool_id = 'velocity_calculator'
    tool_name = '世界空间位移速度计算'
    category = 'animation'
    version = '1.0.0-candidate.1'
    description = 'Measure endpoint displacement per second or backward finite-difference velocity using read-only time contexts. Supports Maya time/linear units and parent animation; does not change currentTime or animation keys.'
    parameters_schema = {'type': 'object', 'properties': {'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'minItems': 1}, 'mode': {'type': 'string', 'enum': ['average', 'instant'], 'default': 'average'}, 'start_frame': {'type': 'number', 'minimum': -10000000, 'maximum': 10000000}, 'end_frame': {'type': 'number', 'minimum': -10000000, 'maximum': 10000000}, 'frame': {'type': 'number', 'minimum': -10000000, 'maximum': 10000000}, 'sample_step': {'type': 'number', 'exclusiveMinimum': 0, 'maximum': 10000000, 'default': 1}, 'show_result': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='Read-only velocity measurement preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from maya import cmds
        p = normalize(**kwargs)
        plan = preflight(p)
        measurements = []
        for path in plan['objects']:
            start = position_at(path, plan['start_frame'])
            end = position_at(path, plan['end_frame'])
            if any(not math.isfinite(v) for v in start + end):
                raise ValueError('Nonfinite world transform: ' + path)
            displacement = [b - a for a, b in zip(start, end)]
            measurements.append({'object': path, 'start_position': start, 'end_position': end, 'distance': get_linear_distance(start, end), 'speed': get_linear_distance(start, end) / plan['duration_seconds'], 'velocity_vector': [v / plan['duration_seconds'] for v in displacement], 'unit': plan['linear_unit'] + '/s'})
        plan['measurements'] = measurements
        if p['show_result']:
            cmds.inViewMessage(amg='速度: %.4f %s' % (measurements[0]['speed'], measurements[0]['unit']), pos='midCenter', fade=True)
        return ToolResult.ok(message='Velocity measurement complete; timeline unchanged', data=plan)

    def show_ui(self, parent=None):
        from .ui import create_ui
        return create_ui(self)
