try:
    reload
except NameError:
    from importlib import reload

import align_objects_rotate
reload(align_objects_rotate)
align_objects_rotate.align_rotate()
