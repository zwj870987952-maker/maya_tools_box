"""Execute the original joint/floatMath algorithm with explicit options and ownership."""
from contextlib import contextmanager
import json
from pathlib import Path
from . import state

PACKAGE = Path(__file__).resolve().parent
_ACTIVE_DEPTH = 0


def require_active():
    if not _ACTIVE_DEPTH:
        raise RuntimeError('请通过 AnimirrorV2Tool.run() 调用，不能直接执行内部 MEL 写场景过程')


@contextmanager
def active():
    global _ACTIVE_DEPTH
    _ACTIVE_DEPTH += 1
    try:
        yield
    finally:
        _ACTIVE_DEPTH -= 1


def load_suite():
    import maya.mel as mel
    path = PACKAGE / 'runtime.mel'
    marker = 'mtbAV2_mirror_animation'
    origin = str(mel.eval('whatIs ' + json.dumps(marker) + ';')).replace('\\', '/').casefold()
    if not origin.endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
    for name in catalog['runtime_procedures']:
        origin = str(mel.eval('whatIs ' + json.dumps(name) + ';')).replace('\\', '/').casefold()
        if not origin.endswith(path.as_posix().casefold()):
            raise RuntimeError('内部 MEL 过程来源冲突: ' + name)
    return {'source': path.as_posix(), 'procedures': catalog['runtime_procedures']}


def configure(args):
    import maya.mel as mel
    catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
    flags = {'TranslationsCheckbox': args['translations'], 'RotationsCheckbox': args['rotations']}
    for axis in 'XYZ':
        flags[axis + 'AxisRotCheckbox'] = axis in args['invert_rotation']
        flags[axis + 'AxisTransRadio'] = args['translation_axis'] == axis
    mel.eval('global int $mtbAV2_flags[]; $mtbAV2_flags = {' + ','.join(str(int(flags[name])) for name in catalog['flag_order']) + '};')
    if args['start'] is not None:
        mel.eval('global float $mtbAV2_startFrame; global float $mtbAV2_finishFrame; $mtbAV2_startFrame = ' + repr(args['start']) + '; $mtbAV2_finishFrame = ' + repr(args['end']) + ';')


def clear_owned():
    require_active()
    return state.clear()


def execute(args):
    import maya.cmds as cmds
    import maya.mel as mel
    load_suite()
    saved_time = cmds.currentTime(query=True)
    saved_selection = []
    for item in cmds.ls(selection=True, long=True) or []:
        node, separator, suffix = item.partition('.')
        saved_selection.append((state.identity(node), separator + suffix))
    saved_refresh = cmds.refresh(query=True, suspend=True)
    result = None
    try:
        with active():
            if args['action'] == 'clear':
                result = state.clear()
                mel.eval('mtbAV2_globals_variables();')
                return result
            state.rebuild_globals()
            configure(args)
            if args['action'] in ('mirror', 'mirror_bake'):
                before_ids = {state.identity(node) for node in (cmds.ls(long=True) or [])}
                record = state.create_record(args['objects'], args)
                cmds.select(args['objects'], replace=True)
                error = None
                try:
                    # Build a live mirror first. Python orchestrates the immediate bake
                    # so every new helper is recorded before the original cleanup call.
                    mel.eval('mtbAV2_mirror_animation(0);')
                except Exception as caught:
                    error = caught
                    raise
                finally:
                    entries = state.capture(record, before_ids, error)
                result = {'target': args['objects'][2], 'metadata': record['node'], 'owned_nodes': entries, 'interactive': True}
            if args['action'] in ('bake', 'mirror_bake'):
                all_records = state.records()
                state.safe_to_clear(all_records)
                targets = list(dict.fromkeys(state.find(record['data']['inputs'][2], required=True) for record in all_records))
                # Keep full original bake/delete-static/filterCurve sequence. The
                # embedded delete_all_created now routes to UUID-safe clear_owned.
                mel.eval('mtbAV2_fast_bake(0);')
                result = dict(result or {}, targets=targets, range=[args['start'], args['end']], interactive=False,
                              warnings=['烘焙处理全部累计镜像目标；删除目标静态曲线并执行 filterCurve，保留范围外键。'])
            return result
    finally:
        cmds.refresh(suspend=saved_refresh)
        cmds.currentTime(saved_time)
        surviving = []
        for value, suffix in saved_selection:
            node = state.find(value)
            if node and cmds.objExists(node + suffix):
                surviving.append(node + suffix)
        cmds.select(surviving, replace=True) if surviving else cmds.select(clear=True)


def open_ui():
    import maya.cmds as cmds
    import maya.mel as mel
    if cmds.about(batch=True):
        raise RuntimeError('原窗口只能在真实 Maya GUI 打开')
    loaded = load_suite()
    # Sourcing is definition-only. Opening does not reset live owned scene records.
    mel.eval('mtbAV2_aniMirror_menu();')
    return dict(loaded, window='mtbAV2_AniMirror')
