import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.OpenMaya as OpenMaya

from . import main

def run():
	
	global win

	open_windows = cmds.lsUI(windows=True)

	for obj in open_windows:
		if obj.find("UISetup_DirCycleTool") != -1:
			cmds.deleteUI(obj)

	win = main.UISetup_DirCycleTool()

	win.show(dockable = True)

run()
