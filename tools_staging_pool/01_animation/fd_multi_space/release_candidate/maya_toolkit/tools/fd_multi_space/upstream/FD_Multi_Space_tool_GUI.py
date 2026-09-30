import maya.cmds as mc

def launch_script1(*args):
    import FD_Multi_Space_tool_reference as Multi_Space_1
    Multi_Space_1.create_ui()

def launch_script2(*args):
    import FD_Multi_Space_tool_no_reference as Multi_Space_2
    Multi_Space_2.create_ui()

def create_main_ui():
    if mc.window("MainUI", exists=True):
        mc.deleteUI("MainUI", window=True)

    mc.window("MainUI", title="Multi Space version", widthHeight=(200, 100))
    mc.columnLayout(adjustableColumn=True)
    mc.separator(height=15, style= 'none')
    mc.button(label="Multi Space (reference)", bgc=[.8, .5, 0], command=launch_script1)
    mc.separator(height=20)
    mc.button(label="Multi Space (open file)", command=launch_script2)
    mc.showWindow("MainUI")

create_main_ui()