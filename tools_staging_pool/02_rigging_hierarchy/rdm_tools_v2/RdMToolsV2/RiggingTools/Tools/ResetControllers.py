"""
--------------------------------------------------------------------------------------------------------------------
resetControllers.py - Python Script
--------------------------------------------------------------------------------------------------------------------
Copyright 2012 Carlos Chacon L. All rights reserved.

DESCRIPTION:
Resets the selected controllers to their default value.

USAGE:
*Select the controllers to be reset.
*Run the script.

AUTHOR:
Carlos Chacon L. (caedo.00 at gmail dot com)
--------------------------------------------------------------------------------------------------------------------
"""

import maya.cmds as cmds

def isSingleAttribute(attr, obj):
	"""
    	Checks if the attr is single or multiple value.
    	"""
    	return True if (cmds.attributeQuery(attr, node=obj, nc=True) is None) else False

def resetController(controller):
	"""
	Resets to zero all the non-locked attributes from a controller
	"""
	controller_attrs = cmds.listAttr(controller, k=True)
	for attr in controller_attrs:
		if(isSingleAttribute(attr, controller)):
			default_value = cmds.attributeQuery(attr, ld=True, node=controller)[0]
			try:
				cmds.setAttr(controller+"."+attr, default_value)
			except:
				pass

def resetControllers(controllers):
	"""
	Resets multiple controllers.
	"""
	if(len(controllers) > 0):
		for controller in controllers:
			resetController(controller)
		print "Controllers reset successfully"
	else:
		print "No Controllers selected"

resetControllers(cmds.ls(sl=True))

