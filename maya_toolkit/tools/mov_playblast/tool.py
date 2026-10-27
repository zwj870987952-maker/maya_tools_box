import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import media

ACTIONS = ['inspect', 'export', 'encode_images', 'convert_mp4', 'convert_gif', 'ffmpeg_version', 'open_ui', 'settings_export', 'settings_import']
DEFAULTS = {'action': 'inspect', 'mode': 'images', 'output_dir': '', 'basename': 'untitled', 'cameras': [], 'multi_camera': False, 'panel': '', 'start': None, 'end': None, 'scale': 1.0, 'width': 0, 'height': 0, 'fps': 0.0, 'include_audio': False, 'audio_node': '', 'audio_file': '', 'audio_offset_frames': 0, 'hold': 1, 'convert_mp4': False, 'convert_gif': False, 'overwrite': False, 'increment': False, 'ffmpeg_path': '', 'timeout': 600, 'source_file': '', 'image_folder': '', 'settings_file': ''}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'mode': {'type': 'string', 'enum': ['images', 'qt'], 'default': 'images'}, 'cameras': {'type': 'array', 'maxItems': 100, 'uniqueItems': True, 'items': {'type': 'string'}, 'description': '明确camera，空列表表示当前viewport相机'}, 'start': {'type': ['integer', 'null']}, 'end': {'type': ['integer', 'null']}}}
for k, v in DEFAULTS.items():
    if k not in SCHEMA['properties']:
        SCHEMA['properties'][k] = {'type': 'boolean' if type(v) is bool else 'integer' if type(v) is int else 'number' if type(v) is float else 'string', 'default': v}
SCHEMA['properties']['output_dir']['description'] = '已存在本地绝对输出目录；外部文件不由Maya Undo恢复'
SCHEMA['properties']['overwrite']['description'] = '明确允许覆盖所有规划的MOV/MP4/GIF/设置输出'


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    a = dict(DEFAULTS, **kwargs)
    if a['action'] not in ACTIONS or a['mode'] not in ('images', 'qt'):
        raise ValueError('action/mode无效')
    for k, v in DEFAULTS.items():
        if type(v) is bool and type(a[k]) is not bool:
            raise ValueError(k + '须bool')
        if isinstance(v, str) and (not isinstance(a[k], str) or '\x00' in a[k]):
            raise ValueError(k + '须string无NUL')
    if not isinstance(a['cameras'], list) or len(a['cameras']) > 100 or any(not isinstance(v, str) or not v or any(c in v for c in '*?[]\n\r') for v in a['cameras']) or len(set(a['cameras'])) != len(a['cameras']):
        raise ValueError('cameras须明确唯一节点名')
    for k in ('start', 'end'):
        if a[k] is not None and (type(a[k]) is not int or not -1000000 <= a[k] <= 1000000):
            raise ValueError('start/end须整数帧')
    for k, low, high in (('hold', 1, 10), ('timeout', 1, 3600), ('width', 0, 8192), ('height', 0, 8192), ('audio_offset_frames', -1000000, 1000000)):
        if type(a[k]) is not int or not low <= a[k] <= high:
            raise ValueError(k + '整数范围无效')
    for k, low, high in (('scale', .1, 1), ('fps', 0, 1000)):
        if type(a[k]) not in (int, float) or not math.isfinite(a[k]) or not low <= a[k] <= high:
            raise ValueError(k + '有限数范围无效')
    if a['mode'] == 'qt' and a['hold'] != 1:
        raise ValueError('几拍一只支持高分辨率图像序列模式')
    return a


def plan(**kwargs):
    a = normalize(**kwargs)
    from . import runtime
    if runtime.ACTIVE:
        raise ValueError('已有拍屏/媒体转换正在运行')
    if a['action'] in ('inspect', 'open_ui'):
        if a['action'] == 'open_ui':
            from maya import cmds
            if cmds.about(batch=True):
                raise ValueError('真实Maya GUI需要')
        return a
    if a['action'].startswith('settings_'):
        p = media.absolute(a['settings_file'])
        if p.suffix.lower() != '.json':
            raise ValueError('设置路径须.json')
        if a['action'] == 'settings_import':
            if not p.is_file() or p.stat().st_size > 65536:
                raise ValueError('小型现有JSON设置文件需要')
            a['settings'] = runtime.read_settings(p)
        else:
            a['outputs'] = media.destinations(str(p.parent), [(p.stem, [p.suffix])], a['overwrite'], False)
        a['settings_file'] = str(p)
        return a
    if a['action'] in ('ffmpeg_version', 'convert_mp4', 'convert_gif', 'encode_images'):
        a['ffmpeg_path'] = media.executable(a['ffmpeg_path'])
    if a['action'] == 'ffmpeg_version':
        return a
    if a['action'] == 'export':
        runtime.scene_plan(a)
    else:
        if a['action'] == 'encode_images':
            a['images'] = [str(p) for p in media.sequence_files(a['image_folder'])]
            if not a['fps']:
                raise ValueError('encode_images需要fps')
            if a['audio_file']:
                a['audio_file'] = str(media.absolute(a['audio_file']))
                if not Path(a['audio_file']).is_file():
                    raise ValueError('音频文件不存在')
            extensions = ['.mov']
        else:
            source = media.absolute(a['source_file'])
            if not source.is_file() or source.stat().st_size == 0:
                raise ValueError('源媒体不存在/为空')
            a['source_file'] = str(source)
            extensions = ['.mp4' if a['action'] == 'convert_mp4' else '.gif']
            if a['action'] == 'convert_gif' and (not a['fps'] or not a['width'] or not a['height']):
                raise ValueError('GIF需要fps/width/height')
        a['outputs'] = media.destinations(a['output_dir'], [(a['basename'], extensions)], a['overwrite'], a['increment'])
        if a['source_file'] and any(Path(v['path']) == Path(a['source_file']) for g in a['outputs'] for v in g):
            raise ValueError('输入媒体不能覆盖自己')
    return a


class MovPlayblastTool(BaseMayaTool):
    tool_id = 'mov_playblast'
    tool_name = '多相机MOV拍屏与MP4/GIF'
    category = 'animation'
    version = '11.1-candidate.1'
    description = '完整高图像序列/低QT、多相机/音频偏移/几拍一/增序/MP4/GIF；只读预检、外部文件显式覆盖、视图finally恢复。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读参数/相机/范围/输出冲突/媒体路径检查，不执行拍屏或进程')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from . import runtime
        try:
            return ToolResult.ok(data=runtime.execute(plan(**kwargs)), warnings=['输出/覆盖媒体与设置文件不能Maya Undo；用户正常保存场景由用户执行'])
        except runtime.PartialFailure as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], data=error.data)

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
