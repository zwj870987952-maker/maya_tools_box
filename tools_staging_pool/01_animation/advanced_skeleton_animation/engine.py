"""Call original ADV procedures without changing vendor source or algorithms."""
import json
import math
from pathlib import Path
import re
import time
import uuid

from maya_toolkit.tools.advanced_skeleton_mirror import runtime as mirror
from maya_toolkit.core import UndoChunkContext
from .catalog import OPERATIONS, RANGE_OPERATIONS
from maya_toolkit.core import advanced_skeleton as discovery

JOBS = {}


def project_source():
    root = next(p for p in Path(__file__).resolve().parents if (p / 'maya_toolkit').is_dir())
    return root / 'tools_closed_source_pool/02_rigging_hierarchy/advanced_skeleton_v6_640/vendor/AdvancedSkeleton.mel'


def inspect_source(path=None):
    info = discovery.resolve(path)
    return info['source_path'], info['version']


def load_source(source):
    _, mel = mirror.maya()
    expected = 'Mel procedure found in: ' + source
    if mel.eval('whatIs asMirror').replace('\\', '/').lower() != expected.lower():
        mel.eval('source ' + json.dumps(source) + ';')
    return mel.eval('asGetScriptLocation()')


def _layers(cmds, controls):
    names = {n.split('|')[-1] for n in controls}
    return [layer for layer in (cmds.ls(type='animLayer') or []) if any(
        p.rsplit('.', 1)[0].split('|')[-1] in names
        for p in (cmds.animLayer(layer, q=True, attribute=True) or []))]


def preflight(operation='catalog', namespace=None, nodes=None, limb=None, time_range=None,
              control_set='ControlSet', source_path=None, accept_undo_history_loss=False, **unknown):
    if unknown:
        raise ValueError('未知参数: ' + ', '.join(sorted(unknown)))
    if not isinstance(operation, str) or operation not in set(OPERATIONS) | {'catalog', 'status'}:
        raise ValueError('未知 operation；使用 catalog 查看固定入口。')
    if source_path is not None and not isinstance(source_path, str):
        raise ValueError('source_path 必须为字符串。')
    source, version = inspect_source(source_path)
    base = dict(operation=operation, source_path=source, native_version=version)
    if operation in ('catalog', 'status'):
        return base
    cmds, _ = mirror.maya()
    if cmds.about(batch=True) or cmds.play(q=True, state=True) or not cmds.undoInfo(q=True, state=True):
        raise ValueError('需要停止播放的 Maya GUI，并启用 Undo。')
    if cmds.getModifiers():
        raise ValueError('请松开 Shift/Ctrl/Alt；原生入口会根据修饰键改变操作含义。')
    if control_set not in ('ControlSet', 'FaceControlSet'):
        raise ValueError('control_set 仅支持 ControlSet 或 FaceControlSet。')
    ns = mirror.resolve_namespace(namespace)
    if not cmds.objExists(ns + control_set):
        raise ValueError('找不到 ' + ns + control_set)
    controls = cmds.sets(ns + control_set, q=True) or []
    if not controls:
        raise ValueError('控制器集合为空。')
    spec = OPERATIONS[operation]
    discovery.resolve(source, required_procedures=[spec['proc']])
    conflicts = [p for p in (cmds.pluginInfo(q=True,listPlugins=True) or []) if 'animrescue' in p.lower()]
    if conflicts and spec['effect'] != 'ui':
        raise ValueError('本轮测试遇到 animRescue 回调崩溃。检测到 '+', '.join(conflicts)+
                         '；API 暂停场景操作，请在不加载该插件的独立环境使用。不会自动卸载插件。')
    if not isinstance(accept_undo_history_loss, bool):
        raise ValueError('accept_undo_history_loss 必须是布尔值。')
    if operation in ('pose_paste', 'animation_paste') and not accept_undo_history_loss:
        raise ValueError('ADV 原生粘贴会清空 Maya 撤销历史。明确接受该影响时传 accept_undo_history_loss=True；建议在场景副本中使用。')
    if nodes is not None and (not isinstance(nodes, (tuple, list)) or any(not isinstance(n, str) for n in nodes)):
        raise ValueError('nodes 必须是有序节点名称数组。')
    selection = list(nodes) if nodes is not None else (cmds.ls(sl=True, long=True) or [])
    if len(selection) < spec['selection_min'] or ('exact_selection' in spec and len(selection) != spec['exact_selection']):
        raise ValueError('所需选择数量不满足: ' + spec['requirements'])
    for n in selection:
        matches = cmds.ls(n, long=True) or []
        if len(matches) != 1 or any(c in n for c in '*?[];"\n') or cmds.nodeType(matches[0]) not in ('transform', 'joint'):
            raise ValueError('节点必须是唯一且存在的 transform/joint: ' + n)
    if spec['selection_min']:
        targets = selection[-1:] if operation.startswith('parent_constraint') or operation == 'switch_pivot' else selection
        if any((not n.split('|')[-1].startswith(ns)) if ns else (':' in n.split('|')[-1]) for n in targets):
            raise ValueError('操作目标不属于指定角色。')
    if spec['binding'] in ('limb', 'bake_one', 'bake_zero'):
        if not isinstance(limb, str) or not re.fullmatch(r'[A-Za-z0-9_]+_[LRM]', limb):
            raise ValueError('请明确指定 limb，例如 Arm_L、Leg_R 或 Spine_M。')
        if not cmds.objExists(ns + 'FKIK' + limb + '.FKIKBlend'):
            raise ValueError('目标肢体不存在: ' + ns + 'FKIK' + limb)
    elif limb is not None:
        raise ValueError('该 operation 不接受 limb。')
    if time_range is not None:
        if operation not in RANGE_OPERATIONS:
            raise ValueError('该原生入口不支持 time_range；不能把全曲线操作冒充范围操作。')
        if not isinstance(time_range, (list, tuple)) or len(time_range) != 2 or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v != int(v) for v in time_range):
            raise ValueError('time_range 必须是两个整数帧。')
        if time_range[0] > time_range[1] or time_range[1] - time_range[0] > 5000:
            raise ValueError('时间范围无效或超过5001帧。')
    layers = _layers(cmds, controls)
    if layers and (operation.startswith('bake_') and operation != 'bake_options' or operation in ('animation_copy', 'animation_paste', 'dynamics_bake')):
        raise ValueError('该批量操作尚不支持目标动画层: ' + ', '.join(layers))
    if operation in ('pose_reset', 'pose_tpose'):
        if not cmds.objExists(ns + ('faceBuildPose' if control_set == 'FaceControlSet' else 'buildPose') + '.udAttr'):
            raise ValueError('缺少 ADV 原生 buildPose.udAttr。')
    if operation == 'mocap_library' and cmds.upAxis(q=True, axis=True) != 'y':
        raise ValueError('原生 MoCapLibrary 需要 Y-up。')
    if operation == 'connect_mocapx':
        from .mocapx_contract import validate
        validate(cmds, ns)
    if operation in ('pose_copy', 'animation_copy') and cmds.objExists('poserAnimationInfo'):
        raise ValueError('场景已存在原生剪贴板临时节点 poserAnimationInfo。')
    if operation in ('pose_paste', 'animation_paste'):
        if cmds.objExists('tempXform') or cmds.namespace(exists='Selector'):
            raise ValueError('原生粘贴临时名称 tempXform 或 Selector 与场景冲突。')
    if operation == 'pivot_control':
        for n in selection:
            if cmds.objExists(n + '_PivotControl') or any(cmds.listConnections(n+'.'+a, s=True, d=False) for a in ('rotatePivot', 'scalePivot')):
                raise ValueError('已有 PivotControl 或 pivot 输入连接: ' + n)
    if operation == 'switch_pivot' or operation == 'parent_constraint_extra':
        parents = cmds.listRelatives(selection[-1], p=True) or []
        if not parents or 'Extra' not in parents[0]:
            raise ValueError('目标控制器需要原生 Extra 父节点。')
    if operation in ('bake_controls_to_extra', 'bake_extra_to_controls') and not any('Extra' in n for n in controls):
        raise ValueError('目标集合没有 Extra 控制器。')
    if operation == 'bake_quick_ik' and not cmds.objExists('QuickIK'):
        raise ValueError('场景尚未建立 QuickIK。')
    if operation == 'dynamics_bake' and not cmds.objExists('Dynamics'):
        raise ValueError('场景尚未建立 ADV Dynamics。')
    if operation == 'dynamics_bake' and cmds.objExists('BakeXforms'):
        raise ValueError('已存在原生烘焙临时节点 BakeXforms。')
    if operation == 'dynamics_add':
        joints = [ns+n.split('|')[-1][len(ns)+2:] for n in selection
                  if n.split('|')[-1].startswith(ns+'FK')]
        if len(joints) != len(selection) or any(not cmds.objExists(j) or
                not cmds.listRelatives(j, parent=True) for j in joints):
            raise ValueError('Standard Dynamics 需要 FK 控制器、对应变形关节及其父节点。')
    if operation in ('mirror', 'mirror_options') and control_set != 'ControlSet':
        raise ValueError('Mirror 当前封装只验证过 ControlSet。')
    return dict(base, namespace=ns, nodes=selection, limb=limb, time_range=time_range,
                control_set=control_set, control_count=len(controls), animation_layers=layers,
                **spec)


def _command(plan, holder):
    q = json.dumps
    binding, proc = plan['binding'], plan['proc']
    if binding == 'none':
        return proc + ';'
    if binding == 'limb':
        return proc + ' ' + q(plan['namespace']) + ' {' + q('FKIK' + plan['limb']) + '};'
    if binding == 'nodes':
        # asKey resolves a short selector name; full DAG names already resolve directly.
        return proc + ' "" {' + ','.join(q(n) for n in plan['nodes']) + '};'
    if binding.startswith('bake_'):
        return proc + ' ' + q(plan['limb']) + (' 1 ' if binding == 'bake_one' else ' 0 ') + q(holder) + ';'
    return proc + ' ' + q(holder) + (' 1' if binding == 'ui_one' else ' 0' if binding == 'ui_zero' else '') + ';'


def _cleanup(holder):
    cmds, _ = mirror.maya()
    if holder and cmds.window(holder, exists=True):
        cmds.deleteUI(holder)


def _invoke(plan, holder):
    cmds, mel = mirror.maya()
    old_selection = cmds.ls(sl=True, long=True) or []
    old_time = cmds.currentTime(q=True)
    auto = cmds.autoKeyframe(q=True, state=True)
    playback = {k: cmds.playbackOptions(q=True, **{k: True}) for k in ('minTime', 'maxTime', 'animationStartTime', 'animationEndTime')}
    try:
        if plan['nodes']:
            cmds.select(plan['nodes'], r=True)
        else:
            cmds.select(clear=True)
        if plan['time_range']:
            a, b = plan['time_range']
            cmds.playbackOptions(animationStartTime=a, animationEndTime=b, minTime=a, maxTime=b)
        return mel.eval(_command(plan, holder))
    finally:
        # Keep Interactive Playback running when that is the requested operation.
        if plan['execution_mode'] != 'interactive_playback':
            cmds.currentTime(old_time)
        cmds.autoKeyframe(state=auto)
        if plan['time_range']:
            cmds.playbackOptions(**playback)
        valid = [n for n in old_selection if cmds.objExists(n)]
        cmds.select(valid, r=True) if valid else cmds.select(clear=True)
        if plan['binding'].startswith('bake_'):
            mel.eval('global int $asBakeFKIK; $asBakeFKIK=0;')


def execute(**kwargs):
    plan = preflight(**kwargs)
    op = plan['operation']
    if op == 'catalog':
        return dict(plan, operations=OPERATIONS, state='catalog', verified_version='6.640',
                    lifecycle='staging', stability='not_passed; animRescue callback crash observed')
    if op == 'status':
        return dict(plan, jobs=dict(JOBS), state='status')
    if plan['binding'] == 'mirror':
        result = mirror.execute(action='open_options' if op == 'mirror_options' else 'mirror',
                                source_path=plan['source_path'], namespace=plan['namespace'])
        return dict(result, operation=op, execution_mode=plan['execution_mode'])
    cmds, mel = mirror.maya()
    load_source(plan['source_path'])
    if not mel.eval('exists ' + plan['proc']):
        raise ValueError('原版缺少入口: ' + plan['proc'])
    holder = mirror._holder(plan['namespace'])
    cmds.text(holder + 'ControlSetsText', e=True, label=plan['control_set'])
    started = time.perf_counter()
    keep = False
    try:
        if plan['execution_mode'] == 'interactive_dialog':
            job = uuid.uuid4().hex
            identity = cmds.ls(plan['namespace'] + plan['control_set'], uuid=True)
            JOBS[job] = {'operation': op, 'state': 'queued', 'completed_effect': False}
            def invoke_later():
                try:
                    if identity != cmds.ls(plan['namespace'] + plan['control_set'], uuid=True):
                        raise ValueError('等待期间角色已更换，已取消调用。')
                    preflight(**kwargs)
                    with UndoChunkContext(chunk_name='ADV_' + op):
                        _invoke(plan, holder)
                    JOBS[job]['state'] = 'native_dialog_returned'
                    # Original MEL returns no acceptance/cancellation flag.
                    JOBS[job]['completed_effect'] = None
                except Exception as exc:
                    JOBS[job].update(state='failed', error=str(exc))
                finally:
                    _cleanup(holder)
            cmds.evalDeferred(invoke_later)
            keep = True
            return dict(plan, state='awaiting_native_dialog', job_id=job, completed_effect=False)
        _invoke(plan, holder)
        if plan['window']:
            if not cmds.window(plan['window'], exists=True):
                raise RuntimeError('原生窗口未创建: ' + plan['window'])
            cmds.scriptJob(uiDeleted=[plan['window'], lambda h=holder: _cleanup(h)], runOnce=True)
            keep = True
        return dict(plan, state='ui_open' if keep else 'playback_started' if plan['effect']=='playback' else 'native_call_returned',
                    completed_effect=False if keep else None, native_seconds=round(time.perf_counter()-started, 4))
    finally:
        if not keep:
            _cleanup(holder)
