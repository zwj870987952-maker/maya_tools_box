'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Select 1 vertex and run with:

import maya_toolkit.tools.anim_polish_premium_v1_23.vendor.animPolish.copyPasteAttrs as copyPasteAttrs
reload (copyPasteAttrs)
copyPasteAttrs.func ()

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
from maya_toolkit.tools.anim_polish_premium_v1_23 import state as _state
import maya_toolkit.tools.anim_polish_premium_v1_23.vendor.animPolish as jsap
reload (jsap)



def copy (path = '', k = 0):

	return _state.copy_attrs(path,k)



def paste (path = ''):

	return _state.paste_attrs(path)
