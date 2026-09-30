# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.
from . import decorators

@decorators.getTimelineMarker
def hotkey(timelineMarker, action):
    from ..runtime import widget
    if action not in ('add', 'remove', 'clear'):
        raise ValueError('未知hotkey action')
    if widget() is None:
        raise ValueError('先打开候选Timeline Marker')
    if action == 'add':
        return timelineMarker.addFromUI()
    if action == 'remove':
        return timelineMarker.removeFromUI()
    return timelineMarker.clear()
