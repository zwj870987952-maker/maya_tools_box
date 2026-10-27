"""Pure configuration validation; compatible with the original list JSON."""
import json
import math
from pathlib import Path

DEFAULT_MODES = {'translate': 'constraint', 'rotate': 'constraint', 'scale': 'constraint', 'other': 'none'}
ACTIONS = ('align', 'numeric_copy', 'bake', 'load_scene', 'restore_pose', 'save_config', 'load_config')


def pairs(value, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError('pairs 必须为非空配对数组')
    result = []
    seen = set()
    for row in value:
        if not isinstance(row, dict) or set(row) - {'source', 'target', 'text', 'modes'}:
            raise ValueError('每行仅接受 source/target 或旧 text，以及 modes')
        if 'text' in row:
            if 'source' in row or 'target' in row or not isinstance(row['text'], str):
                raise ValueError('不能混合 text 和 source/target')
            parts = row['text'].split(',')
            if len(parts) != 2:
                raise ValueError('旧 text 必须恰含一对对象')
            source, target = (part.strip() for part in parts)
        else:
            source, target = row.get('source'), row.get('target')
        for node in (source, target):
            if not isinstance(node, str) or not node.strip() or any(c in node for c in ',\n\r*?[]') or '.' in node:
                raise ValueError('对象名必须为明确的 DAG 节点名，不能含通配符或组件')
        source, target = source.strip(), target.strip()
        if source == target or (source, target) in seen:
            raise ValueError('不能自配对或重复配对')
        seen.add((source, target))
        modes = row.get('modes', {})
        if not isinstance(modes, dict) or set(modes) - set(DEFAULT_MODES):
            raise ValueError('modes 仅接受 translate/rotate/scale/other')
        merged = dict(DEFAULT_MODES, **modes)
        for channel, mode in merged.items():
            if mode not in (('numeric', 'none') if channel == 'other' else ('constraint', 'numeric', 'none')):
                raise ValueError('无效通道模式: ' + channel)
        result.append({'source': source, 'target': target, 'modes': merged})
    return result


def normalize(action='align', pairs_value=None, start=None, end=None, smart=False, path='', **extra):
    if extra or action not in ACTIONS or type(smart) is not bool:
        raise ValueError('未知参数、操作或无效 smart 布尔值')
    normalized = pairs(pairs_value if pairs_value is not None else [], allow_empty=action in ('load_scene', 'restore_pose', 'load_config', 'save_config'))
    if (start is None) != (end is None):
        raise ValueError('start/end 必须同时提供')
    for value in (start, end):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
            raise ValueError('时间范围必须为有限数字')
    if start is not None and start > end:
        raise ValueError('start 不得大于 end')
    if not isinstance(path, str):
        raise ValueError('path 必须为字符串')
    if action in ('save_config', 'load_config'):
        file = Path(path)
        package = Path(__file__).resolve().parent
        if not path or not file.is_absolute() or file.suffix.lower() != '.json' or package == file.resolve() or package in file.resolve().parents:
            raise ValueError('配置必须为候选包以外的绝对 .json 路径')
        if action == 'save_config' and (file.exists() or not file.parent.is_dir()):
            raise ValueError('保存路径已存在或父目录不存在；请使用新文件')
        if action == 'load_config':
            if not file.is_file():
                raise ValueError('配置文件不存在')
            # Validate content during preflight; reading does not rebuild UI or scene.
            normalized = pairs(json.loads(file.read_text(encoding='utf-8-sig')), allow_empty=True)
    return {'action': action, 'pairs': normalized, 'start': start, 'end': end, 'smart': smart, 'path': path}


PAIR_SCHEMA = {'type': 'object', 'properties': {
    'source': {'type': 'string'}, 'target': {'type': 'string'}, 'text': {'type': 'string'},
    'modes': {'type': 'object', 'properties': {key: {'type': 'string', 'enum': ['numeric', 'none'] if key == 'other' else ['constraint', 'numeric', 'none']} for key in DEFAULT_MODES}, 'additionalProperties': False}},
    'oneOf': [{'required': ['source', 'target'], 'not': {'required': ['text']}}, {'required': ['text'], 'not': {'anyOf': [{'required': ['source']}, {'required': ['target']}]}}], 'additionalProperties': False}
SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': list(ACTIONS), 'default': 'align'},
    'pairs': {'type': 'array', 'items': PAIR_SCHEMA, 'default': []},
    'start': {'type': ['number', 'null'], 'default': None}, 'end': {'type': ['number', 'null'], 'default': None},
    'smart': {'type': 'boolean', 'default': False}, 'path': {'type': 'string', 'default': ''}}, 'additionalProperties': False}
