from . import runtime as r


class Commands:
    def __getattr__(self, name):
        c = r.mc()
        function = getattr(c, name)
        def call(*args, **kwargs):
            query = kwargs.get('query') or kwargs.get('q')
            if name in ('cutKey', 'setKeyframe', 'keyframe', 'keyTangent', 'undoInfo') and not query:
                if not r._ACTIVE:
                    raise RuntimeError('关键帧写入须经KeyframeReductionTool.run')
                if name != 'undoInfo':
                    if not args or not isinstance(args[0], str) or c.ls(args[0], uuid=True)[0] not in r._CURVES:
                        raise ValueError('曲线超出已验证范围')
            return function(*args, **kwargs)
        return call


cmds = Commands()
