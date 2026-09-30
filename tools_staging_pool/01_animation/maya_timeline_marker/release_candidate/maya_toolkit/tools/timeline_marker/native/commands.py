# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.
from . import decorators

@decorators.getTimelineMarker
def add(timelineMarker, frame, color, comment=''):
    return timelineMarker.add(frame, color, comment)

@decorators.getTimelineMarker
def remove(timelineMarker, frames):
    from ..runtime import run_api
    return run_api(action='remove', frames=frames if isinstance(frames, list) else [frames])

@decorators.getTimelineMarker
def clear(timelineMarker):
    return timelineMarker.clear()

@decorators.getTimelineMarker
def set(timelineMarker, frames=[], colors=[], comments=[]):
    from ..runtime import run_api
    return run_api(action='set', frames=frames, colors=colors, comments=comments)
