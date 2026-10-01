"""Bounded public parameters and complete native preset validation, no Maya imports."""
import copy
import math
from pathlib import Path
import json

DEFAULTS = dict(action='overlap', targets=None, mode='rotation', frame_range=None,
                order='selection', axes='xyz', main_axis='x+', up_axis='y+', stiffness=0.5,
                stiffness_values=None, strength=1.0, frame_lag=1.0, cycle=False,
                ignore_translation=True, remove_parent=None, distance=None, distance_only=False,
                animation_type='replacer', target_layer=None, new_layer=False, override=False,
                overshoot=False, overshoot_first=False, overshoot_between=True, overshoot_end=True,
                overshoot_strength=1.0, overshoot_frequency=3, wind=False, winds=None,
                wind_strength=1.0, wind_absolute=False, enabled=True,
                preset_path=None, preset_data=None, overwrite=False)
BOOLS = [k for k, v in DEFAULTS.items() if type(v) is bool]
ENUMS = dict(action=['inspect', 'overlap', 'create_wind', 'set_winds', 'select_winds', 'open_ui', 'close_ui', 'read_preset', 'write_preset'], mode=['rotation', 'translation'], order=['selection', 'name', 'split by name'], animation_type=['replacer', 'additive', 'deleteall'], main_axis=['x+', 'x-', 'y+', 'y-', 'z+', 'z-'], up_axis=['x+', 'x-', 'y+', 'y-', 'z+', 'z-'])
RANGES = dict(stiffness=(0, 1), strength=(-1000, 1000), frame_lag=(0, 1000), wind_strength=(-1000, 1000), overshoot_strength=(-1000, 1000), overshoot_frequency=(1, 100), distance=(0.000001, 1000000))
PROPERTIES = {k: {'type': 'boolean', 'default': DEFAULTS[k]} for k in BOOLS}
PROPERTIES.update({k: {'type': 'string', 'enum': v, 'default': DEFAULTS[k]} for k, v in ENUMS.items()})
PROPERTIES.update({k: {'type': 'integer' if k == 'overshoot_frequency' else 'number', 'minimum': v[0], 'maximum': v[1]} for k, v in RANGES.items()})
PROPERTIES.update({k: {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 500, 'uniqueItems': True} for k in ('targets', 'winds')})
PROPERTIES.update({k: {'type': 'string', 'maxLength': 2048} for k in ('axes', 'remove_parent', 'target_layer', 'preset_path')})
PROPERTIES['axes']['pattern'] = '^(x|y|z|xy|xz|yz|xyz)$'
PROPERTIES['frame_range'] = {'type': 'array', 'items': {'type': 'integer', 'minimum': -1000000, 'maximum': 1000000}, 'minItems': 2, 'maxItems': 2}
PROPERTIES['stiffness_values'] = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'number', 'minimum': 0, 'maximum': 1}, 'maxItems': 500}, 'maxItems': 500}
PROPERTIES['preset_data'] = {'type': 'object', 'description': '完整原版八组 JSON；read_preset 获取模板，write_preset 验证后写入。'}
SCHEMA = {'type': 'object', 'properties': PROPERTIES, 'additionalProperties': False}


def number(value, low, high, name):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(name + ' must be a finite number in [%s, %s]' % (low, high))
    return value


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('Unknown parameters: ' + ', '.join(sorted(set(kwargs) - set(DEFAULTS))))
    o = copy.deepcopy(DEFAULTS)
    o.update(copy.deepcopy(kwargs))
    for k in BOOLS:
        if type(o[k]) is not bool:
            raise ValueError(k + ' must be boolean')
    for k, enum in ENUMS.items():
        if o[k] not in enum:
            raise ValueError(k + ' invalid enum')
    for k, limits in RANGES.items():
        if k == 'distance' and o[k] is None:
            continue
        number(o[k], *limits, k)
    if type(o['overshoot_frequency']) is not int:
        raise ValueError('overshoot_frequency must be integer')
    if o['axes'] not in ('x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz'):
        raise ValueError('axes must be ordered unique xyz subset')
    if o['main_axis'][0] == o['up_axis'][0]:
        raise ValueError('main/up axes must be perpendicular')
    for k in ('remove_parent', 'target_layer', 'preset_path'):
        if o[k] is not None and (not isinstance(o[k], str) or not o[k].strip() or len(o[k]) > 2048 or '\0' in o[k]):
            raise ValueError(k + ' invalid string')
    for k in ('targets', 'winds'):
        if o[k] is not None and (not isinstance(o[k], list) or not 1 <= len(o[k]) <= 500 or any(not isinstance(v, str) or not v or '\0' in v for v in o[k]) or len(set(o[k])) != len(o[k])):
            raise ValueError(k + ' requires unique node strings')
    r = o['frame_range']
    if r is not None and (not isinstance(r, list) or len(r) != 2 or any(type(v) is not int or abs(v) > 1000000 for v in r) or r[1] <= r[0] or r[1] - r[0] > 20000):
        raise ValueError('frame_range requires two bounded integer frames start < end')
    s = o['stiffness_values']
    if s is not None:
        if not isinstance(s, list) or not s or len(s) > 500 or any(not isinstance(g, list) or not g or len(g) > 500 for g in s):
            raise ValueError('stiffness_values requires nonempty groups')
        for g in s:
            for v in g:
                number(v, 0, 1, 'stiffness_values')
    if o['new_layer'] and o['target_layer']:
        raise ValueError('Choose new_layer OR target_layer')
    if o['distance_only'] and o['distance'] is None:
        raise ValueError('distance_only requires explicit distance')
    if o['overshoot'] and not o['overshoot_strength']:
        raise ValueError('overshoot_strength cannot be zero')
    if o['action'] in ('read_preset', 'write_preset') and not o['preset_path']:
        raise ValueError('preset_path required')
    if o['action'] == 'write_preset':
        o['preset_data'] = validate_preset(o['preset_data'])
    elif o['preset_data'] is not None:
        raise ValueError('preset_data only used for write_preset')
    return o


def validate_preset(data):
    template = json.loads((Path(__file__).parent / 'native/default.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != set(template):
        raise ValueError('Preset requires all eight original sections')
    data = copy.deepcopy(data)
    for group, example in template.items():
        if isinstance(example, dict):
            allowed = set(example) | ({'frame_lag'} if group == 'base_overlap' else {'strength'} if group == 'wind' else set())
            required = set(example) - ({'cycle'} if group == 'bonus' else set())
            if not isinstance(data[group], dict) or not required <= set(data[group]) or set(data[group]) - allowed:
                raise ValueError('Malformed preset group: ' + group)
            for k, v in data[group].items():
                reference = example.get(k, '1.0')
                if type(reference) is bool and type(v) is not bool:
                    raise ValueError(group + '.' + k + ' must be boolean')
                if type(reference) is int and type(v) is not int:
                    raise ValueError(group + '.' + k + ' must be integer')
                if type(reference) is str and (not isinstance(v, str) or len(v) > 2048 or '\0' in v):
                    raise ValueError(group + '.' + k + ' must be bounded text')
                if isinstance(reference, list):
                    if not isinstance(v, list) or not 2 <= len(v) <= 100:
                        raise ValueError('Preset gradient requires 2..100 points')
                    for point in v:
                        if not isinstance(point, str) or len(point) > 100:
                            raise ValueError('Gradient point must be text')
                        parts = point.split(',')
                        if len(parts) != 3:
                            raise ValueError('Gradient point needs value,position,interpolation')
                        number(float(parts[0]), 0, 1, 'gradient value')
                        number(float(parts[1]), 0, 1, 'gradient position')
                        if parts[2] not in ('0', '1', '2', '3'):
                            raise ValueError('Gradient interpolation invalid')
        elif type(data[group]) is not int:
            raise ValueError('overlap_type must be integer')
    for group, k, high in (('base_overlap', 'time_type', 2), ('base_overlap', 'main_axis', 5), ('base_overlap', 'up_axis', 3), ('order_key_type', 'order', 2), ('order_key_type', 'key_type', 2)):
        if not 0 <= data[group][k] <= high:
            raise ValueError('Preset index outside range: ' + k)
    if data['overlap_type'] not in (0, 1):
        raise ValueError('Preset mode invalid')
    for group, k, low, high in (('base_overlap', 'stifness', 0, 1), ('base_overlap', 'strength', -1000, 1000), ('base_overlap', 'frame_lag', 0, 1000), ('wind', 'strength', -1000, 1000), ('overshoot', 'strength', -1000, 1000), ('overshoot', 'frequency', 1, 100), ('bonus', 'distance', 0.000001, 1000000)):
        if k in data[group]:
            value = float(data[group][k])
            number(value, low, high, group + '.' + k)
            if k == 'frequency' and (not value.is_integer() or str(int(value)) != data[group][k]):
                raise ValueError('Preset frequency requires integer text')
    for k in ('start_time', 'end_time'):
        text = data['base_overlap'][k]
        if text not in ('start', 'end'):
            number(float(text), -1000000, 1000000, k)
    data['bonus'].setdefault('cycle', False)
    return data
