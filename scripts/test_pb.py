import maya.cmds as cmds
try:
    cmds.playblast(startTime=1, endTime=2, format='image', compression='png', viewer=False, width=640, height=480, framePadding=4)
    print("Playblast test with width/height worked!")
except Exception as e:
    print("Error with width/height:", e)
