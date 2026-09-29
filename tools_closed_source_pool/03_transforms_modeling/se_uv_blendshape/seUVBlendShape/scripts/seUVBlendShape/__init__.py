'''
This Python module contains useful tools to work with the seUVBlendShape
deformer plugin. The plugin already an associated built in
:doc:`MEL command <melCommand>` which this module uses.

Not only does this module provide functions you can use in your own tools, but
it also comes with a user interface. *(See ui module)* This can be opened by
calling the :py:func:`.launchEditor` function.::

    import seUVBlendShape
    seUVBlendShape.launchEditor()

Upon importing this module, an attempt to load the plug-in will be peformed.
No special Python libary requirements are needed. Maya provides all
neccessary modules.

.. note::

    Undo operations are limited to only creating a new deformer node. It is not currently
    supported to undo any editing (adding, removing, rebinding, etc) operations.
'''
from __future__ import absolute_import

__author__ = 'Scott Englert - seuvblendshape@scottenglert.com'
__version__ = "3.0"

from .core import *

def launchEditor():
    '''
    Launch the seUVBlendShape editor. Only available if called from an
    interactive Maya session.
    '''
    if not cmds.about(b=True):
        from . import ui
        ui.launchEditor()
    else:
        cmds.warning('You can not launch the editor in batch mode.')
