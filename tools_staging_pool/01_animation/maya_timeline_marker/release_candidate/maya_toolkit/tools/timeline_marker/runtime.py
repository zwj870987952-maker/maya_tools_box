"""Scene API and undo command loader; GUI remains lazy. GPL-3.0-or-later adaptation."""
import json
from pathlib import Path
import sys
from . import model

ACTIVE = False
COMMAND = 'mtkTimelineMarkerData'
KEY = 'timelineMarkers'


def widget():
    module = sys.modules.get(__package__ + '.native.ui')
    return getattr(module, 'TIMELINE_MARKER', None)


def read_scene():
    from maya import cmds
    stored = cmds.fileInfo(KEY, query=True) or []
    if not stored:
        return model.empty()
    if len(stored) != 1 or len(stored[0]) > 16000000:
        raise ValueError('timelineMarkers metadata过大或含多值')
    return model.decode(stored[0])


def ensure_plugin():
    from maya import cmds
    expected = Path(__file__).with_name('undo_plugin.py').resolve()
    for name in cmds.pluginInfo(query=True, listPlugins=True) or []:
        commands = cmds.pluginInfo(name, query=True, command=True) or []
        if COMMAND in commands:
            if Path(cmds.pluginInfo(name, query=True, path=True)).resolve() != expected:
                raise RuntimeError('同名marker命令来自其他插件，拒绝覆盖')
            return name
    names = cmds.loadPlugin(str(expected), quiet=True)
    name = names[0] if isinstance(names, list) else names
    if COMMAND not in (cmds.pluginInfo(name, query=True, command=True) or []):
        raise RuntimeError('marker undo命令未注册')
    return name


def notify():
    w = widget()
    if w is not None:
        w.readFromCurrentScene()


def execute(a):
    global ACTIVE
    from maya import cmds
    action = a['action']
    if action == 'inspect':
        return {'markers': a['before'], 'count': len(a['before']['frames'])}
    if action in ('open_ui', 'close_ui', 'hotkey'):
        from .native import ui
        if action == 'open_ui':
            ui.install()
        elif action == 'close_ui':
            ui.uninstall()
        else:
            from .native.hotkey import hotkey
            hotkey(a['hotkey_action'])
        return {'ui_open': widget() is not None, 'action': action}
    if a['before'] == a['after']:
        return {'markers': a['before'], 'count': len(a['before']['frames']), 'changed': False}
    ACTIVE = True
    try:
        plugin = ensure_plugin()
        getattr(cmds, COMMAND)(json.dumps(a['after'], ensure_ascii=True))
        return {'markers': read_scene(), 'count': len(a['after']['frames']), 'changed': True, 'plugin': plugin}
    finally:
        ACTIVE = False
        notify()


def run_api(**kwargs):
    from .tool import TimelineMarkerTool
    result = TimelineMarkerTool().run(**kwargs)
    if not result.success:
        raise RuntimeError(result.message)
    return result


class CommandsAdapter:
    def add(self, frame, color, comment=''):
        return run_api(action='add', frames=[frame], color=color, comment=comment)

    def remove(self, frame):
        return run_api(action='remove', frames=[frame])

    def clear(self):
        return run_api(action='clear')

    def addFromUI(self):
        w = widget()
        if w is None:
            raise ValueError('打开候选GUI后再使用hotkey add')
        return w.addFromUI()

    def removeFromUI(self):
        w = widget()
        if w is None:
            raise ValueError('打开候选GUI后再使用hotkey remove')
        return w.removeFromUI()
