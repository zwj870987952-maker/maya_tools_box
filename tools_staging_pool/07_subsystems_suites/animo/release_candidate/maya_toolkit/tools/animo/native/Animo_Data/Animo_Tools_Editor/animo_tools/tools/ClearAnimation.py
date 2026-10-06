import maya.cmds as cmds

def clear_animation():
    cb = cmds.channelBox("mainChannelBox", q=True, sma=True)
    
    if cb:
        cmds.cutKey(cl=True, at=cb)
    else:
        cmds.cutKey(cl=True)

clear_animation()
