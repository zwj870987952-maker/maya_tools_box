from maya import cmds

def DisplaySize(value,*args): 
    cmds.jointDisplayScale(value)

    
#lambda x:DIsplaySize(float(x))