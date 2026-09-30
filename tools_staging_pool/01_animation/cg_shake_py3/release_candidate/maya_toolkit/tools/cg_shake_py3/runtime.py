import json
from pathlib import Path
import random
import uuid
from . import files
from .contracts import CHANNELS

_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('写键/缓存仅允许CgShakeTool.run()')


def restore(node, record):
    require_active()
    from maya import cmds
    cmds.select(node, replace=True)
    cmds.cutKey(node, clear=True)
    cmds.file(record['path'], i=True, type='animImport', ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, options='targetTime=4;copies=1;option=replace;pictures=0;connect=0;', pr=True, importTimeRange='combine')


def write_json(target, data):
    require_active()
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(data, indent=4, sort_keys=True), encoding='utf-8')
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def execute(args):
    global _ACTIVE
    if args['action'] == 'load_preset':
        return {'file_path': args['file_path'], 'preset': args['preset']}
    from maya import cmds
    selection = cmds.ls(selection=True, long=True) or []
    time = cmds.currentTime(query=True)
    playback = {flag: cmds.playbackOptions(query=True, **{flag: True}) for flag in ('minTime', 'maxTime', 'animationStartTime', 'animationEndTime')}
    try:
        _ACTIVE = True
        if args['action'] == 'save_preset':
            write_json(args['file_path'], args['preset'])
            return {'file_path': args['file_path'], 'warnings': ['预设文件写入不能由Maya Undo撤回。']}
        node = args['object']
        if args['action'] == 'cache':
            target = Path(args['file_path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.stem + '.' + uuid.uuid4().hex + '.tmp.anim')
            try:
                cmds.select(node, replace=True)
                cmds.file(str(temporary), force=True, options='precision=17;intValue=17;nodeNames=1;verboseUnits=0;whichRange=1;range=1:120;options=keys;hierarchy=none;controlPoints=0;shapes=1;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0 -shape 1 ', type='animExport', pr=True, es=True)
                temporary.replace(target)
            finally:
                if temporary.exists():
                    temporary.unlink()
            record = {'owner': files.OWNER, 'uuid': cmds.ls(node, uuid=True)[0], 'path': str(target), 'sha256': files.digest(target)}
            write_json(str(target) + '.json', record)
            if not cmds.attributeQuery(files.ATTR, node=node, exists=True):
                cmds.addAttr(node, longName=files.ATTR, dataType='string')
            cmds.setAttr(node + '.' + files.ATTR, json.dumps(record), type='string')
            return {'cache_record': record, 'warnings': ['.anim与sidecar文件不能由Maya Undo撤回；仅cache场景属性可撤销，导出还会改Maya动画clipboard。']}
        if args['action'] == 'restore':
            restore(node, args['cache_record'])
            return {'object': node, 'restored': args['cache_record']['path'], 'warnings': ['恢复前清除对象动画键，未限定时间范围或只某层。']}
        if args['action'] == 'clear':
            cmds.cutKey(node, clear=True)
            return {'object': node, 'cleared': True, 'warnings': ['对象动画键全范围删除，层作用域需真实验收。']}
        # Original order: overwrite first, optional cache restore, snapshot then shake.
        if args['overwrite']:
            cmds.cutKey(node, clear=True)
        if args['use_cache']:
            restore(node, args['cache_record'])
        baseline = [[cmds.getAttr(node + '.' + channel, time=frame) for channel in CHANNELS] for frame in args['frames']]
        rng = random.Random(args['seed']) if args['seed'] is not None else random
        keyable = [channel for channel in CHANNELS if args['amounts'][channel] != 0]
        rows = []
        for frame, values, falloff in zip(args['frames'], baseline, args['falloff_samples']):
            updated = [value + falloff * rng.uniform(0, args['amounts'][channel]) for value, channel in zip(values, CHANNELS)]
            cmds.currentTime(frame)
            for channel, value in zip(CHANNELS[3:], updated[3:]):
                cmds.setAttr(node + '.' + channel, value)
            cmds.setAttr(node + '.translate', *updated[:3], type='double3')
            cmds.setKeyframe(node, at=keyable)
            rows.append({'frame': frame, 'falloff': falloff, 'values': dict(zip(CHANNELS, updated))})
        return {'object': node, 'samples': rows, 'keyed_channels': keyable, 'warnings': ['原uniform(0,amount)为正向偏移而非对称噪声，六TR都会setAttr，仅非零amount通道打键；全对象Overwrite/Cache恢复会清旧键。']}
    finally:
        errors = []
        try:
            for callback in (lambda: cmds.playbackOptions(**playback), lambda: cmds.currentTime(time), lambda: cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True)):
                try:
                    callback()
                except Exception as error:
                    errors.append(str(error))
        finally:
            _ACTIVE = False
        if errors:
            raise RuntimeError('恢复时间/选择失败，请检查并Undo: ' + '; '.join(errors))
