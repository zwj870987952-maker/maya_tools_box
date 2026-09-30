# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.
from functools import wraps

def getTimelineMarker(func):
    from ..runtime import CommandsAdapter

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(CommandsAdapter(), *args, **kwargs)
    return wrapper
