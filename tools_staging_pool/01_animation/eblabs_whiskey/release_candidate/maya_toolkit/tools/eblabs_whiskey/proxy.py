"""Native suite command adapter; UI remains native, writes require validated scope."""
from maya import cmds as real_cmds, mel as real_mel

WRITE_COMMANDS = {'setAttr', 'setKeyframe', 'cutKey', 'pasteKey', 'scaleKey', 'snapKey', 'keyTangent', 'keyframe', 'filterCurve', 'disconnectAttr', 'connectAttr', 'delete', 'animLayer'}


class Commands:
    def __getattr__(self, name):
        callback = getattr(real_cmds, name)

        def invoke(*args, **kwargs):
            from . import runtime as r
            if name == 'undoInfo':
                # Framework owns chunks; native drag/Undo-off may not change it.
                return callback(*args, **kwargs) if kwargs.get('q') or kwargs.get('query') else None
            if name == 'autoKeyframe':
                if kwargs.get('q') or kwargs.get('query'):
                    return r._AUTO if r._ACTIVE else callback(*args, **kwargs)
                r.require_active()
                return callback(*args, **kwargs)
            if r._ACTIVE and r._MODE == 'api':
                if name == 'getPanel' and kwargs.get('withFocus') and r._ARGS.get('camera'):
                    return 'mtbWK_headlessCameraPanel'
                if name == 'modelEditor' and kwargs.get('camera') and (kwargs.get('q') or kwargs.get('query')) and r._ARGS.get('camera'):
                    return r._ARGS['camera']
                if name == 'channelBox' and (kwargs.get('q') or kwargs.get('query')):
                    return list(r._ARGS['attributes'])
                if name == 'confirmDialog':
                    return 'Yes'
                if name == 'layoutDialog':
                    return 'TrueLeaveFirst' if r._ARGS['leave_first'] else 'TrueLeaveNone'
                if name == 'timeControl':
                    # No highlighted interval in API; original full playback behavior.
                    return '0:1'
                if name == 'progressBar':
                    return False if kwargs.get('isCancelled') else None
                if name == 'floatSlider':
                    return r._ARGS['value'] if kwargs.get('query') or kwargs.get('q') else None
            if real_cmds.about(batch=True) and name in ('waitCursor', 'progressBar'):
                return False if kwargs.get('isCancelled') else None
            if name in WRITE_COMMANDS and not (kwargs.get('q') or kwargs.get('query')):
                r.require_active()
                try:
                    r.check_write(name, args, kwargs)
                    return callback(*args, **kwargs)
                except Exception as error:
                    r._ERRORS.append(str(error))
                    raise
            return callback(*args, **kwargs)

        return invoke


class Mel:
    def eval(self, command):
        from . import runtime as r
        if r._ACTIVE and r._MODE == 'api' and '$gMainProgressBar' in command:
            return 'mtbWK_headlessProgress'
        if r._ACTIVE and r._MODE == 'api' and '$gPlayBackSlider' in command:
            return 'mtbWK_headlessTime'
        if command.startswith('keyTangent -global'):
            r.require_active()
        return real_mel.eval(command)


cmds, mel = Commands(), Mel()
