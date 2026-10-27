"""Pure marker model. Adaptation of Robert Joosten Timeline Marker 2.0.2, GPL-3.0-or-later."""
import json

MAX_MARKERS = 20000


def frame(value):
    if type(value) is not int or not -1000000 <= value <= 1000000:
        raise ValueError('frame须整数且在±1000000内')
    return value


def color(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in value):
        raise ValueError('color须三个0..255整数')
    return list(value)


def comment(value):
    if not isinstance(value, str) or len(value) > 4096 or '\x00' in value:
        raise ValueError('comment须无NUL的≤4096字符字符串')
    return value


def dataset(value):
    if not isinstance(value, dict) or set(value) != {'frames', 'colors', 'comments'}:
        raise ValueError('标记数据须frames/colors/comments，无额外字段')
    if any(not isinstance(v, list) for v in value.values()):
        raise ValueError('标记数据须列表')
    frames = [frame(v) for v in value['frames']]
    if len(frames) > MAX_MARKERS or len(set(frames)) != len(frames) or not len(frames) == len(value['colors']) == len(value['comments']):
        raise ValueError('标记须唯一，三列表长度一致，最多20000')
    data = {'frames': frames, 'colors': [color(v) for v in value['colors']], 'comments': [comment(v) for v in value['comments']]}
    if len(json.dumps(data, ensure_ascii=True).encode('utf-8')) > 4000000:
        raise ValueError('序列化标记总量超过4MB')
    return data


def empty():
    return {'frames': [], 'colors': [], 'comments': []}


def decode(raw):
    """Maya fileInfo queries return MEL-escaped strings, including doubled backslashes."""
    try:
        return dataset(json.loads(raw))
    except json.JSONDecodeError:
        return dataset(json.loads(json.loads('"' + raw + '"')))


def remap(data, old_range, new_range):
    data = dataset(data)
    if any(not isinstance(r, list) or len(r) != 2 or r[0] > r[1] for r in (old_range, new_range)):
        raise ValueError('范围须有序闭区间[start,end]')
    a, b = [frame(v) for v in old_range]
    c, d = [frame(v) for v in new_range]
    if a == b and c != d:
        raise ValueError('单帧源范围须映射到单帧')
    if old_range == new_range:
        return data
    records = dict(zip(data['frames'], zip(data['colors'], data['comments'])))
    moving = sorted(f for f in records if a <= f <= b)
    frozen = [(f, records.pop(f)) for f in moving]
    for f, value in frozen:
        target = c if a == b else int(((f - a) * (d - c) / (b - a)) + c)
        records[target] = value  # Original truncation; later source frame wins collisions.
    return dataset({'frames': list(records), 'colors': [v[0] for v in records.values()], 'comments': [v[1] for v in records.values()]})
