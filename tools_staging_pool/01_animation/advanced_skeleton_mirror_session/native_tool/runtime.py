"""Only native invocation and time/key orchestration; no mirror mapping math.

AdvancedSkeleton source remains in the user's local installation, unmodified.
Source loading and option windows are outside Maya scene Undo.
"""
import json
import math
from pathlib import Path
import re
import time
import uuid

CONFIG = 'mayaToolkitAdvancedSkeletonMirrorSource'
SIDES = {'swap': 'asMOSideFlip', 'left_to_right': 'asMOSideL2R', 'right_to_left': 'asMOSideR2L'}
SPACES = {'world': 'asMOSpaceWorld', 'main': 'asMOSpaceMain', 'root': 'asMOSpaceCenter'}
OPTIONS = ('asMOSide', 'asMOSpace', 'asMOAxis', 'asMOSelOnly')
ALLOWED = {'action', 'namespace', 'source_path', 'side', 'axis', 'space', 'time_range'}


def maya():
    import maya.cmds as cmds
    import maya.mel as mel
    return cmds, mel


def source_info(path):
    source = Path(path).expanduser().resolve()
    if source.suffix.lower() != '.mel' or not source.is_file():
        raise ValueError('请指定原版 AdvancedSkeleton.mel 文件。')
    text = source.read_text(encoding='utf-8-sig', errors='replace')
    version = re.search(r'//\s*Version\s+([\d.]+)', text[:1800])
    if not version or not re.search(r'global proc asMirror\s*\(', text):
        raise ValueError('文件没有可识别的 ADV 版本或 asMirror 入口。')
    if float(version.group(1)) < 6.0:
        raise ValueError('此封装使用 ADV 6.x 原生 Mirror；请指定新版源文件，避免回退到旧版 5.740。')
    return str(source).replace('\\', '/'), version.group(1)


def configured_source():
    cmds, mel = maya()
    if cmds.optionVar(exists=CONFIG):
        return cmds.optionVar(q=CONFIG)
    found = mel.eval('whatIs asMirror')
    prefix = 'Mel procedure found in: '
    return found[len(prefix):] if found.startswith(prefix) else ''


def configure(path):
    """Explicit local preference write; does not load ADV or alter the scene."""
    source, version = source_info(path)
    cmds, _ = maya()
    cmds.optionVar(sv=(CONFIG, source))
    return {'source_path': source, 'version': version}


def resolve_namespace(namespace):
    cmds, _ = maya()
    candidates = sorted({n.rsplit(':', 1)[0] + ':' if ':' in n else ''
                         for n in (cmds.ls('*:ControlSet', 'ControlSet', type='objectSet', recursive=True) or [])})
    if namespace is not None:
        if not isinstance(namespace, str) or not re.fullmatch(r'[\w:]*', namespace):
            raise ValueError('namespace 必须是明确的命名空间，不接受路径、通配符或代码。')
        prefix = namespace.strip(':') + ':' if namespace.strip(':') else ''
        if prefix not in candidates:
            raise ValueError('找不到该角色的 ControlSet: ' + prefix)
        return prefix
    selected = cmds.ls(sl=True, long=True) or []
    matches = [ns for ns in candidates if any(
        node.split('|')[-1].startswith(ns) if ns else ':' not in node.split('|')[-1]
        for node in selected)]
    if len(matches) == 1:
        return matches[0]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError('存在多个角色或未找到角色，请指定 namespace 或只选择一个角色。')


def preflight(**kwargs):
    unknown = set(kwargs) - ALLOWED
    if unknown:
        raise ValueError('未知参数: ' + ', '.join(sorted(unknown)))
    cmds, _ = maya()
    action = kwargs.get('action', 'mirror')
    side, axis, space = kwargs.get('side', 'swap'), kwargs.get('axis', 'X'), kwargs.get('space', 'main')
    if action not in ('mirror', 'mirror_animation', 'open_options') or side not in SIDES or axis not in ('X', 'Y', 'Z') or space not in SPACES:
        raise ValueError('无效的 action/side/axis/space。')
    if not cmds.undoInfo(q=True, state=True):
        raise ValueError('请先启用 Maya Undo。')
    if cmds.about(batch=True) or cmds.play(q=True, state=True):
        raise ValueError('请在未播放动画的 Maya GUI 中调用。')
    if cmds.getModifiers() == 5:
        raise ValueError('请松开 Ctrl+Shift；ADV 会将这个组合键解释为创建 Shelf 按钮。')
    source, version = source_info(kwargs.get('source_path') or configured_source())
    ns = resolve_namespace(kwargs.get('namespace'))
    controls = cmds.sets(ns + 'ControlSet', q=True) or []
    if not controls or any(not cmds.objExists(n) or cmds.nodeType(n) not in ('transform', 'joint') for n in controls):
        raise ValueError('ControlSet 必须包含明确的角色控制器。')
    if any(cmds.lockNode(n, q=True, lock=True)[0] for n in controls):
        raise ValueError('ControlSet 中有锁定节点。')
    if cmds.objExists('flipGroup'):
        raise ValueError('场景已有 flipGroup；ADV 原生过程使用该名称，请先处理名称冲突。')
    if space != 'world' and not cmds.objExists(ns + ('Main' if space == 'main' else 'RootX_M')):
        raise ValueError('镜像空间所需控制器不存在。')
    frame_range = kwargs.get('time_range')
    if frame_range is not None and action != 'mirror_animation':
        raise ValueError('time_range 仅用于 mirror_animation；Mirror 原生入口处理当前姿态。')
    control_names = set(controls)
    layers = [layer for layer in (cmds.ls(type='animLayer') or [])
              if any(plug.rsplit('.', 1)[0] in control_names
                     for plug in (cmds.animLayer(layer, q=True, attribute=True) or []))]
    if action == 'mirror_animation':
        if layers:
            raise ValueError('逐帧扩展尚不支持动画层。请先在副本中合并层；当前姿态仍可按原生行为使用。')
        if frame_range is None:
            frame_range = [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
        if not isinstance(frame_range, (list, tuple)) or len(frame_range) != 2 or any(
                isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x != int(x) for x in frame_range):
            raise ValueError('time_range 必须是两个整数帧。')
        frame_range = [int(x) for x in frame_range]
        if frame_range[0] > frame_range[1] or frame_range[1] - frame_range[0] > 5000:
            raise ValueError('时间范围必须递增且不超过 5001 帧。')
    return {'action': action, 'namespace': ns, 'source_path': source, 'native_version': version,
            'native_entrypoint': 'asMirror', 'side': side, 'axis': axis, 'space': space,
            'time_range': frame_range, 'control_count': len(controls),
            'animation_layers': layers}


def _set_options(plan):
    cmds, _ = maya()
    values = {'asMOSide': SIDES[plan['side']], 'asMOSpace': SPACES[plan['space']],
              'asMOAxis': 'asMOAxis' + plan['axis'], 'asMOSelOnly': 'asMOSelOnlyAll'}
    for name, value in values.items():
        cmds.optionVar(sv=(name, value))
        if cmds.radioCollection(name + 'RadioCollection', exists=True):
            cmds.radioCollection(name + 'RadioCollection', e=True, select=value)


def _holder(ns):
    cmds, _ = maya()
    name = 'mtbAdvMirror_' + uuid.uuid4().hex[:10]
    cmds.window(name, title='ADV Mirror context')
    cmds.columnLayout()
    cmds.optionMenu(name + 'OptionMenu')
    cmds.menuItem(label=ns or ':')
    cmds.text(name + 'ControlSetsText', label='ControlSet')
    return name


def execute(**kwargs):
    cmds, mel = maya()
    plan = preflight(**kwargs)
    started = time.perf_counter()
    current_time, selection = cmds.currentTime(q=True), cmds.ls(sl=True, long=True) or []
    auto = cmds.autoKeyframe(q=True, state=True)
    options = {name: cmds.optionVar(q=name) if cmds.optionVar(exists=name) else None for name in OPTIONS}
    radios = {name: cmds.radioCollection(name + 'RadioCollection', q=True, select=True)
              for name in OPTIONS if cmds.radioCollection(name + 'RadioCollection', exists=True)}
    holder = None
    keep_options = plan['action'] == 'open_options'
    opened = False
    try:
        # Load the complete ORIGINAL script. Do not install a shelf or call its main UI.
        actual = mel.eval('whatIs asMirror')
        if plan['source_path'].lower() not in actual.replace('\\', '/').lower():
            mel.eval('source ' + json.dumps(plan['source_path']) + ';')
        holder = _holder(plan['namespace'])
        _set_options(plan)
        if keep_options:
            mel.eval('asMirrorOptions ' + json.dumps(holder) + ';')
            _set_options(plan)
            # Native button needs this hidden namespace holder until its window closes.
            cmds.scriptJob(uiDeleted=['asMirrorOptions', lambda h=holder: cmds.deleteUI(h) if cmds.window(h, exists=True) else None], runOnce=True)
            opened = True
            return dict(plan, window='asMirrorOptions', state='native_options_open')
        cmds.refresh(suspend=True)
        if plan['action'] == 'mirror':
            mel.eval('asMirror ' + json.dumps(holder) + ';')
            changed = None
        else:
            cmds.autoKeyframe(state=False)
            changed = _animation(plan, holder)
        return dict(plan, changed_channels=changed, native_seconds=round(time.perf_counter() - started, 4),
                    state='native_call_completed', custom_mapping=False)
    finally:
        # Keep scene Undo intact; UI/options and refresh should not hide the one operation.
        if not opened:
            for name, value in options.items():
                if value is None:
                    cmds.optionVar(remove=name)
                else:
                    cmds.optionVar(sv=(name, value))
            for name, value in radios.items():
                if cmds.radioCollection(name + 'RadioCollection', exists=True):
                    cmds.radioCollection(name + 'RadioCollection', e=True, select=value)
            if holder and cmds.window(holder, exists=True):
                cmds.deleteUI(holder)
        cmds.autoKeyframe(state=auto)
        cmds.currentTime(current_time)
        if selection:
            cmds.select(selection, r=True)
        else:
            cmds.select(clear=True)
        cmds.refresh(suspend=False)


def _animation(plan, holder):
    """Snapshot input first so previously written keys cannot affect later input.

    Pairing, sign changes and world-space solving are entirely native asMirror.
    Uses the same original key/curve layout outside the requested interval.
    """
    cmds, mel = maya()
    controls = cmds.sets(plan['namespace'] + 'ControlSet', q=True)
    plugs = [n + '.' + a for n in controls for a in (cmds.listAttr(n, k=True, scalar=True) or [])
             if cmds.getAttr(n + '.' + a, settable=True)]
    start, end = plan['time_range']
    frames = range(start, end + 1)
    original = {f: {p: cmds.getAttr(p, time=f) for p in plugs} for f in frames}
    mirrored = {}
    try:
        for f in frames:
            cmds.currentTime(f)
            for p, value in original[f].items():
                if abs(cmds.getAttr(p) - value) > 1e-9:
                    cmds.setAttr(p, value)
            mel.eval('asMirror ' + json.dumps(holder) + ';')
            mirrored[f] = {p: cmds.getAttr(p) for p in plugs}
    finally:
        # Restore pose overrides before changing curves, including on native errors.
        last = cmds.currentTime(q=True)
        if last in original:
            for p, value in original[last].items():
                if cmds.getAttr(p, settable=True):
                    cmds.setAttr(p, value, clamp=True)
        cmds.currentTime(last + 1)
        cmds.currentTime(last)
    changed = [p for p in plugs if any(abs(original[f][p] - mirrored[f][p]) > 1e-6 for f in frames)]
    for p in changed:
        for guard in (start - 1, end + 1):
            if not cmds.keyframe(p, q=True, time=(guard, guard), kc=True):
                if cmds.listConnections(p, s=True, d=False, type='animCurve'):
                    cmds.setKeyframe(p, time=guard, insert=True)
                else:
                    cmds.setKeyframe(p, time=guard, value=original[start][p])
        cmds.cutKey(p, time=(start, end), clear=True)
        discrete = cmds.getAttr(p, type=True) in ('bool', 'enum', 'long', 'short', 'byte')
        for f in frames:
            cmds.setKeyframe(p, time=f, value=mirrored[f][p], inTangentType='linear',
                             outTangentType='step' if discrete else 'linear')
    return len(changed)
