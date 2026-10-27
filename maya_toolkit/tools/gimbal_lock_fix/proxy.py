from maya import cmds as real


class Commands:
    def __getattr__(self, name):
        function = getattr(real, name)

        def guarded(*args, **kwargs):
            if name in ('setKeyframe', 'createNode', 'connectAttr', 'keyTangent') and not kwargs.get('q') and not kwargs.get('query'):
                from . import runtime
                runtime.require_active()
                if name in ('createNode', 'connectAttr'):
                    raise RuntimeError('预检要求已有三轴直接曲线，拒绝临时补接图')
                if not args or any(node not in runtime._CURVES for node in args):
                    raise ValueError('写入超出已验证旋转曲线')
            return function(*args, **kwargs)
        return guarded


cmds = Commands()
