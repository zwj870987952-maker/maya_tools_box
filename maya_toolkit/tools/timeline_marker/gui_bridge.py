"""Private timeline integration, preserving handlers/menu ownership. GUI not offline certified."""
import importlib
import json
import sys
import uuid
from maya import OpenMaya, cmds, mel
from . import runtime

_HOOKS = {}


def read(widget):
    try:
        data = runtime.read_scene()
    except Exception as error:
        cmds.warning('Timeline Marker metadata保留原样: ' + str(error))
        data = runtime.model.empty()
    widget.frames, widget.colors, widget.comments = data['frames'], data['colors'], data['comments']
    widget.update()


def write(widget, **kwargs):
    result = runtime.run_api(**kwargs)
    read(widget)
    return result


def release(widget):
    timeline = widget.utils.getMayaTimeline() if hasattr(widget, 'utils') else importlib.import_module(__package__ + '.native.utils').getMayaTimeline()
    cmds.timeControl(timeline, edit=True, endScrub=True)
    begin = widget._range
    widget._range = None
    if not begin or not widget.menu.moveA.isChecked():
        return
    utils = importlib.import_module(__package__ + '.native.utils')
    end = utils.getTimelineRange()
    if not end or not cmds.timeControl(timeline, query=True, rangeVisible=True) or len(begin) == 1 and len(end) != 1:
        return
    return write(widget, action='remap', old_range=[begin[0], begin[-1]], new_range=[end[0], end[-1]])


def dispatch(token, event):
    record = _HOOKS.get(token)
    if record is None:
        return
    widget, old, own, timeline = record
    previous = old[event]
    if event == 'press':
        if previous:
            mel.eval(previous)
        widget.pressCommand()
    else:
        try:
            widget.releaseCommand()
        finally:
            if previous:
                mel.eval(previous)


def add_callbacks(widget):
    if getattr(widget, '_callbacks', []):
        raise RuntimeError('callbacks已安装')
    widget._callbacks = []
    widget._token = None
    utils = importlib.import_module(__package__ + '.native.utils')
    timeline = utils.getMayaTimeline()
    old = {k: cmds.timeControl(timeline, query=True, **{k + 'Command': True}) or '' for k in ('press', 'release')}
    if any(not isinstance(v, str) for v in old.values()):
        raise RuntimeError('非MEL callback不能安全保留，拒绝覆盖')
    token = uuid.uuid4().hex
    own = {}
    for event in old:
        code = 'import importlib; importlib.import_module(' + repr(__name__) + ').dispatch(' + repr(token) + ',' + repr(event) + ')'
        own[event] = 'python(' + json.dumps(code) + ');'
    _HOOKS[token] = (widget, old, own, timeline)
    widget._token = token
    try:
        widget.newID = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, widget.readFromCurrentScene)
        widget._callbacks.append(widget.newID)
        widget.openID = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, widget.readFromCurrentScene)
        widget._callbacks.append(widget.openID)
        for event in ('Undo', 'Redo'):
            widget._callbacks.append(OpenMaya.MEventMessage.addEventCallback(event, widget.readFromCurrentScene))
        cmds.timeControl(timeline, edit=True, pressCommand=own['press'], releaseCommand=own['release'])
    except Exception:
        remove_callbacks(widget)
        raise


def remove_callbacks(widget):
    for callback in getattr(widget, '_callbacks', []):
        try:
            OpenMaya.MMessage.removeCallback(callback)
        except RuntimeError as error:
            cmds.warning('Marker callback cleanup: ' + str(error))
    widget._callbacks = []
    widget.newID = widget.openID = None
    token = getattr(widget, '_token', None)
    record = _HOOKS.pop(token, None)
    widget._token = None
    if record:
        _, old, own, timeline = record
        if cmds.timeControl(timeline, exists=True):
            for event in old:
                current = cmds.timeControl(timeline, query=True, **{event + 'Command': True}) or ''
                if current == own[event]:
                    cmds.timeControl(timeline, edit=True, **{event + 'Command': old[event]})
                elif current != old[event]:
                    cmds.warning('Marker卸载保留后来设置的' + event + 'Command')


def install(module):
    if module.TIMELINE_MARKER is not None:
        raise RuntimeError('候选Timeline Marker已打开')
    if cmds.about(batch=True):
        raise RuntimeError('真实Maya GUI需要')
    parent = module.utils.getTimeline()
    if parent is None:
        raise RuntimeError('未找到Maya时间轴widget')
    if parent.findChild(module.utils.QWidget, 'timelineMarker') is not None:
        raise RuntimeError('原版Timeline Marker仍运行，请先关闭原版')
    widget = module.TimelineMarker()
    try:
        layout = parent.layout()
        if layout is None:
            layout = module.utils.QVBoxLayout(parent)
            layout.setContentsMargins(0, 0, 0, 0)
        widget.setParent(parent)
        layout.addWidget(widget)
        module.TIMELINE_MARKER = widget
        widget.destroyed.connect(lambda *args: remove_callbacks(widget))
        widget.show()
    except Exception:
        widget.deleteLater()
        raise


def uninstall(module):
    widget = module.TIMELINE_MARKER
    if widget is None:
        raise RuntimeError('候选Timeline Marker未打开')
    module.TIMELINE_MARKER = None
    widget.hide()
    widget.deleteLater()


def delete_menu(menu):
    for button in list(menu.buttons):
        menu.menu.removeAction(button)
        button.deleteLater()
    menu._buttons = []
