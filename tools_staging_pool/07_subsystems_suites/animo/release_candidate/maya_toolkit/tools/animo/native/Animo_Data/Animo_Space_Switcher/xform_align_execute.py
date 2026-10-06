try:
    reload
except NameError:
    from importlib import reload

import align_objects
reload(align_objects)
align_objects.align()
