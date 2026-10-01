"""Own one optional Maya progress window; batch execution has no GUI calls."""
from contextlib import contextmanager
from maya import cmds


class Commands:
    owned = False
    def progressWindow(self, **kwargs):
        if cmds.about(batch=True):
            return False
        if kwargs.get('query'):
            return cmds.progressWindow(**kwargs) if self.owned else False
        if kwargs.get('endProgress'):
            if self.owned:
                cmds.progressWindow(endProgress=True)
                self.owned = False
            return
        if kwargs.get('edit'):
            if self.owned:
                return cmds.progressWindow(**kwargs)
            return
        if self.owned:
            self.progressWindow(endProgress=True)
        self.owned = bool(cmds.progressWindow(**kwargs))
        if not self.owned:
            raise ValueError('Another Maya progress window is active')
        return self.owned

commands = Commands()


@contextmanager
def cleanup():
    try:
        yield
    finally:
        commands.progressWindow(endProgress=True)
