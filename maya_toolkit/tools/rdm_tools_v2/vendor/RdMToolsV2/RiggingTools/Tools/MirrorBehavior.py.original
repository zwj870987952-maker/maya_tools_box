from maya import cmds

def mirrorParts(world = False, *args):
    
    sel = cmds.ls(sl=True)
    GroupVar =cmds.group(sel[0], n = str(sel[0])+'_Mirror')
    if world:
        cmds.xform(GroupVar,rp=(0,0,0), sp=(0,0,0))
    
    cmds.setAttr(str(GroupVar)+'.rx', 180)
    cmds.setAttr(str(GroupVar)+'.sx', -1)
    cmds.setAttr(str(GroupVar)+'.sy', -1)
    cmds.setAttr(str(GroupVar)+'.sz', -1)


#mirrorParts()
#mirrorParts(world = True)