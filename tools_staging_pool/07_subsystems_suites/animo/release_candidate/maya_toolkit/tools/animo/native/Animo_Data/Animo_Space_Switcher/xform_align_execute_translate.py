try:
    reload
except NameError:
    from importlib import reload

import align_objects_translate
reload(align_objects_translate)
align_objects_translate.align_translate()
