_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部平滑仅允许SmoothMocapTool.run()')


def execute(args):
    global _ACTIVE
    from maya import cmds
    from . import algorithms
    from .tool import curve_plan
    from .backend import legacy, runtime as backend_runtime, scene
    selection = cmds.ls(selection=True, long=True) or []
    time = cmds.currentTime(query=True)
    refresh = cmds.refresh(query=True, suspend=True)
    paused = None if cmds.about(batch=True) else cmds.ogs(query=True, pause=True)
    selected_keys = {curve: cmds.keyframe(curve, query=True, selected=True, indexValue=True) or [] for curve in (cmds.keyframe(query=True, name=True, selected=True) or [])}
    before_backend_active = backend_runtime._ACTIVE
    locators = []
    rows = []
    try:
        _ACTIVE = True
        if args['action'] == 'smooth_keys':
            rows = args['curve_plan']
            passes = 1
        else:
            backend_runtime._ACTIVE = True
            legacy._options = dict(annotation=args['annotation'], constrain=True, bake_all=args['bake_all'], in_timeline=args['in_timeline'], translate=True, rotate=True)
            # No global/staging scripts directory dependency; full private snapshot.
            legacy.BRSAnimLocGrp = scene.GROUP
            cmds.select(args['joints'], replace=True)
            legacy.objectToLocatorSnap(toGroup=False, forceConstraint=False)
            locators = [scene.locator_for(joint, required=True) for joint in args['joints']]
            curves = cmds.keyframe(locators, query=True, name=True) or []
            rows = curve_plan(curves, False)
            passes = args['strength'] - 1
        before_values = {row['curve']: cmds.keyframe(row['curve'], query=True, timeChange=True) for row in rows}
        for _ in range(passes):
            for row in rows:
                if row['eligible']:
                    algorithms.valueAverage(row['curve'], row['times'])
        if args['action'] == 'smooth_mocap':
            times = sorted(set(cmds.keyframe(locators, query=True, timeChange=True) or []))
            if len(times) < 2:
                raise RuntimeError('私有定位器生成时间键不足')
            legacy.bakeKey(args['joints'], times, inTimeline=False)
            for joint in args['joints']:
                scene.delete_constraints(joint)
            for locator in locators:
                scene.delete_locator(locator)
        return {'action': args['action'], 'passes': passes, 'processed_curves': [row['curve'] for row in rows if row['eligible']], 'source_key_times': before_values,
                'joints': args.get('joints', []), 'skipped_joints': args.get('skipped', []),
                'remaining_private_locators': scene.by_role('locator'), 'retained_blend_nodes': scene.by_role('aux'),
                'warnings': ['端点保持与三点平均按所选键序列，不按时间间隔加权；Mocap按原round/bake/filter行为回写六TR，blend可能保留。']}
    finally:
        errors = []
        def restore_key_selection():
            cmds.selectKey(clear=True)
            for curve, indices in selected_keys.items():
                if cmds.objExists(curve):
                    count = cmds.keyframe(curve, query=True, keyframeCount=True)
                    for index in indices:
                        if index < count:
                            cmds.selectKey(curve, index=(index, index), add=True)
        callbacks = [lambda: cmds.refresh(suspend=refresh), lambda: cmds.currentTime(time), lambda: cmds.select([n for n in selection if cmds.objExists(n)], replace=True) if selection else cmds.select(clear=True), restore_key_selection]
        if paused is not None:
            def restore_pause():
                if cmds.ogs(query=True, pause=True) != paused:
                    cmds.ogs(pause=True)
            callbacks.append(restore_pause)
        try:
            for callback in callbacks:
                try:
                    callback()
                except Exception as error:
                    errors.append(str(error))
        finally:
            _ACTIVE = False
            backend_runtime._ACTIVE = before_backend_active
        if errors:
            raise RuntimeError('状态恢复失败，请检查时间/选择/视口并Undo: ' + '; '.join(errors))
