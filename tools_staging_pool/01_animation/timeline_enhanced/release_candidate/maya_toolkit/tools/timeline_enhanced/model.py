"""Pure timeline marker document operations: these are not Maya keys."""
import copy
import json
import math

DEFAULT = {'start_frame': 1, 'frame_count': 100, 'blocks': {}, 'selected': [], 'clipboard': {}}
STYLES = {
    'keyframe': {'color': [1., .3, .3], 'label': 'K', 'name': '关键帧'},
    'breakdown': {'color': [.3, 1., .3], 'label': 'B', 'name': '分解帧'},
    'inbetween': {'color': [.3, .3, 1.], 'label': 'I', 'name': '中间帧'},
    'hold': {'color': [1., 1., .3], 'label': 'H', 'name': '保持帧'},
    'camera': {'color': [1., .6, 0.], 'label': 'C', 'name': '镜头'},
    'effect': {'color': [.8, 0., .8], 'label': 'E', 'name': '特效'},
}


def integer(value, low=-10000000, high=10000000):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Expected bounded integer frame/count')
    return value


def block(value):
    if not isinstance(value, dict) or set(value) - {'color', 'label', 'name'}:
        raise ValueError('Block requires color/label/name fields only')
    out = copy.deepcopy(value)
    color = out.get('color', [.5, .5, .5])
    if not isinstance(color, (list, tuple)) or len(color) != 3 or any(type(c) not in (int, float) or not math.isfinite(c) or not 0 <= c <= 1 for c in color):
        raise ValueError('RGB color must contain three finite values in 0..1')
    out['color'] = list(color)
    for key in ('label', 'name'):
        if key in out and (not isinstance(out[key], str) or len(out[key]) > 256):
            raise ValueError('Block labels/names must be strings up to 256 chars')
    return out


def mapping(value):
    if not isinstance(value, dict) or len(value) > 10000:
        raise ValueError('Expected bounded block map')
    result = {}
    for key, item in value.items():
        if not isinstance(key, str) or str(int(key)) != key:
            raise ValueError('Frames must use canonical integer string keys')
        integer(int(key))
        result[key] = block(item)
    return result


def document(value=None):
    if value is None:
        return copy.deepcopy(DEFAULT)
    if not isinstance(value, dict) or set(value) - set(DEFAULT):
        raise ValueError('Invalid timeline document')
    result = copy.deepcopy(DEFAULT)
    result.update(copy.deepcopy(value))
    integer(result['start_frame'])
    integer(result['frame_count'], 10, 1000)
    integer(result['start_frame'] + result['frame_count'] - 1)
    result['blocks'] = mapping(result['blocks'])
    result['clipboard'] = mapping(result['clipboard'])
    selected = result['selected']
    if not isinstance(selected, list) or any(type(f) is not int or str(f) not in result['blocks'] for f in selected) or len(selected) != len(set(selected)):
        raise ValueError('Selection must contain unique existing block frames')
    result['selected'] = sorted(selected)
    return result


def visible(state, frame):
    integer(frame)
    if not state['start_frame'] <= frame < state['start_frame'] + state['frame_count']:
        raise ValueError('Target frame is outside visible document range')
    return str(frame)


def transform(state, action, **params):
    """Always return a new document; no input mutation, UI, scene or files."""
    data = document(state)
    blocks = data['blocks']
    overwrite = params.get('overwrite', False)
    if action == 'configure':
        data['start_frame'] = params.get('start_frame', data['start_frame'])
        data['frame_count'] = params.get('frame_count', data['frame_count'])
    elif action == 'add':
        target = visible(data, params['frame'])
        if target in blocks and not overwrite:
            raise ValueError('Existing target block requires overwrite=True')
        blocks[target] = block(params.get('block', STYLES[params.get('block_type', 'keyframe')]))
    elif action == 'edit':
        target = visible(data, params['frame'])
        if target not in blocks:
            raise ValueError('No block to edit')
        blocks[target] = block(dict(blocks[target], **params['block']))
    elif action == 'move':
        source, target = str(params['source_frame']), visible(data, params['frame'])
        if source not in blocks:
            raise ValueError('Source block does not exist')
        if source != target and target in blocks and not overwrite:
            raise ValueError('Move would replace an existing block')
        item = blocks.pop(source)
        blocks[target] = item
        data['selected'] = sorted({params['frame'] if x == params['source_frame'] else x for x in data['selected']})
    elif action == 'select':
        data['selected'] = list(params['frames'])
    elif action == 'copy':
        data['clipboard'] = {str(f): copy.deepcopy(blocks[str(f)]) for f in data['selected']}
    elif action == 'paste':
        if data['clipboard']:
            target = integer(params['frame'])
            offset = target - min(int(k) for k in data['clipboard'])
            pending = {str(int(k) + offset): copy.deepcopy(v) for k, v in data['clipboard'].items() if data['start_frame'] <= int(k) + offset < data['start_frame'] + data['frame_count']}
            if not overwrite and set(pending) & set(blocks):
                raise ValueError('Paste would replace existing blocks')
            blocks.update(pending)
    elif action == 'delete':
        for f in params.get('frames', data['selected']):
            integer(f)
            blocks.pop(str(f), None)
        data['selected'] = [f for f in data['selected'] if str(f) in blocks]
    elif action == 'clear':
        blocks.clear()
        data['selected'] = []
    elif action != 'inspect':
        raise ValueError('Unknown document action')
    return document(data)


def load_bytes(data):
    if len(data) > 4 * 1024 * 1024:
        raise ValueError('Config exceeds 4 MiB')
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate JSON key: ' + key)
            value[key] = item
        return value
    return document(json.loads(data.decode('utf-8-sig'), object_pairs_hook=unique))
